# Compilation and analysis: Friendly Society of Corvids.
from pathlib import Path
from datetime import datetime,timezone
import json,csv,collections,hashlib,zipfile,shutil
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'account_post_mapping';OUT.mkdir(exist_ok=True)
rows=json.loads((ROOT/'mapped_evidence.json').read_text());posts=json.loads((ROOT/'recovered_post_views.json').read_text());blocks=json.loads((ROOT/'inputs/block_record_snapshot.json').read_text());target='did:plc:ksjfbda7262bbqmuoly54lww'
# The list is text-reviewed. Categories describe statements, not proven crimes or motives.
flags={
 'harm_rhetoric':{0,1,4,5,6,7,9,10},
 'ambiguous_harm_rhetoric':{2,3,8,11},
 'coordination_rhetoric':{0,9},
 'sexual_allegation':{12,20,28,32,36},
 'sexualized_ridicule':{15,26,30,31,35,38},
 'ambiguous_sexual_insinuation':{17},
 'association_allegation':{12,32,40},
 'neutral_inquiry_or_rebuttal':{18,37},
 'policy_criticism_or_rules_discussion':{13,14,16,21,22,23,24,25,27,29,33,34,39},
 'porn_like_story_reference':set(range(13,28))|{29,30,31,33,34,35,38,39},
}
def quri(v):
 e=v.get('embed') or {}
 if e.get('$type')=='app.bsky.embed.recordWithMedia':e=e.get('record') or {}
 return (e.get('record') or {}).get('uri','')
def ts(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
case={b['value']['subject']:b for b in blocks if '2026-09-28'<=b['value']['createdAt']<'2026-10-09'}
unique={}
for i,r in enumerate(rows):
 p=posts[r['source_post_uri']];v=p['record'];did=r['author_did'];b=case.get(did);date=b['value']['createdAt'] if b else ''
 assert r['unchanged_text_hash']
 parent=(v.get('reply') or {}).get('parent',{}).get('uri','');quote=quri(v)
 direct=parent.startswith('at://'+target+'/app.bsky.feed.post/') or quote.startswith('at://'+target+'/app.bsky.feed.post/')
 if r.get('directly_replies_or_quotes_aaron') is not None:assert direct==(r['directly_replies_or_quotes_aaron']=='True')
 item={'source_post_uri':p['uri'],'source_post_url':r['source_url'],'post_cid':p['cid'],'author_did':did,'current_handle':p['author']['handle'],'post_created_at':v['createdAt'],'appview_indexed_at':p['indexedAt'],'known_block_created_at':date,'in_recovered_block_window':int(bool(b)),'created_before_known_block':int(ts(v['createdAt'])<ts(date)) if date else '', 'indexed_before_known_block':int(ts(p['indexedAt'])<ts(date)) if date else '', 'direct_reply_or_quote_of_aaron':int(direct),'reply_parent_uri':parent,'quote_uri':quote,'text_sha256':r['current_text_sha256'],'text_unchanged_from_earlier_capture':1,'excerpt':r['current_text'][:85], 'selection':'published_example_list' if r.get('sample_row') else 'targeted_storyline_search', 'published_sample_row':r.get('sample_row','')}
 for k,indices in flags.items():item[k]=int(i in indices)
 if i==37:item['excerpt']='So it\u2019s defamatory lies meant to foment feelings of revulsion and hate...';item['coding_note']='Quotes an allegation to condemn it. No sexual-allegation endorsement coded.'
 else:item['coding_note']='One-reader text coding; no finding about allegation truth or motive.'
 if p['uri'] in unique:
  assert all(item[k]==unique[p['uri']][k] for k in flags)
  unique[p['uri']]['selection']+='; targeted_storyline_search'
 else:unique[p['uri']]=item
postmap=list(unique.values())
with (OUT/'account_post_map.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(postmap[0]));w.writeheader();w.writerows(postmap)
accountmap=[]
for did,b in sorted(case.items()):
 date=b['value']['createdAt'];selected=[p for p in postmap if p['author_did']==did and p['created_before_known_block']==1]
 accountmap.append({'subject_did':did,'block_record_uri':b['uri'],'block_record_cid':b['cid'],'block_created_at':date,'bulk_import_minute':int(date[:16] in {'2026-09-30T08:23','2026-09-30T08:54','2026-09-30T12:07','2026-09-30T12:08'}),'selected_preblock_posts_mapped':len(selected),'complete_history_collected':False})
with (OUT/'block_account_map.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(accountmap[0]));w.writeheader();w.writerows(accountmap)
# Keep exact numeric features and observed source metadata, with short text excerpts.
metadata=[]
for uri,p in posts.items():metadata.append({'uri':uri,'cid':p['cid'],'author_did':p['author']['did'],'createdAt':p['record']['createdAt'],'indexedAt':p['indexedAt'],'text_sha256':hashlib.sha256(p['record'].get('text','').encode()).hexdigest()})
(OUT/'source_metadata.json').write_text(json.dumps(metadata,indent=2));shutil.copy(ROOT/'new_retrieval_log.json',OUT/'retrieval_log.json')
source=ROOT/'recovered_autoblock_data' if (ROOT/'recovered_autoblock_data').exists() else ROOT
for name in ['anonymous_account_rows.json','embedded_chart_data.json','check_recovered_rows.py','recovered_data_check.json']:
 shutil.copy(source/name,OUT/name)
a=json.load(open(OUT/'anonymous_account_rows.json'));keys=['toxicity_band','blocked','trans_explicit','any_trans_signal','pronouns_listed','quoted_aaron'];combos=collections.Counter(tuple(r[k] for k in keys) for r in a)
sample=[r for r in postmap if r['published_sample_row'] and r['created_before_known_block']==1]
summary={'recovered_block_window_accounts':len(case),'bulk_import_accounts':sum(r['bulk_import_minute'] for r in accountmap),'unique_selected_evidence_posts':len(postmap),'selected_evidence_posts_before_known_block':sum(r['created_before_known_block']==1 for r in postmap),'selected_evidence_authors_before_known_block':len({r['author_did'] for r in postmap if r['created_before_known_block']==1}),'published_sample_posts_before_block':len(sample),'published_sample_preblock_authors':len({r['author_did'] for r in sample}),'published_sample_preblock_outside_reply_quote':sum(not r['direct_reply_or_quote_of_aaron'] for r in sample),'anonymous_rows':len(a),'anonymous_nonunique_feature_rows':sum(n for n in combos.values() if n>1),'anonymous_singleton_combinations':sum(n==1 for n in combos.values()),'anonymous_largest_feature_group':max(combos.values()),'campaign_adjusted_model':'NOT ESTIMATED','expanded_collection_status':'Expanded scratch collection lost in environment reset; not included or used to report a fitted result.'}
(OUT/'mapping_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
(OUT/'README.txt').write_text('''Account/post mapping and methodology check — 13 October 2026

Finding: the audit omitted documented relevant conduct from its behavior
comparison. It therefore does not establish anti-trans discrimination. This
package provides a verified mapping of selected evidence; the contribution of
the broader conduct to the overall sample difference remains unmeasured.

Files
block_account_map.csv: all 1,271 recovered block subjects in 28 September–8 October,
with record IDs, CIDs, dates, bulk-import classification and selected evidence counts.
A zero selected-evidence count DOES NOT mean no abuse occurred: histories are incomplete.
account_post_map.csv: 40 selected public posts with stable actor/post IDs, links,
record/index/block timestamps, short excerpts, source hashes and text-reviewed context.
source_metadata.json and retrieval_log.json: observed source metadata for 44 posts,
including Aaron\u2019s explanation and description of the sitewide seed query.
anonymous_account_rows.json and embedded_chart_data.json: the chart\u2019s anonymous data.
check_recovered_rows.py: reproducible numerical check; requires NumPy and SciPy.
recovered_data_check.json: preserved result of the subset-model numerical check.

Verification
Every evidence post was retrieved again. All 41 provenance-table entries retained
the same text hash as the earlier capture (one post occurs in both tables).
Mapped block dates exactly match the saved block-record snapshot. Twenty unique
selected posts have both record-created and AppView index timestamps before their
known block. Of the published hand-selected examples, 10 posts from 9 blocked
accounts predate blocking; 8 are outside direct reply/quote scoring.
These are selected examples, not a representative sample or a prevalence estimate.

Coding
Flags describe language in a post, not established facts about Aaron or a finding
about the writer\u2019s motive. Plain porn-like references, policy criticism, neutral
questions and rebuttals are separated from sexual allegations/ridicule and harm
rhetoric. The quoted allegation in the rebuttal post is not coded as endorsement.
Ambiguous harm/sexual rhetoric is marked separately. One reader did the coding;
there was no independent second coder. No gender identity is inferred for these
mapped authors, and no claim is made that all criticism belongs to a campaign.

What remains missing
1. The original author\u2019s account-ID and post-ID/CID mapping for the 1,678 anonymous rows.
   1,668 rows share their encoded feature combination with another row. Even unique
   combinations cannot be safely identified without the original sampling/coding rules.
2. Frozen pre-decision post histories and historical profile snapshots for both
   blocked and comparison accounts, including deletion/collection coverage.
3. Exact toxicity scores, post counts, swear/threat features, preprocessing,
   inclusion rules, model code, and the seed-selection query/lookback.
4. A complete comparison cohort with equivalent retrieval and context coding.

The subset numerical model reproduces an odds ratio of 2.465 (95% model-based
interval 1.646–3.691), close to the published full-model 2.48. It uses toxicity-band
indicators and quote status. It does not validate the full original regression,
source-post coverage, identity labels or causal interpretation.

A sound further test should separate bulk imports from incoming blocks; use a
common pre-import cutoff; count only conduct available before the decision;
compare the same accounts before/after adding contextual conduct; and examine
missingness, sparse cells and alternative identity/context definitions. A residual
association would not itself establish intent; attenuation would not prove no bias.

Status of this attempt
A much larger collection was attempted but lost when the working environment reset.
It was not preserved well enough to report a verifiable adjusted result. This package
contains only recovered, independently rechecked material. No campaign-adjusted
effect estimate is claimed. The earlier limited context report remains valid.

This is evidence about personal block records, not platform suspensions. Aaron\u2019s
account of an accidental like during an investigation is a public statement, not
independent proof of the accident. Campaign origin, coordination, and the truth
of sexual allegations are not established by this mapping.
''')
# Include the standalone rebuild/check source; no full repositories or third-party site code.
shutil.copy(Path(__file__),OUT/'build_mapping.py');shutil.copy(ROOT/'recover_evidence.py',OUT/'recover_evidence.py')
shutil.copytree(ROOT/'inputs',OUT/'inputs',dirs_exist_ok=True)
with zipfile.ZipFile(ROOT/'account_post_mapping.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for file in sorted(OUT.rglob('*')):
  if file.is_file():z.write(file,file.relative_to(OUT))
print('Package bytes',(ROOT/'account_post_mapping.zip').stat().st_size)
