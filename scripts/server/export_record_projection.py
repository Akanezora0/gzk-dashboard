#!/usr/bin/env python3
"""Export only the current Dashboard records response projection, read-only."""
from pathlib import Path
import collections
import gzip
import hashlib
import html
import json
import os
import re
import sqlite3
import time

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project-root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
ROOT = args.project_root.resolve()
DEST = args.output.resolve()
if DEST.exists() and any(DEST.iterdir()):
    parser.error('Output must be empty; export to a new staging directory first.')
NAMES = {
    'nsfc_fund': '基金项目', 'nsfc_paper': '基金资助论文',
    'cnki_paper': '中文期刊文献', 'legacy_patent': '专利',
    'legacy_software': '软件著作权', 'legacy_product': '载体产品',
    'legacy_news': '产业新闻', 'legacy_policy': '既有政策',
    'ai_policy': 'AI政策文本', 'ai_company': '企业候选', 'ai_report': '行业报告',
}


def portable_source(value):
    if not isinstance(value, str):
        return value
    for prefix in ('/root/gzk_jc/', '/data/gzk_jc/'):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value


def main():
    started = time.time()
    config = json.loads((ROOT / 'dashboard/llm/config.json').read_text())
    source = ROOT / config['snapshot'] / 'candidates.sqlite3'
    before = source.stat()
    db = sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    db.execute('BEGIN')
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = {
        'schema_version': 1,
        'source_endpoint': '/api/llm/records',
        'source_version': config['snapshot'].split('/')[-1],
        'scope': 'ai',
        'query': {'namespace': '<namespace>', 'scope': 'ai', 'q': '', 'offset': 0, 'limit': 10},
        'ordering': 'year DESC, uid ASC (id in exported rows)',
        'format': 'gzip-compressed UTF-8 JSON Lines; each line is one API rows[] object',
        'source_file_normalization': 'Remove only project-root absolute prefixes; preserve relative provenance and row_number.',
        'search_semantics': {
            'field': 'title', 'operation': 'contains',
            'ascii_case_insensitive': True, 'unicode_case_insensitive': False,
            'percent_underscore_backslash': 'literal characters',
            'q_max_length': 100, 'offset_min': 0, 'offset_max': 300000,
            'limit_min': 1, 'limit_max': 50, 'default_limit': 20,
            'current_ui_limit': 10,
        },
        'namespaces': [],
    }
    for namespace in NAMES:
        expected = db.execute('SELECT COUNT(*) FROM entity WHERE namespace=? AND ai=1', (namespace,)).fetchone()[0]
        cur = db.execute('SELECT * FROM entity WHERE namespace=? AND ai=1 ORDER BY year DESC,uid', (namespace,))
        count = 0
        parts = []
        part = None
        raw_file = None
        compressed = None
        uncompressed_bytes = 0
        uncompressed_sha = None
        part_count = 0

        def close_part():
            nonlocal part, raw_file, compressed, uncompressed_bytes, uncompressed_sha, part_count
            if compressed is None:
                return
            compressed.close()
            raw_file.close()
            size = part.stat().st_size
            if size >= 40_000_000:
                raise RuntimeError(f'Compressed part exceeds 40 MB: {part}')
            parts.append({'file': part.name, 'count': part_count, 'bytes': size,
                          'uncompressed_bytes': uncompressed_bytes,
                          'sha256': hashlib.file_digest(part.open('rb'), 'sha256').hexdigest(),
                          'uncompressed_sha256': uncompressed_sha.hexdigest()})
            part = raw_file = compressed = uncompressed_sha = None
            uncompressed_bytes = part_count = 0

        while True:
            selected = cur.fetchmany(500)
            if not selected:
                break
            ids = [x['uid'] for x in selected]
            evidence = {uid: [] for uid in ids}
            placeholders = ','.join('?' for _ in ids)
            for m in db.execute('SELECT uid,field,keyword,term_id,snippet,source_file,row_number '
                                f'FROM match_evidence WHERE uid IN ({placeholders})', ids):
                bucket = evidence[m['uid']]
                if len(bucket) < 8:
                    item = {k: m[k] for k in m.keys() if k != 'uid'}
                    item['source_file'] = portable_source(item['source_file'])
                    bucket.append(item)
            for x in selected:
                meta = json.loads(x['metadata_json'])
                matches = evidence[x['uid']]
                row = dict(id=x['uid'], title=x['title'], year=x['year'], source=NAMES[namespace], source_id=x['source_id'],
                           url=x['source_id'] if x['source_id'].startswith(('https://', 'http://')) else None,
                           authors=re.sub(r'<[^>]*>', '', html.unescape(meta.get('author') or '')) or None,
                           institution=meta.get('author_institution'),
                           subject=meta.get('申请人') or meta.get('企业名称') or meta.get('proj_school') or meta.get('dependUnit') or meta.get('制定机关'),
                           matched_terms=list(dict.fromkeys(m['keyword'] for m in matches)), evidence=matches,
                           doi=x['doi'], source_scope=x['source_scope'], expert_reviewed=False)
                payload = (json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
                if compressed is not None and uncompressed_bytes + len(payload) > 30_000_000:
                    close_part()
                if compressed is None:
                    part = DEST / f'{namespace}.{len(parts) + 1:03d}.jsonl.gz'
                    raw_file = part.open('wb')
                    compressed = gzip.GzipFile(filename='', mode='wb', compresslevel=6, fileobj=raw_file, mtime=0)
                    uncompressed_sha = hashlib.sha256()
                compressed.write(payload)
                uncompressed_sha.update(payload)
                uncompressed_bytes += len(payload)
                part_count += 1
                count += 1
        close_part()
        if count != expected:
            raise RuntimeError(f'Count mismatch for {namespace}: {count} != {expected}')
        item = {'namespace': namespace, 'source': NAMES[namespace], 'scope': 'ai', 'total': expected,
                'count': count, 'parts': parts, 'bytes': sum(p['bytes'] for p in parts),
                'uncompressed_bytes': sum(p['uncompressed_bytes'] for p in parts)}
        manifest['namespaces'].append(item)
        print(json.dumps({k: v for k, v in item.items() if k != 'parts'}, ensure_ascii=False), flush=True)
    db.rollback()
    db.close()
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError('Source database changed during export; review snapshot consistency.')
    manifest['total_records'] = sum(x['count'] for x in manifest['namespaces'])
    manifest['total_compressed_bytes'] = sum(x['bytes'] for x in manifest['namespaces'])
    manifest['total_uncompressed_bytes'] = sum(x['uncompressed_bytes'] for x in manifest['namespaces'])
    manifest['source_stat_unchanged'] = True
    manifest['elapsed_seconds'] = round(time.time() - started, 2)
    (DEST / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'done': True, 'manifest': str(DEST / 'manifest.json'),
                      'total_records': manifest['total_records'],
                      'bytes': manifest['total_compressed_bytes'],
                      'elapsed_seconds': manifest['elapsed_seconds']}), flush=True)


if __name__ == '__main__':
    main()
