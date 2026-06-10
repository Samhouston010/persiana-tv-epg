import json
with open("channels_master.json", encoding="utf-8") as f:
    channels = json.load(f)
print("Channels with خوزستان or khoz in slug/name:")
for ch in channels:
    slug = ch.get("telewebion_slug","")
    name = ch.get("name","")
    if "خوز" in name or "khoz" in slug.lower() or "khouz" in slug.lower():
        print("  slug=" + slug + " | name=" + name)
