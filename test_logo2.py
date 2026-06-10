import requests
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://telewebion.ir/"}
img = "9aa86b5c-5cfb-44d0-ba60-8f2af3ef4c9a"
patterns = [
    "https://static.telewebion.ir/channelsLogo/" + img + "/default",
    "https://static.telewebion.ir/channelsImage/" + img + "/default",
    "https://static.telewebion.ir/" + img,
    "https://static.telewebion.ir/images/" + img + ".png",
]
for p in patterns:
    try:
        r = requests.head(p, headers=HEADERS, timeout=8, allow_redirects=True)
        print(str(r.status_code) + " | " + p)
    except:
        print("ERR | " + p)
