# Compilation and analysis: Friendly Society of Corvids.
from pathlib import Path
import json,csv,urllib.request,urllib.parse,hashlib,datetime
ROOT=Path(__file__).resolve().parent
D=ROOT/'inputs'
rows=[]
for name in ['verified_sample_sources.csv','context_source_metadata.csv']:
 with (D/name).open() as f:
  for r in csv.DictReader(f):r['provenance_table']=name;rows.append(r)
uris=sorted({r['source_post_uri'] for r in rows}|{'at://did:plc:ksjfbda7262bbqmuoly54lww/app.bsky.feed.post/3m2kgo3c3bk2u','at://did:plc:ksjfbda7262bbqmuoly54lww/app.bsky.feed.post/3mwqeidhoo22w','at://did:plc:ksjfbda7262bbqmuoly54lww/app.bsky.feed.post/3mwsv6uvlrc27','at://did:plc:ksjfbda7262bbqmuoly54lww/app.bsky.feed.post/3mwsv6uvvjs27'})
posts={};logs=[]
for i in range(0,len(uris),25):
 url='https://public.api.bsky.app/xrpc/app.bsky.feed.getPosts?'+urllib.parse.urlencode({'uris':uris[i:i+25]},doseq=True)
 log={'url':url,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(url,timeout=30) as response:body=response.read();log.update(status=response.status,sha256=hashlib.sha256(body).hexdigest())
  data=json.loads(body);posts.update({p['uri']:p for p in data['posts']})
 except Exception as e:log['error']=type(e).__name__+': '+str(e)
 logs.append(log)
(ROOT/'recovered_post_views.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2))
(ROOT/'new_retrieval_log.json').write_text(json.dumps(logs,indent=2))
print('Recovered post views',len(posts),'requested',len(uris))
for r in rows:
 p=posts.get(r['source_post_uri']);text=p['record'].get('text','') if p else ''
 r['current_source_returned']=bool(p);r['current_text_sha256']=hashlib.sha256(text.encode()).hexdigest() if p else '';r['unchanged_text_hash']=r['current_text_sha256']==r['source_text_sha256'];r['current_text']=text;r['current_cid']=p.get('cid','') if p else '';r['indexed_at']=p.get('indexedAt','') if p else '';r['author_did']=r['source_post_uri'].split('/')[2]
(ROOT/'mapped_evidence.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for i,r in enumerate(rows):print(i,r.get('sample_row',''),r['predates_block'],r['author_did'],json.dumps(r['current_text'],ensure_ascii=False))
