with open("all.m3u","r",encoding="utf-8") as f:
    lines = f.readlines()

# خط اول رو کامل با هدر تمیز جایگزین کن
lines[0] = '#EXTM3U x-tvg-url="https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz"\n'

with open("all.m3u","w",encoding="utf-8") as f:
    f.writelines(lines)

print("Fixed header:")
print(repr(lines[0]))
