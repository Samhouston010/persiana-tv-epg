import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timezone, timedelta

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CONSUMER_KEY = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, signature_method="HMAC-SHA1")
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# همه برنامه‌های امروز این id ها رو نشون بده تا از روی محتوا شبکه رو حدس بزنیم
for cid in [43, 47, 54]:
    r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": cid, "date": date}, auth=auth, timeout=15)
    progs = r.json().get("list") or []
    print(f"\n===== id={cid} ({len(progs)} programs) =====")
    for p in progs[:12]:
        print(f"  {p.get('title','')}")
