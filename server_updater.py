#!/usr/bin/env python3
"""Server-side updater: proxy Telewebion via EasyProxy, add Israel Ch12, merge Sepehr EPG."""
import re, gzip, requests, time
from pathlib import Path
from urllib.parse import quote

PROXY_BASE = "http://localhost:7860"
SERVER_IP = "181.214.140.229"
SEPEHR_EPG_URLS = [
    "https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz",
    "https://sepehr.irib.ir/IRIB/XML/fa/EPG.xml",
]

def proxy_url(original_url):
    return f"http://{SERVER_IP}:7860/proxy/manifest.m3u8?url={quote(original_url, safe='')}"

def update_irib_m3u():
    """Rewrite irib.m3u: route telewebion streams through EasyProxy. Uses original URLs from irib_original.m3u."""
    orig = Path("irib_original.m3u")
    src_file = Path("irib.m3u")
    # save original once, always read from it to avoid double-proxying
    if not orig.exists():
        # strip any existing proxy wrapping to recover originals
        lines = src_file.read_text(encoding="utf-8").splitlines()
        clean = []
        for line in lines:
            if "proxy/manifest" in line and "telewebion" in line:
                # extract original URL from proxy wrapper
                import urllib.parse
                m = re.search(r'url=(.+)', line)
                if m:
                    decoded = urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(m.group(1))))
                    if "telewebion" in decoded:
                        clean.append(decoded.split("url=")[-1] if "url=" in decoded else decoded)
                        continue
                clean.append(line)
            else:
                clean.append(line)
        orig.write_text("\n".join(clean) + "\n", encoding="utf-8")
    # always read from original, apply proxy fresh
    lines = orig.read_text(encoding="utf-8").splitlines()
    out = []
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("http") and "telewebion" in stripped:
            out.append(proxy_url(stripped))
            count += 1
        else:
            out.append(line)
    src_file.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"irib.m3u proxied — {count} streams via EasyProxy")

def add_israel_ch12():
    """Add Channel 12 Israel (from Kodi repo) to extra_channels.tsv if not present."""
    tsv = Path("extra_channels.tsv").read_text(encoding="utf-8")
    # remove old Channel 12 entry if exists, re-add with new URL
    lines = tsv.splitlines()
    lines = [l for l in lines if "Channel 12" not in l and "شبکه 12 اسرائیل" not in l]
    Path("extra_channels.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    ch12_url = f"http://{SERVER_IP}:8891/"
    ch12_line = 'شبکه‌های خارجی|شبکه 12 اسرائیل|Channel 12 Israel|https://upload.wikimedia.org/wikipedia/he/thumb/4/4e/Keshet_12_Logo_2018.svg/320px-Keshet_12_Logo_2018.svg.png|' + ch12_url
    with open("extra_channels.tsv", "a", encoding="utf-8") as f:
        f.write(ch12_line + "\n")
    print("Channel 12 Israel added (via proxy for geo-bypass)")

def fetch_sepehr_epg():
    """Fetch IRIB EPG from Sepehr or iptv-org fallback."""
    for url in SEPEHR_EPG_URLS:
        print(f"Trying EPG: {url[:60]}...")
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
            if r.status_code != 200:
                print(f"  HTTP {r.status_code}, skipping")
                continue
            data = r.content
            if url.endswith(".gz"):
                xml_text = gzip.decompress(data).decode("utf-8", errors="replace")
            else:
                xml_text = data.decode("utf-8", errors="replace")
            if "<programme" not in xml_text:
                print("  No programmes found, skipping")
                continue
            Path("irib.xml").write_text(xml_text, encoding="utf-8")
            with gzip.open("irib.xml.gz", "wb") as f:
                f.write(xml_text.encode("utf-8"))
            programs = xml_text.count("<programme")
            channels = xml_text.count("<channel")
            print(f"  EPG OK — {channels} channels, {programs} programs")
            return
        except Exception as e:
            print(f"  Failed: {e}")
    print("All EPG sources failed, keeping existing")

def build_final():
    """Run generate_all.py then build_all.py to produce final.m3u + final.xml.gz."""
    import subprocess
    print("Running generate_all.py...")
    subprocess.run(["python3", "generate_all.py"], check=True)
    print("Proxying Telewebion streams...")
    update_irib_m3u()
    print("Running build_all.py...")
    subprocess.run(["python3", "build_all.py"], check=True)
    if Path("all.m3u").exists():
        Path("final.m3u").write_text(Path("all.m3u").read_text(encoding="utf-8"), encoding="utf-8")
    if Path("all.xml.gz").exists():
        Path("final.xml.gz").write_bytes(Path("all.xml.gz").read_bytes())
    print("final.m3u + final.xml.gz ready")

if __name__ == "__main__":
    add_israel_ch12()
    fetch_sepehr_epg()
    build_final()
    print("ALL DONE!")
