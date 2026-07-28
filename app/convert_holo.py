#!/usr/bin/env python3

from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

MAX_INPUT_BYTES = 500 * 1024 * 1024
ALLOWED_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".webm",
}


def fail(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def run_command(command: list[str], timeout: int) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        fail(f"Command timed out after {timeout} seconds")
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip()
        fail(detail or "Command failed")


def probe_video(path: Path) -> dict:
    result = run_command(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries",
            "stream=codec_name,width,height,pix_fmt,duration",
            "-of", "json",
            str(path),
        ],
        timeout=20,
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        fail("ffprobe returned invalid JSON")

    streams = data.get("streams", [])

    if not streams:
        fail("No video stream found")

    return streams[0]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Universal Dragon HoloCore safe MP4 preprocessor"
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    output_path = args.output.expanduser().resolve()

    if not input_path.is_file():
        fail(f"Input file not found: {input_path}")

    if input_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        fail(f"Unsupported input extension: {input_path.suffix}")

    input_size = input_path.stat().st_size

    if input_size <= 0:
        fail("Input file is empty")

    if input_size > MAX_INPUT_BYTES:
        fail("Input exceeds 500 MB safety limit")

    if shutil.which("ffmpeg") is None:
        fail("ffmpeg not found")

    if shutil.which("ffprobe") is None:
        fail("ffprobe not found")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
        mode=0o700,
    )

    free_bytes = shutil.disk_usage(output_path.parent).free

    if free_bytes < max(input_size * 3, 1024 * 1024 * 1024):
        fail("Not enough free disk space")

    before = probe_video(input_path)

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", str(input_path),
        "-map", "0:v:0",
        "-an",
        "-vf",
        (
            "scale=512:512:"
            "force_original_aspect_ratio=decrease,"
            "pad=512:512:(ow-iw)/2:(oh-ih)/2:color=black,"
            "setsar=1,"
            "fps=30"
        ),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path),
    ]

    run_command(command, timeout=300)

    if not output_path.is_file() or output_path.stat().st_size == 0:
        fail("Output file was not created")

    after = probe_video(output_path)

    print(json.dumps(
        {
            "status": "PASS",
            "stage": "MP4 preprocessing only",
            "fan_bin_ready": False,
            "input": {
                "path": str(input_path),
                "size_bytes": input_size,
                "video": before,
            },
            "output": {
                "path": str(output_path),
                "size_bytes": output_path.stat().st_size,
                "video": after,
            },
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
