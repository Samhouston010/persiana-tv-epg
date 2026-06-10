import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timezone

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CONSUMER_KEY = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"

auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, signature_method="HMAC-SHA1")
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

print("Searching for correct شبکه سه channel_id...")
for cid in range(30, 50):
    try:
        r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": cid, "date": date}, auth=auth, timeout=15)
        if r.status_code == 200:
            progs = r.json().get("list") or []
            titles = [p.get("title","")[:25] for p in progs[:3]]
            # اگه عنوان‌ها ساعت نباشن یعنی داده واقعی داره
            real = any(t and not t[0].isdigit() for t in titles)
            mark = "<-- REAL DATA" if real else ""
            print(f"id={cid}: {len(progs)} progs | {titles} {mark}")
    except Exception as e:
        print(f"id={cid}: ERR {str(e)[:30]}")
