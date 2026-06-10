import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timezone

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CK = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CS = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CK, CS, signature_method="HMAC-SHA1")
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# دنبال شبکه ای بگرد که قرارگاه پخش می کنه
print("Searching for قرارگاه / جنگ...")
for cid in range(30, 60):
    try:
        r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": cid, "date": date}, auth=auth, timeout=8)
        if r.status_code == 200:
            progs = r.json().get("list") or []
            for p in progs:
                t = p.get("title","")
                if "قرارگاه" in t or ("جنگ" in t and "رنگ" not in t):
                    print(f"id={cid}: FOUND -> {t}")
                    break
    except: pass
print("done")
