import requests, json
from requests_oauthlib import OAuth1
from datetime import datetime, timezone

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CONSUMER_KEY = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, signature_method="HMAC-SHA1")

# امتحان endpoint هایی که ممکنه نام کانال بدن
for ep in ["/epg/livechannel", "/live/list", "/epg", "/livestream/list", "/channel/list/all", "/epg/channellist", "/program/channels"]:
    try:
        r = requests.get(f"{API_BASE}{ep}", auth=auth, timeout=8)
        if r.status_code == 200:
            print(f"{ep}: WORKS")
            print(r.text[:500])
            print("---")
    except: pass

# همینطور با channel_id=39 جزئیات کامل بگیر
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": 39, "date": date}, auth=auth, timeout=15)
data = r.json()
print("Keys in response:", list(data.keys()))
if data.get("list"):
    print("First program keys:", list(data["list"][0].keys()))
    print("Sample:", json.dumps(data["list"][0], ensure_ascii=False)[:400])
