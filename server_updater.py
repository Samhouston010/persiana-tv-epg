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

# channels that stay in سراسری — everything else national → خبری و سرگرمی
SARASARI_SLUGS = {'tv1','tv2','tv3','tv4','tehran','ofogh','amouzesh','salamat','faratar'}

SLUG_LOGO = {
    'tv1':'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/IRIBTV1.svg/960px-IRIBTV1.svg.png',
    'tv2':'https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/IRIB_TV2_logo.svg/960px-IRIB_TV2_logo.svg.png',
    'tv3':'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/IRIB_TV3_LOGO.svg/960px-IRIB_TV3_LOGO.svg.png',
    'tv4':'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/IRIB_TV4_logo.svg/960px-IRIB_TV4_logo.svg.png',
    'tehran':'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/IRIBTV5.svg/500px-IRIBTV5.svg.png',
    'varzesh':'https://upload.wikimedia.org/wikipedia/fa/thumb/f/f5/Iribvarzesh2022.png/960px-Iribvarzesh2022.png',
    'ofogh':'https://upload.wikimedia.org/wikipedia/fa/thumb/f/fe/Ofogh_TV_logo.svg/960px-Ofogh_TV_logo.svg.png',
    'amouzesh':'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Amouzesh_TV_logo_%282023%29.svg/500px-Amouzesh_TV_logo_%282023%29.svg.png',
    'irinn':'https://i.imgur.com/8tzsC9h.png',
    'irinn2':'https://i.imgur.com/8tzsC9h.png',
    'nasim':'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Nasim_TV_logo.svg/960px-Nasim_TV_logo.svg.png',
    'namayesh':'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Namayesh_TV_logo.svg/960px-Namayesh_TV_logo.svg.png',
    'mostanad':'https://upload.wikimedia.org/wikipedia/fa/8/89/Mostanad-tv.png',
    'ifilm':'https://upload.wikimedia.org/wikipedia/commons/b/b9/IFILM.png',
    'salamat':'https://upload.wikimedia.org/wikipedia/fa/f/f0/IRIB_Salamat_Logo.png',
    'pooya':'https://upload.wikimedia.org/wikipedia/fa/5/5a/POOYA_tv_2.png',
    'omid':'https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/IRIB_Omid.svg/500px-IRIB_Omid.svg.png',
    'sepehr':'https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Sepehrtv.png/960px-Sepehrtv.png',
    'faratar':'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/IRIB_FARATAR_UHD.png/960px-IRIB_FARATAR_UHD.png',
    'tamasha':'https://upload.wikimedia.org/wikipedia/fa/thumb/f/f2/IRIB_tamashaTV.svg/960px-IRIB_tamashaTV.svg.png',
    'abadan':'https://upload.wikimedia.org/wikipedia/fa/3/39/Abadan_tv.png',
    'azarbayjangharbi':'https://upload.wikimedia.org/wikipedia/fa/thumb/2/21/Urmia_TV.svg/960px-Urmia_TV.svg.png',
    'ara':'https://i.ibb.co/dwSHt2SG/Ara.png',
    'aftab':'https://upload.wikimedia.org/wikipedia/fa/thumb/6/6e/Arak_AFTAB.svg/960px-Arak_AFTAB.svg.png',
    'atrak':'https://upload.wikimedia.org/wikipedia/fa/thumb/2/28/Bojnourd_ATRAK_TV.svg/960px-Bojnourd_ATRAK_TV.svg.png',
    'esfahan':'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/IsfahanTV.svg/960px-IsfahanTV.svg.png',
    'aflak':'https://i.imgur.com/LkLCHpf.png',
    'alborz':'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Alborz_TV_logo.svg/960px-Alborz_TV_logo.svg.png',
    'ilam':'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Ilam_TV.png/960px-Ilam_TV.png',
    'baran':'https://upload.wikimedia.org/wikipedia/fa/thumb/b/b9/TV_Baran.svg/500px-TV_Baran.svg.png',
    'bushehr':'https://upload.wikimedia.org/wikipedia/fa/thumb/9/94/Bushehr_TV.svg/500px-Bushehr_TV.svg.png',
    'jahanbin':'https://upload.wikimedia.org/wikipedia/fa/thumb/4/4a/Shahrekord_Jahanbin.svg/960px-Shahrekord_Jahanbin.svg.png',
    'khavaran':'https://upload.wikimedia.org/wikipedia/fa/8/86/KHAVARAN_tv.png',
    'khorasanrazavi':'https://upload.wikimedia.org/wikipedia/fa/b/bd/%D9%84%D9%88%DA%AF%D9%88_%D8%B4%D8%A8%DA%A9%D9%87_%D8%AE%D8%B1%D8%A7%D8%B3%D8%A7%D9%86_%D8%B1%D8%B6%D9%88%DB%8C.png',
    'khalijefars':'https://upload.wikimedia.org/wikipedia/fa/thumb/7/7c/Bandar_KHALI_J_e_FARS_TV.svg/960px-Bandar_KHALI_J_e_FARS_TV.svg.png',
    'khoozestan':'https://upload.wikimedia.org/wikipedia/fa/thumb/9/9a/Ahwaz_TV.svg/960px-Ahwaz_TV.svg.png',
    'dena':'https://upload.wikimedia.org/wikipedia/fa/thumb/1/1c/Yasuj_DENA.svg/960px-Yasuj_DENA.svg.png',
    'zagros':'https://upload.wikimedia.org/wikipedia/fa/thumb/e/e4/Kermanshah_Zaghros.svg/960px-Kermanshah_Zaghros.svg.png',
    'sabalan':'https://upload.wikimedia.org/wikipedia/fa/f/f2/Ardabil_SABALAN.png',
    'semnan':'https://upload.wikimedia.org/wikipedia/fa/3/35/Semnan_TV.png',
    'sahand':'https://upload.wikimedia.org/wikipedia/fa/thumb/3/37/Tabriz_Sahand.svg/960px-Tabriz_Sahand.svg.png',
    'fars':'https://upload.wikimedia.org/wikipedia/fa/7/7b/Iribfars.png',
    'qazvin':'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/QazvinTV.svg/960px-QazvinTV.svg.png',
    'tabarestan':'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/IRIB_Mazandaran_Last_Orange_Logo.png/960px-IRIB_Mazandaran_Last_Orange_Logo.png',
    'mahabad':'https://upload.wikimedia.org/wikipedia/fa/c/cb/Mahabad_tv.png',
    'hamoon':'https://upload.wikimedia.org/wikipedia/fa/b/bc/Zahedan_Hamoon.png',
    'sina':'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/IRIB_Hamadan_tv.svg/960px-IRIB_Hamadan_tv.svg.png',
    'kordestan':'https://upload.wikimedia.org/wikipedia/fa/thumb/2/2c/Sanandaj_KORDESTAN.svg/960px-Sanandaj_KORDESTAN.svg.png',
    'kerman':'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Kerman_irib_logo_%28blue_version%29.png/960px-Kerman_irib_logo_%28blue_version%29.png',
    'kish':'https://upload.wikimedia.org/wikipedia/fa/thumb/1/14/Kish_tv.svg/960px-Kish_tv.svg.png',
    'taban':'https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Yazd_taban.svg/960px-Yazd_taban.svg.png',
    'hdtest':'https://upload.wikimedia.org/wikipedia/fa/thumb/f/f2/IRIB_tamashaTV.svg/960px-IRIB_tamashaTV.svg.png',
    'nesfejahan':'https://static.televebion.net/web/content_images/channel_images/thumbs/new/240/v4/nesfejahan.png',
    'quran':'https://static.televebion.net/web/content_images/channel_images/thumbs/new/240/v4/quran.png',
    'noor':'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/IRIB_Noor_logo.png/960px-IRIB_Noor_logo.png',
    'sabz':'https://upload.wikimedia.org/wikipedia/fa/thumb/e/e3/Golestan_TV.svg/960px-Golestan_TV.svg.png',
    'kawthar':'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/AlKawtharTV.svg/960px-AlKawtharTV.svg.png',
    'alalam':'https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Al_Alam_News_Network_logo.svg/960px-Al_Alam_News_Network_logo.svg.png',
    'presstv':'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Press_TV_logo.svg/960px-Press_TV_logo.svg.png',
    'palestine':'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Palestine_TV_logo.png/960px-Palestine_TV_logo.png',
    'velayat':'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Velayat_TV.png/960px-Velayat_TV.png',
    'tv1plus':'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/IRIB_TV1plus.png/960px-IRIB_TV1plus.png',
    'sport1':'https://upload.wikimedia.org/wikipedia/fa/thumb/f/f5/Iribvarzesh2022.png/960px-Iribvarzesh2022.png',
    'sport2':'https://upload.wikimedia.org/wikipedia/fa/thumb/f/f5/Iribvarzesh2022.png/960px-Iribvarzesh2022.png',
    'sport3':'https://upload.wikimedia.org/wikipedia/fa/thumb/f/f5/Iribvarzesh2022.png/960px-Iribvarzesh2022.png',
}

SLUG_TVG_ID = {
    'tv1':'IRIB1.ir','tv2':'IRIB2.ir','tv3':'IRIB3.ir','tv4':'IRIB4.ir',
    'tehran':'TehranTV.ir','varzesh':'VarzeshTV.ir','ofogh':'OfoghTV.ir',
    'amouzesh':'AmouzeshTV.ir','irinn':'IRINN.ir','irinn2':'IRINN2.ir',
    'nasim':'Nasim.ir','namayesh':'NamayeshTV.ir','mostanad':'IRIBMostanad.ir',
    'ifilm':'iFilmPersian.ir','salamat':'SalamatTV.ir','pooya':'PooyaTV.ir',
    'omid':'IRIBOmid.ir','sepehr':'SepehrTV.ir','faratar':'IRIBUHD.ir',
    'tamasha':'Tamasha.ir','abadan':'AbadanTV.ir','azarbayjangharbi':'WestAzerbaijanTV.ir',
    'esfahan':'IsfahanTV.ir','alborz':'AlborzTV.ir','ilam':'IlamTV.ir',
    'baran':'BaranTV.ir','bushehr':'BoushehrTV.ir','khorasanrazavi':'KhorasanRazaviTV.ir',
    'khalijefars':'KhalijeFarsTV.ir','khoozestan':'KhozestanTV.ir','dena':'DenaTV.ir',
    'zagros':'ZagrosTV.ir','sabalan':'SabalanTV.ir','semnan':'SemnanTV.ir',
    'sahand':'SahandTV.ir','fars':'FarsTV.ir','qazvin':'QazvinTV.ir',
    'tabarestan':'TabarestanTV.ir','mahabad':'MahabadTV.ir','hamoon':'HamoonTV.ir',
    'sina':'HamedanTV.ir','karoon':'KaroonTV.ir','kordestan':'KordestanTV.ir',
    'kerman':'KermanTV.ir','kish':'KishTV.ir','taban':'YazdTV.ir',
}

def fetch_irib_m3u():
    """Fetch live channel list from Telewebion API and rebuild irib.m3u + irib_original.m3u."""
    API = "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=300&v=5.9.0"
    HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://telewebion.ir/"}
    try:
        data = requests.get(API, headers=HEADERS, timeout=20).json()
        channels = data["body"]["queryChannel"]
    except Exception as e:
        print(f"Telewebion API failed: {e} — keeping existing irib.m3u")
        return

    lines = ['#EXTM3U x-tvg-url="https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz"']
    count = 0
    for ch in sorted(channels, key=lambda x: x.get("priority", 99)):
        slug = ch.get("descriptor", "")
        t = ch.get("type", {}).get("descriptor", "")
        if t in ("radio",):
            continue
        name = ch.get("name", slug)
        img = ch.get("image_name", "")
        logo = SLUG_LOGO.get(slug) or (f"https://cdn.telewebion.ir/channelsLogo/{img}/default" if img else "")
        tvg_id = SLUG_TVG_ID.get(slug, "")
        url = f"https://ncdn.telewebion.ir/{slug}/live/playlist.m3u8"

        if t == "provincial":
            group = "استانی"
        elif t == "national" and slug in SARASARI_SLUGS:
            group = "سراسری"
        else:
            group = "خبری و سرگرمی"

        lines.append(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}')
        lines.append(url)
        count += 1

    content = "\n".join(lines) + "\n"
    Path("irib.m3u").write_text(content, encoding="utf-8")
    Path("irib_original.m3u").write_text(content, encoding="utf-8")
    print(f"irib.m3u fetched from API — {count} channels")

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

def refresh_world_channels():
    """Re-download Free-TV playlists and update extra_channels.tsv with new channels."""
    FREETV = "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists"
    IPTV_ORG = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams"
    SOURCES = {
        f"{FREETV}/playlist_usa.m3u8": "آمریکا",
        f"{FREETV}/playlist_uk.m3u8": "انگلیس",
        f"{FREETV}/playlist_canada.m3u8": "کانادا",
        f"{IPTV_ORG}/jp.m3u": "ژاپن",
        f"{FREETV}/playlist_germany.m3u8": "آلمان",
        f"{FREETV}/playlist_france.m3u8": "فرانسه",
        f"{FREETV}/playlist_spain.m3u8": "اسپانیا",
        f"{FREETV}/playlist_italy.m3u8": "ایتالیا",
        f"{FREETV}/playlist_turkey.m3u8": "ترکیه",
        f"{FREETV}/playlist_india.m3u8": "هند",
        f"{FREETV}/playlist_australia.m3u8": "استرالیا",
        f"{FREETV}/playlist_netherlands.m3u8": "هلند",
        f"{IPTV_ORG}/lb.m3u": "لبنان",
    }
    # read existing URLs to avoid duplicates
    tsv = Path("extra_channels.tsv").read_text(encoding="utf-8")
    existing_urls = set()
    for line in tsv.splitlines():
        parts = line.split("|")
        if len(parts) >= 5:
            existing_urls.add(parts[4].strip())
    # groups that we manage (don't touch manually-added groups)
    managed_groups = set(SOURCES.values())
    added = 0
    with open("extra_channels.tsv", "a", encoding="utf-8") as f:
        for url, group in SOURCES.items():
            try:
                r = requests.get(url, timeout=20)
                if r.status_code != 200:
                    continue
                lines = r.text.splitlines()
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if line.startswith("#EXTINF"):
                        name_m = re.match(r'.*,(.+)$', line)
                        name = name_m.group(1).strip() if name_m else "Unknown"
                        logo_m = re.search(r'tvg-logo="([^"]*)"', line)
                        logo = logo_m.group(1) if logo_m else ""
                        if i + 1 < len(lines):
                            stream = lines[i+1].strip()
                            if stream.startswith("http") and "youtube.com" not in stream and stream not in existing_urls:
                                f.write(f"{group}|{name}|{name}|{logo}|{stream}\n")
                                existing_urls.add(stream)
                                added += 1
                        i += 2
                    else:
                        i += 1
            except Exception:
                pass
    print(f"World channels: {added} new channels added")

def build_final():
    """Run generate_all.py then build_all.py to produce final.m3u + final.xml.gz."""
    import subprocess
    print("Refreshing world channels...")
    refresh_world_channels()
    print("Running generate_all.py...")
    subprocess.run(["python3", "generate_all.py"], check=True)
    print("Fetching Telewebion channels from API...")
    fetch_irib_m3u()
    print("Running build_all.py...")
    subprocess.run(["python3", "build_all.py"], check=True)
    if Path("all.m3u").exists():
        Path("final.m3u").write_text(Path("all.m3u").read_text(encoding="utf-8"), encoding="utf-8")
    if Path("all.xml.gz").exists():
        Path("final.xml.gz").write_bytes(Path("all.xml.gz").read_bytes())
    print("Adding anti-freeze tags...")
    add_antifreeze()
    print("final.m3u + final.xml.gz ready")

def add_antifreeze():
    """Add anti-freeze tags to every channel in final.m3u."""
    TAGS = [
        '#EXTVLCOPT:network-caching=5000',
        '#EXTVLCOPT:http-reconnect=true',
        '#EXTVLCOPT:http-continuous=true',
        '#KODIPROP:inputstream=inputstream.adaptive',
        '#KODIPROP:inputstream.adaptive.manifest_type=hls',
        '#KODIPROP:inputstream.adaptive.stream_selection_type=adaptive',
    ]
    f = Path("final.m3u")
    lines = f.read_text(encoding="utf-8").splitlines()
    out = []
    count = 0
    for line in lines:
        if line.startswith("#EXTINF"):
            for tag in TAGS:
                out.append(tag)
            count += 1
        out.append(line)
    f.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Anti-freeze tags added to {count} channels")

if __name__ == "__main__":
    add_israel_ch12()
    fetch_sepehr_epg()
    build_final()
    print("ALL DONE!")
