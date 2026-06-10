import requests
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
endpoints = [
    "https://gateway.telewebion.com/kandoo/channels/",
    "https://gateway.telewebion.com/v1/channels",
    "https://api.telewebion.com/v1/channels",
    "https://gateway.telewebion.com/channels",
    "https://gateway.telewebion.com/kandoo/live/getList",
]
for ep in endpoints:
    try:
        r = requests.get(ep, headers=HEADERS, timeout=10)
        print(ep + " -> " + str(r.status_code))
        if r.status_code == 200:
            print("  WORKS: " + r.text[:200])
    except Exception as e:
        print(ep + " -> ERR")
