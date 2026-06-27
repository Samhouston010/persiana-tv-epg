"""
api_check.py — Persiana API health check + auto-fallback
Runs daily. Updates api_config.json and generate_persiana.py if endpoint changes.
"""
import json, os, re, urllib.request
from pathlib import Path
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT  = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.persianagroup.tv/"}

# ── Persiana API alternatives ──────────────────────────────────────────────────
PERSIANA_ALTERNATIVES = [
    "https://www.persianagroup.tv/api/v1",
    "https://app.persianagroup.tv/api/v1",
    "https://api.persianagroup.tv/v1",
    "https://www.persianagroup.tv/api/v2",
]

# ── Telewebion Kandoo API (for channel-list used in import_channels.py) ────────
KANDOO_ALTERNATIVES = [
    "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=300&v=5.9.0",
    "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=300&v=6.0.0",
    "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=300&v=5.8.0",
]


def alert(msg):
    print(f"[ALERT] {msg}")
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return
    try:
        data = json.dumps({"chat_id": TELEGRAM_CHAT, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  Telegram error: {e}")


def test_persiana(base_url):
    try:
        r = requests.get(f"{base_url}/channels", headers=HEADERS, timeout=15)
        return r.ok and "channels" in r.text
    except Exception:
        return False


def test_kandoo(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.ok and "queryChannel" in r.text
    except Exception:
        return False


def load_cfg():
    p = Path("api_config.json")
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_cfg(cfg):
    Path("api_config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def patch_generate_persiana(new_base):
    """Update API constant in generate_persiana.py."""
    gp = Path("generate_persiana.py")
    if not gp.exists():
        return
    text = gp.read_text(encoding="utf-8")
    new_text = re.sub(r"API\s*=\s*'https://[^']*api[^']*'", f"API='{new_base}'", text)
    new_text = re.sub(r'API\s*=\s*"https://[^"]*api[^"]*"', f'API="{new_base}"', new_text)
    if new_text != text:
        gp.write_text(new_text, encoding="utf-8")
        print(f"  generate_persiana.py patched → {new_base}")


def patch_import_channels(new_url):
    """Update Kandoo URL in import_channels.py."""
    ip = Path("import_channels.py")
    if not ip.exists():
        return
    text = ip.read_text(encoding="utf-8")
    new_text = re.sub(r'https://gateway\.telewebion\.ir/kandoo/[^\'"]+', new_url, text)
    if new_text != text:
        ip.write_text(new_text, encoding="utf-8")
        print(f"  import_channels.py patched → {new_url}")


def check_persiana(cfg):
    current = cfg.get("persiana_api", PERSIANA_ALTERNATIVES[0])
    if test_persiana(current):
        print(f"✅ Persiana API OK: {current}")
        return True

    print(f"❌ Persiana API FAILED: {current}")
    for alt in PERSIANA_ALTERNATIVES:
        if alt == current:
            continue
        if test_persiana(alt):
            print(f"  ✅ Fallback: {alt}")
            cfg["persiana_api"] = alt
            save_cfg(cfg)
            patch_generate_persiana(alt)
            alert(f"⚠️ Persiana API changed!\nNew: {alt}\nAuto-updated generate_persiana.py")
            return True

    alert("🚨 Persiana API ALL FAILED!\npersianagroup.tv is unreachable. Manual fix needed.")
    return False


def check_kandoo(cfg):
    current = cfg.get("kandoo_url", KANDOO_ALTERNATIVES[0])
    if test_kandoo(current):
        print(f"✅ Kandoo API OK")
        return True

    print(f"❌ Kandoo API FAILED")
    for alt in KANDOO_ALTERNATIVES:
        if alt == current:
            continue
        if test_kandoo(alt):
            print(f"  ✅ Fallback: {alt}")
            cfg["kandoo_url"] = alt
            save_cfg(cfg)
            patch_import_channels(alt)
            alert(f"⚠️ Telewebion Kandoo API changed!\nNew: {alt}\nAuto-updated import_channels.py")
            return True

    alert("🚨 Kandoo API ALL FAILED! import_channels.py cannot discover channels.")
    return False


def main():
    cfg = load_cfg()
    print("=== Persiana API Health Check ===")
    p_ok = check_persiana(cfg)
    k_ok = check_kandoo(cfg)
    print(f"\nSummary: persiana={'✅' if p_ok else '❌'} kandoo={'✅' if k_ok else '❌'}")
    if not (p_ok and k_ok):
        exit(1)


if __name__ == "__main__":
    main()
