import re

# 1. اسکریپت update_with_iptvorg.py رو درست کن
with open("update_with_iptvorg.py","r",encoding="utf-8") as f:
    script = f.read()

# خط هدر رو با هدر ثابت تمیز جایگزین کن
script = script.replace(
    'header = base_content.splitlines()[0]',
    'header = \'#EXTM3U x-tvg-url="https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz"\''
)

with open("update_with_iptvorg.py","w",encoding="utf-8") as f:
    f.write(script)
print("Script fixed")

# 2. all.m3u رو هم درست کن
with open("all.m3u","r",encoding="utf-8") as f:
    lines = f.readlines()
lines[0] = '#EXTM3U x-tvg-url="https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz"\n'
with open("all.m3u","w",encoding="utf-8") as f:
    f.writelines(lines)
print("all.m3u fixed")
