# Merge fresh Persiana channels (persiana.m3u, made by generate_persiana.py)
# with the static Persian news channels (news.m3u) into one hosted playlist.
import io

RAW = "https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main"
EPG = RAW + "/persiana.xml.gz"

persiana = io.open("persiana.m3u", encoding="utf-8").read().splitlines()
news = io.open("news.m3u", encoding="utf-8").read().splitlines()

out = ['#EXTM3U x-tvg-url="%s"' % EPG]
# Persiana channels (skip the playlist's own #EXTM3U header line)
out += [l for l in persiana if not l.startswith("#EXTM3U")]
# News channels (no EPG, but live)
out += [l for l in news if l.strip() and not l.startswith("#EXTM3U")]

io.open("persian_all.m3u", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("persian_all.m3u -", sum(1 for l in out if l.startswith("#EXTINF")), "channels")
