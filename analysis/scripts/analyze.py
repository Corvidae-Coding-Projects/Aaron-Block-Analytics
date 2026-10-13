# Compilation and analysis: Friendly Society of Corvids.
"""Reproduce descriptive findings and an aggregate association check.

No coefficient adjusting for campaign participation is estimated: the recovered
search corpus is incomplete and the original account-level analysis is absent.
"""
import csv
import hashlib
import json
import math
import pathlib
import re
from collections import Counter
from datetime import datetime
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 'deliverables'
OUT.mkdir(exist_ok=True)
DID = 'did:plc:ksjfbda7262bbqmuoly54lww'
PREFIX = 'at://' + DID + '/'
ARTIFACT_URL = 'https://claude.ai/artifact/Fiy5MLT3eSoNnXZ5Rpfey7'
SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSqDngHpDnBvSvSxvxaJO4679WlwqfNBgPsX3qJMqWMHJlUmHlZ0siklD73gZI-5fTX1S6bpKB2ifdj/pubhtml'

def stamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

def relation(record):
    reply = any(x.get('uri', '').startswith(PREFIX) for x in record.get('reply', {}).values())
    quote = record.get('embed', {}).get('record', {})
    quote = quote.get('record', quote)
    quoted = quote.get('uri', '').startswith(PREFIX)
    mentioned = any(x.get('did') == DID for f in record.get('facets', []) for x in f.get('features', []))
    return reply, quoted, mentioned

def post_url(post):
    return 'https://bsky.app/profile/' + post['author']['did'] + '/post/' + post['uri'].rsplit('/', 1)[1]

def write_csv(name, rows):
    with (OUT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)

blocks = json.loads((ROOT / 'app.bsky.graph.block.json').read_text())
block_times = {x['value']['subject']:x['value']['createdAt'] for x in blocks}
window = [x for x in blocks if '2026-09-28' <= x['value']['createdAt'] < '2026-10-09']
assert len(block_times) == len(blocks), 'Duplicate subjects require explicit resolution'
counts = Counter(x['value']['createdAt'][:16] for x in window)
seed_minutes = {'2026-09-30T08:23', '2026-09-30T08:54', '2026-09-30T12:07', '2026-09-30T12:08'}
seed_count = sum(counts[x] for x in seed_minutes)
assert len(window) == 1271 and seed_count == 1087
write_csv('blocks_by_day.csv', [{'date_utc':k,'block_count':v} for k,v in sorted(Counter(x['value']['createdAt'][:10] for x in window).items())])

# Manual transcription of the artifact's expanded tables. Counts are not
# independently validated identity or toxicity labels.
bands = {
 'all': [('Very mild',18,47,138,862),('Mild',7,15,52,151),('Moderate',15,21,69,149),('Harsh',34,44,231,389)],
 'recent': [('Very mild',16,41,130,548),('Mild',6,13,46,113),('Moderate',13,19,48,108),('Harsh',34,44,200,326)],
 'seed': [('Very mild',14,39,97,693),('Mild',7,11,39,116),('Moderate',13,17,54,114),('Harsh',26,34,191,305)],
 'live': [('Very mild',3,11,41,224),('Mild',1,5,13,42),('Moderate',2,4,12,35),('Harsh',7,10,32,82)],
}
summary = {}
all_rows = []
for label, rows in bands.items():
    design=[];success=[];totals=[]
    mh_n=mh_d=0
    for i,(band,a,nt,c,no) in enumerate(rows):
        assert 0 <= a <= nt and 0 <= c <= no
        mh_n += a*(no-c)/(nt+no)
        mh_d += (nt-a)*c/(nt+no)
        for group,n,y in [(1,nt,a),(0,no,c)]:
            design.append([1,group]+[int(i==j) for j in range(1,4)])
            success.append(y);totals.append(n)
        all_rows.append(dict(window=label,band=band,trans_marked_blocked=a,trans_marked_total=nt,
                             other_blocked=c,other_total=no,source_url=ARTIFACT_URL))
    X=np.asarray(design,dtype=float);y=np.asarray(success,dtype=float);n=np.asarray(totals,dtype=float)
    def objective(beta):
        z=X@beta
        return np.sum(n*np.logaddexp(0,z)-y*z)
    def gradient(beta):return X.T@(n*expit(X@beta)-y)
    fit=minimize(objective,np.zeros(5),jac=gradient,method='BFGS',options={'gtol':1e-8})
    assert np.max(np.abs(gradient(fit.x)))<1e-5
    p=expit(X@fit.x);information=X.T@((n*p*(1-p))[:,None]*X)
    se=math.sqrt(np.linalg.inv(information)[1,1]);beta=fit.x[1]
    a=sum(r[1] for r in rows);nt=sum(r[2] for r in rows);c=sum(r[3] for r in rows);no=sum(r[4] for r in rows)
    summary[label]={'trans_blocked':a,'trans_total':nt,'other_blocked':c,'other_total':no,
                    'trans_rate':a/nt,'other_rate':c/no,'risk_ratio':(a/nt)/(c/no),
                    'crude_odds_ratio':a*(no-c)/((nt-a)*c),'mh_band_adjusted_or':mh_n/mh_d,
                    'bin_adjusted_logistic_or':math.exp(beta),
                    'bin_adjusted_logistic_ci95':[math.exp(beta-1.96*se),math.exp(beta+1.96*se)]}
write_csv('artifact_counts.csv',all_rows)

verification=json.loads((ROOT/'sample_verification.json').read_text())
verified=[]
for item in verification:
    for post in item['exact_matches']:
        rec=post['record'];bt=block_times.get(post['author']['did']);before=bool(bt and stamp(rec['createdAt'])<stamp(bt))
        replied,quoted,mentioned=relation(rec)
        verified.append(dict(sample_row=item['number'],source_url=post_url(post),created_at_utc=rec['createdAt'],
                             block_record_time_utc=bt or '',predates_block=before,
                             directly_replies_or_quotes_aaron=replied or quoted,mentions_aaron=mentioned,
                             source_text_sha256=hashlib.sha256(rec.get('text','').encode()).hexdigest(),
                             source_post_uri=post['uri']))
write_csv('verified_sample_sources.csv',verified)

context={}
for path in ROOT.glob('search_*.json'):
    for post in json.loads(path.read_text())['posts']:
        text=post['record'].get('text','')
        if re.search(r'aaron\s+(?:[“\"].*?[”\"]\s+)?roderick',text,re.I) and re.search(r'pedoph|pedo\b|chomo|underage|teen.?\s*porn|barely.?legal|porn',text,re.I):
            context[post['uri']]=post
context_rows=[]
for uri,post in sorted(context.items(),key=lambda p:p[1]['record']['createdAt']):
    rec=post['record'];bt=block_times.get(post['author']['did']);before=bool(bt and stamp(rec['createdAt'])<stamp(bt));seed=bool(bt and bt[:16] in seed_minutes)
    context_rows.append(dict(source_url=post_url(post),source_post_uri=uri,created_at_utc=rec['createdAt'],
                             block_record_time_utc=bt or '',predates_block=before,bulk_load=seed,
                             # References include questions and rebuttals. They are not
                             # automatically labeled harassment or campaign membership.
                             classification='sexual_allegation_reference_candidate',
                             source_text_sha256=hashlib.sha256(rec.get('text','').encode()).hexdigest()))
write_csv('context_source_metadata.csv',context_rows)

# These are model constructions, not observations of campaign prevalence.
# A binary omitted behavior factor with the same effect in both identity groups
# can reproduce the observed aggregate rates. This establishes non-identification,
# not that this particular factor explains the observed disparity.
low,high=.2,.8
sensitivity={
 'label':'Hypothetical model; no identity effect; no estimated campaign prevalence',
 'blocking_probability_without_omitted_behavior':low,
 'blocking_probability_with_omitted_behavior':high,
 'required_trans_marked_behavior_prevalence':(summary['all']['trans_rate']-low)/(high-low),
 'required_other_behavior_prevalence':(summary['all']['other_rate']-low)/(high-low),
}
search_coverage=[]
for path in ROOT.glob('search_*.json'):
    r=json.loads(path.read_text())
    search_coverage.append(dict(label=r['label'],query=r['query'],since=r['since'],until=r['until'],
                               unique_posts=len(r['posts']),exhausted=r['exhausted'],reported_hits=r['reported_hits'],error=r['error']))

prior=[r for r in verified if r['predates_block']]
results={
 'block_records_total':len(blocks),'audit_window_blocks':len(window),'bulk_load_blocks':seed_count,
 'other_window_blocks':len(window)-seed_count,'bulk_fraction':seed_count/len(window),
 'aggregate_checks':summary,
 'sample_rows':50,'sample_rows_exactly_recovered':len(verified),'sample_posts_predating_block':len(prior),
 'sample_preblock_unique_authors':len({p['author']['did'] for x in verification for p in x['exact_matches'] if block_times.get(p['author']['did']) and stamp(p['record']['createdAt'])<stamp(block_times[p['author']['did']])}),
 'sample_preblock_outside_direct_reply_quote':sum(not r['directly_replies_or_quotes_aaron'] for r in prior),
 'context_candidate_posts':len(context_rows),'context_candidates_predating_block':sum(r['predates_block'] for r in context_rows),
 'context_candidates_preblock_in_bulk_loads':sum(r['predates_block'] and r['bulk_load'] for r in context_rows),
 'search_coverage':search_coverage,'hypothetical_sensitivity':sensitivity,
 'campaign_adjusted_identity_effect':'NOT ESTIMATED: absent original account-level data and incomplete eligible control population',
}
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
