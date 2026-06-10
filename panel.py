# -*- coding: utf-8 -*-
import os, re, subprocess, requests
from flask import Flask, request, jsonify, Response

APP_DIR = os.path.dirname(os.path.abspath(__file__))
M3U_FILE = os.path.join(APP_DIR, "final.m3u")
HDR = {"User-Agent": "Mozilla/5.0", "Referer": "https://telewebion.ir/"}
app = Flask(__name__)

def parse():
    if not os.path.exists(M3U_FILE): return []
    lines = open(M3U_FILE, encoding="utf-8").read().splitlines()
    ch, ext = [], None
    for line in lines:
        s = line.strip()
        if s.startswith("#EXTINF"): ext = s
        elif s and not s.startswith("#") and ext is not None:
            def gv(k):
                m = re.search(k + r'="([^"]*)"', ext); return m.group(1) if m else ""
            ch.append({"name": ext.split(",",1)[-1].strip(), "logo": gv("tvg-logo"),
                       "tvgid": gv("tvg-id"), "group": gv("group-title"), "url": s})
            ext = None
    return ch

def write(ch):
    q = chr(34); out = ["#EXTM3U"]
    for c in ch:
        p = ["#EXTINF:-1"]
        if c.get("tvgid"): p.append("tvg-id="+q+c["tvgid"]+q)
        p.append("tvg-logo="+q+c.get("logo","")+q)
        p.append("group-title="+q+c.get("group","")+q)
        out.append(" ".join(p)+","+c["name"]); out.append(c["url"])
    open(M3U_FILE,"w",encoding="utf-8").write("\n".join(out)+"\n")

@app.route("/api/channels")
def ch_api(): return jsonify(parse())

@app.route("/api/save", methods=["POST"])
def save_api():
    write(request.get_json().get("channels", []))
    return jsonify({"ok": True})

@app.route("/api/test", methods=["POST"])
def test_api():
    url = request.get_json().get("url","")
    try:
        r = requests.get(url, headers=HDR, timeout=10, stream=True, allow_redirects=True)
        ok = r.status_code == 200
        c = next(r.iter_content(256), b"") if ok else b""
        r.close()
        return jsonify({"alive": bool(ok and len(c)>0), "status": r.status_code})
    except Exception as e:
        return jsonify({"alive": False, "status": type(e).__name__})

@app.route("/api/push", methods=["POST"])
def push_api():
    try:
        log = []
        for c in [["git","add","final.m3u"],["git","commit","-m","update via panel"],["git","push"]]:
            p = subprocess.run(c, cwd=APP_DIR, capture_output=True, text=True, timeout=60)
            log.append((p.stdout+p.stderr).strip()[:150])
        return jsonify({"ok": True, "log": log})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.route("/")
def index(): return Response(PAGE, mimetype="text/html")

PAGE = r"""<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Panel</title>
<style>body{font-family:Tahoma;background:#0f1419;color:#e0e0e0;margin:0;padding:20px}
h1{color:#2dd4bf;font-size:19px}.bar{display:flex;gap:8px;margin:14px 0;flex-wrap:wrap}
button{background:#1e293b;color:#e0e0e0;border:1px solid #334155;padding:8px 13px;border-radius:8px;cursor:pointer;font-family:inherit}
button:hover{background:#334155}.primary{background:#0d9488;border-color:#0d9488}.danger{background:#7f1d1d;border-color:#7f1d1d}
input,select{background:#1e293b;color:#e0e0e0;border:1px solid #334155;padding:7px;border-radius:6px;font-family:inherit}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:right;padding:7px;border-bottom:1px solid #1e293b}
th{color:#2dd4bf}tr:hover{background:#1a2332}.grp{color:#fbbf24}.live{color:#4ade80}.dead{color:#f87171}
.small{font-size:11px;color:#94a3b8}#search{width:200px}</style></head><body>
<h1>Playlist Manager - final.m3u</h1>
<div class="bar"><input id="search" placeholder="search...">
<select id="gf"><option value="">all groups</option></select>
<button class="primary" onclick="add()">+ new</button>
<button onclick="testAll()">test all</button>
<button class="primary" onclick="save()">save</button>
<button onclick="push()">save + push</button>
<span id="status" class="small"></span></div>
<table><thead><tr><th>#</th><th>name</th><th>group</th><th>url</th><th>status</th><th>act</th></tr></thead>
<tbody id="rows"></tbody></table><script>
let C=[];
async function load(){C=await(await fetch('/api/channels')).json();render();}
function grps(){return[...new Set(C.map(c=>c.group))].filter(Boolean);}
function render(){
 let gf=document.getElementById('gf'),cur=gf.value;
 gf.innerHTML='<option value="">all groups</option>'+grps().map(g=>'<option '+(g===cur?'selected':'')+'>'+g+'</option>').join('');
 let q=document.getElementById('search').value.toLowerCase(),fg=gf.value,tb=document.getElementById('rows');tb.innerHTML='';
 C.forEach((c,i)=>{if(q&&!c.name.toLowerCase().includes(q))return;if(fg&&c.group!==fg)return;
  let tr=document.createElement('tr');
  tr.innerHTML='<td>'+(i+1)+'</td>'+
  '<td><input value="'+esc(c.name)+'" onchange="u('+i+",'name',this.value)\" style=\"width:140px\"></td>"+
  '<td><input value="'+esc(c.group)+'" onchange="u('+i+",'group',this.value)\" class=\"grp\" style=\"width:110px\"></td>"+
  '<td><input value="'+esc(c.url)+'" onchange="u('+i+",'url',this.value)\" style=\"width:250px\" class=\"small\"></td>"+
  '<td id="st'+i+'" class="small">-</td>'+
  '<td><button onclick="t('+i+')">test</button> <button class="danger" onclick="d('+i+')">del</button></td>';
  tb.appendChild(tr);});
 document.getElementById('status').textContent=C.length+' channels';}
function esc(s){return(s||'').replace(/"/g,'&quot;');}
function u(i,k,v){C[i][k]=v;}
function d(i){if(confirm('delete '+C[i].name+'?')){C.splice(i,1);render();}}
function add(){let n=prompt('name:');if(!n)return;let url=prompt('url:');if(!url)return;
 let g=prompt('group:','new')||'';C.unshift({name:n,url:url,group:g,logo:'',tvgid:''});render();}
async function t(i){let st=document.getElementById('st'+i);st.textContent='...';
 let d=await(await fetch('/api/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:C[i].url})})).json();
 st.innerHTML=d.alive?'<span class=live>live</span>':'<span class=dead>dead('+d.status+')</span>';}
async function testAll(){for(let i=0;i<C.length;i++){if(document.getElementById('st'+i))await t(i);}}
async function save(){let d=await(await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({channels:C})})).json();
 document.getElementById('status').textContent='saved';}
async function push(){await save();document.getElementById('status').textContent='pushing...';
 let d=await(await fetch('/api/push',{method:'POST'})).json();
 document.getElementById('status').textContent=d.ok?'pushed to github':'error';}
document.getElementById('search').addEventListener('input',render);
document.getElementById('gf').addEventListener('change',render);
load();
</script></body></html>"""

if __name__ == "__main__":
    print("="*50)
    print(" Playlist Manager running")
    print(" Open: http://127.0.0.1:8080")
    print("="*50)
    app.run(host="127.0.0.1", port=5500, debug=False)
