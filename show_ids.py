import json
with open("channels.json", encoding="utf-8-sig") as f:
    channels = json.load(f)
print("Channels with channel_id:")
for ch in channels:
    cid = ch.get("channel_id")
    if cid:
        name = ch["name"]
        tvg = ch.get("tvg_id")
        print("  id=" + str(cid) + " -> " + name + " (tvg=" + str(tvg) + ")")
