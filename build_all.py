import gzip, requests
from pathlib import Path

RAW = "https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main"
ALL_EPG = f"{RAW}/all.xml.gz"

def fetch(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content

def build_all_m3u():
    print("Reading persiana.m3u...")
    persiana = Path("persiana.m3u").read_text(encoding="utf-8")
    print("Reading irib.m3u...")
    irib = Path("irib.m3u").read_text(encoding="utf-8")
    lines = persiana.splitlines()
    lines[0] = f'#EXTM3U x-tvg-url="{ALL_EPG}"'
    irib_lines = irib.splitlines()[1:]
    all_lines = lines + [""] + irib_lines
    content = "\n".join(all_lines)
    Path("all.m3u").write_text(content, encoding="utf-8")
    count = content.count("#EXTINF")
    print(f"all.m3u — {count} channels")
    return count

def build_all_xml():
    print("Reading persiana.xml.gz...")
    try:
        persiana_xml = gzip.decompress(Path("persiana.xml.gz").read_bytes()).decode("utf-8")
    except:
        print("  fetching from GitHub...")
        persiana_xml = gzip.decompress(fetch(f"{RAW}/persiana.xml.gz")).decode("utf-8")
    print("Reading irib.xml.gz...")
    irib_xml = gzip.decompress(Path("irib.xml.gz").read_bytes()).decode("utf-8")
    persiana_body = persiana_xml.strip()
    if persiana_body.endswith("</tv>"):
        persiana_body = persiana_body[:-5].rstrip()
    irib_inner = []
    skip = True
    for line in irib_xml.splitlines():
        s = line.strip()
        if s.startswith("<channel") or s.startswith("<programme"):
            skip = False
        if s == "<tv>" or s.startswith("<?xml") or s.startswith("<tv "):
            continue
        if s == "</tv>":
            break
        if not skip:
            irib_inner.append(line)
    combined = persiana_body + "\n" + "\n".join(irib_inner) + "\n</tv>"
    Path("all.xml").write_text(combined, encoding="utf-8")
    with gzip.open("all.xml.gz", "wb") as f:
        f.write(combined.encode("utf-8"))
    print(f"all.xml.gz — {combined.count('<channel ')} channels, {combined.count('<programme ')} programs")

def main():
    build_all_m3u()
    build_all_xml()
    print("Done!")

if __name__ == "__main__":
    main()
