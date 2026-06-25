"""Add anti-freeze tags to every channel in final.m3u. Telewebion gets bigger buffer."""
from pathlib import Path
import re

TAGS_NORMAL = '\n'.join([
    '#EXTVLCOPT:network-caching=2000',
    '#EXTVLCOPT:http-reconnect=true',
    '#EXTVLCOPT:http-continuous=true',
    '#KODIPROP:inputstream=inputstream.adaptive',
    '#KODIPROP:inputstream.adaptive.manifest_type=hls',
    '#KODIPROP:inputstream.adaptive.stream_selection_type=adaptive',
])

TAGS_TELEWEBION = '\n'.join([
    '#EXTVLCOPT:network-caching=8000',
    '#EXTVLCOPT:http-reconnect=true',
    '#EXTVLCOPT:http-continuous=true',
    '#KODIPROP:inputstream=inputstream.adaptive',
    '#KODIPROP:inputstream.adaptive.manifest_type=hls',
    '#KODIPROP:inputstream.adaptive.stream_selection_type=adaptive',
])

f = Path(__file__).parent / "final.m3u"
text = f.read_text(encoding="utf-8")
# strip old tags
text = re.sub(r'#EXTVLCOPT:[^\n]*\n', '', text)
text = re.sub(r'#KODIPROP:[^\n]*\n', '', text)

lines = text.splitlines()
out = []
count = 0
for i, line in enumerate(lines):
    if line.startswith('#EXTINF:'):
        # check if next line is telewebion
        url = lines[i+1] if i+1 < len(lines) else ''
        if 'telewebion' in url:
            out.append(TAGS_TELEWEBION)
        else:
            out.append(TAGS_NORMAL)
        count += 1
    out.append(line)

f.write_text('\n'.join(out) + '\n', encoding='utf-8')
print(f"Anti-freeze: {count} channels (telewebion=4s buffer, rest=2s)")
