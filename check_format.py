import requests
HEADERS = {"User-Agent": "Mozilla/5.0"}
logo = "https://static.telewebion.ir/channelsLogo/MzYyMzM1NmVhYjc5MmZlY2ZmNzJlMGY3ZmJjZjc5Y2UwNDkyODQxNDU4YzU5MjE0MzFlYjg4NWM4NDZiNzA5NA/default"
r = requests.get(logo, headers=HEADERS, timeout=10)
print("Status:", r.status_code)
print("Content-Type:", r.headers.get("content-type"))
print("First bytes (hex):", r.content[:8].hex())
# PNG با 89504e47 شروع میشه، JPEG با ffd8
