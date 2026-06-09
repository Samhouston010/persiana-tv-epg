import re, requests

content = requests.get("https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.m3u").text

lines = content.splitlines()
header = lines[0]
result = [header, ""]
seen_urls = set()
removed = 0
i = 1

while i < len(lines):
    line = lines[i].strip()
    if line.startswith("#EXTINF:"):
        url = lines[i+1].strip() if i+1 < len(lines) else ""
        if url and url not in seen_urls:
            seen_urls.add(url)
            result.append(lines[i])
            result.append(url)
            result.append("")
        else:
            removed += 1
        i += 2
    else:
        i += 1

final = "\n".join(result)
with open("all.m3u","w",encoding="utf-8") as f: f.write(final)
total = final.count("#EXTINF:")
print(f"Removed {removed} duplicates")
print(f"Total remaining: {total} channels")
