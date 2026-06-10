import requests
from requests_oauthlib import OAuth1

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CONSUMER_KEY = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, signature_method="HMAC-SHA1")

endpoints = [
    "/epg/channels", "/channels", "/channel", "/epg/channel",
    "/tv/channels", "/tv/list", "/live/channels", "/epg/list",
    "/channel/all", "/tvchannel", "/epg/tvchannel"
]

for ep in endpoints:
    try:
        r = requests.get(f"{API_BASE}{ep}", auth=auth, timeout=10)
        print(f"{ep}: HTTP {r.status_code}", end="")
        if r.status_code == 200:
            print(f" <-- WORKS! | {r.text[:150]}")
        else:
            print()
    except Exception as e:
        print(f"{ep}: ERR {str(e)[:30]}")
