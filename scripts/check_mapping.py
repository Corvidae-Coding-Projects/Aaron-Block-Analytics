"""Verify the preserved mapping against independently retained source metadata.

Compilation and analysis: Friendly Society of Corvids.
This checks the saved records offline; it does not fetch public posts.
"""
from pathlib import Path
from datetime import datetime
from collections import Counter
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
MAPPING = ROOT / 'mapping'

def read_csv(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))

def time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

posts = read_csv(MAPPING / 'account_post_map.csv')
accounts = read_csv(MAPPING / 'block_account_map.csv')
snapshot = json.loads((MAPPING / 'inputs/block_record_snapshot.json').read_text())
metadata = {r['uri']: r for r in json.loads((MAPPING / 'source_metadata.json').read_text())}
summary = json.loads((MAPPING / 'mapping_summary.json').read_text())
blocks = {r['value']['subject']: r for r in snapshot if '2026-09-28' <= r['value']['createdAt'] < '2026-10-09'}
assert len(accounts) == len(blocks) == 1271
assert len({r['subject_did'] for r in accounts}) == 1271
assert len(posts) == len({r['source_post_uri'] for r in posts}) == 40

prior = []
for post in posts:
    source = metadata[post['source_post_uri']]
    assert source['cid'] == post['post_cid']
    assert source['text_sha256'] == post['text_sha256']
    assert source['author_did'] == post['author_did']
    assert source['createdAt'] == post['post_created_at']
    assert source['indexedAt'] == post['appview_indexed_at']
    block = blocks.get(post['author_did'])
    if block is not None:
        assert post['known_block_created_at'] == block['value']['createdAt']
        created_before = time(post['post_created_at']) < time(post['known_block_created_at'])
        indexed_before = time(post['appview_indexed_at']) < time(post['known_block_created_at'])
        assert int(post['created_before_known_block']) == int(created_before)
        assert int(post['indexed_before_known_block']) == int(indexed_before)
        if created_before and indexed_before:
            prior.append(post)
    else:
        assert post['known_block_created_at'] == ''

counts = Counter(r['author_did'] for r in posts if r['created_before_known_block'] == '1')
for account in accounts:
    block = blocks[account['subject_did']]
    assert account['block_record_uri'] == block['uri']
    assert account['block_record_cid'] == block['cid']
    assert account['block_created_at'] == block['value']['createdAt']
    assert int(account['selected_preblock_posts_mapped']) == counts[account['subject_did']]
    assert account['complete_history_collected'] == 'False'

sample = [r for r in posts if r['published_sample_row'] and r['created_before_known_block'] == '1']
outside = [r for r in sample if r['direct_reply_or_quote_of_aaron'] == '0']
assert len(prior) == summary['selected_evidence_posts_before_known_block'] == 20
assert len({r['author_did'] for r in prior}) == summary['selected_evidence_authors_before_known_block'] == 18
assert len(sample) == summary['published_sample_posts_before_block'] == 10
assert len(outside) == summary['published_sample_preblock_outside_reply_quote'] == 8
assert sum(int(r['bulk_import_minute']) for r in accounts) == summary['bulk_import_accounts'] == 1087

manifest = json.loads((ROOT / 'chart/manifest.json').read_text())
for name, expected in manifest['files'].items():
    assert hashlib.sha256((ROOT / 'chart' / name).read_bytes()).hexdigest() == expected, name

print(json.dumps({'accounts': len(accounts), 'mapped_posts': len(posts), 'preblock_posts': len(prior),
                  'preblock_authors': len({r['author_did'] for r in prior}), 'sample_preblock': len(sample),
                  'sample_preblock_outside_scored_scope': len(outside), 'checks': 'passed'}, indent=2))
