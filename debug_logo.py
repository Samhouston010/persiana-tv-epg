import requests
HEADERS = {"User-Agent": "Mozilla/5.0"}

# tvg-id های تلوبیون
tw = requests.get("https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ir_telewebion.m3u", headers=HEADERS, timeout=20).text
import re
tw_ids = re.findall(r'tvg-id="([^"]*)"', tw)
print("Telewebion sample IDs:")
for x in tw_ids[:5]:
    print("  " + repr(x))

# دیتابیس
db = requests.get("https://iptv-org.github.io/api/channels.json", headers=HEADERS, timeout=30).json()
ir = [c for c in db if c.get("country") == "IR"]
print("\nDatabase Iran sample IDs:")
for c in ir[:5]:
    print("  " + repr(c.get("id")) + " | " + c.get("name","") + " | logo:" + str(bool(c.get("logo"))))
print("\nTotal Iran channels in DB:", len(ir))
