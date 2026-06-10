import requests, json
from requests_oauthlib import OAuth1
from datetime import datetime, timezone

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CONSUMER_KEY = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, signature_method="HMAC-SHA1")
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# همه id ها رو اسکن کن و اونایی که داده واقعی دارن رو پیدا کن
print("Scanning all channel IDs (1-120)...")
good = {}
for cid in range(1, 120):
    try:
        r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": cid, "date": date}, auth=auth, timeout=10)
        if r.status_code == 200:
            progs = r.json().get("list") or []
            if len(progs) > 20:  # داده واقعی معمولا بیشتر از 20 برنامه داره
                titles = [p.get("title","")[:20] for p in progs[:2]]
                real = any(t and not t[0].isdigit() for t in titles)
                if real:
                    good[cid] = (len(progs), titles)
                    print(f"id={cid}: {len(progs)} progs | {titles}")
    except: pass

print(f"\nFound {len(good)} channels with real data")
# ذخیره برای استفاده بعدی
with open("good_ids.json","w",encoding="utf-8") as f:
    json.dump(good, f, ensure_ascii=False, indent=2)
