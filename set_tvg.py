import json
with open("channels_master.json", encoding="utf-8") as f:
    channels = json.load(f)

# slug -> tvg_id که EPG سپهر داره
TVG_MAP = {
    "tv1": "IRIB1.ir",
    "tv3": "IRIB3.ir",
    "jahanbin": "JahanbinTV.ir",
    "khoozestan": "KhozestanTV.ir",
    "atrak": "AtrakTV.ir",
}

count = 0
for ch in channels:
    slug = ch.get("telewebion_slug","")
    if slug in TVG_MAP:
        ch["tvg_id"] = TVG_MAP[slug]
        print("  " + ch["name"] + " -> tvg-id=" + TVG_MAP[slug])
        count += 1

with open("channels_master.json", "w", encoding="utf-8") as f:
    json.dump(channels, f, ensure_ascii=False, indent=2)

print("\nSet tvg-id for " + str(count) + " channels")
