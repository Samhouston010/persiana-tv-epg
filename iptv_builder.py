import json, argparse, requests
from datetime import datetime, timezone
try:
    from requests_oauthlib import OAuth1
    HAS_OAUTH = True
except ImportError:
    HAS_OAUTH = False

TELEWEBION_TPL = "https://ncdn.telewebion.ir/{slug}/live/playlist.m3u8"
SEPEHR_API = "https://sepehrapi.sepehrtv.ir/beta/v0"
SEPEHR_CK = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
SEPEHR_CS = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
HEADERS = {"User-Agent": "Mozilla/5.0"}
CHANNELS_FILE = "channels_master.json"
OUTPUT_M3U = "stable.m3u"
TIMEOUT = 8

def is_alive(url):
    if not url:
        return False
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        if r.status_code in (200, 206):
            chunk = next(r.iter_content(512), b"")
            r.close()
            return b"#EXT" in chunk
        r.close()
        return False
    except:
        return False

def get_telewebion(ch):
    slug = ch.get("telewebion_slug")
    if not slug:
        return None
    url = TELEWEBION_TPL.format(slug=slug)
    return url if is_alive(url) else None

def get_sepehr(ch, auth):
    cid = ch.get("sepehr_channel_id")
    if not cid or not auth:
        return None
    try:
        r = requests.get(SEPEHR_API + "/livestream/" + str(cid), auth=auth, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            url = data.get("url") or data.get("streamUrl") or data.get("hls") or ""
            if url and is_alive(url):
                return url
    except:
        pass
    return None

def resolve(ch, auth):
    url = get_telewebion(ch)
    if url:
        return url, "telewebion"
    url = get_sepehr(ch, auth)
    if url:
        return url, "sepehr"
    return None, "dead"

def build_m3u(channels, results):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    epg = "https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz"
    q = chr(34)
    lines = ["#EXTM3U x-tvg-url=" + q + epg + q, "# Generated " + now, ""]
    for ch in channels:
        url, src = results[ch["name"]]
        if not url:
            continue
        tvg = ch.get("tvg_id", "")
        name = ch["name"]
        logo = ch.get("logo", "")
        group = ch.get("group", "Iranian")
        extinf = "#EXTINF:-1 tvg-id=" + q + tvg + q + " tvg-name=" + q + name + q + " tvg-logo=" + q + logo + q + " group-title=" + q + group + q + "," + name
        lines.append(extinf)
        lines.append(url)
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    with open(CHANNELS_FILE, encoding="utf-8-sig") as f:
        channels = json.load(f)
    print(str(len(channels)) + " channels loaded")
    auth = OAuth1(SEPEHR_CK, SEPEHR_CS, signature_method="HMAC-SHA1") if HAS_OAUTH else None
    results = {}
    stats = {"telewebion": 0, "sepehr": 0, "dead": 0}
    for i, ch in enumerate(channels, 1):
        name = ch["name"]
        print("[" + str(i) + "/" + str(len(channels)) + "] " + name + " ...", end=" ", flush=True)
        url, src = resolve(ch, auth)
        results[name] = (url, src)
        stats[src] += 1
        label = {"telewebion": "OK telewebion", "sepehr": "OK sepehr", "dead": "DEAD"}
        print(label[src])
    print("=" * 40)
    print("telewebion: " + str(stats["telewebion"]) + " | sepehr: " + str(stats["sepehr"]) + " | dead: " + str(stats["dead"]))
    if not args.report:
        m3u = build_m3u(channels, results)
        with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
            f.write(m3u)
        print(OUTPUT_M3U + " written - " + str(stats["telewebion"] + stats["sepehr"]) + " live")

if __name__ == "__main__":
    main()