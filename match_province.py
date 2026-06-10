import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timezone

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CK = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CS = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CK, CS, signature_method="HMAC-SHA1")
date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# عنوان‌های شاخص هر id که اسم استان توش باشه
for cid in [43, 47, 54]:
    r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": cid, "date": date}, auth=auth, timeout=15)
    progs = r.json().get("list") or []
    print("===== id=" + str(cid) + " =====")
    # دنبال اسم استان بگرد
    keywords = ["خوزستان","فارس","سمنان","قزوین","همدان","خراسان","اشراق","زنجان","شیراز","اهواز","بجنورد","مشهد","بیرجند"]
    for p in progs:
        t = p.get("title","")
        for kw in keywords:
            if kw in t:
                print("  " + t)
                break
    print()
