import json
with open("channels.json", encoding="utf-8-sig") as f:
    channels = json.load(f)

# دنبال این شبکه‌ها بگرد
targets = ["IRIB1","IRIB3","Jahanbin","Khozestan","Atrak","Khorasan"]
print("Current assignments:")
for ch in channels:
    tvg = ch.get("tvg_id","")
    name = ch["name"]
    cid = ch.get("channel_id")
    for t in targets:
        if t.lower() in tvg.lower() or "خوزستان" in name or "خراسان" in name or "جهان" in name:
            print("  " + name + " | tvg=" + str(tvg) + " | channel_id=" + str(cid))
            break
