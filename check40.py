import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timezone, timedelta

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CK = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CS = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CK, CS, signature_method="HMAC-SHA1")
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": 40, "date": date}, auth=auth, timeout=15)
progs = r.json().get("list") or []
print("id=40 has", len(progs), "programs today (Tehran time):")
for p in progs:
    start = datetime.fromtimestamp(p.get("start",0)/1000, tz=timezone.utc)
    tehran = start + timedelta(hours=3, minutes=30)
    hhmm = tehran.strftime("%H:%M")
    title = p.get("title","")
    print("  " + hhmm + " - " + title)
