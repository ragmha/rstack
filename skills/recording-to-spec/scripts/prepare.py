#!/usr/bin/env python3
"""Prepare local recording evidence. Copilot, not this script, authors the spec."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


class EvidenceError(Exception):
    """An actionable input, dependency, or media-processing failure."""


@dataclass(frozen=True)
class Media:
    duration: float
    width: int
    height: int
    video_stream: int
    has_audio: bool


@dataclass(frozen=True)
class Segment:
    id: str
    start_seconds: float
    end_seconds: float
    text: str


def tool(name: str) -> str:
    executable = shutil.which(name)
    if not executable:
        raise EvidenceError(f"Missing executable: {name}. Install it or add it to PATH.")
    return executable


def execute(arguments: list[str], timeout: int = 600) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            arguments,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "No diagnostic output.").strip()
        raise EvidenceError(f"{Path(arguments[0]).name} failed:\n{detail[-3000:]}") from error
    except subprocess.TimeoutExpired as error:
        raise EvidenceError(
            f"{Path(arguments[0]).name} exceeded {timeout} seconds. Use a shorter recording."
        ) from error


def local_file(value: str, extensions: set[str] | None = None) -> Path:
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", value) or value.startswith(("\\\\", "//")):
        raise EvidenceError("Use a local file, not a URL or network share.")
    path = Path(value).expanduser().resolve(strict=True)
    if not path.is_file():
        raise EvidenceError(f"Not a file: {path}")
    if extensions and path.suffix.lower() not in extensions:
        raise EvidenceError(f"Unsupported file type {path.suffix!r}; expected {', '.join(sorted(extensions))}.")
    if path.stat().st_size == 0:
        raise EvidenceError(f"Empty file: {path}")
    return path


def probe(source: Path, ffprobe: str) -> Media:
    result = execute([
        ffprobe, "-v", "error", "-protocol_whitelist", "file",
        "-show_streams", "-show_format", "-of", "json", str(source),
    ])
    try:
        data = json.loads(result.stdout)
        video = next(
            (stream for stream in data["streams"]
             if stream.get("codec_type") == "video"
             and not stream.get("disposition", {}).get("attached_pic")),
            None,
        )
        if video is None:
            raise EvidenceError("The recording has no video stream.")
        duration = 0.0
        for value in (video.get("duration"), data.get("format", {}).get("duration")):
            try:
                candidate = float(value)
            except (TypeError, ValueError):
                continue
            if math.isfinite(candidate) and candidate > 0:
                duration = candidate
                break
        width, height = int(video["width"]), int(video["height"])
        if duration <= 0 or width <= 0 or height <= 0:
            raise EvidenceError("The recording needs a finite duration and valid video dimensions.")
        return Media(
            duration, width, height, int(video["index"]),
            any(stream.get("codec_type") == "audio" for stream in data["streams"]),
        )
    except (ValueError, KeyError, TypeError) as error:
        raise EvidenceError("ffprobe returned invalid recording metadata.") from error


def scene_times(source: Path, media: Media, ffmpeg: str) -> list[float]:
    result = execute([
        ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "info",
        "-protocol_whitelist", "file", "-i", str(source),
        "-map", f"0:{media.video_stream}", "-an", "-sn", "-dn",
        "-vf", "setpts=PTS-STARTPTS,fps=2,scale=320:-2,format=rgb24,select='gt(scene,0.28)',showinfo",
        "-f", "null", "-",
    ])
    return [float(value) for value in re.findall(r"pts_time:\s*([0-9.eE+-]+)", result.stderr)]


def choose_times(duration: float, scenes: list[float], budget: int) -> list[float]:
    if not math.isfinite(duration) or duration <= 0 or not 1 <= budget <= 48:
        raise EvidenceError("Use a positive finite duration and a frame budget between 1 and 48.")
    last = max(0.0, duration - 0.1)
    if budget == 1 or last == 0:
        return [0.0]
    count = min(budget, max(2, (budget + 1) // 2))
    selected = {last * index / (count - 1) for index in range(count)}
    candidates = {
        min(last, value + 0.15) for value in scenes
        if math.isfinite(value) and 0 <= value < duration
    }
    # Reserve uniform coverage before spending the remaining budget on changes.
    while candidates and len(selected) < budget:
        best = max(sorted(candidates), key=lambda value: min(abs(value - old) for old in selected))
        if min(abs(best - old) for old in selected) < min(0.35, duration / (2 * budget)):
            break
        selected.add(best)
        candidates.remove(best)
    return sorted({round(value, 3) for value in selected})


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    whole, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds_part = divmod(whole, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds_part:02}.{milliseconds:03}"


def caption_time(value: str) -> float:
    match = re.fullmatch(r"(?:(\d+):)?([0-5]\d):([0-5]\d)[.,](\d{3})", value)
    if not match:
        raise EvidenceError(f"Invalid caption timestamp: {value!r}")
    hours, minutes, seconds, milliseconds = match.groups()
    return int(hours or 0) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000


def parse_captions(text: str, duration: float) -> list[Segment]:
    segments: list[Segment] = []
    for block in re.split(r"\n\s*\n", text.lstrip("\ufeff").replace("\r\n", "\n").strip()):
        lines = block.strip().splitlines()
        if not lines:
            continue
        if lines[0].startswith("WEBVTT"):
            lines = lines[1:]
            if not any("-->" in line for line in lines):
                continue
        if not lines or re.match(r"^(NOTE(?:\s|$)|STYLE$|REGION$)", lines[0]):
            continue
        timing_lines = [index for index, line in enumerate(lines) if "-->" in line]
        if len(timing_lines) != 1 or timing_lines[0] > 1:
            raise EvidenceError("Each caption cue must contain one timestamp range and text.")
        index = timing_lines[0]
        match = re.fullmatch(r"(\S+)\s+-->\s+(\S+)(?:\s+.*)?", lines[index].strip())
        if not match:
            raise EvidenceError(f"Invalid caption timing: {lines[index]!r}")
        start, end = (caption_time(value) for value in match.groups())
        if end <= start or (segments and start < segments[-1].start_seconds):
            raise EvidenceError("Caption cues must have increasing start times and positive durations.")
        if start >= duration or end > duration + 0.5:
            raise EvidenceError("Caption timestamps extend beyond the recording; align the transcript first.")
        content = html.unescape(re.sub(r"<[^>]*>", "", "\n".join(lines[index + 1:]))).strip()
        if not content:
            raise EvidenceError("A caption cue contains no text.")
        segments.append(Segment(f"T{len(segments) + 1:03}", start, end, content))
    if not segments:
        raise EvidenceError("The transcript contains no timed caption cues.")
    return segments


def read_captions(path: Path, duration: float, allow_empty: bool = False) -> list[Segment]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise EvidenceError(f"Transcript must be UTF-8 encoded: {path.name}") from error
    return [] if allow_empty and not text.strip() else parse_captions(text, duration)


def transcribe(
    source: Path, media: Media, model: Path, whisper: str,
    ffmpeg: str, language: str, scratch: Path,
) -> list[Segment]:
    if not media.has_audio:
        raise EvidenceError("Local transcription was requested, but the recording has no audio stream.")
    with tempfile.TemporaryDirectory(prefix="speech-", dir=scratch) as temporary:
        folder = Path(temporary)
        audio, prefix = folder / "audio.wav", folder / "speech"
        execute([
            ffmpeg, "-nostdin", "-v", "error", "-protocol_whitelist", "file",
            "-i", str(source), "-map", "0:a:0", "-vn",
            "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(audio),
        ])
        execute([
            whisper, "-m", str(model), "-f", str(audio), "-l", language,
            "-osrt", "-of", str(prefix),
        ], timeout=3600)
        subtitles = prefix.with_suffix(".srt")
        if not subtitles.is_file():
            raise EvidenceError("whisper.cpp finished without producing the requested SRT file.")
        return read_captions(subtitles, media.duration, allow_empty=True)


def prepare(args: argparse.Namespace) -> Path:
    source = local_file(args.recording, {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"})
    output = Path(args.output).expanduser().resolve()
    if output.exists():
        raise EvidenceError(f"Output already exists; choose a new directory: {output}")
    ffmpeg, ffprobe = tool("ffmpeg"), tool("ffprobe")
    media = probe(source, ffprobe)
    transcript = local_file(args.transcript, {".srt", ".vtt"}) if args.transcript else None
    model = local_file(args.whisper_model) if args.whisper_model else None
    if model and not media.has_audio:
        raise EvidenceError("Local transcription was requested, but the recording has no audio stream.")
    whisper = tool(args.whisper_cli) if model else None
    segments = read_captions(transcript, media.duration) if transcript else []
    source_hash = hashlib.sha256()
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            source_hash.update(chunk)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".recording-evidence-", dir=output.parent) as temporary:
        stage = Path(temporary)
        if model and whisper:
            segments = transcribe(source, media, model, whisper, ffmpeg, args.language, stage)
        moments = choose_times(media.duration, scene_times(source, media, ffmpeg), args.max_frames)
        (stage / "frames").mkdir()
        frames = []
        for index, moment in enumerate(moments, 1):
            relative = f"frames/F{index:03}.png"
            destination = stage / relative
            execute([
                ffmpeg, "-nostdin", "-v", "error", "-protocol_whitelist", "file",
                "-ss", f"{moment:.3f}", "-i", str(source),
                "-map", f"0:{media.video_stream}", "-frames:v", "1",
                "-vf", "scale='min(iw,1600)':-2", "-update", "1", str(destination),
            ])
            if not destination.is_file() or destination.stat().st_size == 0:
                raise EvidenceError(f"No video frame was available at {timestamp(moment)}.")
            frames.append({
                "id": f"F{index:03}", "seconds": moment,
                "timestamp": timestamp(moment), "image": relative,
            })
        warnings = [
            "Frames are sampled, not an exhaustive interaction log. Transient states can be missed.",
            "Frame timestamps are seek positions, with precision limited by the recording's frame rate.",
        ]
        if media.has_audio and not transcript and not model:
            warnings.append("Audio is present but untranscribed; narration has not been reviewed.")
        if model and not segments:
            warnings.append("Local speech recognition produced no segments; this does not prove there is no speech.")
        if segments:
            warnings.append("Transcript statements are narration evidence, not proof of visible behavior or backend implementation.")
        evidence = {
            "schema_version": 1,
            "source": {
                "name": source.name, "sha256": source_hash.hexdigest(),
                "duration_seconds": media.duration, "width": media.width, "height": media.height,
                "has_audio": media.has_audio,
            },
            "frames": frames,
            "transcript": {
                "method": "provided" if transcript else "whisper.cpp" if model else "none",
                "segments": [asdict(segment) for segment in segments],
            },
            "limitations": warnings,
        }
        (stage / "evidence.json").write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n",
        )
        lines = [
            "# Recording evidence - not yet reviewed", "",
            "This is an evidence bundle, not a generated specification.",
            "Read `evidence.json`, inspect the images, and use the Copilot skill to draft the spec.", "",
            "| Evidence | Seek timestamp | Image |", "| --- | --- | --- |",
        ]
        lines.extend(f"| {frame['id']} | {frame['timestamp']} | [Open]({frame['image']}) |" for frame in frames)
        lines.extend(["", "## Coverage limits", ""])
        lines.extend(f"- {warning}" for warning in warnings)
        (stage / "evidence.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        # Reserve the destination exclusively; never replace even an empty directory.
        output.mkdir()
        for entry in sorted(stage.iterdir(), key=lambda path: path.name == "evidence.json"):
            entry.rename(output / entry.name)
    return output


def frame_budget(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Frame budget must be an integer between 1 and 48.") from error
    if not 1 <= number <= 48:
        raise argparse.ArgumentTypeError("Frame budget must be between 1 and 48.")
    return number


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recording", help="Local MP4, MOV, MKV, WebM, AVI, or M4V file; no URLs.")
    parser.add_argument("--output", required=True, help="New evidence directory; existing directories are never overwritten.")
    parser.add_argument("--max-frames", type=frame_budget, default=16, help="Image budget, 1-48 (default: 16).")
    speech = parser.add_mutually_exclusive_group()
    speech.add_argument("--transcript", help="Aligned local SRT or WebVTT transcript.")
    speech.add_argument("--whisper-model", help="Existing local whisper.cpp model file; nothing is downloaded.")
    parser.add_argument("--whisper-cli", default="whisper-cli", help="Local whisper.cpp executable, used with --whisper-model.")
    parser.add_argument("--language", default="en", help="Speech language for whisper.cpp (default: en).")
    args = parser.parse_args()
    if not args.whisper_model and (args.whisper_cli != "whisper-cli" or args.language != "en"):
        parser.error("--whisper-cli and --language require --whisper-model.")
    try:
        output = prepare(args)
    except (EvidenceError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Evidence prepared: {output}")
    print("No specification has been generated yet. Inspect the evidence with the Copilot skill.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
