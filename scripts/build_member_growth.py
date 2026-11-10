"""项目参与人成长为项目负责人：从基金中心关联库生成 member-growth.json。

用法（在有关联库的服务器上）：
  python scripts/build_member_growth.py \
    --db /root/gzk_jc/data/warehouse/shared/innovation/releases/innovation_relations_20261102_v1/relations.duckdb \
    --out snapshot/public/chain-analysis/v1/member-growth.json

口径：同一 person_id 先以非负责人角色出现在项目 A，之后（批准年份更晚）以 principal_investigator 出现在项目 B；
每人取最早一次“参与→负责”转变作为代表；后续项目限定为 AI 基金范围（project_scope），与研究团队其他板块一致。
身份依据保留 identity_basis，默认只用稳定 ID 与姓名+机构匹配。
"""
import argparse, json, datetime
import duckdb

ap = argparse.ArgumentParser()
ap.add_argument('--db', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--bases', default='nsfc_source_person_id,name_organization')
args = ap.parse_args()
bases = [b.strip() for b in args.bases.split(',') if b.strip()]
con = duckdb.connect(args.db, read_only=True)
q = lambda sql, *p: con.execute(sql, list(p)).fetchall()

print('role values:', q("SELECT role,count(*) FROM project_person GROUP BY 1 ORDER BY 2 DESC"))

con.execute(f"""
CREATE TEMP TABLE pp AS
SELECT DISTINCT p.person_id, p.project_id, p.role, p.identity_basis, p.original_institution_name inst,
       d.approval_year yr, d.project_type, d.title, d.grant_no, d.institution, d.principal_investigator pi_name, d.amount_raw, d.amount_unit
FROM project_person p JOIN project_detail_summary d USING(project_id)
WHERE d.approval_year IS NOT NULL AND p.identity_basis IN ({','.join('?'*len(bases))})
""", bases)
con.execute("""
CREATE TEMP TABLE growth AS
SELECT a.person_id, a.project_id early_id, a.yr early_year, a.project_type early_type, a.title early_title, a.grant_no early_grant,
       a.institution early_inst, a.pi_name early_pi, a.role early_role,
       b.project_id later_id, b.yr later_year, b.project_type later_type, b.title later_title, b.grant_no later_grant,
       b.institution later_inst, b.amount_raw later_amount, b.amount_unit later_unit, b.identity_basis,
       b.yr-a.yr gap,
       row_number() OVER (PARTITION BY a.person_id ORDER BY b.yr, a.yr DESC, b.project_id) rn
FROM pp a JOIN pp b ON a.person_id=b.person_id AND b.yr>a.yr
WHERE a.role<>'principal_investigator' AND b.role='principal_investigator'
  AND b.project_id IN (SELECT project_id FROM project_scope)
""")
con.execute("CREATE TEMP TABLE first_growth AS SELECT * FROM growth WHERE rn=1")
names = dict(q("SELECT person_id, display_name FROM person WHERE person_id IN (SELECT person_id FROM first_growth)"))

total = q("SELECT count(*) FROM first_growth")[0][0]
participants = q("""SELECT count(DISTINCT person_id) FROM pp WHERE role<>'principal_investigator'
                    AND project_id IN (SELECT project_id FROM project_scope)""")[0][0]
summary = {
  'people': total,
  'ai_participants': participants,
  'same_institution': q("SELECT count(*) FROM first_growth WHERE early_inst=later_inst")[0][0],
  'median_gap': q("SELECT median(gap) FROM first_growth")[0][0],
  'gap_dist': [{'gap': g, 'people': n} for g, n in q("SELECT least(gap,10),count(*) FROM first_growth GROUP BY 1 ORDER BY 1")],
  'by_later_year': [{'year': y, 'people': n} for y, n in q("SELECT later_year,count(*) FROM first_growth GROUP BY 1 ORDER BY 1")],
  'later_types': [{'type': t, 'people': n} for t, n in q("SELECT coalesce(later_type,'未注明'),count(*) FROM first_growth GROUP BY 1 ORDER BY 2 DESC LIMIT 8")],
  'early_types': [{'type': t, 'people': n} for t, n in q("SELECT coalesce(early_type,'未注明'),count(*) FROM first_growth GROUP BY 1 ORDER BY 2 DESC LIMIT 8")],
}
cols = [c[0] for c in con.execute("SELECT * FROM first_growth LIMIT 0").description]
cases = []
for r in q("SELECT * FROM first_growth ORDER BY later_year DESC, gap, person_id"):
  d = dict(zip(cols, r)); d.pop('rn')
  d['person_name'] = names.get(d['person_id'])
  cases.append(d)
out = {'version': 'member_growth_v1', 'generated_at': datetime.date.today().isoformat(),
       'source': args.db, 'identity_bases': bases, 'summary': summary, 'cases': cases}
json.dump(out, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print(json.dumps(summary, ensure_ascii=False, default=str)[:1500])
print('cases', len(cases), '→', args.out)
