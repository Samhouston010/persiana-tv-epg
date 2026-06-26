#!/usr/bin/env python3
"""Simple HTTP server to serve IPTV playlist and EPG files."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import os

PORT = 8888
BASE = Path(__file__).parent

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress access logs

    def do_GET(self):
        path = self.path.lstrip("/") or "final.m3u"
        file = BASE / path
        if not file.exists() or not file.is_file():
            self.send_error(404)
            return
        ext = file.suffix.lower()
        types = {".m3u": "application/x-mpegurl", ".m3u8": "application/x-mpegurl",
                 ".gz": "application/gzip", ".xml": "application/xml"}
        ctype = types.get(ext, "application/octet-stream")
        data = file.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(data))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    os.chdir(BASE)
    print(f"Serving on port {PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
