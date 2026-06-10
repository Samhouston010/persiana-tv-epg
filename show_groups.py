import re
with open("all.m3u", "r", encoding="utf-8") as f:
    content = f.read()
groups = re.findall(r'group-title="([^"]*)"', content)
from collections import Counter
for g, c in Counter(groups).most_common():
    print(str(c) + "  " + g)
