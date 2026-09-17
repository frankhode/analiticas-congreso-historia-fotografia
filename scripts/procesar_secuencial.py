#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SUB_RE=re.compile(r'\$\$([0-9a-z])([^$]*)')
SUBJECT_TAGS=('600','610','611','630','650','651','655')
SUBDIV={'x','y','z','v'}
IGNORE={'e','4','0','1','2','3','5','6','7','8','9'}
MAIN={'600':{'a','b','c','q','d','t','n','p','l'},'610':{'a','b','c','d','n','t','p','l'},'611':{'a','n','c','d','t','p','l'},'630':{'a','d','f','k','l','n','p','s'},'650':None,'651':None,'655':None}

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def strip_terminal(s):
    s=clean(s); s=re.sub(r'\s*([/,:;])\s*$','',s); s=re.sub(r'\s*\.$','',s); return s.strip()
def subfields(s): return [(m.group(1),m.group(2).strip()) for m in SUB_RE.finditer(s)]
def allf(fs,t): return [v for k,v in fs if k==t]
def first(fs,t):
    for k,v in fs:
        if k==t:return v
    return ''
def linked(parts): return re.sub(r'\s+([,.;:])',r'\1',clean(' '.join(parts)))
def fmt_name(sf): return strip_terminal(linked([v for c,v in sf if c in {'a','b','c','q','d'} and v]))
def fmt_subject(tag,sf):
    main=[]; subs=[]; allowed=MAIN[tag]
    for c,v in sf:
        if not v: continue
        if c in SUBDIV: subs.append(strip_terminal(v))
        elif c in IGNORE: continue
        elif allowed is None or c in allowed: main.append(v)
    h=strip_terminal(linked(main)); return ' — '.join(([h] if h else [])+[x for x in subs if x])
def page_start(p):
    m=re.search(r'(\d+)',p or ''); return int(m.group(1)) if m else 999999

def parse(path):
    recs={}; order=[]
    for raw in path.read_text(encoding='utf-8-sig',errors='replace').splitlines():
        if ' L ' not in raw: continue
        left,content=raw.split(' L ',1); parts=left.split()
        if len(parts)<2 or not re.fullmatch(r'\d{9}',parts[0]): continue
        rid,tag=parts[0],parts[1][:3]
        if rid not in recs: recs[rid]=[]; order.append(rid)
        recs[rid].append((tag,content))
    analytics=[]; hosts=set(); tag_counts=Counter()
    for rid in order:
        for tag,_ in recs[rid]:
            if tag in SUBJECT_TAGS: tag_counts[tag]+=1
        fs=recs[rid]
        if not first(fs,'245') or not first(fs,'773'): continue
        sf=subfields(first(fs,'245')); vals={}
        for c,v in sf: vals.setdefault(c,[]).append(v)
        title=strip_terminal(clean(' '.join(vals.get('a',[]))+(' ' if vals.get('a') and vals.get('b') else '')+' '.join(vals.get('b',[]))).replace(' :',':').replace(' /',''))
        statement=strip_terminal(' '.join(vals.get('c',[])))
        authors=[]
        for t in ('100','700'):
            for f in allf(fs,t):
                n=fmt_name(subfields(f))
                if n and n not in authors: authors.append(n)
        subjects=[]; subject_tags=[]
        for t in SUBJECT_TAGS:
            for f in allf(fs,t):
                s=fmt_subject(t,subfields(f))
                if s and s not in subjects: subjects.append(s); subject_tags.append(t)
        alt=[]
        for f in allf(fs,'246'):
            s=strip_terminal(linked([v for c,v in subfields(f) if c in {'a','b','n','p'}]))
            if s and s not in alt: alt.append(s)
        contents=[]
        for f in allf(fs,'505'):
            s=strip_terminal(' '.join(v for c,v in subfields(f) if c in {'a','t','r'}))
            if s: contents.append(s)
        bibliography=[]
        for f in allf(fs,'504'):
            s=strip_terminal(' '.join(v for c,v in subfields(f) if c=='a'))
            if s: bibliography.append(s)
        notes=[]
        for t in ('500','520'):
            for f in allf(fs,t):
                s=strip_terminal(' '.join(v for c,v in subfields(f) if c in {'a','b'}))
                if s: notes.append(s)
        h={}
        for c,v in subfields(first(fs,'773')): h.setdefault(c,[]).append(v)
        congress=clean(' '.join(h.get('a',[]))); host_title=strip_terminal(' '.join(h.get('t',[]))); pages=strip_terminal(' '.join(h.get('g',[]))); host_id=clean(' '.join(h.get('w',[]))).replace('(AR-BaBN)','').strip()
        if host_id: hosts.add(host_id)
        m=re.search(r'\((\d+)o\s*:\s*(\d{4})',congress); cno=int(m.group(1)) if m else None; year=int(m.group(2)) if m else None
        analytics.append({'id':rid,'title':title,'statement':statement,'authors':authors,'subjects':subjects,'subjectTags':subject_tags,'alternateTitles':alt,'contents':contents,'bibliography':bibliography,'notes':notes,'congressNo':cno,'year':year,'congress':congress,'hostTitle':host_title,'pages':pages,'pageStart':page_start(pages),'hostId':host_id})
    analytics.sort(key=lambda r:(r['congressNo'] or 999,r['pageStart'],r['title'].casefold()))
    cc=Counter(r['congressNo'] for r in analytics if r['congressNo'] is not None)
    summary={'generatedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'sourceFile':path.name,'totalRecords':len(order),'analytics':len(analytics),'hostRecords':len([x for x in order if x in hosts]),'congresses':{str(k):v for k,v in sorted(cc.items())},'subjectFieldOccurrences':{t:tag_counts.get(t,0) for t in SUBJECT_TAGS},'warnings':{'sin_autor':[r['id'] for r in analytics if not r['authors']],'sin_materias':[r['id'] for r in analytics if not r['subjects']],'sin_congreso_identificado':[r['id'] for r in analytics if r['congressNo'] is None]}}
    return analytics,summary

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source',type=Path); ap.add_argument('root',type=Path,nargs='?',default=Path('.')); args=ap.parse_args()
    data,summary=parse(args.source); root=args.root; root.mkdir(parents=True,exist_ok=True)
    chunk=math.ceil(len(data)/5) if data else 1
    for i in range(5):
        rows=data[i*chunk:(i+1)*chunk]
        (root/f'data{i+1}.js').write_text('window.DATA=window.DATA.concat('+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+');\n',encoding='utf-8')
    subject_map={r['id']:r['subjects'] for r in data}; keys=list(subject_map); schunk=math.ceil(len(keys)/5) if keys else 1
    for i in range(5):
        part={k:subject_map[k] for k in keys[i*schunk:(i+1)*schunk]}
        (root/f'subjects{i+1}.js').write_text('window.SUBJECTS=Object.assign(window.SUBJECTS||{},'+json.dumps(part,ensure_ascii=False,separators=(',',':'))+');\n',encoding='utf-8')
    d=root/'datos'; d.mkdir(exist_ok=True); (d/'resumen.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"{len(data)} ponencias procesadas"); print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
