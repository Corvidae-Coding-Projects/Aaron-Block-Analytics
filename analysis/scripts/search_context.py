# Compilation and analysis: Friendly Society of Corvids.
"""Collect declared public searches; result coverage is measured, never assumed."""
import concurrent.futures
import json
from urllib.parse import urlencode
from collect import ROOT, DID, fetch_url

SEARCHES = [
    ('recent_full_name', '"Aaron Rodericks"', '2026-09-15T00:00:00Z', '2026-10-09T00:00:00Z', {}),
    ('recent_mentions', 'Aaron', '2026-09-15T00:00:00Z', '2026-10-09T00:00:00Z', {'mentions': DID}),
    ('likes_origin', 'Aaron', '2024-12-18T00:00:00Z', '2024-12-23T00:00:00Z', {}),
    ('sexual_allegation', '"Aaron" "pedophile"', '2026-01-01T00:00:00Z', '2026-10-09T00:00:00Z', {}),
    ('porn_allegation', '"Aaron" "porn"', '2026-01-01T00:00:00Z', '2026-10-09T00:00:00Z', {}),
    ('bot_creator', '"Aaron"', '2024-12-01T00:00:00Z', '2026-10-09T00:00:00Z', {'author': 'queen-of-the.pelf.ie'}),
]

def search(spec):
    label, query, since, until, extra = spec
    params = dict(q=query, since=since, until=until, sort='latest', limit=100, **extra)
    rows = {}
    cursors = set()
    hits = []
    pages = 0
    error = None
    exhausted = False
    while pages < 50:
        data = fetch_url('https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?' + urlencode(params))
        if 'posts' not in data:
            error = data
            break
        pages += 1
        hits.append(data.get('hitsTotal'))
        new = 0
        for post in data['posts']:
            if post['uri'] not in rows:
                new += 1
            rows[post['uri']] = post
        cursor = data.get('cursor')
        print(json.dumps({'search': label, 'page': pages, 'unique_posts': len(rows), 'reported_hits': hits[-1]}), flush=True)
        if not cursor or not data['posts']:
            exhausted = True
            break
        if cursor in cursors or new == 0:
            error = {'error': 'PaginationStopped', 'reason': 'repeated cursor or no new posts'}
            break
        cursors.add(cursor)
        params['cursor'] = cursor
    output = {'label': label, 'query': query, 'since': since, 'until': until, 'extra': extra,
              'pages': pages, 'reported_hits': hits, 'exhausted': exhausted, 'error': error,
              'posts': list(rows.values())}
    (ROOT / ('search_' + label + '.json')).write_text(json.dumps(output, ensure_ascii=False))
    return label, len(rows), exhausted

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(search, SEARCHES):
            print(json.dumps({'completed': result}), flush=True)
