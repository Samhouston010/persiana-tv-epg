import json

with open("channels.json", encoding="utf-8-sig") as f:
    channels = json.load(f)

# لوگوی تلوبیون برای 5 شبکه
TW_LOGO = "https://static.telewebion.ir/channelsLogo/{img}/default"
LOGOS = {
    "IRIB1.ir": "9aa86b5c-5cfb-44d0-ba60-8f2af3ef4c9a",
    "IRIB3.ir": "MWUxYmE4YjJhZTc4OWZiOTVkMzczODdkN2NjY2I4YjNiZTFjYjRiODM3NjhiMzcxOGI5YzdjMWNlODA3YjMzYg",
    "JahanbinTV.ir": "ODY4NmQ1MzFkYmE0NDdlYzY1YmQ4NTlhOWZkNjIxMDg4ZTc1OGJjMzZkYWM1Mjk1OGYwZWU2YjY5OWRhZmY5Nw",
    "AtrakTV.ir": "c059616c-053f-4044-baf1-4444c7101161",
    "KhozestanTV.ir": "fa5cadf8-318c-48c3-b067-33bd67b1ef49",
}

count = 0
for ch in channels:
    tvg = ch.get("tvg_id","")
    if tvg in LOGOS:
        ch["logo"] = TW_LOGO.format(img=LOGOS[tvg])
        print("  " + ch["name"] + " logo updated")
        count += 1

with open("channels.json", "w", encoding="utf-8") as f:
    json.dump(channels, f, ensure_ascii=False, indent=2)

print("Updated " + str(count) + " logos")
