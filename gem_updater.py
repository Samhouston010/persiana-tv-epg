# -*- coding: utf-8 -*-
"""
GEM Group Auto-Updater
======================
- Source list ra az iptvcat my_list migirad (khodash rozane update mishavad)
- Faghat kanal-haye GEM ra filter mikonad
- Har link ra LIVE test mikonad (morde-ha hazf mishavand)
- Esm-haye farsi + logo-haye rasmi gemgroup.tv ra mizarad
- Agar source ghabel dastres nabud, az cache-e akharin link-haye salem estefade mikonad
Output: gem.m3u  +  gem_cache.json
Python 3.10 compatible (no backslash in f-strings)
"""

import json
import os
import re
import sys
import requests

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
SOURCE_URLS = [
    # iptvcat "My List" - in link daynamik ast va iptvcat khodash
    # link-haye morde ra rozane avaz mikonad
    "https://list.iptvcat.com/my_list/4054703369901391cbe0018d77f6da0b.m3u8",
]

OUT_M3U = "gem.m3u"
CACHE_FILE = "gem_cache.json"
GROUP_TITLE = "جم گروپ"
TIMEOUT = 15           # seconds per request
STREAM_TEST_TIMEOUT = 12

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0 Safari/537.36"),
    "Accept": "*/*",
}

# ------------------------------------------------------------------
# GEM channel map: normalized-key -> (Persian name, official logo)
# Logos: official icons from gemgroup.tv
# ------------------------------------------------------------------
LOGO = "https://www.gemgroup.tv/assets/images/channels/icon_{}.png"

GEM_MAP = {
    "gem tv plus":        ("جم تی‌وی پلاس",     LOGO.format(17)),
    "gem tv +":           ("جم تی‌وی پلاس",     LOGO.format(17)),
    "gem tv":             ("جم تی‌وی",           LOGO.format(16)),
    "gem 24b":            ("جم ۲۴بی",            LOGO.format(2)),
    "gem arabia":         ("جم عربیا",           LOGO.format(4)),
    "gem az":             ("جم آذری",            LOGO.format(10)),
    "gem bollywood":      ("جم بالیوود",         LOGO.format(6)),
    "gem classic":        ("جم کلاسیک",          LOGO.format(12)),
    "gem comedy":         ("جم کمدی",            LOGO.format(13)),
    "gem documentary":    ("جم مستند",           LOGO.format(14)),
    "gem drama plus":     ("جم درама پلاس",      LOGO.format(7)),
    "gem drama":          ("جم درама",           LOGO.format(36)),
    "gem entertainment":  ("جم سرگرمی",          LOGO.format(8)),
    "gem film":           ("جم فیلم",            LOGO.format(15)),
    "gem fit":            ("جم فیت",             LOGO.format(5)),
    "gem food":           ("جم آشپزی",           LOGO.format(9)),
    "gem junior":         ("جم جونیور",          LOGO.format(18)),
    "gem kids":           ("جم کیدز",            LOGO.format(19)),
    "gem latino":         ("جم لاتینو",          LOGO.format(20)),
    "gem life":           ("جم لایف",            LOGO.format(21)),
    "gem mifa plus":      ("جم میفا پلاس",       LOGO.format(37)),
    "gem mifa":           ("جم میفا",            LOGO.format(22)),
    "gem modern economy": ("جم اقتصاد مدرن",     LOGO.format(23)),
    "gem nature":         ("جم طبیعت",           LOGO.format(25)),
    "gem onyx":           ("جم اونیکس",          LOGO.format(26)),
    "gem pixel":          ("جم پیکسل",           LOGO.format(27)),
    "gem river plus":     ("جم ریور پلاس",       LOGO.format(29)),
    "gem river":          ("جم ریور",            LOGO.format(28)),
    "gem rubix plus":     ("جم روبیکس پلاس",     LOGO.format(31)),
    "gem rubix":          ("جم روبیکس",          LOGO.format(30)),
    "gem series plus":    ("جم سریز پلاس",       LOGO.format(33)),
    "gem series":         ("جم سریز",            LOGO.format(32)),
    "gem sport":          ("جم اسپورت",          LOGO.format(34)),
}

# Fix accidental Cyrillic in two names above (safety)
GEM_MAP["gem drama plus"] = ("جم دراما پلاس", LOGO.format(7))
GEM_MAP["gem drama"] = ("جم دراما", LOGO.format(36))


def normalize(name):
    """lowercase, strip quality tags / brackets / extra spaces"""
    n = name.lower()
    n = re.sub(r"[\(\[].*?[\)\]]", " ", n)          # remove (720p) [Not 24/7]
    n = n.replace("plus", "plus").replace("+", " plus ")
    n = re.sub(r"[^a-z0-9 ]+", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def match_gem(raw_name):
    """return (persian_name, logo, sort_key) if this is a GEM channel"""
    n = normalize(raw_name)
    if "gem" not in n:
        return None
    # longest key first so 'gem series plus' wins over 'gem series'
    for key in sorted(GEM_MAP.keys(), key=len, reverse=True):
        if key in n:
            fa, logo = GEM_MAP[key]
            return (fa, logo, key)
    # unknown GEM channel -> keep it anyway with original name
    return (raw_name.strip(), LOGO.format(16), "zzz " + n)


def parse_m3u(text):
    """yield (display_name, url) pairs"""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = None
    for line in lines:
        if line.startswith("#EXTINF"):
            # name = text after last comma
            name = line.split(",")[-1].strip()
        elif not line.startswith("#") and name:
            yield (name, line)
            name = None


def fetch_source():
    """try each source URL, return raw m3u text or None"""
    for url in SOURCE_URLS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 200 and "#EXT" in r.text:
                print("[OK] source fetched:", url, "| bytes:", len(r.text))
                return r.text
            print("[WARN] source", url, "-> HTTP", r.status_code)
        except Exception as e:
            print("[WARN] source", url, "->", repr(e))
    return None


def is_alive(url):
    """quick liveness test: stream returns 200 and looks like HLS/TS"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=STREAM_TEST_TIMEOUT,
                         stream=True, allow_redirects=True)
        if r.status_code != 200:
            return False
        chunk = next(r.iter_content(chunk_size=512), b"")
        r.close()
        if b"#EXTM3U" in chunk:
            return True
        if len(chunk) > 0:          # raw TS bytes also fine
            return True
        return False
    except Exception:
        return False


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_cache(d):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def write_m3u(channels):
    """channels: list of dicts {fa, logo, url, key}"""
    out = ["#EXTM3U"]
    q = chr(34)
    for ch in sorted(channels, key=lambda c: c["key"]):
        tvgid = "GEM." + re.sub(r"[^a-z0-9]+", "", ch["key"])
        ext = ("#EXTINF:-1 tvg-id=" + q + tvgid + q +
               " tvg-logo=" + q + ch["logo"] + q +
               " group-title=" + q + GROUP_TITLE + q +
               "," + ch["fa"])
        out.append(ext)
        out.append(ch["url"])
    with open(OUT_M3U, "w", encoding="utf-8") as f:
        f.write(chr(10).join(out) + chr(10))


def main():
    cache = load_cache()
    text = fetch_source()

    candidates = {}   # key -> {fa, logo, url, key}

    if text:
        for raw_name, url in parse_m3u(text):
            m = match_gem(raw_name)
            if not m:
                continue
            fa, logo, key = m
            # first occurrence wins (iptvcat puts best first)
            if key not in candidates:
                candidates[key] = {"fa": fa, "logo": logo,
                                   "url": url, "key": key}
        print("[INFO] GEM candidates from source:", len(candidates))
    else:
        print("[WARN] no source reachable - will rely on cache only")

    # merge: source candidates + cached links for channels missing in source
    for key, ch in cache.items():
        if key not in candidates:
            candidates[key] = ch

    # liveness test
    alive, dead = [], []
    for key, ch in candidates.items():
        if is_alive(ch["url"]):
            alive.append(ch)
        else:
            dead.append(ch)
            # fallback: maybe old cached link still works
            old = cache.get(key)
            if old and old["url"] != ch["url"] and is_alive(old["url"]):
                print("[HEAL] using cached link for:", ch["fa"])
                alive.append(old)
                dead.pop()

    print("[INFO] alive:", len(alive), "| dead:", len(dead))
    for d in dead:
        print("   [DEAD]", d["fa"], "->", d["url"][:80])

    if not alive:
        print("[ERROR] no working GEM channels at all - keeping previous gem.m3u")
        sys.exit(0)

    write_m3u(alive)
    save_cache({c["key"]: c for c in alive})
    print("[DONE] gem.m3u written with", len(alive), "channels")


if __name__ == "__main__":
    main()
