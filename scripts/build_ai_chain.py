"""Build the AI chain presentation from accepted snapshots; no database writes.

Run: python manage.py run dashboard/cursor_ui/scripts/build_ai_chain.py
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import shutil
from gzk.paths import ROOT

OUT = ROOT / 'data/outputs/shared/ui_handoff/cursor_20260924/analysis_public/chain-analysis/v1'
BASE = ROOT / 'data/runs/llm/innovation'
HANDOFF = ROOT / 'data/outputs/shared/innovation_research/claude_research_design_handoff_20261103_v1/Claude_研究力量展示设计交接包'
SOURCES = []

def read(path):
    content = path.read_bytes()
    SOURCES.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(content).hexdigest()})
    return json.loads(content)

def public(value):
    """Keep analysis fields; remove server locators and internal operational notes."""
    if isinstance(value, list):
        return [public(v) for v in value]
    if isinstance(value, dict):
        return {k: public(v) for k, v in value.items() if k not in {
            'queries', 'sql', 'source_database', 'database', 'local_source_file',
            'source_locator', 'earlier_direct_source_locators', 'later_direct_source_locators',
            'remaining_limits', 'not_claimed', 'new_facts_vs_prior', 'output_scope'}}
    return value

def landscape():
    # Curated primary-source records. Publication year is the displayed event year.
    orgs = [
        ('tsinghua','清华大学','中国 · 高校','cn','高校与科研机构'),
        ('zhipu','智谱 AI','中国 · 企业','cn','高校与科研机构'),
        ('shlab','上海人工智能实验室','中国 · 科研机构','cn','高校与科研机构'),
        ('qwen','阿里巴巴 · 通义','中国 · 企业','cn','模型研发企业'),
        ('deepseek','DeepSeek','中国 · 企业','cn','模型研发企业'),
        ('brain','Google Brain','国际 · Google Research','intl','国际研究机构'),
        ('deepmind','Google DeepMind','国际 · 企业研究','intl','国际研究机构'),
        ('openai','OpenAI','国际 · 企业研究','intl','国际研究机构'),
        ('anthropic','Anthropic','国际 · 企业研究','intl','国际研究机构'),
        ('meta','Meta AI','国际 · 企业研究','intl','国际研究机构'),
        ('stanford','斯坦福大学等','国际 · 高校合作','intl','高校系统研究'),
        ('berkeley','加州大学伯克利分校等','国际 · 高校合作','intl','高校系统研究'),
    ]
    rows = [
        ('tsinghua',2021,'GLM','自回归空白填充预训练，连接语言理解与生成任务。','https://arxiv.org/abs/2103.10360','预训练方法'),
        ('tsinghua',2022,'GLM-130B','清华与智谱共同研究的双语预训练模型，公开大规模训练的设计与工程经验。','https://arxiv.org/abs/2210.02414','联合研究'),
        ('zhipu',2023,'ChatGLM','沿 GLM 模型系列推进双语对话模型及开放实践。','https://github.com/THUDM/ChatGLM-6B','对话模型'),
        ('zhipu',2024,'GLM-4','模型系列进一步扩展到工具使用和多类任务。','https://arxiv.org/abs/2406.12793','模型系列'),
        ('shlab',2023,'书生·浦语','上海 AI 实验室、商汤及多所高校联合发布大语言模型。','https://www.shlab.org.cn/news/5443407','联合研究'),
        ('qwen',2023,'Qwen-VL','将视觉理解、文字识别与定位能力纳入视觉语言模型。','https://arxiv.org/abs/2308.12966','多模态'),
        ('qwen',2025,'Qwen3','模型系列推进推理与非推理模式的统一。','https://arxiv.org/abs/2505.09388','推理模型'),
        ('deepseek',2024,'DeepSeek-V2','以混合专家和多头潜在注意力探索更高效的模型训练与推理。','https://arxiv.org/abs/2405.04434','架构与效率'),
        ('deepseek',2025,'DeepSeek-R1','通过强化学习推进大语言模型的推理能力。','https://arxiv.org/abs/2501.12948','推理模型'),
        ('brain',2017,'Transformer','以注意力机制构建序列转换架构，成为后续预训练模型的重要基础。','https://arxiv.org/abs/1706.03762','基础架构'),
        ('brain',2018,'BERT','双向预训练与任务微调结合，推进通用语言表示。','https://arxiv.org/abs/1810.04805','预训练方法'),
        ('deepmind',2023,'Gemini','原生多模态模型系列，整合文本、图像等能力。','https://arxiv.org/abs/2312.11805','多模态'),
        ('deepmind',2024,'Gemini 1.5','扩展长上下文能力，支持多模态信息理解。','https://arxiv.org/abs/2403.05530','长上下文'),
        ('openai',2018,'GPT','将生成式预训练与监督微调结合，用于多类语言任务。','https://openai.com/index/language-unsupervised/','预训练方法'),
        ('openai',2022,'ChatGPT','通过对话交互和人类反馈训练，推动大语言模型进入广泛使用。','https://openai.com/index/chatgpt/','对话应用'),
        ('openai',2023,'GPT-4','扩展多模态输入与复杂任务能力。','https://openai.com/index/gpt-4-research/','多模态'),
        ('anthropic',2023,'Claude','围绕有用、诚实和无害的目标推进对话模型。','https://www.anthropic.com/news/introducing-claude','对齐与应用'),
        ('anthropic',2024,'Claude 3','推出不同能力与成本取向的模型系列。','https://www.anthropic.com/news/claude-3-family','模型系列'),
        ('meta',2023,'LLaMA','探索更高效的基础语言模型训练，扩大研究模型的可用性。','https://arxiv.org/abs/2302.13971','基础模型'),
        ('stanford',2022,'FlashAttention','围绕显存读写重新组织注意力计算，提升系统执行效率。','https://arxiv.org/abs/2205.14135','系统优化'),
        ('berkeley',2023,'vLLM','用 PagedAttention 改进大语言模型服务中的显存管理。','https://arxiv.org/abs/2309.06180','推理服务'),
    ]
    return {
        'range': [2017,2025], 'checkedAt':'2026-11-03',
        'organizations':[dict(id=a,name=b,subtitle=c,region=d,group=e) for a,b,c,d,e in orgs],
        'events':[dict(id=f'event-{i}',org=a,year=b,label=c,description=d,url=e,topic=f) for i,(a,b,c,d,e,f) in enumerate(rows)],
        'connections':[
            dict(id='tsinghua-zhipu',source='tsinghua',target='zhipu',year=2019,label='实验室成果转化',description='清华大学计算机系公开材料记载：知识工程实验室于 2019 年转化了智谱 AI。GLM 系列体现了后续校企联合研究。',url='https://www.cs.tsinghua.edu.cn/info/1088/4451.htm'),
            dict(id='brain-deepmind',source='brain',target='deepmind',year=2023,label='研究团队合并',description='Google 于 2023 年宣布将 DeepMind 与 Google Research 的 Brain 团队合并为 Google DeepMind。',url='https://deepmind.google/blog/announcing-google-deepmind/')
        ]
    }

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    raw = read(HANDOFF/'关系明细/真实关系原始结构.json')
    focus = read(BASE/'research_graph_focus_20261103_v2/verified_institution_data.json')
    branches = read(BASE/'research_graph_branches_20261103_v3/verified_branch_data.json')
    detail = read(BASE/'research_graph_branches_20261103_v3/case_content_evidence.json')
    institution_analysis = read(BASE/'relations_review_20261103_v1/institution_analysis.json')
    continuity = raw['continuity']['records']
    assert len(continuity)==286
    assert len({r['person_id'] for r in continuity})==278
    assert all(r['shared_official_source_person_ids'] for r in continuity)
    graph=raw['institution_cohort']
    assert len(graph['project_nodes'])==242
    assert len(graph['paper_nodes'])==2971
    # The page needs references and project identifiers, not raw source-row payloads.
    graph={k:v for k,v in graph.items() if k!='project_paper_evidence'}
    payload=public(dict(version='ai-chain-20261103-v1',graph=graph,continuity=continuity,
                       focus=focus,branches=branches,caseDetail=detail,landscape=landscape(),
                       institutionSummary=institution_analysis['retained_vs_new_2021']))
    (OUT/'research.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')))
    animations={
        'funding.html':'red_animations_20261027_v9/1.1_在研项目批准经费_人大红.html',
        'outputs.html':'seven_layer_patent_20261027_v1/2.1_七大层_论文与专利年度动画.html',
        'funding-terms.html':'keyword_tiles_20261027_v2/1.1_70技术点投入演进.html',
        'output-terms.html':'patent_terms_reclassified_20261027_v2/2.1_论文与专利_专利逐年播放.html',
        'curves.html':'patent_terms_reclassified_20261027_v1/七大技术方向_投入与产出曲线_专利重分类.html',
    }
    for name,relative in animations.items():
        src=ROOT/'data/outputs/shared/innovation_research'/relative
        shutil.copy2(src,OUT/name)
        h=hashlib.sha256(src.read_bytes()).hexdigest()
        assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==h
        SOURCES.append(dict(path=str(src.relative_to(ROOT)),sha256=h,asset=name))
    # Provenance is retained outside the public asset directory.
    manifest=OUT.parents[2]/'analysis_v1_sources.json'
    manifest.write_text(json.dumps({'version':payload['version'],'sources':SOURCES,'checks':{
        'continuity_edges':286,'continuity_people':278,'projects':242,'papers':2971,
        'milestones':len(payload['landscape']['events']),'animations':len(animations),
        'original_animation_bytes_unchanged':True}},ensure_ascii=False,indent=2))
    print(json.dumps({'output':str(OUT),'payload_bytes':(OUT/'research.json').stat().st_size,'checks':'passed'},ensure_ascii=False))

if __name__=='__main__':
    main()
