import re, requests
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE_M3U_URL = "https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.m3u"
IPTV_ORG_SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ir_telewebion.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ir_wnslive.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ir.m3u",
]

# این گروه‌ها هرگز دست نمی‌خورن
LOCKED_GROUPS = [
    "پرشیانا", "جم تی وی", "رادیو فارسی",
    "شبکه‌های خارجی", "سراسری", "استانی",
    "خبری", "ورزشی", "سرگرمی", "مستند",
    "کودک", "مذهبی", "ALL",
]

# این کانال‌ها با هر اسمی هرگز آپدیت نمی‌شن (لینک ثابت دارن)
LOCKED_NAMES = [
    "VOA Persian", "صدای آمریکا",
    "BBC Persian", "بی‌بی‌سی فارسی",
    "Radio Farda TV", "رادیو فردا TV",
    "Manoto", "منوتو",
    "Iran International", "ایران اینترنشنال",
    "Pars TV", "پارس",
    "Kanal Jadid", "کانال جدید",
    "Press TV", "پرس TV",
    "iFilm", "آی‌فیلم",
]

FILM_MUSIC_GROUPS = ["Entertainment","Music","Kids","Family","Series","Movies","Comedy","Animation"]
FILM_MUSIC_KEYWORDS = ["film","movie","cinema","series","serial","music","موزیک","فیلم","سینما","سریال","موسیقی","drama","comedy","bollywood","classic","kids","junior","family","nostalgia","folk","travel","reality","korea","animation","cartoon"]

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status(); return r.text
    except Exception as e:
        print(f"  ERR: {e}"); return ""

def parse(content):
    channels = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            url = ""
            j = i+1
            while j < len(lines):
                nl = lines[j].strip()
                if nl and not nl.startswith("#"): url = nl; break
                j += 1
            if url:
                channels.append({
                    "extinf": line, "url": url,
                    "name":     re.search(r',(.+)$', line).group(1).strip() if re.search(r',(.+)$', line) else "",
                    "tvg_id":   re.search(r'tvg-id="([^"]*)"', line).group(1) if re.search(r'tvg-id="([^"]*)"', line) else "",
                    "tvg_name": re.search(r'tvg-name="([^"]*)"', line).group(1) if re.search(r'tvg-name="([^"]*)"', line) else "",
                    "group":    re.search(r'group-title="([^"]*)"', line).group(1) if re.search(r'group-title="([^"]*)"', line) else "",
                })
            i = j+1
        else:
            i += 1
    return channels

def norm(s): return re.sub(r'[^a-zA-Z0-9\u0600-\u06FF]','',s.lower().strip())

def match(a,b):
    if a["tvg_id"] and b["tvg_id"] and a["tvg_id"]==b["tvg_id"]: return True
    for n1 in {norm(a["name"]),norm(a["tvg_name"])}-{""}:
        for n2 in {norm(b["name"]),norm(b["tvg_name"])}-{""}:
            if n1==n2: return True
            if len(n1)>4 and len(n2)>4 and (n1 in n2 or n2 in n1): return True
    return False

def is_locked(ch):
    if ch["group"] in LOCKED_GROUPS: return True
    name_norm = norm(ch["name"])
    for ln in LOCKED_NAMES:
        if norm(ln) in name_norm or name_norm in norm(ln): return True
    return False

def is_fm(ch):
    text=(ch["name"]+" "+ch["group"]+" "+ch["tvg_name"]).lower()
    if any(g.lower()==ch["group"].lower() for g in FILM_MUSIC_GROUPS): return True
    return any(k in text for k in FILM_MUSIC_KEYWORDS)

def set_group(extinf, g):
    if 'group-title=' in extinf: return re.sub(r'group-title="[^"]*"',f'group-title="{g}"',extinf)
    return extinf.rstrip()+f' group-title="{g}"'

def dedup(channels):
    seen = set(); result = []
    for ch in channels:
        if ch["url"] not in seen:
            seen.add(ch["url"]); result.append(ch)
    return result

print("Fetching all.m3u...")
base_content = fetch(BASE_M3U_URL)
if not base_content:
    with open("all.m3u","r",encoding="utf-8") as f: base_content=f.read()
header = base_content.splitlines()[0]
base = parse(base_content)
print(f"  {len(base)} channels in all.m3u")

print("Fetching iptv-org sources...")
iptvorg = []
for src in IPTV_ORG_SOURCES:
    name=src.split("/")[-1]; print(f"  {name}...",end=" ")
    c=fetch(src)
    if c:
        ch=parse(c); print(f"OK {len(ch)}"); iptvorg.extend(ch)
    else: print("FAIL")

seen=set(); uniq=[]
for ch in iptvorg:
    if ch["url"] not in seen: seen.add(ch["url"]); uniq.append(ch)
print(f"  Total unique: {len(uniq)}")

# تطابق — فقط کانال‌های غیر locked آپدیت می‌شن
print("Matching...")
base_urls = {ch["url"] for ch in base}
updated=0; new_fm=[]; new_oth=[]

for ipch in uniq:
    # اگه URL قبلاً توی all.m3u هست، skip کن
    if ipch["url"] in base_urls:
        continue

    idx=next((i for i,b in enumerate(base) if match(ipch,b)),None)
    if idx is not None:
        if is_locked(base[idx]):
            continue
        if base[idx]["url"]!=ipch["url"]:
            print(f"  UPDATE: {base[idx]['name']} [{base[idx]['group']}]")
            base[idx]["url"]=ipch["url"]; updated+=1
    else:
        (new_fm if is_fm(ipch) else new_oth).append(ipch)

# حذف تکراری‌ها
base = dedup(base)
print(f"Updated: {updated}, New FM: {len(new_fm)}, New others: {len(new_oth)}")

now=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
out=[header,""]
for ch in base: out+=[ch["extinf"],ch["url"],""]
if new_fm:
    out.append(f"# === Film & Music - iptv-org - {now} ===")
    for ch in new_fm: out+=[set_group(ch["extinf"],"فیلم و موسیقی"),ch["url"],""]
if new_oth:
    out.append(f"# === Iranian Channels - iptv-org - {now} ===")
    for ch in new_oth: out+=[set_group(ch["extinf"],"کانال‌های ایرانی"),ch["url"],""]

final="\n".join(out)
with open("all.m3u","w",encoding="utf-8") as f: f.write(final)
print(f"Done! Total: {final.count('#EXTINF:')} channels")
