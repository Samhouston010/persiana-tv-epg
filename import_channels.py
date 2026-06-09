import re, json, requests

# منبع کامل کانال‌های تلوبیون
url = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ir_telewebion.m3u"
r = requests.get(url, timeout=20)
content = r.text

channels = []
lines = content.split("\n")
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line.startswith("#EXTINF:"):
        # اسم
        name_m = re.search(r",(.+)$", line)
        name = name_m.group(1).strip() if name_m else ""
        # tvg-id
        id_m = re.search(r'tvg-id="([^"]*)"', line)
        tvg = id_m.group(1) if id_m else ""
        # logo
        logo_m = re.search(r'tvg-logo="([^"]*)"', line)
        logo = logo_m.group(1) if logo_m else ""
        # URL بعدی - slug رو ازش در میاریم
        url_line = lines[i+1].strip() if i+1 < len(lines) else ""
        slug_m = re.search(r'telewebion\.ir/([^/]+)/live', url_line)
        slug = slug_m.group(1) if slug_m else ""
        if slug:
            channels.append({
                "name": name,
                "tvg_id": tvg,
                "group": "تلوبیون",
                "logo": logo,
                "telewebion_slug": slug,
                "sepehr_channel_id": None
            })
        i += 2
    else:
        i += 1

with open("channels_master.json", "w", encoding="utf-8") as f:
    json.dump(channels, f, ensure_ascii=False, indent=2)

print("Saved " + str(len(channels)) + " channels from telewebion")
for ch in channels[:10]:
    print("  " + ch["name"] + " -> " + ch["telewebion_slug"])
