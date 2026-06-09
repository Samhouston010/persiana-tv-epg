import re

with open("all.m3u","r",encoding="utf-8") as f:
    content = f.read()

# VOA Persian رو به لینک اصلی برگردون
old = "https://voaphls.wns.live/hls/stream.m3u8"
new = "https://voa-ingest.akamaized.net/hls/live/2033876/tvmc07/playlist.m3u8"

if old in content:
    content = content.replace(old, new)
    print(f"Fixed VOA Persian URL")
else:
    print("VOA URL not found - checking...")
    # پیدا کن الان چه لینکی داره
    lines = content.splitlines()
    for i,line in enumerate(lines):
        if "VOA" in line or "صدای آمریکا" in line:
            print(f"  Found: {lines[i]}")
            print(f"  URL:   {lines[i+1] if i+1<len(lines) else 'N/A'}")

with open("all.m3u","w",encoding="utf-8") as f:
    f.write(content)
