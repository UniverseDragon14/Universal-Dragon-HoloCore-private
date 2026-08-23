# Universal Dragon HoloCore

A localhost-only prototype for validating and preprocessing video assets intended for a future holographic display workflow.

## Implemented

- safe input validation for common video containers
- a 500 MB input limit
- `ffprobe` metadata inspection
- FFmpeg conversion to a 512×512, 30 FPS, H.264 MP4 preview
- JSON conversion results
- a loopback-only status page and health endpoint

## Current boundary

The repository currently implements MP4 preview preprocessing only. Fan-specific BIN conversion and wireless upload are not implemented and remain disabled.

## Requirements

- Python 3
- `ffmpeg`
- `ffprobe`
- at least 1 GB free disk space, or three times the input size

## Convert a video

```bash
python3 app/convert_holo.py input.mp4 runtime/processed/output.mp4
```

Supported input extensions:

```text
.mp4 .mov .mkv .avi .webm
```

Audio is removed. The output is scaled and padded to 512×512, converted to H.264/YUV420p, and prepared for progressive playback.

## Run the local status server

```bash
python3 app/public_server.py
```

Open:

```text
http://127.0.0.1:8095/
http://127.0.0.1:8095/health
```

The service binds only to `127.0.0.1`; it is not exposed publicly by this code.

## Repository layout

- `app/convert_holo.py` — validated video preprocessor
- `app/public_server.py` — local status page and health endpoint
- `app/health_server.py` — extended local health reporting
- `runtime/processed/` — generated preview output
- `runtime/tmp/` — temporary input/output workspace
