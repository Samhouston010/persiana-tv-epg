import re, requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

# منابع
STABLE_URL = "https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/stable.m3u"
ALL_URL = "https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.m3u"

# دو منبع EPG
EPG_PERSIANA = "https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.xml.gz"
EPG_SEPEHR = "https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz"

# گروه‌هایی که از all.m3u می‌خوایم (سراسری، استانی، کانال‌های ایرانی رو نمی‌خوایم)
KEEP_GROUPS = [
    "پرشیانا",
    "اخبار فارسی",
    "شبکه‌های فارسی",
    "رادیو فارسی",
    "شبکه‌های خارجی",
    "جم تی وی",
    "فیلم و موسیقی",
    "ALL",
]

def fetch(url):
    return requests.get(url, headers=HEADERS, timeout=25).text

def parse(content):
    """لیست (extinf, url) برمی‌گردونه"""
    out = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            url = ""
            j = i + 1
            while j < len(lines):
                nl = lines[j].strip()
                if nl and not nl.startswith("#"):
                    url = nl
                    break
                j += 1
            if url:
                out.append((line, url))
            i = j + 1
        else:
            i += 1
    return out

def get_group(extinf):
    m = re.search(r'group-title="([^"]*)"', extinf)
    return m.group(1) if m else ""

print("Fetching stable.m3u (telewebion)...")
stable = parse(fetch(STABLE_URL))
print("  " + str(len(stable)) + " telewebion channels")

print("Fetching all.m3u (persiana)...")
all_ch = parse(fetch(ALL_URL))
print("  " + str(len(all_ch)) + " total in all.m3u")

# فیلتر گروه‌های مورد نظر از all.m3u
kept = []
for extinf, url in all_ch:
    g = get_group(extinf)
    if g in KEEP_GROUPS:
        # ALL رو به همه تغییر بده
        if g == "ALL":
            extinf = extinf.replace('group-title="ALL"', 'group-title="همه"')
        kept.append((extinf, url))
print("  " + str(len(kept)) + " channels kept from all.m3u")

# ساخت فایل نهایی
q = chr(34)
epg = EPG_PERSIANA + "," + EPG_SEPEHR
lines = ["#EXTM3U x-tvg-url=" + q + epg + q, ""]

# اول تلوبیون
for extinf, url in stable:
    lines.append(extinf)
    lines.append(url)

# بعد کانال‌های پرشیانا و بقیه
for extinf, url in kept:
    lines.append(extinf)
    lines.append(url)

with open("final.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

total = len(stable) + len(kept)
print("")
print("final.m3u created with " + str(total) + " channels")
print("  telewebion: " + str(len(stable)))
print("  persiana+others: " + str(len(kept)))