import requests
HEADERS = {"User-Agent": "Mozilla/5.0"}

# چند کانال مختلف رو تست کن - اگه همه 681 بایت باشن یعنی placeholder خالیه
import json
with open("channels_master.json", encoding="utf-8") as f:
    channels = json.load(f)

for ch in channels[:5]:
    logo = ch["logo"]
    if logo:
        r = requests.get(logo, headers=HEADERS, timeout=10)
        print(ch["name"] + ": " + str(len(r.content)) + " bytes")
