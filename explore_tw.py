import requests, json
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://telewebion.ir/"}

url = "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=300&v=5.9.0"
r = requests.get(url, headers=HEADERS, timeout=20)
print("Status:", r.status_code)
data = r.json()

# ساختار رو ببین
print("Top keys:", list(data.keys()) if isinstance(data, dict) else "list")

# پیدا کردن لیست کانال‌ها
if isinstance(data, dict):
    for k, v in data.items():
        if isinstance(v, list) and len(v) > 5:
            print("Found channel list in key:", k, "| count:", len(v))
            print("First channel keys:", list(v[0].keys()))
            print("Sample:", json.dumps(v[0], ensure_ascii=False)[:400])
            break
