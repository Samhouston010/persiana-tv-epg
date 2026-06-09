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

def find_exact(name, group=None):
    for c in channels:
        if c["name"] == name:
            if group is None or group == c["group"]: return c["url"]
    return None

def test(label, url):
    if url is None:
        print(f"  ⚠️  {label} — NOT FOUND"); return
    try:
        r = requests.head(url, headers=HEADERS, timeout=6, allow_redirects=True)
        if r.status_code in (200,206):
            print(f"  ✅ {label}")
        else:
            print(f"  ❌ {label} — HTTP {r.status_code} | {url[:60]}")
    except Exception as e:
        print(f"  ❌ {label} — {str(e)[:60]}")
    time.sleep(0.2)

print(f"Total: {len(channels)} channels\n")

print("=== پرشیانا ===")
persiana = [c for c in channels if c["group"]=="پرشیانا"]
for c in persiana:
    test(c["name"], c["url"])

print("\n=== اخبار فارسی ===")
for c in [c for c in channels if c["group"]=="اخبار فارسی"]:
    test(c["name"], c["url"])

print("\n=== شبکه‌های خارجی ===")
for c in [c for c in channels if c["group"]=="شبکه‌های خارجی"]:
    test(c["name"], c["url"])

print("\n=== سراسری ===")
for c in [c for c in channels if c["group"]=="سراسری"]:
    test(c["name"], c["url"])
