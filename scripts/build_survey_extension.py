#!/usr/bin/env python3
"""Publish a completed ten-topic survey extension without modifying any source.

Only the ten new route-B bundles and their index are generated. Existing seventy
bundles stay at their existing API. All checks are local; no model/network calls.
The JSON contract matches dashboard/llm/publish_surveys.py and EvolutionHub.vue.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import urlsplit
import zipfile

SOURCE='data/runs/llm/survey_batches/skills_core10_completion_20261109_v1'
PREVIOUS='data/outputs/llm/survey_publication/skills70_20261029_v1'
LEXICON='retrieval/technology_point/config/ai_keywords_7class_20261109_v6.json'
PUBLIC_REFERENCE_KEYS=('reference_number','ref_id','title','year','authors','doi','arxiv','url','work_id','venue','journal')


def require(condition, message):
    if not condition:raise ValueError(message)


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def sha_bytes(data):return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def publish(root, source, previous, lexicon, output, public_prefix):
    root=root.resolve()
    def local(value):
        raw=str(value)
        for prefix in ('/data/gzk_jc/','/root/gzk_jc/'):
            if raw.startswith(prefix):return (root/raw[len(prefix):]).resolve()
        path=Path(raw)
        return (path if path.is_absolute() else root/path).resolve()
    source,previous,lexicon=map(local,(source,previous,lexicon));output=output.resolve()
    require(not output.exists(),'Use a new output directory; publication is immutable')
    require(not output.is_relative_to(source) and not output.is_relative_to(previous),'Output must not be inside a source publication')
    require(public_prefix.startswith('/') and not public_prefix.startswith('//') and '?' not in public_prefix and '#' not in public_prefix,'public-prefix must be an absolute URL path')
    public_prefix=public_prefix.rstrip('/')
    frozen={};verified={}
    def checked(path,expected=None):
        path=local(path)
        require(path.is_file(),f'Missing file: {path}')
        actual=sha(path)
        if expected is not None:require(actual==expected,f'SHA256 mismatch: {path}')
        frozen[str(path)]=actual
        return actual
    def binding(value):
        checked(value['path'],value['sha256'])
        return read(local(value['path']))
    source_index=read(source/'survey_index.json');source_index_sha=checked(source/'survey_index.json')
    plan=read(source/'plan.json');plan_sha=checked(source/'plan.json',read(source/'seal.json')['sha256'])
    original_plan=binding(plan['source_plan'])
    original_topics=read(local(original_plan['lexicon_path']))
    checked(original_plan['lexicon_path'],original_plan['lexicon_sha256'])
    previous_sha=checked(previous/'survey_index.json');old=read(previous/'survey_index.json')
    lexicon_sha=checked(lexicon);config=read(lexicon)
    terms={t['term_id']:t for t in config['terms']}
    old_entries=[e for e in old['entries'] if e.get('route')=='B']
    old_ids={e['topic_id'] for e in old_entries}
    entries=source_index['entries'];new_ids={e['topic_id'] for e in entries}
    require(len(terms)==len(config['terms'])==80,'Expected eighty unique current topics')
    require(len(old_entries)==len(old_ids)==70,'Expected seventy unchanged route-B topics')
    require(old_ids<=set(terms),'Previous publication contains a topic absent from the current lexicon')
    require(len(entries)==len(new_ids)==10 and new_ids==set(terms)-old_ids,'Extension must exactly equal current eighty minus previous seventy topics')
    jobs={j['spec']['topic_id']:j for j in plan['jobs']};reuse={r['topic_id']:r for r in plan['reuse']}
    require(not(set(jobs)&set(reuse)) and set(jobs)|set(reuse)==new_ids,'Completed plan and extension topic IDs differ')
    source_topics={t['topic_id']:t for t in original_topics['topics']}
    require(set(source_topics)==new_ids,'Sealed source topic config differs from extension')
    receipt=read(source/'package_receipt.json');archive=local(receipt['path']);archive_sha=checked(archive,receipt['sha256'])
    require(receipt['articles']==receipt['total']==len(entries),'Package receipt is not complete')
    bundles={};public_entries=[];topic_checks=[];global_work_ids=set();warnings=[]
    with zipfile.ZipFile(archive) as zipped:
        require(zipped.testzip() is None,'Completed package ZIP integrity failure')
        for entry in sorted(entries,key=lambda e:e['topic_id']):
            topic=entry['topic_id'];term=terms[topic]
            require(entry.get('ready_for_dashboard') is True,f'{topic}: source is not ready')
            require(entry.get('status') in ('completed_draft','reused_completed','completed','draft_completed'),f'{topic}: incomplete status')
            require(entry['name']==term['name']==source_topics[topic]['name'],f'{topic}: topic name mismatch')
            require(all(source_topics[topic].get(k)==term.get(k) for k in ('definition','level1','level2')),f'{topic}: source definition or category differs from current lexicon')
            article=local(entry['article_path']);refs_path=local(entry['references_path'])
            require(topic in article.parts and topic in refs_path.parts,f'{topic}: source paths belong to another topic')
            article_data=article.read_bytes();references_data=refs_path.read_bytes()
            article_hash=checked(article);references_hash=checked(refs_path)
            require(zipped.read(f'Markdown/{topic}.md')==article_data,f'{topic}: source article differs from sealed package')
            package_refs=json.loads(zipped.read(f'参考文献/{topic}.json'))
            package_keys=('reference_number','title','year','authors','doi','arxiv','url')
            projected_refs=[{k:v for k,v in r.items() if k in package_keys} for r in json.loads(references_data)]
            require(package_refs==projected_refs,f'{topic}: public bibliography differs from sealed package')
            provenance_kind='reused_completed' if topic in reuse else 'completed_draft'
            if topic in reuse:
                prior=reuse[topic]
                require(local(prior['article']['path'])==article and local(prior['references']['path'])==refs_path,f'{topic}: reused paths differ from sealed plan')
                checked(article,prior['article']['sha256']);checked(refs_path,prior['references']['sha256'])
                require(prior['actual_references']==entry['actual_references'],f'{topic}: reused reference count mismatch')
            else:
                require(jobs[topic]['spec']['name']==term['name'],f'{topic}: completed job name mismatch')
                result=read(source/topic/'result.json')
                checked(source/topic/'result.json')
                require(result['topic_id']==topic and result['name']==term['name'] and result['status']=='completed_draft',f'{topic}: incomplete or mismatched result')
                require(local(result['article_path'])==article and local(result['references_path'])==refs_path,f'{topic}: result paths mismatch')
                for path,expected in result['artifacts'].items():checked(path,expected)
                source_checks=read(article.parent/'checks.json')
                require(source_checks.get('citation_ids_and_source_hashes_verified') is True,f'{topic}: original reference/hash checks did not pass')
            content=article_data.decode('utf-8');references=json.loads(references_data)
            require(content.strip() and references,f'{topic}: empty article or bibliography')
            require(len(references)==entry['actual_references'],f'{topic}: bibliography count mismatch')
            references=sorted(references,key=lambda r:int(r['reference_number']))
            numbers=[int(r['reference_number']) for r in references]
            require(numbers==list(range(1,len(references)+1)),f'{topic}: bibliography numbering must be consecutive from one')
            require(len({r.get('ref_id') for r in references})==len(references) and all(r.get('ref_id') for r in references),f'{topic}: missing or duplicate reference ID')
            # Exclude the bibliography itself so its numbering cannot hide an unused citation.
            body=re.split(r'^#{1,6}\s*(?:参考文献|References|Bibliography)\s*$',content,flags=re.M|re.I)[0]
            cited={int(x) for x in re.findall(r'\[(\d+)\]',body)}
            require(cited==set(numbers),f'{topic}: body/reference numbering differs; unknown={sorted(cited-set(numbers))}, unused={sorted(set(numbers)-cited)}')
            require(not re.search(r'\[\d+\]\(',body),f'{topic}: linked numeric citations need an explicit renderer adapter')
            for ref in references:
                require(ref.get('title'),f'{topic}: missing reference title')
                require(ref.get('text_path') and ref.get('text_sha256'),f'{topic}: missing cited-text SHA binding')
                path=local(ref['text_path']);expected=ref['text_sha256']
                if str(path) not in verified:verified[str(path)]=checked(path,expected)
                require(verified[str(path)]==expected,f'{topic}: conflicting cited-text hashes')
                if ref.get('url'):require(urlsplit(ref['url']).scheme in ('http','https'),f'{topic}: unsupported reference URL scheme')
                global_work_ids.add(ref.get('work_id') or ref.get('doi') or ref.get('arxiv') or ref['title'])
            title=next((line[2:].strip() for line in content.splitlines() if line.startswith('# ')),term['name']+'研究综述')
            public_refs=[{k:r[k] for k in PUBLIC_REFERENCE_KEYS if k in r} for r in references]
            for ref in public_refs:ref['reference_number']=int(ref['reference_number'])
            bundle={'topic_id':topic,'route':'B','title':title,'content_md':content,'references':public_refs,'article_sha256':article_hash,'references_sha256':references_hash,'expert_reviewed':False,'source_version':source.name}
            bundles[topic]=bundle
            relative=f'{topic}/dashboard_bundle.json'
            public_entries.append({'topic_id':topic,'name':term['name'],'category_id':term['category_id'],'category':term['level1'],'group':term['level2'],'route':'B','status':'draft_completed','ready_for_dashboard':True,'actual_references':len(references),'expert_reviewed':False,'source_status':provenance_kind,'source_version':source.name,'dashboard_bundle_path':relative,'dashboard_bundle_url':public_prefix+'/'+relative,'article_sha256':article_hash,'references_sha256':references_hash})
            topic_checks.append({'topic_id':topic,'name':term['name'],'source_status':provenance_kind,'article_path':str(article),'references_path':str(refs_path),'article_sha256':article_hash,'references_sha256':references_hash,'references':len(references),'body_cited_references':len(cited),'consecutive_reference_numbers':True,'cited_text_sha_bindings_verified':len(references),'sealed_package_article_and_public_bibliography_match':True,'topic_mapping_verified':True,'original_md_preserved':True})
    # A publication is a snapshot, and sources must not change during validation.
    for path,expected in frozen.items():require(sha(Path(path))==expected,f'Source changed during publication: {path}')
    now=datetime.now(timezone.utc).isoformat()
    result_index={'schema_version':1,'batch_id':output.name,'updated_at':now,'join_key':['topic_id','route'],'keyword_version':config['version'],'keyword_sha256':lexicon_sha,'entries':public_entries,'counts':{'total':10,'ready':10,'previous_route_b_preserved':70,'combined_route_b_ready':80},'baseline':{'source_version':previous.name,'survey_index_sha256':previous_sha,'policy':'unchanged; retain the existing API for these seventy topics'},'source_index':{'source_version':source.name,'sha256':source_index_sha},'publication_mode':'static_extension_only','frontend_published':False,'full_bibliographies_in_bundle_and_references_json':False}
    quality={'passed':True,'version':output.name,'built_at':now,'scope':'Local file integrity, topic correspondence and citation numbering; not scientific/expert review','expert_reviewed':False,'model_calls':0,'network_requests':0,'source_originals_modified':False,'previous_seventy_modified':False,'previous_route_b_topic_count':70,'new_topic_count':10,'combined_route_b_topic_count':80,'references_sum':sum(e['actual_references'] for e in public_entries),'unique_work_keys_across_topics':len(global_work_ids),'cited_text_files_sha_verified':len(verified),'all_source_files_sha_verified':len(frozen),'source_plan_sha256':plan_sha,'source_package_sha256':archive_sha,'keyword_sha256':lexicon_sha,'source_index_sha256':source_index_sha,'previous_index_sha256':previous_sha,'checks':topic_checks,'warnings':warnings}
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.'+output.name+'.',dir=output.parent))
    try:
        for entry in public_entries:
            path=temp/entry['dashboard_bundle_path'];dump(path,bundles[entry['topic_id']]);entry['dashboard_bundle_sha256']=sha(path)
        dump(temp/'survey_index.json',result_index);dump(temp/'quality.json',quality);dump(temp/'status.json',{'status':'completed','frontend_published':False,'topics':10})
        require(not output.exists(),'Output appeared during generation; refusing replacement')
        os.rename(temp,output)
    except Exception:
        shutil.rmtree(temp);raise
    print(json.dumps({'output':str(output),'topics':[{'id':e['topic_id'],'references':e['actual_references'],'url':e['dashboard_bundle_url']} for e in public_entries],'references_sum':quality['references_sum'],'cited_text_files_sha_verified':len(verified),'passed':True},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path.cwd())
    parser.add_argument('--source',type=Path,default=Path(SOURCE))
    parser.add_argument('--previous',type=Path,default=Path(PREVIOUS))
    parser.add_argument('--lexicon',type=Path,default=Path(LEXICON))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--public-prefix',default='/evolution-surveys/v1')
    args=parser.parse_args();publish(args.root,args.source,args.previous,args.lexicon,args.output,args.public_prefix)
