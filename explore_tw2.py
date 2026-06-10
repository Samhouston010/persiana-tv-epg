import requests, json
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://telewebion.ir/"}
url = "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=300&v=5.9.0"
data = requests.get(url, headers=HEADERS, timeout=20).json()

body = data["body"]
print("body type:", type(body).__name__)
if isinstance(body, dict):
    print("body keys:", list(body.keys()))
    for k, v in body.items():
        if isinstance(v, list):
            print("  list in body[" + k + "], count:", len(v))
            if v:
                print("  first item keys:", list(v[0].keys()))
                print("  sample:", json.dumps(v[0], ensure_ascii=False)[:500])
elif isinstance(body, list):
    print("body is list, count:", len(body))
    print("first item keys:", list(body[0].keys()))
    print("sample:", json.dumps(body[0], ensure_ascii=False)[:500])
