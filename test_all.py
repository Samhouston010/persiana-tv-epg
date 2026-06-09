import re, requests, time

HEADERS = {"User-Agent":"Mozilla/5.0"}
content = requests.get("https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.m3u").text
lines = content.splitlines()
channels = []
i = 0
while i < len(lines):
    if lines[i].startswith("#EXTINF:"):
        url = lines[i+1].strip() if i+1 < len(lines) else ""
        name_m = re.search(r',(.+)$', lines[i])
        group_m = re.search(r'group-title="([^"]*)"', lines[i])
        channels.append({
            "name": name_m.group(1).strip() if name_m else "",
            "group": group_m.group(1) if group_m else "",
            "url": url
        })
        i += 2
    else:
        i += 1

def find(name, group=None):
    for c in channels:
        if name.lower() in c["name"].lower():
            if group is None or group in c["group"]: return c["url"]
    return ""

def test(name, url):
    if not url:
        print(f"  ⚠️  {name} — NOT IN PLAYLIST"); return
    try:
        r = requests.head(url, headers=HEADERS, timeout=6, allow_redirects=True)
        if r.status_code in (200,206):
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name} — HTTP {r.status_code}")
    except Exception as e:
        print(f"  ❌ {name} — {str(e)[:60]}")
    time.sleep(0.2)

print(f"Total: {len(channels)} channels\n")

print("=== پرشیانا ===")
for n in ["Family","Series","Cinema","Music","Nostalgia","Fight","Junior","Comedy","Reality","Docs","Medical","Travel","SetMix","Folk","Korean","Iranian","Persiana+"]:
    test(n, find(n, "پرشیانا"))

print("\n=== اخبار فارسی ===")
for n in ["بی‌بی‌سی فارسی","صدای آمریکا","ایران اینترنشنال","رادیو فردا TV","منوتو","پارس","کانال جدید"]:
    test(n, find(n))

print("\n=== شبکه‌های خارجی ===")
for n in ["BBC News","Press TV","Al Jazeera","DW News","France 24","CBS News","Bloomberg"]:
    test(n, find(n))

print("\n=== سراسری IRIB ===")
for n in ["شبکه یک","شبکه دو","شبکه سه","شبکه خبر","شبکه ورزش","شبکه نسیم","شبکه افق"]:
    test(n, find(n))

print("\n=== جم تی وی ===")
for n in ["MBC Persia"]:
    test(n, find(n))
