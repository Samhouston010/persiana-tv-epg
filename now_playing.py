import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timezone, timedelta

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CK = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CS = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CK, CS, signature_method="HMAC-SHA1")
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

now = datetime.now(timezone.utc)
for cid in [43, 47, 54]:
    r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": cid, "date": date}, auth=auth, timeout=15)
    progs = r.json().get("list") or []
    # برنامه‌ای که الان پخش میشه رو پیدا کن
    print("=== id=" + str(cid) + " - NOW playing ===")
    for p in progs:
        start = datetime.fromtimestamp(p.get("start",0)/1000, tz=timezone.utc)
        end = start + timedelta(minutes=p.get("duration") or 30)
        if start <= now <= end:
            print("  NOW: " + p.get("title",""))
    # چند برنامه بعدی
    upcoming = [p for p in progs if datetime.fromtimestamp(p.get("start",0)/1000, tz=timezone.utc) > now][:3]
    for p in upcoming:
        print("  NEXT: " + p.get("title",""))
    print()
