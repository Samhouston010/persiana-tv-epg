import requests
HEADERS = {"User-Agent": "Mozilla/5.0"}
logo = "https://static.telewebion.ir/channelsLogo/9aa86b5c-5cfb-44d0-ba60-8f2af3ef4c9a/default"

# بدون referer (مثل کاری که TiviMate می‌کنه)
r = requests.get(logo, headers=HEADERS, timeout=10)
print("Without referer:", r.status_code, "| size:", len(r.content), "| type:", r.headers.get("content-type"))

# با referer
HEADERS2 = {"User-Agent": "Mozilla/5.0", "Referer": "https://telewebion.ir/"}
r2 = requests.get(logo, headers=HEADERS2, timeout=10)
print("With referer:", r2.status_code, "| size:", len(r2.content), "| type:", r2.headers.get("content-type"))
