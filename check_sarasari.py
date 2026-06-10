import re
with open("final.m3u", encoding="utf-8") as f:
    lines = f.read().split("\n")
print("Channels in سراسری group:")
for i, line in enumerate(lines):
    if line.startswith("#EXTINF") and 'group-title="سراسری"' in line:
        name_m = re.search(r",(.+)$", line)
        name = name_m.group(1).strip() if name_m else ""
        url = lines[i+1] if i+1 < len(lines) else ""
        src = "telewebion" if "telewebion.ir" in url else "persiana/other"
        print("  " + name + " [" + src + "]")
