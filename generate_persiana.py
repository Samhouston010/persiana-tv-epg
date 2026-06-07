import requests, gzip
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta
API='https://www.persianagroup.tv/api/v1'; SITE='https://www.persianagroup.tv/'
RAW='https://raw.githubusercontent.com/Samhouston010/persiana-tv-epg/main'
TZ='-0500'; H={'User-Agent':'Mozilla/5.0','Referer':SITE}
s=requests.Session(); s.headers.update(H)
def au(u):
    u=str(u or '')
    return u if u.startswith('http') else (SITE+u.lstrip('/') if u else '')
def dt(d,hm):
    try: h,m=[int(x) for x in str(hm).split(':')[:2]]
    except: h,m=0,0
    return datetime(d.year,d.month,d.day,h,m)
def xt(x): return x.strftime('%Y%m%d%H%M%S')+' '+TZ
def lst(v):
    if not v: return []
    if isinstance(v,list): return [str(x).strip() for x in v if str(x).strip()]
    import json
    sv=str(v)
    if sv.startswith('['):
        try: return [str(x).strip() for x in json.loads(sv) if str(x).strip()]
        except: pass
    return [p.strip() for p in sv.split(',') if p.strip()]
print('Getting channels...')
ch=s.get(API+'/channels',timeout=20).json().get('channels',[])
print('  Channels:',len(ch))
today=datetime.now(); allp=[]
print('Getting programs...')
for off in range(-1,3):
    d=today+timedelta(days=off); ds=d.strftime('%Y-%m-%d')
    r=s.get(API+'/programs',params={'date':ds},timeout=20)
    pr=r.json().get('programs',[]) if r.ok else []
    print('  '+ds+':',len(pr)); allp.append((d,pr))
print('Building M3U...')
L=['#EXTM3U x-tvg-url=\"'+RAW+'/persiana.xml.gz\"']; n=0
for c in ch:
    st=c.get('hls_url') or ''
    if not st: continue
    n+=1; cid=c.get('id',''); nm=c.get('name') or cid; nf=c.get('name_fa') or nm
    lg=au(c.get('logo_url')); g='پرشیانا'
    L.append('#EXTINF:-1 tvg-id=\"'+cid+'\" tvg-name=\"'+nm+'\" tvg-logo=\"'+lg+'\" group-title=\"'+g+'\",'+nf)
    L.append(st)
open('persiana.m3u','w',encoding='utf-8').write('\n'.join(L)+'\n')
print('  M3U done -',n)
print('Building EPG...')
tv=ET.Element('tv')
for c in ch:
    cid=c.get('id',''); nm=c.get('name') or cid; nf=c.get('name_fa') or nm; lg=au(c.get('logo_url'))
    e=ET.SubElement(tv,'channel',{'id':cid})
    ET.SubElement(e,'display-name',{'lang':'fa'}).text=nf
    ET.SubElement(e,'display-name',{'lang':'en'}).text=nm
    if lg: ET.SubElement(e,'icon',{'src':lg})
tot=0
for d,pr in allp:
    for p in pr:
        cid=p.get('channel_id','')
        if not cid: continue
        a=dt(d,p.get('start_time','0:0')); b=dt(d,p.get('end_time','0:0'))
        if b<=a: b+=timedelta(days=1)
        pe=ET.SubElement(tv,'programme',{'start':xt(a),'stop':xt(b),'channel':cid})
        ET.SubElement(pe,'title',{'lang':'fa'}).text=p.get('title_fa') or p.get('title_en') or 'Program'
        if p.get('title_en'): ET.SubElement(pe,'title',{'lang':'en'}).text=p['title_en']
        if p.get('desc_fa'): ET.SubElement(pe,'desc',{'lang':'fa'}).text=p['desc_fa']
        elif p.get('desc_en'): ET.SubElement(pe,'desc',{'lang':'en'}).text=p['desc_en']
        dr=p.get('director'); ca=lst(p.get('cast_list'))
        if dr or ca:
            cr=ET.SubElement(pe,'credits')
            if dr: ET.SubElement(cr,'director').text=str(dr)
            for ac in ca[:8]: ET.SubElement(cr,'actor').text=ac
        if p.get('year'): ET.SubElement(pe,'date').text=str(p['year'])
        gs=lst(p.get('genres_fa')) or lst(p.get('genres_en'))
        if gs:
            for gn in gs[:3]: ET.SubElement(pe,'category',{'lang':'fa'}).text=gn
        ps=au(p.get('poster_url') or p.get('backdrop_url'))
        if ps.startswith('http'): ET.SubElement(pe,'icon',{'src':ps})
        im=p.get('imdb') or p.get('rating')
        if im:
            try:
                sr=ET.SubElement(pe,'star-rating',{'system':'IMDB'})
                ET.SubElement(sr,'value').text=('%.1f'%float(im))+'/10'
            except: pass
        tot+=1
xb=minidom.parseString(ET.tostring(tv,encoding='utf-8')).toprettyxml(indent='  ',encoding='utf-8')
open('persiana.xml','wb').write(xb)
with open('persiana.xml','rb') as fi, gzip.open('persiana.xml.gz','wb') as fo: fo.writelines(fi)
print('  EPG done -',tot); print('DONE!')
