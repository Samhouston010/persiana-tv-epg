import gzip, requests, re

HEADERS = {"User-Agent": "Mozilla/5.0"}

urls = [
    "https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.xml.gz",
    "https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz",
]

# لوگوی تلوبیون برای 5 شبکه EPG
TW_LOGOS = {
    "IRIB1.ir": "https://static.telewebion.ir/channelsLogo/9aa86b5c-5cfb-44d0-ba60-8f2af3ef4c9a/default",
    "IRIB3.ir": "https://static.telewebion.ir/channelsLogo/MWUxYmE4YjJhZTc4OWZiOTVkMzczODdkN2NjY2I4YjNiZTFjYjRiODM3NjhiMzcxOGI5YzdjMWNlODA3YjMzYg/default",
    "JahanbinTV.ir": "https://static.telewebion.ir/channelsLogo/ODY4NmQ1MzFkYmE0NDdlYzY1YmQ4NTlhOWZkNjIxMDg4ZTc1OGJjMzZkYWM1Mjk1OGYwZWU2YjY5OWRhZmY5Nw/default",
    "AtrakTV.ir": "https://static.telewebion.ir/channelsLogo/c059616c-053f-4044-baf1-4444c7101161/default",
    "KhozestanTV.ir": "https://static.telewebion.ir/channelsLogo/fa5cadf8-318c-48c3-b067-33bd67b1ef49/default",
}

all_channels = []
all_programmes = []

for u in urls:
    print("Fetching " + u.split("/")[-1] + " ...")
    data = requests.get(u, headers=HEADERS, timeout=30).content
    try:
        xml = gzip.decompress(data).decode("utf-8")
    except:
        xml = data.decode("utf-8")
    channels = re.findall(r'<channel\b.*?</channel>', xml, re.DOTALL)
    programmes = re.findall(r'<programme\b.*?</programme>', xml, re.DOTALL)
    print("  channels: " + str(len(channels)) + " | programmes: " + str(len(programmes)))
    all_channels.extend(channels)
    all_programmes.extend(programmes)

seen = set()
unique_channels = []
for ch in all_channels:
    m = re.search(r'id="([^"]*)"', ch)
    cid = m.group(1) if m else ""
    if cid and cid not in seen:
        seen.add(cid)
        # اگه از 5 شبکه تلوبیونه، لوگوش رو عوض کن
        if cid in TW_LOGOS:
            new_logo = TW_LOGOS[cid]
            if "<icon" in ch:
                ch = re.sub(r'<icon src="[^"]*"', '<icon src="' + new_logo + '"', ch)
            else:
                ch = ch.replace("</channel>", '<icon src="' + new_logo + '"/></channel>')
        unique_channels.append(ch)

out = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv>']
out.extend(unique_channels)
out.extend(all_programmes)
out.append('</tv>')
xml_final = "\n".join(out)

with gzip.open("final.xml.gz", "wb") as f:
    f.write(xml_final.encode("utf-8"))

print("")
print("final.xml.gz created with telewebion logos")
print("  channels: " + str(len(unique_channels)))
print("  programmes: " + str(len(all_programmes)))