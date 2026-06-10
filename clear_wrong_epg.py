import json

with open("channels.json", encoding="utf-8-sig") as f:
    channels = json.load(f)

# شبکه‌هایی که سپهر EPG واقعی نداره - channel_id رو حذف کن
NO_EPG = ["Tamasha.ir", "Nasim.ir", "VarzeshTV.ir", "OfoghTV.ir"]

count = 0
for ch in channels:
    tvg = ch.get("tvg_id","")
    if tvg in NO_EPG:
        if ch.get("channel_id") is not None:
            print(ch["name"] + ": channel_id " + str(ch.get("channel_id")) + " -> removed")
            ch["channel_id"] = None
            count += 1

with open("channels.json", "w", encoding="utf-8") as f:
    json.dump(channels, f, ensure_ascii=False, indent=2)

print("Cleared " + str(count) + " channels")
