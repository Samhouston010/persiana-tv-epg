import requests
HEADERS = {"User-Agent":"Mozilla/5.0", "Referer":"https://telewebion.com/"}

urls = [
    "https://live-aburayhan1108.telewebion.ir/ek/irinn/live/1080p/index.m3u8",
    "https://ncdn.telewebion.ir/irinn/live/playlist.m3u8",
]
for u in urls:
    try:
        r = requests.get(u, headers=HEADERS, timeout=8)
        print(str(r.status_code) + " | " + u)
    except Exception as e:
        print("ERR | " + u)
