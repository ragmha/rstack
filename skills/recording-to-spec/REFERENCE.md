# Recording to spec reference

## Requirements

- Python 3.10 or later; no third-party Python packages.
- FFmpeg, with `ffmpeg` and `ffprobe` on PATH.
- An agent/client capable of inspecting images.
- Optional: an aligned UTF-8 SRT/WebVTT transcript, or an existing local
  whisper.cpp executable and model.

The extractor does not install dependencies, download models, or upload media.
Keep whisper.cpp's executable and companion libraries together and use a build
matching the machine. Windows uses Python directly; Git Bash and WSL are not
required.

## Commands

Resolve the actual installed skill directory first. These examples run from
that directory, not from an assumed agent-specific installation path.

```powershell
python scripts\prepare.py 'C:\Recordings\task-demo.mp4' `
  --output 'C:\Work\specs\task-demo' `
  --max-frames 16
```

On macOS/Linux, use `python3` and native paths. The script passes argument arrays
to media tools rather than using shell interpolation.

Add exactly one optional transcription source:

```powershell
--transcript 'C:\Recordings\task-demo.vtt'
```

```powershell
--whisper-model 'C:\Models\ggml-small.bin' `
--whisper-cli 'C:\Tools\whisper\whisper-cli.exe' `
--language en
```

Transcription is opt-in. Supplied captions must align with the recording, with
at most 0.5 seconds of end-time rounding. Without captions or a model, existing
audio is explicitly marked unreviewed. Speech language defaults to English;
select a language supported by the model.

Example agent request:

```text
Turn C:\Recordings\task-demo.mp4 into a draft specification.
Put the evidence and documents in C:\Work\specs\task-demo.
Separate what is visible from what is inferred.
```

## Evidence bundle

| File | Producer and purpose |
| --- | --- |
| `evidence.json` | Extractor: source SHA-256, frame IDs/times, transcript segments, and limitations. |
| `evidence.md` | Extractor: human-readable frame index, not a specification. |
| `frames/F001.png` | Extractor: sampled screenshots, up to 1600 pixels wide. |
| `spec.md` | Agent: draft requirements after actual image inspection. |
| `ui-evidence.md` | Agent: observations linked to frames and requirements. |

IDs are stable within one bundle, not across runs with different sampling.
The source video is never copied into the bundle; temporary speech audio is
removed after processing. Absolute input paths are not included in the manifest,
but the original filename is, and it can itself be sensitive.

The destination must be new, even if an existing directory is empty. Preparation
uses a temporary sibling directory, then reserves the destination exclusively
and moves the manifest last. An interrupted final move can leave partial files;
a directory without `evidence.json` is incomplete. Use a new destination to retry.

## Claim classification

| Basis | Meaning |
| --- | --- |
| Observed | A visible screen state or behavior directly supported by inspected frames. |
| Narrated | A timed transcript claim, not independently demonstrated. |
| Inferred | A plausible explanation requiring confirmation. |
| Proposed | A requested or suggested future requirement, not evidence of the current app. |

## Document contract

### spec.md

1. **Purpose and scope**: visible task, actor, boundaries, and draft status.
2. **Recorded workflow**: supported actions and before/after states, with IDs.
3. **Requirements**: a table of `REQ-001`-style IDs, behavior, claim classification,
   and evidence IDs or "not recorded."
4. **Acceptance criteria**: testable Given/When/Then outcomes linked to each
   requirement. Mark unrecorded conditions as proposed, never observed.
5. **Unknowns and decisions**: unresolved behavior and the question or additional
   evidence needed to resolve it. Do not silently choose implementation details.
6. **Out of scope**: features the recording cannot establish or the user excluded.

Plain Markdown is the output. It can fit an existing specification workflow
without depending on or claiming to initialize Spec Kit.

### ui-evidence.md

Include a chronological table of frame ID, seek timestamp, relative image link,
directly visible observation, and related requirement IDs. Include relevant
transcript IDs and text excerpts as **narrated claims**.

Carry over material sampling and transcription limitations. Note unreadable
text, ambiguous transitions, and states not captured. Do not turn a narrated
claim into a visible observation merely because it sounds plausible.

## Sampling and limits

Approximately half the image budget is reserved for evenly spaced coverage,
including the start and end. Scene changes fill the remaining budget, favoring
gaps in existing samples. Detection runs at two frames per second on reduced-
resolution RGB frames so color-only changes can contribute. The default budget
is 16 and the hard cap is 48; static videos may yield fewer images. A budget of
one captures only the start.

Sampling can miss clicks, brief dialogs, loading/error states, and subtle
changes. Frame times are seek positions, not exact interaction timestamps.
Narration and speech recognition can be inaccurate. Request focused evidence
when important behavior is missing.

Supported inputs are local MP4, MOV, MKV, WebM, AVI, and M4V files. V1 does not
download URLs, use cloud transcription, create a hosted application, or generate
implementation code. Media operations time out after ten minutes; local speech
recognition has a one-hour timeout.

## Privacy and sharing

FFmpeg input protocols are restricted to files; the preparation script has no
upload or telemetry integration. This is not a sandbox for hostile media:
use trusted recordings and current media tools.

Agent analysis is **not offline processing**. Inspected images and transcript
text enter the current model context. Use only material authorized for that
environment, or provide a redacted recording first.

Frames, captions, source filenames, and drafts can expose sensitive information.
Nothing is automatically published. Review the exact content, destination,
disclosure authority, and third-party rights before sharing. Local scanners
cannot determine confidentiality, permission, announcement authority, or
internal/pre-release terminology.

## Development

From this skill directory:

```powershell
python -m unittest discover -s tests -v
```

With FFmpeg installed, the tests generate a synthetic video and exercise real
extraction, frame colors, scene changes, caption alignment, output preservation,
and failure handling. Without FFmpeg, media integration tests are explicitly
skipped. No real recording, screenshot, or transcript is committed.

The whisper.cpp adapter is tested at its process boundary with simulated
caption output. A specific model/build still needs a local speech smoke test.
