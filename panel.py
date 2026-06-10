# -*- coding: utf-8 -*-
import json
import os
import re
import subprocess
import requests
from flask import Flask, request, jsonify, Response

APP_DIR = os.path.dirname(os.path.abspath(__file__))
M3U_FILE = os.path.join(APP_DIR, "final.m3u")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Referer": "https://telewebion.ir/",
}

app = Flask(__name__)


def parse_m3u():
    if not os.path.exists(M3U_FILE):
        return []
    with open(M3U_FILE, "r", encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f]
    channels = []
    ext = None
    for line in lines:
        s = line.strip()
        if s.startswith("#EXTINF"):
            ext = s
        elif s and not s.startswith("#") and ext is not None:
            name = ext.split(",", 1)[-1].strip()
            logo = ""
            m = re.search(r'tvg-logo="([^"]*)"', ext)
            if m:
                logo = m.group(1)
            tvgid = ""
            m = re.search(r'tvg-id="([^"]*)"', ext)
            if m:
                tvgid = m.group(1)
            group = ""
            m = re.search(r'group-title="([^"]*)"', ext)
            if m:
                group = m.group(1)
            channels.append({"name": name, "logo": logo, "tvgid": tvgid, "group": group, "url": s})
            ext = None
    return channels


def write_m3u(channels):
    q = chr(34)
    out = ["#EXTM3U"]
    for ch in channels:
        parts = ["#EXTINF:-1"]
        if ch.get("tvgid"):
            parts.append("tvg-id=" + q + ch["tvgid"] + q)
        parts.append("tvg-logo=" + q + ch.get("logo", "") + q)
        parts.append("group-title=" + q + ch.get("group", "") + q)
        ext = " ".join(parts) + "," + ch["name"]
        out.append(ext)
        out.append(ch["url"])
    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


@app.route("/api/channels")
def api_channels():
    return jsonify(parse_m3u())


@app.route("/api/save", methods=["POST"])
def api_save():
    data = request.get_json()
    write_m3u(data.get("channels", []))
    return jsonify({"ok": True, "count": len(data.get("channels", []))})


@app.route("/api/test", methods=["POST"])
def api_test():
    url = request.get_json().get("url", "")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, stream=True, allow_redirects=True)
        ok = r.status_code == 200
        chunk = next(r.iter_content(chunk_size=256), b"") if ok else b""
        r.close()
        return jsonify({"alive": bool(ok and len(chunk) > 0), "status": r.status_code})
    except Exception as e:
        return jsonify({"alive": False, "status": str(type(e).__name__)})


@app.route("/api/push", methods=["POST"])
def api_push():
    try:
        cmds = [
            ["git", "add", "final.m3u"],
            ["git", "commit", "-m", "Update playlist via manager"],
            ["git", "push"],
        ]
        log = []
        for c in cmds:
            p = subprocess.run(c, cwd=APP_DIR, capture_output=True, text=True, timeout=60)
            log.append(" ".join(c) + " -> " + (p.stdout + p.stderr).strip()[:200])
        return jsonify({"ok": True, "log": log})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Playlist Manager</title>
<style>
  body{font-family:Tahoma,sans-serif;background:#0f1419;color:#e0e0e0;margin:0;padding:20px}
  h1{color:#2dd4bf;font-size:20px}
  .bar{display:flex;gap:10px;margin:15px 0;flex-wrap:wrap}
  button{background:#1e293b;color:#e0e0e0;border:1px solid #334155;padding:8px 14px;border-radius:8px;cursor:pointer;font-family:inherit}
  button:hover{background:#334155}
  .primary{background:#0d9488;border-color:#0d9488}
  .danger{background:#7f1d1d;border-color:#7f1d1d}
  input,select{background:#1e293b;color:#e0e0e0;border:1px solid #334155;padding:7px;border-radius:6px;font-family:inherit}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{text-align:right;padding:7px;border-bottom:1px solid #1e293b}
  th{color:#2dd4bf}
  tr:hover{background:#1a2332}
  .grp{color:#fbbf24}
  .live{color:#4ade80}.dead{color:#f87171}
  .small{font-size:11px;color:#94a3b8}
  #search{width:200px}
</style>
</head>
<body>
<h1>Playlist Manager - final.m3u</h1>
<div class="bar">
  <input id="search" placeholder="search...">
  <select id="groupFilter"><option value="">all groups</option></select>
  <button class="primary" onclick="addChannel()">+ new channel</button>
  <button onclick="testAll()">test all</button>
  <button class="primary" onclick="save()">save</button>
  <button onclick="push()">save + push github</button>
  <span id="status" class="small"></span>
</div>
<table>
  <thead><tr><th>#</th><th>name</th><th>group</th><th>url</th><th>status</th><th>action</th></tr></thead>
  <tbody id="rows"></tbody>
</table>
<script>
let channels=[];
async function load(){
  const r=await fetch('/api/channels'); channels=await r.json(); render();
}
function groups(){return [...new Set(channels.map(c=>c.group))].filter(Boolean);}
function render(){
  const gf=document.getElementById('groupFilter');
  const cur=gf.value;
  gf.innerHTML='<option value="">all groups</option>'+groups().map(g=>`<option ${g===cur?'selected':''}>${g}</option>`).join('');
  const q=document.getElementById('search').value.toLowerCase();
  const fg=gf.value;
  const tb=document.getElementById('rows'); tb.innerHTML='';
  channels.forEach((c,i)=>{
    if(q && !c.name.toLowerCase().includes(q))return;
    if(fg && c.group!==fg)return;
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${i+1}</td>
      <td><input value="${esc(c.name)}" onchange="upd(${i},'name',this.value)" style="width:140px"></td>
      <td><input value="${esc(c.group)}" onchange="upd(${i},'group',this.value)" class="grp" style="width:110px"></td>
      <td><input value="${esc(c.url)}" onchange="upd(${i},'url',this.value)" style="width:260px" class="small"></td>
      <td id="st${i}" class="small">-</td>
      <td>
        <button onclick="test(${i})">test</button>
        <button class="danger" onclick="del(${i})">del</button>
      </td>`;
    tb.appendChild(tr);
  });
  document.getElementById('status').textContent=channels.length+' channels';
}
function esc(s){return (s||'').replace(/"/g,'&quot;');}
function upd(i,k,v){channels[i][k]=v;}
function del(i){if(confirm('delete '+channels[i].name+'?')){channels.splice(i,1);render();}}
function addChannel(){
  const name=prompt('channel name:'); if(!name)return;
  const url=prompt('m3u8 url:'); if(!url)return;
  const group=prompt('group:','new')||'';
  channels.unshift({name,url,group,logo:'',tvgid:''});render();
}
async function test(i){
  const st=document.getElementById('st'+i); st.textContent='...';
  const r=await fetch('/api/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:channels[i].url})});
  const d=await r.json();
  st.innerHTML=d.alive?'<span class="live">live</span>':'<span class="dead">dead ('+d.status+')</span>';
}
async function testAll(){
  for(let i=0;i<channels.length;i++){
    const vis=document.getElementById('st'+i); if(vis)await test(i);
  }
}
async function save(){
  const r=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({channels})});
  const d=await r.json();
  document.getElementById('status').textContent='saved: '+d.count+' channels';
}
async function push(){
  await save();
  document.getElementById('status').textContent='pushing...';
  const r=await fetch('/api/push',{method:'POST'});
  const d=await r.json();
  document.getElement
