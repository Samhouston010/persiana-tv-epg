import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timezone

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CK = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CS = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CK, CS, signature_method="HMAC-SHA1")
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": 54, "date": date}, auth=auth, timeout=15)
progs = r.json().get("list") or []
print("id=54 all titles with اذان (shows city):")
for p in progs:
    t = p.get("title","")
    if "اذان" in t or "افق" in t or "استان" in t:
        print("  " + t)
