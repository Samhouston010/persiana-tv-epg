import re
with open("final.m3u", encoding="utf-8") as f:
    content = f.read()
# هدر
print("Header:", content.split(chr(10))[0][:80])
print()
# گروه‌ها
groups = re.findall(r'group-title="([^"]*)"', content)
from collections import Counter
print("Groups:")
for g, c in Counter(groups).most_common():
    print("  " + str(c) + "  " + g)
