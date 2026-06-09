import re, requests

content = requests.get("https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.m3u").text
lines = content.splitlines()
urls = {}
dupes = []
i = 0
while i < len(lines):
    if lines[i].startswith("#EXTINF:"):
        url = lines[i+1].strip() if i+1 < len(lines) else ""
        group_m = re.search(r'group-title="([^"]*)"', lines[i])
        name_m = re.search(r',(.+)$', lines[i])
        group = group_m.group(1) if group_m else ""
        name = name_m.group(1) if name_m else ""
        if url in urls:
            dupes.append(f"DUPE: [{group}] {name} == [{urls[url][0]}] {urls[url][1]}")
        else:
            urls[url] = (group, name)
        i += 2
    else:
        i += 1

print(f"Found {len(dupes)} duplicate URLs:")
for d in dupes: print(" ", d)
