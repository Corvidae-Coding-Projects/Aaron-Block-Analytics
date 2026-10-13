# Compilation and analysis: Friendly Society of Corvids.
"""Find the source of a declared published example without treating search as a census."""
import concurrent.futures
import json
import re
from urllib.parse import urlencode
from collect import ROOT, fetch_url

def normalize(text):
    return re.sub(r'\s+', ' ', text).strip().casefold().replace('’', "'").replace('“', '"').replace('”', '"')

def verify(row):
    number, text = row
    # A deterministic phrase taken from the supplied example, not an invented query.
    words = re.findall(r"[A-Za-z0-9]+", text)
    phrase = ' '.join(words[:10])
    params = dict(q='"' + phrase + '"', since='2026-01-01T00:00:00Z',
                  until='2026-10-01T12:45:17Z', sort='latest', limit=100)
    result = fetch_url('https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?' + urlencode(params))
    matches = []
    for post in result.get('posts', []):
        body = post.get('record', {}).get('text', '')
        if normalize(body) == normalize(text):
            matches.append(post)
    return {'number': int(number), 'query_phrase': phrase, 'reported_hits': result.get('hitsTotal'),
            'exact_matches': matches, 'error': result.get('error')}

if __name__ == '__main__':
    rows = [r for r in json.loads((ROOT / 'published_sample_rows.json').read_text()) if len(r) == 2 and r[0].isdigit()]
    output = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(verify, rows):
            output.append(result)
            print(json.dumps({'sample_row': result['number'], 'exact_matches': len(result['exact_matches']), 'error': result['error']}), flush=True)
    (ROOT / 'sample_verification.json').write_text(json.dumps(output, ensure_ascii=False))
