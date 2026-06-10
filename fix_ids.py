import json

with open("channels.json", encoding="utf-8-sig") as f:
    channels = json.load(f)

# نقشه درست: tvg_id -> channel_id واقعی
fixes = {
    "IRIB1.ir": 31,
    "IRIB3.ir": 39,
    "JahanbinTV.ir": 40,
    "KhozestanTV.ir": 43,
    "AtrakTV.ir": 47,
}

count = 0
for ch in channels:
    tvg = ch.get("tvg_id","")
    if tvg in fixes:
        old = ch.get("channel_id")
        ch["channel_id"] = fixes[tvg]
        print(ch["name"] + ": " + str(old) + " -> " + str(fixes[tvg]))
        count += 1

with open("channels.json", "w", encoding="utf-8") as f:
    json.dump(channels, f, ensure_ascii=False, indent=2)

print("\nFixed " + str(count) + " channels")
