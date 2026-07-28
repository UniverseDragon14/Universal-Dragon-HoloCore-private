#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import shutil
import subprocess
import time

HOST = "127.0.0.1"
PORT = 8095
BASE = Path.home() / "Universal-Dragon-HoloCore"


def ffmpeg_status():
    path = shutil.which("ffmpeg")

    if not path:
        return {
            "available": False,
            "path": None,
            "version": None,
        }

    try:
        result = subprocess.run(
            [path, "-version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        first_line = result.stdout.splitlines()[0] if result.stdout else None

        return {
            "available": result.returncode == 0,
            "path": path,
            "version": first_line,
        }

    except Exception as exc:
        return {
            "available": False,
            "path": path,
            "version": None,
            "error": str(exc),
        }


def health_data():
    usage = shutil.disk_usage(BASE)

    return {
        "service": "Universal Dragon HoloCore",
        "status": "healthy",
        "mode": "localhost-only",
        "fan_upload_enabled": False,
        "converter_enabled": False,
        "base_directory": str(BASE),
        "disk_free_gb": round(usage.free / (1024 ** 3), 2),
        "ffmpeg": ffmpeg_status(),
        "timestamp": int(time.time()),
    }


class HoloHandler(BaseHTTPRequestHandler):
    server_version = "UD-HoloCore/0.1"

    def send_common_headers(self, content_type, content_length):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'",
        )
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            payload = json.dumps(
                health_data(),
                indent=2,
            ).encode("utf-8")

            self.send_common_headers(
                "application/json; charset=utf-8",
                len(payload),
            )
            self.wfile.write(payload)
            return

        if self.path == "/":
            html = b"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Universal Dragon HoloCore</title>
<style>
body {
  background:#080b10;
  color:#e8f7ff;
  font-family:system-ui,sans-serif;
  max-width:700px;
  margin:50px auto;
  padding:20px;
}
.card {
  border:1px solid #37536b;
  border-radius:16px;
  padding:24px;
  background:#101720;
}
.ok { color:#67ff9b; }
code { color:#7fdcff; }
</style>
</head>
<body>
<div class="card">
<h1>Universal Dragon HoloCore</h1>
<p class="ok">Health server is running safely.</p>
<p>Binding: <code>127.0.0.1:8095</code></p>
<p>Converter: disabled</p>
<p>Fan upload: disabled</p>
<p>Current stage: isolated local verification</p>
</div>
</body>
</html>"""

            self.send_common_headers(
                "text/html; charset=utf-8",
                len(html),
            )
            self.wfile.write(html)
            return

        self.send_error(404, "Not Found")

    def log_message(self, fmt, *args):
        print(
            f"{self.client_address[0]} "
            f"[{self.log_date_time_string()}] "
            f"{fmt % args}",
            flush=True,
        )


if __name__ == "__main__":
    print(f"HoloCore listening on http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), HoloHandler).serve_forever()
