import gzip, requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

urls = [
    "https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.xml.gz",
    "https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz",
]

all_channels = []
all_programmes = []

for u in urls:
    print("Fetching " + u.split("/")[-1] + " ...")
    data = requests.get(u, headers=HEADERS, timeout=30).content
    try:
        xml = gzip.decompress(data).decode("utf-8")
    except:
        xml = data.decode("utf-8")
    # استخراج channel ها و programme ها
    import re
    channels = re.findall(r'<channel\b.*?</channel>', xml, re.DOTALL)
    programmes = re.findall(r'<programme\b.*?</programme>', xml, re.DOTALL)
    print("  channels: " + str(len(channels)) + " | programmes: " + str(len(programmes)))
    all_channels.extend(channels)
    all_programmes.extend(programmes)

# حذف channel های تکراری (بر اساس id)
seen = set()
unique_channels = []
for ch in all_channels:
    m = re.search(r'id="([^"]*)"', ch)
    cid = m.group(1) if m else ""
    if cid and cid not in seen:
        seen.add(cid)
        unique_channels.append(ch)

# ساخت XML نهایی
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv>']
out.extend(unique_channels)
out.extend(all_programmes)
out.append('</tv>')
xml_final = "\n".join(out)

# ذخیره gz
with gzip.open("final.xml.gz", "wb") as f:
    f.write(xml_final.encode("utf-8"))

print("")
print("final.xml.gz created")
print("  channels: " + str(len(unique_channels)))
print("  programmes: " + str(len(all_programmes)))
