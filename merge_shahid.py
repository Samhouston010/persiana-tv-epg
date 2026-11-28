#!/usr/bin/env python3
# owner 2026-11-28: fold the server's Shahid/MBC EPG (programmes carry images) into
# persiana.xml(.gz) so the GitHub guide covers MBC Persia + the Shahid/Arabic channels
# too. Built by shahid_epg.py on the Oracle box. Non-fatal if the server is unreachable.
import gzip, urllib.request
import xml.etree.ElementTree as ET

SRC = "https://147-224-130-108.nip.io/static/shahid_epg.xml.gz"
try:
    data = gzip.decompress(urllib.request.urlopen(SRC, timeout=40).read())
    src = ET.fromstring(data)
except Exception as e:
    print("Shahid fold skipped:", e)
    raise SystemExit(0)

tv = ET.parse("persiana.xml").getroot()
n = 0
for el in src:          # <channel> and <programme> elements, images already inside
    tv.append(el)
    n += 1
ET.ElementTree(tv).write("persiana.xml", encoding="utf-8", xml_declaration=True)
with open("persiana.xml", "rb") as fi, gzip.open("persiana.xml.gz", "wb") as fo:
    fo.writelines(fi)
print("folded", n, "Shahid channels+programmes into persiana.xml.gz")
