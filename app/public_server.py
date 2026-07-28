#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import time

HOST = "127.0.0.1"
PORT = 8095


class Handler(BaseHTTPRequestHandler):
    server_version = "UD-HoloCore/0.1"

    def send_ok_headers(self, content_type: str, length: int) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'",
        )
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            data = json.dumps({
                "service": "Universal Dragon HoloCore",
                "status": "healthy",
                "converter": "preview-ready",
                "fan_bin": "not-ready",
                "upload": "disabled",
                "timestamp": int(time.time()),
            }).encode()

            self.send_ok_headers(
                "application/json; charset=utf-8",
                len(data),
            )
            self.wfile.write(data)
            return

        if self.path == "/":
            page = b"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Universal Dragon HoloCore</title>
<style>
body {
  margin:0;
  min-height:100vh;
  display:grid;
  place-items:center;
  background:#070b12;
  color:#eef8ff;
  font-family:system-ui,sans-serif;
}
main {
  width:min(720px,85%);
  padding:32px;
  border:1px solid #31506b;
  border-radius:20px;
  background:#101923;
}
h1 { margin-top:0; }
.ok { color:#6dffa0; }
code { color:#75dfff; }
</style>
</head>
<body>
<main>
<h1>Universal Dragon HoloCore</h1>
<p class="ok">HoloCore bridge is online.</p>
<p>MP4 preprocessing: <code>READY</code></p>
<p>Fan BIN conversion: <code>UNDER ANALYSIS</code></p>
<p>Fan wireless upload: <code>DISABLED</code></p>
</main>
</body>
</html>"""

            self.send_ok_headers(
                "text/html; charset=utf-8",
                len(page),
            )
            self.wfile.write(page)
            return

        self.send_error(404, "Not Found")

    def log_message(self, fmt: str, *args) -> None:
        print(
            f"{self.client_address[0]} "
            f"{self.log_date_time_string()} "
            f"{fmt % args}",
            flush=True,
        )


if __name__ == "__main__":
    print(f"HoloCore listening on {HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
