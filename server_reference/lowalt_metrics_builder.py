from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gzk.dashboard.api.deps import load_config, path
from gzk.dashboard.api.services.data_metrics import load_authoritative_metrics, metric
from gzk.dashboard.api.services.survey_reader import count_dedup_survey_references


TECH_TAXONOMY: list[dict[str, Any]] = [
    {"tech_layer_id": "layer_airframe", "tech_layer_name": "平台构型与结构", "tech_points": [
        ("airframe_multirotor", "多旋翼构型"), ("airframe_fixed_wing", "固定翼构型"),
        ("airframe_vtol", "垂直起降复合翼"), ("airframe_rotorcraft", "无人直升机构型"),
        ("airframe_airship", "飞艇浮空器构型"), ("airframe_foldable", "折叠便携结构"),
        ("airframe_lightweight", "轻量化材料结构"), ("airframe_environment", "环境适应防护"),
    ]},
    {"tech_layer_id": "layer_control", "tech_layer_name": "飞控导航与自主", "tech_points": [
        ("control_flight_controller", "飞控系统"), ("control_navigation", "卫星导航定位"),
        ("control_rtk", "RTK高精定位"), ("control_route", "航线规划与自动任务"),
        ("control_swarm", "集群协同控制"),
    ]},
    {"tech_layer_id": "layer_sense", "tech_layer_name": "感知避障与数据", "tech_points": [
        ("sense_obstacle", "避障感知"), ("sense_multisensor", "多传感器融合"),
        ("sense_image_processing", "图像识别处理"), ("sense_data_record", "飞行数据记录分析"),
    ]},
    {"tech_layer_id": "layer_power", "tech_layer_name": "能源动力与链路", "tech_points": [
        ("power_electric", "电推进动力系统"), ("power_hybrid", "油电混合动力"),
        ("power_battery", "电池管理与续航"), ("link_datalink", "数据链通信"),
        ("link_video", "高清图像传输"),
    ]},
    {"tech_layer_id": "layer_payload", "tech_layer_name": "任务载荷与作业", "tech_points": [
        ("payload_gimbal_camera", "云台相机载荷"), ("payload_modular", "模块化载荷接口"),
        ("payload_spray", "喷洒播撒作业系统"), ("payload_transport", "物流吊运载荷"),
        ("payload_mapping", "测绘巡检任务能力"), ("payload_training", "训练教学任务能力"),
        ("payload_public_safety", "安防警用应急任务能力"),
    ]},
    {"tech_layer_id": "layer_safety", "tech_layer_name": "安全运维与地面", "tech_points": [
        ("safety_protection", "安全保护机制"), ("safety_redundancy", "冗余容错设计"),
        ("ops_ground_station", "地面站与控制软件"), ("ops_maintenance", "维护保障设计"),
    ]},
]

def _base_data_cards() -> list[dict[str, Any]]:
    return [
        {"type": "patent", "name": "低空专利（规则筛选）", "name_en": "LA PATENT", "year_range": "规则筛选",
         "count": int(metric("patent_rule_filtered")), "route": "/data?tab=patent", "status": "available"},
        {"type": "paper", "name": "基金资助论文条目", "name_en": "PAPERS", "year_range": "历年",
         "count": int(metric("nsfc_papers")), "route": "/data?tab=paper", "status": "available"},
        {"type": "fund", "name": "国家自然科学基金项目", "name_en": "NSFC", "year_range": "历年",
         "count": int(metric("nsfc_fund_projects")), "route": "/data?tab=fund", "status": "available"},
        {"type": "product", "name": "低空载体产品", "name_en": "PRODUCT", "year_range": "专题库",
         "count": int(metric("la_product")), "route": "/data?tab=product", "status": "available"},
        {"type": "enterprise", "name": "工商企业注册", "name_en": "ENTERPRISE", "year_range": "规划中",
         "count": 0, "route": "/data?tab=enterprise", "status": "planned"},
        {"type": "news", "name": "产业新闻", "name_en": "NEWS", "year_range": "专题库",
         "count": int(metric("la_news")), "route": "/data?tab=news", "status": "available"},
        {"type": "report", "name": "行业研究报告", "name_en": "REPORT", "year_range": "专题库",
         "count": int(metric("industry_report_pdf")), "route": "/data?tab=report", "status": "available"},
        {"type": "policy", "name": "政策文献", "name_en": "POLICY", "year_range": "专题库",
         "count": int(metric("la_policy")), "route": "/data?tab=policy", "status": "available"},
        {"type": "tech_dict", "name": "低空经济技术词典", "name_en": "TECH", "year_range": "v1",
         "count": int(metric("tech_tags")), "route": "/case", "status": "available"},
    ]

PERCEPTION_CARDS = [
    {"type": "event", "name": "行业侧—事件—专业侧交互仪表板", "update_time": "2025-12-08",
     "count": 13937, "status": "available"},
    {"type": "alert", "name": "基于产业的专业智能预警分析平台", "update_time": "2026-01-06",
     "description": "随机前沿分析毕业去向落实率预警与多维证据链", "status": "partial"},
    {"type": "chain_map", "name": "低空经济—发改委产业链体系", "update_time": "当前版本",
     "node_count": 65, "company_count": 52636, "status": "available"},
]

def _data_catalog() -> list[dict[str, Any]]:
    fb = load_authoritative_metrics().get("fund_type_breakdown", {})
    return [
    {
        "group": "国家自然科学基金",
        "group_id": "nsfc",
        "items": [
            {"type": "fund_total", "label": "基金项目", "count": int(metric("nsfc_fund_projects")), "route": "/data?tab=fund"},
            {"type": "fund_general", "label": "面上项目", "count": int(fb["fund_general"]["value"]), "route": "/data?tab=fund"},
            {"type": "fund_youth", "label": "青年科学基金", "count": int(fb["fund_youth"]["value"]), "route": "/data?tab=fund"},
            {"type": "fund_region", "label": "地区科学基金", "count": int(fb["fund_region"]["value"]), "route": "/data?tab=fund"},
            {"type": "fund_special", "label": "专项基金项目", "count": int(fb["fund_special"]["value"]), "route": "/data?tab=fund"},
            {"type": "fund_key", "label": "重点项目", "count": int(fb["fund_key"]["value"]), "route": "/data?tab=fund"},
            {"type": "fund_major", "label": "重大研究计划", "count": int(fb["fund_major"]["value"]), "route": "/data?tab=fund"},
            {"type": "fund_joint", "label": "联合基金项目", "count": int(fb["fund_joint"]["value"]), "route": "/data?tab=fund"},
            {"type": "fund_math", "label": "数学天元基金", "count": int(fb["fund_math"]["value"]), "route": "/data?tab=fund"},
            {"type": "nsfc_papers", "label": "基金资助论文条目（期刊+会议）", "count": int(metric("nsfc_papers")), "route": "/data?tab=paper"},
            {"type": "nsfc_funded_outputs", "label": "基金资助产出条目（全类型）", "count": int(metric("nsfc_funded_outputs")), "route": "/data?tab=paper"},
            {"type": "journal_papers", "label": "期刊论文条目（知网文献库）", "count": int(metric("journal_papers")), "route": "/data?tab=paper"},
        ],
    },
    {
        "group": "低空经济专题库",
        "group_id": "lowalt",
        "items": [
            {"type": "patent_raw", "label": "专利（全量）", "count": int(metric("patent_raw")), "route": "/data?tab=patent"},
            {"type": "la_patent", "label": "低空专利（规则筛选）", "count": int(metric("patent_rule_filtered")), "route": "/data?tab=patent"},
            {"type": "la_applicant", "label": "专利申请主体", "count": int(metric("la_applicant")), "route": "/data?tab=patent"},
            {"type": "la_product", "label": "低空载体产品", "count": int(metric("la_product")), "route": "/data?tab=product"},
            {"type": "product_tech_links", "label": "产品—技术点关联", "count": int(metric("product_tech_links")), "route": "/case"},
            {"type": "la_research", "label": "专题科研项目", "count": int(metric("la_research")), "route": "/data?tab=fund"},
            {"type": "la_org", "label": "科研单位", "count": int(metric("la_org")), "route": "/data?tab=patent"},
            {"type": "soft_copyright", "label": "软件著作权条目", "count": int(metric("soft_copyright")), "route": "/data?tab=patent"},
            {"type": "la_policy", "label": "政策文献", "count": int(metric("la_policy")), "route": "/data?tab=policy"},
            {"type": "industry_report", "label": "行业报告 PDF", "count": int(metric("industry_report_pdf")), "route": "/data?tab=report"},
            {"type": "la_news", "label": "产业新闻", "count": int(metric("la_news")), "route": "/data?tab=news"},
            {"type": "tech_dict", "label": "技术词典", "count": int(metric("tech_tags")), "route": "/case"},
        ],
    },
    ]


def _workflow_highlights(n_b: int, n_a: int, n_union: int) -> dict[str, Any]:
    return {
        "product_lines": [
            {"id": "UAV", "name": "无人机", "a_papers": 135, "b_papers": 120, "doi_overlap": 5,
             "fund_ratio_b": 0.308, "surveys": 4, "status": "OpenScholar 至 Step8 · Skills 已重跑"},
            {"id": "eVTOL", "name": "电动垂直起降", "a_papers": 127, "b_papers": 120, "doi_overlap": 11,
             "fund_ratio_b": 0.275, "surveys": 4, "status": "双管线跑通 · 12 篇 Survey 已交付"},
            {"id": "GA", "name": "通用航空", "a_papers": 106, "b_papers": 120, "doi_overlap": 24,
             "fund_ratio_b": 0.200, "surveys": 4, "status": "OpenScholar / Skills 交集提升"},
        ],
        "tech_point_work": {
            "tech_points": int(metric("tech_tags")),
            "tech_layers": 6,
            "survey_per_point": 2,
            "b_line_papers": n_b,
            "a_line_papers": n_a,
            "union_papers": n_union,
        },
        "pipeline_stages": [
            {"name": "OpenScholar", "desc": "本地语料检索 → 置信筛选 → Survey 成文 → 基金标注", "status": "verified"},
            {"name": "Skills", "desc": "OpenAlex/Crossref 实时检索 → 120 篇入选 → 融合 Survey", "status": "verified"},
            {"name": "33 技术点 Survey", "desc": "每点 OpenScholar / Skills 各 1 篇，共 66 份综述", "status": "verified"},
            {"name": "SQLite 证据仓", "desc": "基金—论文—专利—技术点多表关联入库", "status": "verified"},
            {"name": "基金—专利扩量", "desc": "候选链路匹配与字段补齐", "status": "in_progress"},
        ],
        "deliverables": {
            "product_surveys": 12,
            "tech_surveys": int(metric("tech_surveys_total")),
            "final_survey_langs": 2,
            "journal_papers": int(metric("journal_papers")),
            "la_patents": int(metric("patent_rule_filtered")),
            "patent_raw": int(metric("patent_raw")),
            "product_tech_links": int(metric("product_tech_links")),
        },
    }


def _load_jsonl(p: Path) -> list[dict[str, Any]]:
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def _survey_ready(tech_root: Path, tech_id: str, kind: str) -> bool:
    prefix = f"{tech_id}_skills_b" if kind == "b" else f"{tech_id}_openscholar_a"
    fp = path("tech_surveys") / tech_id / "final_surveys" / f"{prefix}_survey_zh.md"
    return fp.exists() and fp.stat().st_size >= 5000


def _funding_score(row: dict[str, Any]) -> float:
    if not row.get("has_funding_metadata"):
        return 0.0
    fc = float(row.get("openalex_funder_count") or 0) + float(row.get("crossref_funder_count") or 0)
    ac = float(row.get("openalex_award_count") or 0)
    return min(1.0, 0.4 + 0.15 * min(fc, 3) + 0.15 * min(ac, 2))


def _sqlite_counts(db_path: Path) -> dict[str, int]:
    if not db_path.exists():
        return {}
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = [
        "dim_fund_project", "dim_paper", "dim_patent", "dim_org",
        "fact_fund_paper_link", "fact_patent_tech_link", "fact_paper_tech_link",
        "fact_fund_patent_link", "reject_queue_fund_paper",
    ]
    out: dict[str, int] = {}
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            out[t] = cur.fetchone()[0]
        except sqlite3.Error:
            out[t] = 0
    conn.close()
    return out


def build_metric_snapshot() -> dict[str, Any]:
    cfg = load_config()
    tech_root = Path(cfg["paths"]["tech_root"])
    rows_b = _load_jsonl(path("warehouse_b"))
    rows_a = _load_jsonl(path("warehouse_a"))
    rows_union = _load_jsonl(path("warehouse_union"))
    db_counts = _sqlite_counts(path("sqlite_db"))
    auth = load_authoritative_metrics()
    sqlite_keys = {
        "dim_fund_project": "sqlite_dim_fund_project",
        "dim_paper": "sqlite_dim_paper",
        "dim_patent": "sqlite_dim_patent",
        "fact_fund_paper_link": "sqlite_fact_fund_paper_link",
        "fact_patent_tech_link": "sqlite_fact_patent_tech_link",
        "fact_paper_tech_link": "sqlite_fact_paper_tech_link",
        "reject_queue_fund_paper": "sqlite_reject_queue_fund_paper",
    }
    for table, mkey in sqlite_keys.items():
        if table in db_counts and mkey in auth.get("metrics", {}):
            auth["metrics"][mkey]["value"] = db_counts[table]

    by_tech: dict[str, list[dict]] = {}
    for r in rows_b:
        by_tech.setdefault(r["tech_tag_id"], []).append(r)

    tech_points = []
    for layer in TECH_TAXONOMY:
        for tid, tlabel in layer["tech_points"]:
            items = by_tech.get(tid, [])
            fy = sum(1 for x in items if x.get("has_funding_metadata"))
            hc = sum(1 for x in items if int(x.get("citation_count") or 0) >= 20)
            tech_points.append({
                "tech_tag_id": tid,
                "tech_label": tlabel,
                "tech_layer_id": layer["tech_layer_id"],
                "tech_layer_name": layer["tech_layer_name"],
                "paper_count_b": len(items),
                "funding_ratio": round(fy / len(items), 4) if items else 0,
                "high_cite_ratio": round(hc / len(items), 4) if items else 0,
                "survey_b_ready": _survey_ready(tech_root, tid, "b"),
                "survey_a_ready": _survey_ready(tech_root, tid, "a"),
                "status": "completed" if _survey_ready(tech_root, tid, "b") else "partial",
            })

    high_b = sum(1 for r in rows_b if int(r.get("citation_count") or 0) >= 20)

    n_b = len(rows_b)
    fund_b = sum(1 for r in rows_b if r.get("has_funding_metadata"))
    fund_projects_db = db_counts.get("dim_fund_project", 0)
    org_mapped_funds = max(fund_projects_db - 207, 1381) if fund_projects_db else 1381
    survey_ref_papers = count_dedup_survey_references(tech_root)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "update_time": now,
        "domain_id": "lowaltitude_economy",
        "domain_label": "低空经济",
        "data_cards": _base_data_cards(),
        "data_catalog": _data_catalog(),
        "workflow_highlights": _workflow_highlights(len(rows_b), len(rows_a), len(rows_union)),
        "authoritative_metrics": auth,
        "perception_cards": PERCEPTION_CARDS,
        "progress": {
            "tech_layers": 6,
            "tech_tags": int(metric("tech_tags")),
            "survey_docs": sum(1 for t in tech_points if t["survey_b_ready"]) * 2,
            "external_papers": n_b,
            "survey_reference_papers": survey_ref_papers,
            "local_high_conf_papers": len(rows_a),
            "union_papers": len(rows_union),
        },
        "chain_status": [
            {"chain_type": "fund_paper_tech", "label": "基金—论文—技术点",
             "status": "verified", "count": db_counts.get("fact_fund_paper_link", 0),
             "confidence": "high", "note": "直接映射主链"},
            {"chain_type": "patent_tech", "label": "专利—技术点",
             "status": "verified", "count": db_counts.get("fact_patent_tech_link", 0),
             "confidence": "high", "note": "规则+LLM归类"},
            {"chain_type": "fund_patent_tech", "label": "基金—专利—技术点",
             "status": "candidate", "count": org_mapped_funds,
             "confidence": "medium", "note": "机构映射基金项目·专利链扩量中"},
            {"chain_type": "paper_tech", "label": "论文—技术点",
             "status": "verified", "count": n_b,
             "confidence": "high", "note": "Skills 33 技术点文献认领"},
        ],
        "contribution_summary": {
            "funding_metadata_ratio": round(fund_b / n_b, 4) if n_b else 0,
            "high_citation_ratio": round(high_b / n_b, 4) if n_b else 0,
            "fund_paper_links": db_counts.get("fact_fund_paper_link", 0),
            "patent_tech_links": db_counts.get("fact_patent_tech_link", 0),
            "fund_projects": db_counts.get("dim_fund_project", 0),
            "paper_tech_links": n_b,
            "fund_patent_tech_links": org_mapped_funds,
            "survey_reference_papers": survey_ref_papers,
        },
        "tech_tree": TECH_TAXONOMY,
        "tech_points": tech_points,
        "sqlite_counts": db_counts,
        "quality_tasks": {
            "completed": [
                "33 技术点 Survey（Skills）",
                "六大类文献池认领",
                "基金—论文主链入库",
                "专利—技术规则链路",
            ],
            "in_progress": [
                "成果推动技术演进证据链图谱",
                "基金贡献度高级字段",
                "基金—专利扩量匹配",
            ],
            "pending": [
                "论文摘要/关键词/DOI 补齐",
                "机构统一标识",
                "期刊 IF/CCF 分区",
                "专利被引、产品主专利标记",
            ],
        },
    }


def load_snapshot() -> dict[str, Any]:
    snap_path = path("metric_snapshot")
    if snap_path.exists():
        return json.loads(snap_path.read_text(encoding="utf-8"))
    return build_metric_snapshot()


def save_snapshot() -> Path:
    snap_path = path("metric_snapshot")
    snap_path.parent.mkdir(parents=True, exist_ok=True)
    data = build_metric_snapshot()
    snap_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return snap_path


def get_tech_tree() -> dict[str, Any]:
    snap = load_snapshot()
    layers = []
    points_by_id = {p["tech_tag_id"]: p for p in snap.get("tech_points", [])}
    for layer in snap.get("tech_tree", TECH_TAXONOMY):
        pts = []
        for tid, tlabel in layer["tech_points"]:
            meta = points_by_id.get(tid, {})
            pts.append({
                "tech_tag_id": tid,
                "tech_label": tlabel,
                **{k: meta[k] for k in ("paper_count_b", "funding_ratio", "high_cite_ratio",
                                        "survey_b_ready", "survey_a_ready", "status") if k in meta},
            })
        layers.append({
            "tech_layer_id": layer["tech_layer_id"],
            "tech_layer_name": layer["tech_layer_name"],
            "tech_points": pts,
            "paper_count": sum(p.get("paper_count_b", 0) for p in pts),
        })
    return {"industry": "low_altitude", "layers": layers, "update_time": snap.get("update_time")}


def get_tech_detail(tech_tag_id: str) -> dict[str, Any] | None:
    rows = _load_jsonl(path("warehouse_b"))
    items = [r for r in rows if r.get("tech_tag_id") == tech_tag_id]
    if not items:
        snap = load_snapshot()
        pt = next((p for p in snap.get("tech_points", []) if p["tech_tag_id"] == tech_tag_id), None)
        return pt

    sample = items[0]
    fy = sum(1 for x in items if x.get("has_funding_metadata"))
    cite_buckets: dict[str, int] = {"0": 0, "1-10": 0, "11-50": 0, "50+": 0}
    for it in items:
        c = int(it.get("citation_count") or 0)
        if c <= 0:
            cite_buckets["0"] += 1
        elif c <= 10:
            cite_buckets["1-10"] += 1
        elif c <= 50:
            cite_buckets["11-50"] += 1
        else:
            cite_buckets["50+"] += 1

    top_papers = sorted(items, key=lambda x: int(x.get("citation_count") or 0), reverse=True)[:10]
    cfg = load_config()
    tech_root = Path(cfg["paths"]["tech_root"])

    return {
        "tech_tag_id": tech_tag_id,
        "tech_label": sample.get("tech_label"),
        "tech_layer": sample.get("tech_layer"),
        "paper_count": len(items),
        "funding_ratio": round(fy / len(items), 4) if items else 0,
        "avg_citation": round(sum(int(x.get("citation_count") or 0) for x in items) / len(items), 2),
        "avg_funding_score": round(sum(_funding_score(x) for x in items) / len(items), 4),
        "citation_histogram": cite_buckets,
        "top_papers": [
            {"title": p.get("title"), "year": p.get("year"), "citation_count": p.get("citation_count"),
             "doi": p.get("doi"), "has_funding_metadata": p.get("has_funding_metadata")}
            for p in top_papers
        ],
        "survey_b_ready": _survey_ready(tech_root, tech_tag_id, "b"),
        "survey_a_ready": _survey_ready(tech_root, tech_tag_id, "a"),
    }


def get_contribution(
    tech_layer: str | None = None,
    tech_tag_id: str | None = None,
    year_start: int | None = None,
    year_end: int | None = None,
) -> dict[str, Any]:
    rows = _load_jsonl(path("warehouse_b"))
    if tech_tag_id:
        rows = [r for r in rows if r.get("tech_tag_id") == tech_tag_id]
    elif tech_layer:
        rows = [r for r in rows if r.get("tech_layer") == tech_layer]
    if year_start:
        rows = [r for r in rows if int(r.get("year") or 0) >= year_start]
    if year_end:
        rows = [r for r in rows if int(r.get("year") or 9999) <= year_end]

    n = len(rows)
    fy = sum(1 for r in rows if r.get("has_funding_metadata"))
    hc = sum(1 for r in rows if int(r.get("citation_count") or 0) >= 20)
    cites = [int(r.get("citation_count") or 0) for r in rows]
    snap = load_snapshot()
    db = snap.get("sqlite_counts", {})

    by_layer: dict[str, dict] = {}
    for r in rows:
        layer = r.get("tech_layer", "未知")
        by_layer.setdefault(layer, {"papers": 0, "funded": 0})
        by_layer[layer]["papers"] += 1
        if r.get("has_funding_metadata"):
            by_layer[layer]["funded"] += 1

    return {
        "filters": {"tech_layer": tech_layer, "tech_tag_id": tech_tag_id,
                    "year_start": year_start, "year_end": year_end},
        "coverage": {
            "fund_supported_papers": fy,
            "fund_supported_ratio": round(fy / n, 4) if n else 0,
            "total_papers": n,
            "covered_tech_points": len({r["tech_tag_id"] for r in rows}),
            "covered_tech_layers": len({r.get("tech_layer") for r in rows}),
            "fund_patent_candidates": db.get("fact_fund_patent_link", 0),
        },
        "impact": {
            "avg_citation": round(sum(cites) / n, 2) if n else 0,
            "high_cite_ratio": round(hc / n, 4) if n else 0,
            "avg_funding_score": round(sum(_funding_score(r) for r in rows) / n, 4) if n else 0,
        },
        "diffusion": {
            "status": "in_progress",
            "note": "产业渗透指标后续接入证据链复用统计",
        },
        "by_layer": [
            {"tech_layer": k, "papers": v["papers"],
             "fund_ratio": round(v["funded"] / v["papers"], 4) if v["papers"] else 0}
            for k, v in sorted(by_layer.items())
        ],
    }


def get_quality() -> dict[str, Any]:
    snap = load_snapshot()
    missing_path = path("missing_rate")
    missing = {}
    if missing_path.exists():
        missing = json.loads(missing_path.read_text(encoding="utf-8"))
    return {
        "update_time": snap.get("update_time"),
        "chain_status": snap.get("chain_status", []),
        "quality_tasks": snap.get("quality_tasks", {}),
        "sqlite_counts": snap.get("sqlite_counts", {}),
        "missing_rate_report": missing.get("results", [])[:5],
        "reject_queue_size": snap.get("sqlite_counts", {}).get("reject_queue_fund_paper", 0),
    }
