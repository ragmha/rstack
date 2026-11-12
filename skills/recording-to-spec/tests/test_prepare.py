import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "prepare.py"
SPEC = importlib.util.spec_from_file_location("prepare", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
prepare = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = prepare
SPEC.loader.exec_module(prepare)


class CaptionsTests(unittest.TestCase):
    def test_vtt_metadata_markup_and_multiline_text(self):
        segments = prepare.parse_captions(
            "\ufeffWEBVTT\r\n\r\nNOTE recording notes\r\nnot a cue\r\n\r\n"
            "STYLE\r\n::cue { color: white; }\r\n\r\n"
            "intro\r\n00:00.100 --> 00:01.200 align:start\r\n"
            "<v Speaker><b>Open</b> tasks &amp; edit.</v>\r\nKeep the title.\r\n", 3,
        )
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].text, "Open tasks & edit.\nKeep the title.")
        self.assertEqual((segments[0].start_seconds, segments[0].end_seconds), (0.1, 1.2))

    def test_srt_comma_times_and_overlapping_cues(self):
        segments = prepare.parse_captions(
            "1\n00:00:00,000 --> 00:00:02,000\nFirst\n\n"
            "2\n00:00:01,500 --> 00:00:03,000\nSecond\n", 3,
        )
        self.assertEqual([segment.id for segment in segments], ["T001", "T002"])
        self.assertEqual(segments[1].start_seconds, 1.5)

    def test_rejects_malformed_reversed_empty_and_out_of_range_captions(self):
        cases = [
            "This is an untimed transcript.",
            "00:00.000 --> tomorrow\nText",
            "00:02.000 --> 00:01.000\nText",
            "00:01.000 --> 00:02.000",
            "00:00.000 --> 00:03.501\nBeyond tolerance",
            "00:03.000 --> 00:03.100\nStarts after recording",
            "00:01.000 --> 00:02.000\nOne\n\n00:00.000 --> 00:01.000\nTwo",
            "WEBVTT\n\nNOTE no speech cues",
        ]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(prepare.EvidenceError):
                prepare.parse_captions(text, 3)

    def test_end_rounding_tolerance_is_bounded(self):
        self.assertEqual(prepare.parse_captions("00:00.000 --> 00:03.500\nEnd", 3)[0].end_seconds, 3.5)


class SelectionTests(unittest.TestCase):
    def test_dense_early_scenes_do_not_displace_timeline_coverage(self):
        times = prepare.choose_times(120, [index / 10 for index in range(100)], 8)
        self.assertLessEqual(len(times), 8)
        self.assertEqual(times[0], 0)
        self.assertAlmostEqual(times[-1], 119.9)
        self.assertTrue(any(39 < value < 41 for value in times))
        self.assertTrue(any(79 < value < 81 for value in times))
        self.assertTrue(any(0 < value < 10 for value in times))
        self.assertEqual(times, sorted(set(times)))

    def test_short_recording_and_single_frame_budget(self):
        self.assertEqual(prepare.choose_times(0.04, [0.03], 16), [0])
        self.assertEqual(prepare.choose_times(60, [10, 20], 1), [0])

    def test_invalid_budget_or_duration_is_rejected(self):
        for duration, budget in [(0, 3), (float("nan"), 3), (4, 0), (4, 49)]:
            with self.subTest(duration=duration, budget=budget), self.assertRaises(prepare.EvidenceError):
                prepare.choose_times(duration, [], budget)


class BoundaryTests(unittest.TestCase):
    def test_remote_inputs_are_rejected(self):
        for value in ("https://example.com/video.mp4", "file:///video.mp4", r"\\server\video.mp4"):
            with self.subTest(value=value), self.assertRaisesRegex(prepare.EvidenceError, "local file"):
                prepare.local_file(value)

    def test_media_reader_diagnostic_survives_failure(self):
        with patch.object(prepare.subprocess, "run", side_effect=subprocess.CalledProcessError(
            1, ["ffmpeg"], stderr="Unsupported codec",
        )):
            with self.assertRaisesRegex(prepare.EvidenceError, "Unsupported codec"):
                prepare.execute(["ffmpeg"])

    def test_transcription_without_audio_is_not_silently_skipped(self):
        with self.assertRaisesRegex(prepare.EvidenceError, "no audio"), patch.object(prepare, "execute") as run:
            prepare.transcribe(Path("source.mp4"), prepare.Media(3, 320, 180, 0, False),
                               Path("model.bin"), "whisper-cli", "ffmpeg", "en", Path("."))
        run.assert_not_called()

    def test_whisper_requires_actual_caption_output_and_cleans_audio(self):
        with tempfile.TemporaryDirectory() as temporary:
            scratch = Path(temporary)
            media = prepare.Media(3, 320, 180, 0, True)

            def fake_run(arguments, timeout=600):
                if arguments[0] == "whisper-cli":
                    prefix = Path(arguments[arguments.index("-of") + 1])
                    prefix.with_suffix(".srt").write_text(
                        "1\n00:00:00,000 --> 00:00:01,000\nOpen tasks.\n", encoding="utf-8",
                    )
                else:
                    Path(arguments[-1]).write_bytes(b"temporary audio")

            with patch.object(prepare, "execute", side_effect=fake_run):
                segments = prepare.transcribe(Path("source.mp4"), media, Path("model.bin"),
                                              "whisper-cli", "ffmpeg", "en", scratch)
            self.assertEqual(segments[0].text, "Open tasks.")
            self.assertEqual(list(scratch.iterdir()), [])
            with patch.object(prepare, "execute"):
                with self.assertRaisesRegex(prepare.EvidenceError, "without producing"):
                    prepare.transcribe(Path("source.mp4"), media, Path("model.bin"),
                                       "whisper-cli", "ffmpeg", "en", scratch)
            self.assertEqual(list(scratch.iterdir()), [])


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "Integration tests require FFmpeg.")
class MediaIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.source = cls.root / "sample [local]; recording.mp4"
        subprocess.run([
            shutil.which("ffmpeg"), "-nostdin", "-v", "error",
            "-f", "lavfi", "-i", "color=c=red:size=320x180:rate=10:duration=1",
            "-f", "lavfi", "-i", "color=c=green:size=320x180:rate=10:duration=1",
            "-f", "lavfi", "-i", "color=c=blue:size=320x180:rate=10:duration=1",
            "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0",
            "-c:v", "mpeg4", "-q:v", "3", str(cls.source),
        ], check=True, capture_output=True, timeout=60)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, arguments)],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )

    def test_real_video_produces_timestamped_images_and_aligned_transcript(self):
        output = self.root / "with transcript"
        captions = self.root / "narration.vtt"
        captions.write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nThe first screen is red.\n", encoding="utf-8")
        result = self.cli(self.source, "--output", output, "--max-frames", 6, "--transcript", captions)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((output / "evidence.json").read_text(encoding="utf-8"))
        self.assertTrue(3 <= len(data["frames"]) <= 6)
        self.assertTrue(any(1 <= frame["seconds"] < 1.4 for frame in data["frames"]))
        self.assertTrue(any(2 <= frame["seconds"] < 2.4 for frame in data["frames"]))
        self.assertEqual(data["source"]["duration_seconds"], 3)
        self.assertFalse(data["source"]["has_audio"])
        self.assertEqual(data["transcript"]["segments"][0]["text"], "The first screen is red.")
        self.assertEqual(len(data["source"]["sha256"]), 64)
        self.assertNotIn(str(self.root), json.dumps(data))
        for frame in data["frames"]:
            self.assertTrue(0 <= frame["seconds"] < 3)
            self.assertEqual((output / frame["image"]).read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            pixel = subprocess.run([
                shutil.which("ffmpeg"), "-nostdin", "-v", "error", "-i", str(output / frame["image"]),
                "-vf", "crop=1:1:0:0,format=rgb24", "-frames:v", "1",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
            ], capture_output=True, check=True, timeout=30).stdout
            expected_channel = min(2, int(frame["seconds"]))
            self.assertEqual(max(range(3), key=lambda channel: pixel[channel]), expected_channel)
        self.assertFalse((output / "spec.md").exists())
        self.assertTrue((output / "evidence.md").is_file())
        self.assertFalse(list(self.root.glob(".recording-evidence-*")))

    def test_existing_output_even_if_empty_is_never_replaced(self):
        output = self.root / "existing"
        output.mkdir()
        result = self.cli(self.source, "--output", output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr)
        self.assertEqual(list(output.iterdir()), [])

    def test_invalid_video_leaves_no_success_bundle(self):
        source = self.root / "broken.mp4"
        source.write_text("not a recording", encoding="utf-8")
        output = self.root / "broken-output"
        result = self.cli(source, "--output", output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ffprobe", result.stderr)
        self.assertFalse(output.exists())

    def test_invalid_caption_alignment_leaves_no_success_bundle(self):
        captions = self.root / "late.srt"
        captions.write_text("1\n00:00:03,000 --> 00:00:04,000\nToo late.\n", encoding="utf-8")
        output = self.root / "late-output"
        result = self.cli(self.source, "--output", output, "--transcript", captions)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("align the transcript", result.stderr)
        self.assertFalse(output.exists())

    def test_caption_encoding_error_is_actionable(self):
        captions = self.root / "wrong-encoding.srt"
        captions.write_bytes(b"1\n00:00:00,000 --> 00:00:01,000\nCaf\xe9\n")
        output = self.root / "encoding-output"
        result = self.cli(self.source, "--output", output, "--transcript", captions)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("UTF-8", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(output.exists())

    def test_requested_speech_on_silent_video_fails_clearly(self):
        model = self.root / "dummy-model.bin"
        model.write_bytes(b"not used")
        with patch.object(prepare, "tool", side_effect=lambda name: shutil.which(name) or name):
            args = prepare.argparse.Namespace(
                recording=str(self.source), output=str(self.root / "no-audio"),
                transcript=None, whisper_model=str(model), whisper_cli="whisper-cli",
                language="en", max_frames=6,
            )
            with self.assertRaisesRegex(prepare.EvidenceError, "no audio stream"):
                prepare.prepare(args)


if __name__ == "__main__":
    unittest.main()
