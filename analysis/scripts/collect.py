# Compilation and analysis: Friendly Society of Corvids.
"""Read-only public AT Protocol collection, with cached responses and provenance."""
import concurrent.futures
import hashlib
import json
import pathlib
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
CACHE = ROOT / 'raw'
CACHE.mkdir(exist_ok=True)
API = 'https://public.api.bsky.app'
DID = 'did:plc:ksjfbda7262bbqmuoly54lww'
PDS = 'https://shimeji.us-east.host.bsky.network'

def fetch_url(url):
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.json')
    if path.exists():
        return json.loads(path.read_text())['body']
    request = urllib.request.Request(url, headers={'User-Agent': 'Public-record-methodology-review/1.0'})
    started = datetime.now(timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
            status = response.status
    except urllib.error.HTTPError as error:
        raw = error.read().decode('utf-8', errors='replace')
        try:
            data = json.loads(raw)
        except ValueError:
            data = {'error': raw[:500]}
        status = error.code
    except Exception as error:
        data = {'error': type(error).__name__, 'message': str(error)}
        status = None
    envelope = {'url': url, 'retrieved_at_utc': started, 'status': status, 'body': data}
    path.write_text(json.dumps(envelope, ensure_ascii=False))
    return data

def api(method, **parameters):
    return fetch_url(API + '/xrpc/' + method + '?' + urllib.parse.urlencode(parameters, doseq=True))

def records(collection):
    rows = []
    cursor = None
    seen = set()
    while True:
        params = {'repo': DID, 'collection': collection, 'limit': 100, 'reverse': 'true'}
        if cursor:
            params['cursor'] = cursor
        data = fetch_url(PDS + '/xrpc/com.atproto.repo.listRecords?' + urllib.parse.urlencode(params))
        if 'records' not in data:
            print(json.dumps({'collection': collection, 'error': data}), flush=True)
            break
        rows.extend(data['records'])
        cursor = data.get('cursor')
        if not cursor or cursor in seen:
            break
        seen.add(cursor)
    (ROOT / (collection + '.json')).write_text(json.dumps(rows, ensure_ascii=False))
    print(json.dumps({'collection': collection, 'records': len(rows)}), flush=True)
    return rows

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(records, ['app.bsky.graph.block', 'app.bsky.feed.post']))
