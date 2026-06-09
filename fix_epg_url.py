with open("all.m3u","r",encoding="utf-8") as f:
    content = f.read()

old = 'x-tvg-url="https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.xml.gz"'
new = 'x-tvg-url="https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main/all.xml.gz https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz"'

content = content.replace(old, new)
with open("all.m3u","w",encoding="utf-8") as f:
    f.write(content)
print("Done")
