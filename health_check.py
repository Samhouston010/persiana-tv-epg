"""Channel health checker — tests all channels, removes dead ones, logs slow ones."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import requests, re, concurrent.futures, time
from pathlib import Path

FINAL = Path(__file__).parent / "final.m3u"
TSV   = Path(__file__).parent / "extra_channels.tsv"
TIMEOUT = 8
WORKERS = 30
SPEED_BYTES = 32 * 1024   # download 32KB for speed measurement
SLOW_THRESHOLD_KBPS = 200  # ponytail: below 200 KB/s = slow, raise if too noisy
# groups manually managed — don't auto-remove from TSV
PROTECTED = {"شبکه‌های خارجی"}

def test_channel(url):
    """Returns (alive: bool, speed_kbps: float)."""
    try:
        if "youtube.com" in url:
            return True, 0.0
        if "181.214.140.229:8891" in url or "181.214.140.229:8892" in url:
            return True, 0.0
        t0 = time.monotonic()
        r = requests.get(url, timeout=TIMEOUT, stream=True,
                         headers={"User-Agent": "Mozilla/5.0"},
                         allow_redirects=True)
        if r.status_code != 200:
            return False, 0.0
        data = r.raw.read(SPEED_BYTES)
        elapsed = time.monotonic() - t0
        if not data:
            return False, 0.0
        speed_kbps = (len(data) / 1024) / max(elapsed, 0.001)
        return True, round(speed_kbps, 1)
    except:
        return False, 0.0

def parse_channels(lines):
    """Return list of (extinf_idx, name, url) — works even with anti-freeze tags between EXTINF and URL."""
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            # URL may be directly after or after KODIPROP/EXTVLCOPT tags
            j = i + 1
            while j < len(lines) and (lines[j].startswith("#KODIPROP") or lines[j].startswith("#EXTVLCOPT")):
                j += 1
            if j < len(lines) and lines[j].strip().startswith("http"):
                name = re.search(r',(.+)$', lines[i])
                name = name.group(1).strip() if name else "?"
                channels.append((i, name, lines[j].strip(), j))
            i = j + 1
        else:
            i += 1
    return channels

def run():
    text = FINAL.read_text(encoding="utf-8")
    lines = text.splitlines()
    channels = parse_channels(lines)
    total = len(channels)
    print(f"Testing {total} channels with {WORKERS} threads...\n")

    dead = []
    slow = []
    alive = 0
    def _test(item):
        extinf_idx, name, url, url_idx = item
        ok, speed = test_channel(url)
        return (extinf_idx, name, url, url_idx, ok, speed)

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(_test, ch) for ch in channels]
        for n, f in enumerate(concurrent.futures.as_completed(futs)):
            extinf_idx, name, url, url_idx, ok, speed = f.result()
            if ok:
                alive += 1
                if 0 < speed < SLOW_THRESHOLD_KBPS:
                    slow.append((name, url, speed))
                    print(f"  SLOW ({speed:.0f} KB/s): {name}")
            else:
                dead.append((extinf_idx, name, url, url_idx))
                print(f"  DEAD: {name}")
            if (n + 1) % 100 == 0:
                print(f"  ...tested {n+1}/{total}")

    print(f"\n{'='*50}")
    print(f"Alive: {alive}  Slow: {len(slow)}  Dead: {len(dead)}  Total: {total}")
    print(f"{'='*50}")

    if not dead:
        print("All channels healthy!")
        return

    dead_urls = {url for _, _, url, _ in dead}

    # --- remove from final.m3u (EXTINF block + preceding anti-freeze tags + URL) ---
    dead_line_set = set()
    for extinf_idx, name, url, url_idx in dead:
        # include preceding KODIPROP/EXTVLCOPT lines
        j = extinf_idx - 1
        while j >= 0 and (lines[j].startswith("#KODIPROP") or lines[j].startswith("#EXTVLCOPT")):
            dead_line_set.add(j)
            j -= 1
        dead_line_set.add(extinf_idx)
        dead_line_set.add(url_idx)

    clean_m3u = [l for i, l in enumerate(lines) if i not in dead_line_set]
    FINAL.write_text("\n".join(clean_m3u) + "\n", encoding="utf-8")
    new_count = sum(1 for l in clean_m3u if l.startswith("#EXTINF"))
    print(f"M3U: {total} → {new_count} channels (removed {len(dead)})")

    # --- remove dead URLs from extra_channels.tsv (auto-managed groups only) ---
    tsv_lines = TSV.read_text(encoding="utf-8").splitlines()
    tsv_clean = []
    tsv_removed = 0
    for line in tsv_lines:
        parts = line.split("|")
        if len(parts) >= 5:
            group = parts[0].strip()
            url = parts[4].strip()
            if url in dead_urls and group not in PROTECTED:
                tsv_removed += 1
                continue
        tsv_clean.append(line)
    TSV.write_text("\n".join(tsv_clean) + "\n", encoding="utf-8")
    print(f"TSV: removed {tsv_removed} dead entries (server_updater will refetch fresh ones)")

    dead_log = Path(__file__).parent / "dead_channels.log"
    dead_log.write_text("\n".join(f"{n} | {u}" for _, n, u, _ in dead), encoding="utf-8")
    print(f"Dead log saved → dead_channels.log")

    if slow:
        slow_log = Path(__file__).parent / "slow_channels.log"
        slow_log.write_text(
            "\n".join(f"{speed:.0f} KB/s | {n} | {u}" for n, u, speed in sorted(slow, key=lambda x: x[2])),
            encoding="utf-8"
        )
        print(f"Slow log saved → slow_channels.log ({len(slow)} channels below {SLOW_THRESHOLD_KBPS} KB/s)")

if __name__ == "__main__":
    run()
