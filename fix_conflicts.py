import json
with open("channels.json", encoding="utf-8-sig") as f:
    channels = json.load(f)

CORRECT = {
    "IRIB1.ir": 31,
    "IRIB3.ir": 39,
    "JahanbinTV.ir": 40,
    "KhozestanTV.ir": 43,
    "AtrakTV.ir": 47,
}

for ch in channels:
    tvg = ch.get("tvg_id", "")
    ch["channel_id"] = CORRECT.get(tvg, None)

with open("channels.json", "w", encoding="utf-8") as f:
    json.dump(channels, f, ensure_ascii=False, indent=2)

print("Channels WITH EPG (only these 5):")
for ch in channels:
    if ch.get("channel_id"):
        print("  " + ch["name"] + " -> " + str(ch["channel_id"]))
