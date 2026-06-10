with open("all.m3u", "r", encoding="utf-8") as f:
    lines = f.read().split("\n")

result = []
i = 0
mbc_url = "https://hls.mbcpersia.live/hls/stream.m3u8"
logo = "https://www.aparatchi.com/images/chanells-logo/mbcpersia.svg"

while i < len(lines):
    line = lines[i]
    if line.startswith("#EXTINF:") and "MBC Persia" in line and 'group-title="جم تی وی"' in line:
        # tvg-id رو خالی کن (حذف EPG اشتباه)
        new_line = line.replace('tvg-id="MBC.Persia.ir"', 'tvg-id=""')
        result.append(new_line)
        # خط URL بعدی
        if i+1 < len(lines):
            result.append(lines[i+1])
        i += 2
        continue
    result.append(line)
    i += 1

# یه کپی توی سراسری اضافه کن (آخر فایل)
result.append('#EXTINF:-1 tvg-id="" tvg-name="MBC Persia" tvg-logo="' + logo + '" group-title="سراسری",MBC Persia')
result.append(mbc_url)
result.append("")

with open("all.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(result))

print("Done - MBC Persia EPG cleared + copied to سراسری")
