# -*- coding: utf-8 -*-
import os, re, gzip, subprocess, shutil, requests
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify, Response

APP_DIR = os.path.dirname(os.path.abspath(__file__))
M3U_FILE = os.path.join(APP_DIR, "final.m3u")
EPG_FILE = os.path.join(APP_DIR, "final.xml.gz")
HDR = {"User-Agent": "Mozilla/5.0", "Referer": "https://telewebion.ir/"}
app = Flask(__name__)

VLC_PATHS = [
    r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
]
def find_vlc():
    for p in VLC_PATHS:
        if os.path.exists(p): return p
    return shutil.which("vlc")

def parse_m3u():
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

def build_m3u(ch):
    q = chr(34); out = ["#EXTM3U"]
    for c in ch:
        p = ["#EXTINF:-1"]
        if c.get("tvgid"): p.append("tvg-id="+q+c["tvgid"]+q)
        p.append("tvg-logo="+q+c.get("logo","")+q)
        p.append("group-title="+q+c.get("group","")+q)
        out.append(" ".join(p)+","+c["name"]); out.append(c["url"])
    return "\n".join(out)+"\n"

def write_m3u(ch):
    open(M3U_FILE,"w",encoding="utf-8").write(build_m3u(ch))

def epg_map():
    res = {}
    if not os.path.exists(EPG_FILE): return res
    try:
        with gzip.open(EPG_FILE, "rb") as f:
            tree = ET.parse(f)
        for ch in tree.getroot().findall("channel"):
            cid = ch.get("id",""); icon = ch.find("icon")
            res[cid] = icon.get("src","") if icon is not None else ""
    except Exception:
        pass
    return res

def parse_m3u_text(text, fallback_group):
    lines = text.splitlines(); ch, ext = [], None
    for line in lines:
        s = line.strip()
        if s.startswith("#EXTINF"): ext = s
        elif s and not s.startswith("#") and ext is not None:
            def gv(k):
                m = re.search(k + r'="([^"]*)"', ext); return m.group(1) if m else ""
            g = gv("group-title") or fallback_group
            ch.append({"name": ext.split(",",1)[-1].strip(), "logo": gv("tvg-logo"),
                       "tvgid": gv("tvg-id"), "group": g, "url": s})
            ext = None
    return ch

@app.route("/api/channels")
def ch_api():
    chans = parse_m3u(); em = epg_map()
    for c in chans:
        c["epg_logo"] = em.get(c["tvgid"], "")
        c["has_epg"] = bool(c["tvgid"] and c["tvgid"] in em)
    return jsonify(chans)

@app.route("/api/save", methods=["POST"])
def save_api():
    write_m3u(request.get_json().get("channels", []))
    return jsonify({"ok": True})

@app.route("/api/download", methods=["POST"])
def download_api():
    ch = request.get_json().get("channels", [])
    data = build_m3u(ch)
    return Response(data, mimetype="audio/x-mpegurl",
                    headers={"Content-Disposition": "attachment; filename=selected.m3u"})

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

@app.route("/api/play", methods=["POST"])
def play_api():
    url = request.get_json().get("url","")
    vlc = find_vlc()
    if not vlc: return jsonify({"ok": False, "error": "VLC not found"})
    try:
        subprocess.Popen([vlc, url]); return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.route("/api/import", methods=["POST"])
def import_api():
    d = request.get_json(); url = d.get("url",""); name = d.get("name","import")
    try:
        r = requests.get(url, headers=HDR, timeout=25)
        if r.status_code != 200 or "#EXT" not in r.text:
            return jsonify({"ok": False, "error": "bad m3u (HTTP %s)" % r.status_code})
        new = parse_m3u_text(r.text, name)
        return jsonify({"ok": True, "channels": new, "count": len(new)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

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
<style>body{font-family:Tahoma;background:#0f1419;color:#e0e0e0;margin:0;padding:18px}
h1{color:#2dd4bf;font-size:19px}.bar{display:flex;gap:8px;margin:12px 0;flex-wrap:wrap;align-items:center}
button{background:#1e293b;color:#e0e0e0;border:1px solid #334155;padding:7px 12px;border-radius:8px;cursor:pointer;font-family:inherit;font-size:13px}
button:hover{background:#334155}.primary{background:#0d9488;border-color:#0d9488}.danger{background:#7f1d1d;border-color:#7f1d1d}.play{background:#1d4ed8;border-color:#1d4ed8}.dl{background:#7c3aed;border-color:#7c3aed}
input,select{background:#1e293b;color:#e0e0e0;border:1px solid #334155;padding:6px;border-radius:6px;font-family:inherit;font-size:12px}
.grphead{background:#13202e;padding:10px 14px;margin-top:8px;border-radius:8px;display:flex;justify-content:space-between;align-items:center;border:1px solid #1e293b}
.grphead:hover{background:#1a2a3a}.gname{color:#fbbf24;font-size:15px;font-weight:bold;cursor:pointer}
.gcount{color:#94a3b8;font-size:12px}.gedit{background:none;border:none;color:#94a3b8;cursor:pointer;font-size:14px;padding:2px 6px}
table{width:100%;border-collapse:collapse;font-size:12px}
td{text-align:right;padding:5px;border-bottom:1px solid #1e293b;vertical-align:middle}
tr:hover{background:#1a2332}.live{color:#4ade80}.dead{color:#f87171}.small{font-size:11px;color:#94a3b8}
img.logo{width:30px;height:30px;object-fit:contain;background:#000;border-radius:5px;border:1px solid #334155;vertical-align:middle}
.epgbadge{background:#0d9488;color:#fff;font-size:10px;padding:2px 6px;border-radius:4px}.noepg{color:#64748b;font-size:10px}
input[type=checkbox]{width:16px;height:16px}</style></head><body>
<h1>Playlist Manager - final.m3u</h1>
<div class="bar"><input id="search" placeholder="search...">
<button class="primary" onclick="add()">+ channel</button>
<button class="primary" onclick="doImport()">import m3u</button>
<button onclick="expandAll()">expand all</button>
<button onclick="collapseAll()">collapse all</button>
<button class="dl" onclick="dlSelected()">download selected (<span id=selcount>0</span>)</button>
<button class="primary" onclick="save()">save</button>
<button onclick="push()">save + push</button>
<span id="status" class="small"></span></div>
<div id="groups"></div>
<script>
let C=[], OPEN={}, SEL={};
async function load(){C=await(await fetch('/api/channels')).json();C.forEach((c,i)=>c._id=i);render();}
function grps(){let o=[];C.forEach(c=>{if(!o.includes(c.group))o.push(c.group);});return o;}
function selcount(){return Object.values(SEL).filter(Boolean).length;}
function render(){
 let q=document.getElementById('search').value.toLowerCase();
 let box=document.getElementById('groups');box.innerHTML='';
 grps().forEach(g=>{
  let items=C.filter(c=>c.group===g&&(!q||c.name.toLowerCase().includes(q)));
  if(items.length===0)return;
  let head=document.createElement('div');head.className='grphead';
  head.innerHTML='<span class="gname" onclick="toggle(\''+esc(g).replace(/'/g,"")+'\')">'+(OPEN[g]?'\u25bc ':'\u25b6 ')+esc(g)+'</span>'+
   '<span><button class=gedit onclick="renameGroup(\''+esc(g).replace(/'/g,"")+'\')">\u270e edit name</button> <span class="gcount">'+items.length+' channels</span></span>';
  box.appendChild(head);
  if(OPEN[g]){
   let tbl=document.createElement('table');
   items.forEach(c=>{let i=c._id;
    let tr=document.createElement('tr');
    let img=c.logo?('<img class=logo src="'+esc(c.logo)+'">'):'';
    let epg=c.has_epg?'<span class=epgbadge>EPG</span>':'<span class=noepg>no epg</span>';
    tr.innerHTML='<td><input type=checkbox '+(SEL[i]?'checked':'')+' onchange="sel('+i+',this.checked)"></td>'+
    '<td>'+img+'</td>'+
    '<td><input value="'+esc(c.name)+'" onchange="u('+i+",'name',this.value)\" style=\"width:120px\"></td>"+
    '<td>'+epg+'</td>'+
    '<td><input value="'+esc(c.logo)+'" onchange="u('+i+",'logo',this.value);render()\" class=small style=\"width:130px\" placeholder=\"logo m3u\"></td>"+
    '<td><input value="'+esc(c.tvgid)+'" onchange="u('+i+",'tvgid',this.value)\" class=small style=\"width:100px\" placeholder=\"epg tvg-id\"></td>"+
    '<td>'+(c.epg_logo?('<img class=logo src="'+esc(c.epg_logo)+'">'):'<span class=noepg>-</span>')+'</td>'+
    '<td><input value="'+esc(c.url)+'" onchange="u('+i+",'url',this.value)\" class=small style=\"width:190px\"></td>"+
    '<td id="st'+i+'" class=small>-</td>'+
    '<td><button class=play onclick="play('+i+')">play</button> <button onclick="t('+i+')">test</button> <button class=danger onclick="d('+i+')">del</button></td>';
    tbl.appendChild(tr);
   });
   box.appendChild(tbl);
  }
 });
 document.getElementById('status').textContent=C.length+' channels / '+grps().length+' groups';
 document.getElementById('selcount').textContent=selcount();
}
function esc(s){return(s||'').replace(/"/g,'&quot;');}
function u(i,k,v){C.find(x=>x._id===i)[k]=v;}
function sel(i,v){SEL[i]=v;document.getElementById('selcount').textContent=selcount();}
function toggle(g){OPEN[g]=!OPEN[g];render();}
function renameGroup(oldg){
 let n=prompt('new group name:',oldg);if(!n||n===oldg)return;
 C.forEach(c=>{if(c.group===oldg)c.group=n;});
 OPEN[n]=true;render();
 document.getElementById('status').textContent='group renamed (remember to save)';
}
function d(i){let c=C.find(x=>x._id===i);if(confirm('delete '+c.name+'?')){C=C.filter(x=>x._id!==i);delete SEL[i];render();}}
function expandAll(){grps().forEach(g=>OPEN[g]=true);render();}
function collapseAll(){OPEN={};render();}
function add(){let n=prompt('name:');if(!n)return;let url=prompt('url:');if(!url)return;
 let g=prompt('group:','new')||'';let lg=prompt('logo url (optional):','')||'';
 let ni={name:n,url:url,group:g,logo:lg,tvgid:'',epg_logo:'',has_epg:false,_id:Date.now()};
 C.push(ni);OPEN[g]=true;render();}
async function doImport(){
 let url=prompt('m3u link to import:');if(!url)return;
 let name=prompt('group name (used only if channels have no group):','new source')||'new';
 document.getElementById('status').textContent='importing...';
 let d=await(await fetch('/api/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url,name:name})})).json();
 if(!d.ok){document.getElementById('status').textContent='import error: '+d.error;return;}
 d.channels.forEach(c=>{c.epg_logo='';c.has_epg=false;c._id=Date.now()+Math.random();C.push(c);});
 document.getElementById('status').textContent='imported '+d.count+' channels (remember to save)';render();
}
async function dlSelected(){
 let chosen=C.filter(c=>SEL[c._id]);
 if(chosen.length===0){alert('no channels selected (tick the boxes first)');return;}
 let r=await fetch('/api/download',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({channels:chosen})});
 let blob=await r.blob();let a=document.createElement('a');
 a.href=URL.createObjectURL(blob);a.download='selected.m3u';a.click();
 document.getElementById('status').textContent='downloaded '+chosen.length+' channels';
}
async function t(i){let st=document.getElementById('st'+i);if(!st)return;st.textContent='...';
 let c=C.find(x=>x._id===i);
 let d=await(await fetch('/api/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:c.url})})).json();
 st.innerHTML=d.alive?'<span class=live>live</span>':'<span class=dead>dead('+d.status+')</span>';}
async function play(i){let c=C.find(x=>x._id===i);
 let d=await(await fetch('/api/play',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:c.url})})).json();
 if(!d.ok)document.getElementById('status').textContent='VLC error: '+(d.error||'');}
async function save(){await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({channels:C})});
 document.getElementById('status').textContent='saved';}
async function push(){await save();document.getElementById('status').textContent='pushing...';
 let d=await(await fetch('/api/push',{method:'POST'})).json();
 document.getElementById('status').textContent=d.ok?'pushed to github':'error';}
document.getElementById('search').addEventListener('input',render);
load();
</script></body></html>"""

if __name__ == "__main__":
    print("="*50)
    print(" Playlist Manager running")
    print(" Open: http://127.0.0.1:8090")
    print("="*50)
    app.run(host="127.0.0.1", port=8090, debug=False)
