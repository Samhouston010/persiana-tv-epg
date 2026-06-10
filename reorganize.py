import re

with open("all.m3u", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")
result = []
i = 0

# گروه‌هایی که کانال‌هاشون باید به سراسری بره
MOVE_TO_SARASARI_GROUPS = ["ورزشی", "خبری", "سرگرمی", "مستند", "مذهبی", "کودک"]
# کانال‌های خاصی که با اسم به سراسری می‌رن
MOVE_BY_NAME = ["شبکه جهان‌بین", "شبکه اصفهان", "شبکه نصف جهان (اصفهان)"]

changed_ofogh = 0
moved = 0

while i < len(lines):
    line = lines[i]
    if line.startswith("#EXTINF:"):
        # 1. شبکه افق: tvg-id رو خالی کن
        if 'tvg-id="OfoghTV.ir"' in line:
            line = line.replace('tvg-id="OfoghTV.ir"', 'tvg-id=""')
            changed_ofogh += 1

        # اسم کانال
        name_m = re.search(r",(.+)$", line)
        ch_name = name_m.group(1).strip() if name_m else ""
        # گروه فعلی
        grp_m = re.search(r'group-title="([^"]*)"', line)
        grp = grp_m.group(1) if grp_m else ""

        # 2. اگه گروهش جزو لیست انتقال هست یا اسمش جزو لیست خاصه
        if grp in MOVE_TO_SARASARI_GROUPS or ch_name in MOVE_BY_NAME:
            line = re.sub(r'group-title="[^"]*"', 'group-title="سراسری"', line)
            moved += 1

    result.append(line)
    i += 1

with open("all.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(result))

print("Ofogh tvg-id cleared:", changed_ofogh)
print("Channels moved to سراسری:", moved)
