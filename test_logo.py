import requests
HEADERS = {"User-Agent": "Mozilla/5.0"}

# الگوهای احتمالی لوگوی تلوبیون
patterns = [
    "https://static.telewebion.com/channelsLogo/irinn/default",
    "https://static.telewebion.com/channelsLogo/irinn",
    "https://static.telewebion.com/channels/irinn/logo.png",
    "https://cdnn.telewebion.com/prod/channels/irinn/logo.png",
]
for p in patterns:
    try:
        r = requests.head(p, headers=HEADERS, timeout=8, allow_redirects=True)
        print(str(r.status_code) + " | " + p)
    except Exception as e:
        print("ERR | " + p)
