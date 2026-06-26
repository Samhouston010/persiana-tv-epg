#!/usr/bin/env python3
"""Simple HTTP server to serve IPTV playlist and EPG files."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import os
import urllib.request
import urllib.parse

PORT = 8888
BASE = Path(__file__).parent

# HLS channels to proxy through this server (base URL → path prefix)
HLS_PROXIES = {
    '/eclub/': 'https://dash2.antik.sk/live/test_ectv_hd_1200/',
}

def proxy_url_for(path, server_host):
    for prefix, base in HLS_PROXIES.items():
        if path.startswith(prefix):
            return base + path[len(prefix):]
    return None

def rewrite_hls(content: bytes, path_prefix: str, server_host: str) -> bytes:
    """Rewrite relative URLs in HLS playlist to go through this proxy."""
    text = content.decode('utf-8', errors='replace')
    lines = text.splitlines()
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            # relative URL (segment or sub-playlist)
            if not stripped.startswith('http'):
                line = f'http://{server_host}/{path_prefix.lstrip("/")}{stripped}'
        out.append(line)
    return '\n'.join(out).encode('utf-8')

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        # Check HLS proxy routes first
        upstream = proxy_url_for(self.path, self.server.server_address[0] or 'localhost')
        if upstream:
            self._proxy(upstream)
            return

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

    def _proxy(self, upstream_url):
        try:
            req = urllib.request.Request(upstream_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = r.read()
                ctype = r.headers.get('Content-Type', 'application/octet-stream')
        except Exception:
            self.send_error(502)
            return

        # rewrite m3u8 playlists so segment URLs go through our proxy
        if 'm3u' in ctype or self.path.endswith('.m3u8'):
            # find which proxy prefix this path belongs to
            for prefix in HLS_PROXIES:
                if self.path.startswith(prefix):
                    data = rewrite_hls(data, prefix, self.headers.get('Host', f'181.214.140.229:{PORT}'))
                    break
            ctype = 'application/x-mpegurl'

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
