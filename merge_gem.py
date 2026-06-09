import re, requests
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

GEM_CHANNELS = [
    {"name":"GEM TV","url":"https://www.aparatchi.com/iran-live-tv/farsi-film-tv/gem-tv","logo":"https://www.aparatchi.com/images/chanells-logo/gem/gem-tv.svg","tvg_id":"GEM.TV.ir","group":"جم تی وی"},
    {"name":"GEM Drama","url":"https://www.aparatchi.com/iran-live-tv/farsi-film-tv/gem-drama","logo":"https://www.aparatchi.com/images/chanells-logo/gem/gem-drama.svg","tvg_id":"GEM.Drama.ir","group":"جم تی وی"},
    {"name":"GEM Drama+","url":"https://www.aparatchi.com/iran-live-tv/farsi-film-tv/gem-drama-plus","logo":"https://www.aparatchi.com/images/chanells-logo/gem/gem-drama-plus.svg","tvg_id":"GEM.DramaPlus.ir","group":"جم تی وی"},
    {"name":"GEM Film","url":"https://www.aparatchi.com/iran-live-tv/farsi-film-tv/gem-film","logo":"https://www.aparatchi.com/images/chanells-logo/gem/gem-film.svg","tvg_id":"GEM.Film.ir","group":"جم تی وی"},
    {"name":"GEM Classic","url":"https://www.aparatchi.com/iran-live-tv/farsi-film-tv/gem-classic","logo":"https://www.aparatchi.com/images/chanells-logo/gem/gem-classic.svg","tvg_id":"GEM.Classic.ir","group":"جم تی وی"},
    {"name":"GEM Comedy","url":"https://www.aparatchi.com/iran-live-tv/farsi-film-tv/gem-comedy","logo":"https://www.aparatchi.com/images/chanells-logo/gem/gem-comedy.svg","tvg_id":"GEM.Comedy.ir","group":"جم تی وی"},
    {"name":"GEM Bollywood","url":"https://www.aparatchi.com/iran-live-tv/farsi-film-tv/gem-bollywood","logo":"https://www.aparatchi.com/images/chanells-logo/gem/gem-bollywood.svg","tvg_id":"GEM.Bollywood.ir","group":"جم تی وی"},
    {"name":"GEM Pixel","url":"https://www.aparatchi.com/iran-live-tv/farsi-film-tv/gem-pixel","logo":"https://www.aparatchi.com/images/chanells-logo/gem/gem-pixel.svg","tvg_id":"GEM.Pixel.ir","group":"جم تی وی"},
    {"name":"GEM Onyx","url":"https://www.aparatchi.com/iran-live-tv/farsi-film-tv/onyx","logo":"https://www.aparatchi.com/images/chanells-logo/gem/gem-onyx.svg","tvg_id":"GEM.Onyx.ir","group":"جم تی وی"},
    {"name":"MBC Persia","url":"https://www.aparatchi.com/iran-live-tv/farsi-film-tv/mbc-persia","logo":"https://www.aparatchi.com/images/chanells-logo/mbcpersia.svg","tvg_id":"MBC.Persia.ir","group":"جم تی وی"},
]

OLD_URL = ["ca-rt.onetv.app/gem","gg.hls2.xyz/live/IR%20-%20GEM","gg.hls2.xyz/live/IR%20-%20Gem"]
OLD_GROUPS = ['"شبکه جم"','"جم کمکی"','"جم تی وی"']

def fetch_base():
    r = requests.get("https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.m3u", headers=HEADERS, timeout=20)
    return r.text

def clean(content):
    lines = content.splitlines(keepends=True)
    result, removed, i = [], 0, 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF:"):
            nxt = lines[i+1].strip() if i+1 < len(lines) else ""
            if any(g in line for g in OLD_GROUPS) or any(p in nxt for p in OLD_URL):
                removed += 1; i += 2; continue
        result.append(line); i += 1
    print(f"Removed {removed} dead GEM entries")
    return "".join(result)

def get_url(page):
    try:
        r = requests.get(page, headers=HEADERS, timeout=15)
        m = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', r.text)
        return m[0] if m else None
    except: return None

def test_url(url):
    h = {**HEADERS, "Referer":"https://executeandship.com/","Origin":"https://executeandship.com"}
    try:
        r = requests.head(url, headers=h, timeout=8, allow_redirects=True)
        return r.status_code in (200,206)
    except:
        try:
            r = requests.get(url, headers=h, timeout=8, stream=True); r.close()
            return r.status_code in (200,206)
        except: return False

def build_block():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = ["", f"# جم تی وی — aparatchi.com — {now}"]
    found = skipped = 0
    for ch in GEM_CHANNELS:
        print(f"  Scraping {ch['name']}...", end=" ")
        url = get_url(ch["url"])
        if not url: print("NO URL"); skipped += 1; continue
        print(f"testing...", end=" ")
        if test_url(url):
            print("LIVE - added")
            found += 1
            lines.append(f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}')
            lines.append(url)
        else:
            print("DEAD - skipped"); skipped += 1
    print(f"Result: {found} live, {skipped} dead")
    return "\n".join(lines) + "\n"

print("Fetching all.m3u...")
base = fetch_base()
print("Cleaning dead GEM...")
c = clean(base)
print("Testing GEM channels...")
block = build_block()
final = c.rstrip() + "\n" + block
with open("all.m3u","w",encoding="utf-8") as f: f.write(final)
print(f"Done! Total: {final.count('#EXTINF:')} channels")
