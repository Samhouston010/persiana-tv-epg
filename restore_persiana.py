import re

PERSIANA_ORIGINALS = {
    "Family":    "https://familyhls.persiana.live/hls/stream.m3u8",
    "Series":    "https://onehls.persiana.live/hls/stream.m3u8",
    "Cinema":    "https://cinehls.persiana.live/hls/stream.m3u8",
    "Korea":     "https://korhls.persiana.live/hls/stream.m3u8",
    "Persiana+": "https://euhls.persiana.live/hls/stream.m3u8",
    "Iranian":   "https://irhls.persiana.live/hls/stream.m3u8",
    "Comedy":    "https://comedyhls.persiana.live/hls/stream.m3u8",
    "Reality":   "https://realhls.persiana.live/hls/stream.m3u8",
    "Medical":   "https://phd2hls.persiana.live/hls/stream.m3u8",
    "Docs":      "https://scihls.persiana.live/hls/stream.m3u8",
    "Junior":    "https://junhls.persiana.live/hls/stream.m3u8",
    "Fight":     "https://fighthls.persiana.live/hls/stream.m3u8",
    "Music":     "https://musichls.persiana.live/hls/stream.m3u8",
    "Nostalgia": "https://noshls.persiana.live/hls/stream.m3u8",
    "Folk":      "https://sonhls.persiana.live/hls/stream.m3u8",
    "SetMix":    "https://setmixhls.persiana.live/hls/stream.m3u8",
    "Travel":    "https://ptravelhls.persiana.live/hls/stream.m3u8",
    "4 Kurd":    "https://4kuhls.persiana.live/hls/stream.m3u8",
    "Türkiye":   "https://turkhls.persiana.live/hls/stream.m3u8",
}

with open("all.m3u", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()
result = []
i = 0
restored = 0

while i < len(lines):
    line = lines[i]
    if line.startswith("#EXTINF:") and 'group-title="پرشیانا"' in line:
        # نام کانال رو پیدا کن
        name_m = re.search(r',(.+)$', line)
        ch_name = name_m.group(1).strip() if name_m else ""
        
        # URL بعدی
        next_url = lines[i+1] if i+1 < len(lines) else ""
        
        # اگه در لیست originals هست، restore کن
        if ch_name in PERSIANA_ORIGINALS:
            original_url = PERSIANA_ORIGINALS[ch_name]
            if next_url != original_url:
                print(f"  RESTORE: {ch_name}")
                print(f"    was: {next_url[:70]}")
                print(f"    now: {original_url}")
                result.append(line)
                result.append(original_url)
                if i+2 < len(lines) and lines[i+2] == "":
                    result.append("")
                    i += 3
                else:
                    i += 2
                restored += 1
                continue
    
    result.append(line)
    i += 1

final = "\n".join(result)
with open("all.m3u", "w", encoding="utf-8") as f:
    f.write(final)

print(f"\nRestored {restored} Persiana channels")
print(f"Total: {final.count('#EXTINF:')} channels")
