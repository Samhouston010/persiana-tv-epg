import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timezone

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CONSUMER_KEY = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, signature_method="HMAC-SHA1")

# لیست کانال‌های سپهر رو بگیر
try:
    r = requests.get(f"{API_BASE}/channel/list", auth=auth, timeout=15)
    print("STATUS:", r.status_code)
    if r.status_code == 200:
        data = r.json().get("list") or r.json().get("data") or r.json()
        for ch in data:
            print(f"id={ch.get('id')} | name={ch.get('title') or ch.get('name')}")
except Exception as e:
    print("ERROR:", e)
