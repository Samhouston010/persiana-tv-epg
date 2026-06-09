import re

with open("all.m3u","r",encoding="utf-8") as f:
    content = f.read()

fixes = {
    # VOA Persian — لینک اصلی
    "https://voaphls.wns.live/hls/stream.m3u8": "https://voa-ingest.akamaized.net/hls/live/2033876/tvmc07/playlist.m3u8",
}

for old,new in fixes.items():
    if old in content:
        content = content.replace(old, new)
        print(f"Fixed: {old[:50]} -> {new[:50]}")

# چک کن Folk، Korea، Press TV هستن یا نه
for name in ["سنتی","Folk","4 Kurd","Korea","پرس TV","Press TV"]:
    if name in content:
        print(f"EXISTS: {name}")
    else:
        print(f"MISSING: {name}")

with open("all.m3u","w",encoding="utf-8") as f:
    f.write(content)
