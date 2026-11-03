"""Build the AI chain presentation from accepted snapshots; no database writes.

Run: python manage.py run dashboard/cursor_ui/scripts/build_ai_chain.py
"""
from collections import Counter, defaultdict
from pathlib import Path
import csv
import hashlib
import json
import shutil
from gzk.paths import ROOT

OUT = ROOT / 'data/outputs/shared/ui_handoff/cursor_20260924/analysis_public/chain-analysis/v1'
BASE = ROOT / 'data/runs/llm/innovation'
HANDOFF = ROOT / 'data/outputs/shared/innovation_research/claude_research_design_handoff_20261103_v1/Claude_研究力量展示设计交接包'
SOURCES = []

def _record(path, content):
    try:
        shown = str(path.relative_to(ROOT))
    except ValueError:
        shown = str(path)
    SOURCES.append({'path': shown, 'sha256': hashlib.sha256(content).hexdigest()})

def read(path):
    content = path.read_bytes()
    _record(path, content)
    return json.loads(content)

def table(path):
    """Read one handoff CSV (UTF-8 with BOM) and record its hash."""
    content = path.read_bytes()
    _record(path, content)
    return list(csv.DictReader(content.decode('utf-8-sig').splitlines()))

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

# ---------------------------------------------------------------------------
# Research landscape: curated public milestones (not part of the NSFC database).
# Each event keeps its month so the page can place it precisely; `open` marks
# open-source code or open weights at release; `key` marks a landmark result.
# ---------------------------------------------------------------------------
LANDSCAPE_GROUPS = [
    ('cn-inst', '中国 · 科研机构与高校', 'cn', [
        ('casia', '中科院自动化所', '科研机构', 2017, None, '中国科学院自动化研究所'),
        ('pcl', '鹏城实验室', '国家实验室', 2018.3, None, '鹏城国家实验室'),
        ('baai', '智源 · 上海 AI 实验室', '新型研发机构', 2018.8, None, None),
        ('tsinghua', '清华大学', '高校', 2017, None, '清华大学'),
    ]),
    ('cn-firm', '中国 · 企业', 'cn', [
        ('zhipu', '智谱 AI', '2019 年成立 · 清华衍生', 2019.5, None, None),
        ('modelbest', '面壁智能', '2022 年成立 · 清华衍生', 2022.6, None, None),
        ('moonshot', '月之暗面', '2023 年成立', 2023.3, None, None),
        ('qwen', '阿里巴巴', '达摩院 · 通义实验室', 2017, None, None),
        ('baidu', '百度', '文心大模型', 2017, None, None),
        ('bytedance', '字节跳动', 'Seed 团队', 2017, None, None),
        ('deepseek', 'DeepSeek', '2023 年成立 · 源自幻方量化', 2023.5, None, None),
    ]),
    ('intl-firm', '国际 · 企业', 'intl', [
        ('brain', 'Google Brain', '2023 年并入 Google DeepMind', 2017, 2023.25, None),
        ('deepmind', 'Google DeepMind', '原 DeepMind', 2017, None, None),
        ('openai', 'OpenAI', '2015 年成立', 2017, None, None),
        ('anthropic', 'Anthropic', '2021 年成立', 2021.3, None, None),
        ('meta', 'Meta AI', 'FAIR · 超级智能实验室', 2017, None, None),
        ('msr', '微软研究院', '含微软亚洲研究院', 2017, None, None),
        ('mistral', 'Mistral AI', '2023 年成立 · 法国', 2023.3, None, None),
    ]),
    ('intl-univ', '国际 · 高校', 'intl', [
        ('univ', '斯坦福 · 伯克利', '高校', 2017, None, None),
    ]),
]

# (org, year, month, label, description, open, key, url)
LANDSCAPE_EVENTS = [
    ('casia', 2021, 7, '紫东太初', '图文音三模态预训练大模型。', 0, 0, ''),
    ('pcl', 2021, 4, '鹏程·盘古α', '与华为等联合发布的 2000 亿参数中文预训练模型，开放权重。', 1, 0, 'https://arxiv.org/abs/2104.12369'),
    ('pcl', 2021, 12, '文心·鹏城', '与百度联合发布 ERNIE 3.0 Titan，2600 亿参数。', 0, 0, 'https://arxiv.org/abs/2112.12731'),
    ('baai', 2021, 6, '悟道 2.0', '智源研究院发布的 1.75 万亿参数模型。', 0, 0, ''),
    ('baai', 2023, 6, '书生·浦语', '上海 AI 实验室、商汤及多所高校联合发布大语言模型，开源。', 1, 0, 'https://www.shlab.org.cn/news/5443407'),
    ('baai', 2024, 10, 'Emu3', '智源研究院原生多模态模型，开源。', 1, 0, 'https://arxiv.org/abs/2409.18869'),
    ('tsinghua', 2021, 3, 'GLM', '自回归空白填充预训练，连接语言理解与生成任务。', 1, 0, 'https://arxiv.org/abs/2103.10360'),
    ('tsinghua', 2022, 8, 'GLM-130B', '清华与智谱共同研究的千亿参数双语预训练模型，开源。', 1, 1, 'https://arxiv.org/abs/2210.02414'),
    ('zhipu', 2023, 3, 'ChatGLM', '沿 GLM 模型系列推进双语对话模型，ChatGLM-6B 开源。', 1, 0, 'https://github.com/THUDM/ChatGLM-6B'),
    ('zhipu', 2024, 1, 'GLM-4', '模型系列扩展到工具使用和多类任务。', 0, 0, 'https://arxiv.org/abs/2406.12793'),
    ('zhipu', 2025, 7, 'GLM-4.5', 'GLM-4.5 系列开放权重。', 1, 0, 'https://arxiv.org/abs/2508.06471'),
    ('modelbest', 2024, 2, 'MiniCPM', '端侧小规模语言模型，开源。', 1, 0, 'https://arxiv.org/abs/2404.06395'),
    ('moonshot', 2023, 10, 'Kimi', '长上下文对话助手。', 0, 0, ''),
    ('moonshot', 2025, 1, 'Kimi k1.5', '多模态推理模型。', 0, 0, 'https://arxiv.org/abs/2501.12599'),
    ('moonshot', 2025, 7, 'Kimi K2', '万亿参数混合专家模型，开放权重。', 1, 0, 'https://arxiv.org/abs/2507.20534'),
    ('qwen', 2021, 3, 'M6', '达摩院多模态预训练模型。', 0, 0, 'https://arxiv.org/abs/2103.00823'),
    ('qwen', 2023, 4, '通义千问', '2023 年 4 月发布，8 月起开源 Qwen 系列。', 1, 0, ''),
    ('qwen', 2024, 9, 'Qwen2.5', 'Qwen2.5 系列开源。', 1, 0, ''),
    ('qwen', 2025, 4, 'Qwen3', '模型系列推进推理与非推理模式的统一，开源。', 1, 0, 'https://arxiv.org/abs/2505.09388'),
    ('qwen', 2026, 2, 'Qwen3.5', 'Qwen3.5 开放权重。', 1, 0, ''),
    ('baidu', 2019, 3, 'ERNIE', '知识增强预训练模型，开源。', 1, 0, 'https://arxiv.org/abs/1904.09223'),
    ('baidu', 2023, 3, '文心一言', '对话式大模型。', 0, 0, ''),
    ('baidu', 2025, 6, '文心 4.5', '文心 4.5 系列开放权重。', 1, 0, ''),
    ('bytedance', 2024, 5, '豆包', '豆包大模型发布。', 0, 0, ''),
    ('bytedance', 2025, 1, '豆包 1.5', '豆包 1.5 Pro 发布。', 0, 0, ''),
    ('deepseek', 2023, 11, 'DeepSeek LLM', '首个开源大语言模型。', 1, 0, 'https://arxiv.org/abs/2401.02954'),
    ('deepseek', 2024, 5, 'DeepSeek-V2', '以混合专家和多头潜在注意力探索更高效的训练与推理，开源。', 1, 0, 'https://arxiv.org/abs/2405.04434'),
    ('deepseek', 2025, 1, 'DeepSeek-R1', '通过强化学习推进推理能力，开源（基于 2024 年 12 月发布的 V3）。', 1, 1, 'https://arxiv.org/abs/2501.12948'),
    ('deepseek', 2026, 4, 'DeepSeek-V4', 'V4 开放权重，支持百万级上下文。', 1, 0, ''),
    ('brain', 2017, 6, 'Transformer', '以注意力机制构建序列转换架构，成为后续预训练模型的通用基础。', 1, 1, 'https://arxiv.org/abs/1706.03762'),
    ('brain', 2018, 10, 'BERT', '双向预训练与任务微调结合，推进通用语言表示，开源。', 1, 0, 'https://arxiv.org/abs/1810.04805'),
    ('brain', 2019, 10, 'T5', '统一的“文本到文本”预训练框架，开源。', 1, 0, 'https://arxiv.org/abs/1910.10683'),
    ('brain', 2022, 4, 'PaLM', '5400 亿参数语言模型。', 0, 0, 'https://arxiv.org/abs/2204.02311'),
    ('deepmind', 2017, 10, 'AlphaGo Zero', '无需人类棋谱，仅靠自我对弈达到超人水平。', 0, 0, 'https://doi.org/10.1038/nature24270'),
    ('deepmind', 2018, 12, 'AlphaFold', '蛋白质结构预测（CASP13）。', 0, 0, ''),
    ('deepmind', 2020, 11, 'AlphaFold 2', '蛋白质结构预测接近实验精度，2021 年开源。', 1, 1, 'https://doi.org/10.1038/s41586-021-03819-2'),
    ('deepmind', 2023, 12, 'Gemini', '原生多模态模型系列。', 0, 0, 'https://arxiv.org/abs/2312.11805'),
    ('deepmind', 2024, 10, '诺贝尔化学奖', 'AlphaFold 相关工作获 2024 年诺贝尔化学奖；同年发布 AlphaFold 3。', 0, 1, 'https://www.nobelprize.org/prizes/chemistry/2024/summary/'),
    ('deepmind', 2025, 11, 'Gemini 3', 'Gemini 3 系列发布。', 0, 0, ''),
    ('deepmind', 2026, 5, 'Gemini 3.5', 'Gemini 3.5 Flash 发布。', 0, 0, ''),
    ('openai', 2018, 6, 'GPT', '生成式预训练与监督微调结合，开源代码。', 1, 0, 'https://openai.com/index/language-unsupervised/'),
    ('openai', 2019, 2, 'GPT-2', '15 亿参数语言模型，2019 年 11 月完整开放。', 1, 0, ''),
    ('openai', 2020, 5, 'GPT-3', '1750 亿参数，少样本学习。', 0, 0, 'https://arxiv.org/abs/2005.14165'),
    ('openai', 2021, 1, 'CLIP', '图文对比预训练，开放权重；同期发布 DALL·E。', 1, 0, 'https://arxiv.org/abs/2103.00020'),
    ('openai', 2022, 11, 'ChatGPT', '通过对话交互和人类反馈训练，推动大语言模型进入广泛使用。', 0, 1, 'https://openai.com/index/chatgpt/'),
    ('openai', 2023, 3, 'GPT-4', '扩展多模态输入与复杂任务能力。', 0, 0, 'https://openai.com/index/gpt-4-research/'),
    ('openai', 2024, 9, 'o1', '推理模型。', 0, 0, ''),
    ('openai', 2025, 8, 'GPT-5', 'GPT-5 发布；同月发布开放权重模型 gpt-oss。', 0, 0, ''),
    ('openai', 2026, 4, 'GPT-5.5', 'GPT-5.5 发布。', 0, 0, ''),
    ('anthropic', 2022, 12, '宪法 AI', '以一组原则约束模型的 AI 反馈对齐方法。', 0, 0, 'https://arxiv.org/abs/2212.08073'),
    ('anthropic', 2023, 3, 'Claude', '围绕有用、诚实和无害的目标推进对话模型。', 0, 0, 'https://www.anthropic.com/news/introducing-claude'),
    ('anthropic', 2024, 3, 'Claude 3', '推出不同能力与成本取向的模型系列。', 0, 0, 'https://www.anthropic.com/news/claude-3-family'),
    ('anthropic', 2025, 5, 'Claude 4', 'Claude 4 系列。', 0, 0, ''),
    ('anthropic', 2026, 7, 'Claude 5', 'Claude 5 系列。', 0, 0, ''),
    ('meta', 2018, 12, 'PyTorch 1.0', '深度学习框架正式版，开源。', 1, 0, ''),
    ('meta', 2023, 2, 'LLaMA', '开放权重基础语言模型，带动开源生态。', 1, 1, 'https://arxiv.org/abs/2302.13971'),
    ('meta', 2024, 4, 'Llama 3', 'Llama 3 系列，开放权重。', 1, 0, 'https://arxiv.org/abs/2407.21783'),
    ('meta', 2025, 6, '超级智能实验室', '组建超级智能实验室，大规模引进人才。', 0, 0, ''),
    ('msr', 2020, 2, 'Turing-NLG', '170 亿参数语言模型。', 0, 0, ''),
    ('msr', 2021, 3, 'Swin Transformer', '微软亚洲研究院视觉 Transformer，获 ICCV 2021 最佳论文。', 1, 0, 'https://arxiv.org/abs/2103.14030'),
    ('msr', 2024, 4, 'Phi-3', '小规模高性能语言模型，开放权重。', 1, 0, 'https://arxiv.org/abs/2404.14219'),
    ('mistral', 2023, 10, 'Mistral 7B', 'Mistral 7B（2023.9）与 Mixtral 8×7B 混合专家模型（2023.12），开放权重。', 1, 0, 'https://arxiv.org/abs/2310.06825'),
    ('mistral', 2024, 2, 'Mistral Large', '闭源旗舰模型。', 0, 0, ''),
    ('univ', 2020, 3, 'NeRF', '伯克利等提出神经辐射场，开源。', 1, 0, 'https://arxiv.org/abs/2003.08934'),
    ('univ', 2021, 8, '基础模型报告', '斯坦福提出“基础模型”概念。', 0, 0, 'https://arxiv.org/abs/2108.07258'),
    ('univ', 2022, 5, 'FlashAttention', '围绕显存读写重新组织注意力计算，提升执行效率，开源。', 1, 0, 'https://arxiv.org/abs/2205.14135'),
    ('univ', 2023, 6, 'vLLM', '用 PagedAttention 改进大语言模型服务中的显存管理，开源。', 1, 0, 'https://arxiv.org/abs/2309.06180'),
]

# (source, target, fractional year, label, kind, description, url)
LANDSCAPE_FLOWS = [
    ('tsinghua', 'zhipu', 2019.5, '清华 KEG 实验室成果转化', 'spin', '清华大学计算机系公开材料记载：知识工程实验室于 2019 年转化了智谱 AI。', 'https://www.cs.tsinghua.edu.cn/info/1088/4451.htm'),
    ('tsinghua', 'modelbest', 2022.6, '清华 NLP 实验室衍生', 'spin', '面壁智能由清华大学自然语言处理实验室团队创立。', ''),
    ('tsinghua', 'moonshot', 2023.3, '清华校友创立', 'spin', '月之暗面由清华大学校友创立。', ''),
    ('brain', 'deepmind', 2023.3, '并入', 'merge', 'Google 于 2023 年宣布将 DeepMind 与 Google Research 的 Brain 团队合并为 Google DeepMind。', 'https://deepmind.google/blog/announcing-google-deepmind/'),
    ('openai', 'anthropic', 2021.3, '前 OpenAI 成员创立', 'spin', 'Anthropic 由前 OpenAI 成员于 2021 年创立。', ''),
]
LANDSCAPE_NOTES = [
    ('brain', 2023.75, 'OpenAI 人才外溢：Anthropic · SSI · Thinking Machines'),
    ('mistral', 2023.3, '前 DeepMind、Meta 研究者创立'),
    ('deepseek', 2023.5, '源自幻方量化'),
]
LANDSCAPE_ERAS = [
    (2017, 2020, '架构与预训练', 'Transformer 统一架构，预训练成为范式'),
    (2020, 2023, '规模化与对齐', '参数规模跃升，人类反馈进入训练'),
    (2023, 2025, '产品化与开源', '对话产品普及，开放权重模型全面跟进'),
    (2025, 2027, '推理与开放竞争', '推理模型兴起，中外开放模型同台竞争'),
]

def landscape(project_counts):
    groups = []
    for gid, label, region, lanes in LANDSCAPE_GROUPS:
        rows = []
        for lid, name, note, start, end, nsfc in lanes:
            row = dict(id=lid, name=name, note=note, start=start, end=end)
            if nsfc and project_counts.get(nsfc):
                row['nsfc'] = dict(name=nsfc, projects=project_counts[nsfc])
            rows.append(row)
        groups.append(dict(id=gid, label=label, region=region, lanes=rows))
    return {
        'range': [2017, 2026], 'checkedAt': '2026-11-03',
        'scope': '公开资料整理的代表性里程碑，不属于 NSFC 数据库统计；“NSFC 数据内”项目数为 2017—2021 年 AI 项目承担数。',
        'groups': groups,
        'eras': [dict(start=a, end=b, label=c, description=d) for a, b, c, d in LANDSCAPE_ERAS],
        'events': [dict(id=f'event-{i}', org=o, year=y, month=m, label=l, description=d, open=bool(op), key=bool(k), url=u)
                   for i, (o, y, m, l, d, op, k, u) in enumerate(LANDSCAPE_EVENTS)],
        'connections': [dict(id=f'{s}-{t}', source=s, target=t, year=y, label=l, kind=k, description=d, url=u)
                        for s, t, y, l, k, d, u in LANDSCAPE_FLOWS],
        'notes': [dict(org=o, year=y, text=t) for o, y, t in LANDSCAPE_NOTES],
    }

# Representative continuity cases for the 负责人接续 page. Years, project types and
# institutions are joined from the verified continuity records by person name and
# approval years; the topic phrases condense the two project titles.
CONTINUITY_CASES = [
    ('青年 → 面上', '李晓旭', 2019, 2021, '小样本图像分类', '融合迁移与度量学习'),
    ('青年 → 面上', '鄂海红', 2019, 2021, '医学知识图谱融合补全', '认知图谱复杂结构表示'),
    ('青年 → 面上', '缪小冬', 2019, 2021, '多模态动态目标检测', '工业装备剩余寿命预测'),
    ('面上 → 联合·重点等', '黄民烈', 2018, 2019, '开放领域人机对话', '对话交互基础理论'),
    ('面上 → 联合·重点等', '刘峤', 2017, 2019, '知识图谱关系推理', '认知推理知识图谱构建'),
    ('连续三期', '曹刘娟', 2017, 2020, '遥感小目标检测', '弱监督小目标检测'),
    ('连续三期', '曹刘娟', 2020, 2021, '弱监督小目标检测', '边缘部署检测跟踪'),
]

def strength(handoff=None):
    """Aggregates behind 数据底座 / 机构参与, recomputed from the handoff tables."""
    d = (handoff or HANDOFF) / '数据表'
    metrics = [dict(label=r['label'], value=int(r['value']), unit=r['unit'], scope=r['scope'])
               for r in table(d / '01_首页七项数据.csv')]
    annual = []
    for r in table(d / '02_基金年度支持概览.csv'):
        if r['approval_year'] and 2017 <= int(r['approval_year']) <= 2021:
            annual.append(dict(year=int(r['approval_year']), projects=int(r['projects']),
                               amount_yi=float(r['amount_yi']), institutions=int(r['host_orgs']),
                               top10_amount_pct=float(r['top10_amount_pct'])))
    org_years = defaultdict(dict)
    names = {}
    for r in table(d / '04_全部机构年度项目.csv'):
        org_years[r['organization_id']][int(r['approval_year'])] = int(r['projects'])
        names[r['organization_id']] = r['canonical_name']
    base = {o for o, ys in org_years.items() if 2017 in ys}
    split = []
    for y in range(2017, 2022):
        active = [o for o, ys in org_years.items() if y in ys]
        kept = [o for o in active if o in base]
        new = [o for o in active if o not in base]
        split.append(dict(year=y, retained_institutions=len(kept), entered_institutions=len(new),
                          retained_projects=sum(org_years[o][y] for o in kept),
                          entered_projects=sum(org_years[o][y] for o in new)))
    project_counts = Counter()
    for o, ys in org_years.items():
        project_counts[names[o]] += sum(ys.values())
    footprint = defaultdict(lambda: {'first': None, 'years': set()})
    for r in table(d / '05_168机构后续成果足迹.csv'):
        f = footprint[r['organization_id']]
        f['first'] = int(r['first_observed_approval_year'])
        if r['publication_year'] and int(r['papers'] or 0) > 0:
            f['years'].add(int(r['publication_year']))
    dist = Counter(len(f['years']) for f in footprint.values())
    cohort = dict(
        institutions=len(footprint),
        with_any=sum(1 for f in footprint.values() if f['years']),
        at_least_two=sum(1 for f in footprint.values() if len(f['years']) >= 2),
        all_four=sum(1 for f in footprint.values() if len(f['years']) == 4),
        year_count_distribution=[dict(years=k, institutions=dist[k]) for k in range(5)],
        window=[2022, 2025], entry_years=[2018, 2021])
    summary = table(d / '03_2021机构支持构成.csv')
    return dict(
        metrics=metrics, annual=annual, split=split, cohort=cohort,
        scope=dict(projects=sum(r['projects'] for r in annual), institutions=len(org_years),
                   years=[2017, 2021]),
        retained_2021=[dict(present_2017=r['present_2017'] == 'True', institutions=int(r['orgs']),
                            projects=int(r['projects']), amount_yi=float(r['amount_yi'])) for r in summary],
        cases=[dict(group=g, person_name=n, earlier_year=a, later_year=b, earlier_topic=t1, later_topic=t2)
               for g, n, a, b, t1, t2 in CONTINUITY_CASES],
    ), project_counts

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
    strength_data, project_counts = strength()
    assert strength_data['scope']['projects']==7032 and strength_data['scope']['institutions']==727
    assert strength_data['cohort']['institutions']==168
    payload=public(dict(version='ai-chain-20261103-v2',graph=graph,continuity=continuity,
                       focus=focus,branches=branches,caseDetail=detail,landscape=landscape(project_counts),
                       strength=strength_data,
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
        'strength_scope_projects':7032,'strength_scope_institutions':727,'entry_cohort':168,
        'original_animation_bytes_unchanged':True}},ensure_ascii=False,indent=2))
    print(json.dumps({'output':str(OUT),'payload_bytes':(OUT/'research.json').stat().st_size,'checks':'passed'},ensure_ascii=False))

if __name__=='__main__':
    main()
