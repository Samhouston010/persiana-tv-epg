"""Keshet Channel 12 proxy — ngt token (no geo-lock), refreshes every 10 min, proxies via EasyProxy."""
import requests, json, time, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import quote

TOKEN_URL = "https://mass.mako.co.il/ClicksStatistics/entitlementsServicesV2.jsp"
STREAM_PATH = "/direct/hls/live/2033791/k12/index.m3u8"
CDN = "https://mako-streaming.akamaized.net"
SERVER_IP = "181.214.140.229"
PORT = 8891

_token = {"ticket": "", "ts": 0}

def refresh_token():
    while True:
        try:
            r = requests.post(TOKEN_URL,
                params={"et": "ngt", "lp": STREAM_PATH + "?as=1", "rv": "AKAMAI"},
                timeout=15)
            _token["ticket"] = r.json()["tickets"][0]["ticket"]
            _token["ts"] = time.time()
            print("Token OK", flush=True)
        except Exception as e:
            print(f"Token fail: {e}", flush=True)
        time.sleep(600)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not _token["ticket"]:
            self.send_error(503)
            return
        url = CDN + STREAM_PATH + "?" + _token["ticket"]
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()
    def log_message(self, *a):
        pass

threading.Thread(target=refresh_token, daemon=True).start()
time.sleep(3)
print(f"Keshet12 on port {PORT}", flush=True)
HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
