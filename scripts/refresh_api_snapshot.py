#!/usr/bin/env python3
"""Read existing indexed endpoints into a NEW staging directory, never edit the live DB."""
from pathlib import Path
import argparse, datetime, hashlib, json, urllib.request, urllib.error
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--base',required=True,help='Authorized read-only Dashboard API base URL')
p.add_argument('--output',type=Path,required=True,help='New empty staging directory')
p.add_argument('--index',type=Path,default=Path(__file__).resolve().parents[1]/'snapshot/api/index.json')
a=p.parse_args()
if a.output.exists() and any(a.output.iterdir()):p.error('output must be empty')
a.output.mkdir(parents=True,exist_ok=True)
old=json.loads(a.index.read_text())
responses={}
def portable(x):
    if isinstance(x,dict):return {k:portable(v) for k,v in x.items()}
    if isinstance(x,list):return [portable(v) for v in x]
    if isinstance(x,str):
        for prefix in ['/root/gzk_jc/','/data/gzk_jc/']:x=x.replace(prefix,'')
    return x
for endpoint,spec in old['responses'].items():
    try:
        with urllib.request.urlopen(a.base.rstrip('/')+endpoint,timeout=60) as response:status=response.status;body=response.read()
    except urllib.error.HTTPError as error:status=error.code;body=error.read()
    if status!=spec['status']:raise RuntimeError(f'Status changed for {endpoint}: {status}; inspect before publishing')
    raw=(json.dumps(portable(json.loads(body)),ensure_ascii=False,separators=(',',':'))+'\n').encode()
    name=hashlib.sha256(endpoint.encode()).hexdigest()[:24]+'.json'
    (a.output/name).write_bytes(raw)
    responses[endpoint]=dict(file=name,status=status,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
(a.output/'index.json').write_text(json.dumps(dict(captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='Authorized read-only Dashboard API snapshot',normalization='machine path prefixes only',responses=responses),ensure_ascii=False,indent=2))
print(f'Captured {len(responses)} responses; validate and review before replacing snapshot/api.')
