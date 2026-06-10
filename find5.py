import json
with open("channels_master.json", encoding="utf-8") as f:
    channels = json.load(f)

# دنبال این 5 شبکه بگرد بر اساس slug
slugs = {
    "tv1": "IRIB1.ir",
    "tv3": "IRIB3.ir",
    "jahanbin": "JahanbinTV.ir",
    "khouzestan": "KhozestanTV.ir",
    "khozestan": "KhozestanTV.ir",
    "atrak": "AtrakTV.ir",
}
print("Found channels:")
for ch in channels:
    slug = ch.get("telewebion_slug","")
    if slug in slugs:
        print("  slug=" + slug + " | name=" + ch["name"] + " | current tvg_id=" + repr(ch.get("tvg_id","")))
