import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timezone

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CK = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CS = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CK, CS, signature_method="HMAC-SHA1")
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

print("Channels with REAL data:")
for cid in range(30, 90):
    try:
        r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": cid, "date": date}, auth=auth, timeout=8)
        if r.status_code == 200:
            progs = r.json().get("list") or []
            if len(progs) > 20:
                titles = [p.get("title","") for p in progs]
                if any(t and not t[0].isdigit() for t in titles[:3]):
                    print("id=" + str(cid) + ": " + str(len(progs)) + " | " + titles[0][:30])
    except: pass
print("done")
