import json, requests

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://telewebion.ir/"}

# API رسمی تلوبیون - لیست همه کانال‌ها
url = "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=300&v=5.9.0"
data = requests.get(url, headers=HEADERS, timeout=20).json()
items = data["body"]["queryChannel"]

LOGO_TPL = "https://static.telewebion.ir/channelsLogo/{img}/default"

# نقشه دسته‌بندی به فارسی
TYPE_MAP = {
    "national": "سراسری",
    "province": "استانی",
    "provincial": "استانی",
    "international": "بین‌المللی",
    "special": "ویژه",
}

channels = []
for it in items:
    slug = it.get("descriptor", "")
    name = it.get("name", "")
    img = it.get("image_name", "")
    type_info = it.get("type", {})
    type_desc = type_info.get("descriptor", "") if isinstance(type_info, dict) else ""
    group = TYPE_MAP.get(type_desc, "تلوبیون")
    if not slug:
        continue
    logo = LOGO_TPL.format(img=img) if img else ""
    channels.append({
        "name": name,
        "tvg_id": "",
        "group": group,
        "logo": logo,
        "telewebion_slug": slug,
        "sepehr_channel_id": None
    })

with open("channels_master.json", "w", encoding="utf-8") as f:
    json.dump(channels, f, ensure_ascii=False, indent=2)

withlogo = sum(1 for c in channels if c["logo"])
print("Saved " + str(len(channels)) + " channels")
print("With logo: " + str(withlogo))
print("With Persian name: " + str(sum(1 for c in channels if c["name"])))