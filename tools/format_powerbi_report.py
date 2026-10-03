from __future__ import annotations
from pathlib import Path
import json, re, sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'build/walmart_pbit_pbixproj')

COLUMN_RENAMES = {
    'PlannerActionCenter': {
        'state_id': 'State', 'store_id': 'Store', 'cat_id': 'Category', 'dept_id': 'Department',
        'abc_class': 'ABC Class', 'xyz_class': 'XYZ Class', 'abc_xyz': 'ABC-XYZ',
        'demand_segment': 'Demand Pattern', 'item_id': 'Item', 'planner_action': 'Planner Action',
        'forecast_model_route': 'Forecast Model', 'revenue_365d': 'Revenue ($, 365D)',
        'units_365d': 'Units (365D)', 'forecast_28d_units': 'Forecast (28D)',
        'prior_28d_units': 'Prior (28D)', 'forecast_growth_pct': 'Item-Store Forecast Growth %',
        'planning_change_signal_pct': 'Planning Change %', 'demand_risk_score': 'Risk Score',
        'safety_stock_scenario_units': 'Baseline Safety Stock',
        'reorder_point_scenario_units': 'Baseline Reorder Point',
        'target_stock_scenario_units': 'Baseline Target Stock',
        'service_level_scenario': 'Baseline Service Level', 'avg_daily_forecast': 'Avg Daily Forecast',
        'demand_sigma_90d': 'Demand Sigma 90D',
    },
    'ForecastWeekly': {
        'item_id': 'Item', 'store_id': 'Store', 'week_start_date': 'Week Start',
        'week_end_date': 'Week End', 'forecast_units': 'Forecast Units',
    },
    'BaselineModelSummary': {'segment': 'Demand Pattern', 'model': 'Model'},
    'PriorityModelHoldout': {'model': 'Model'},
    'FeatureImportance': {'feature': 'Feature'},
    'ScenarioLeadTime': {'Value': 'Lead Time (Days)'},
    'ScenarioReviewPeriod': {'Days': 'Review Period (Days)'},
    'ScenarioServiceLevel': {'Scenario': 'Service Level'},
}

COLUMN_FORMATS = {
    ('PlannerActionCenter', 'Forecast Growth %'): r'0.0\%',
    ('PlannerActionCenter', 'Planning Change %'): r'0.0\%',
    ('PlannerActionCenter', 'Revenue ($, 365D)'): '$#,##0',
    ('PlannerActionCenter', 'Risk Score'): '0.0',
}


def lit(value, suffix=None):
    if isinstance(value, bool):
        v = 'true' if value else 'false'
    elif isinstance(value, str) and suffix is None:
        v = "'" + value.replace("'", "''") + "'"
    else:
        v = f'{value}{suffix or ""}'
    return {'expr': {'Literal': {'Value': v}}}


def load_json(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))


def dump_json(p: Path, obj):
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def rename_semantic_columns():
    for table, mapping in COLUMN_RENAMES.items():
        cdir = ROOT / 'Model' / 'tables' / table / 'columns'
        if not cdir.exists():
            continue
        for old, new in mapping.items():
            p = cdir / f'{old}.json'
            if not p.exists():
                p = cdir / f'{new}.json'
            if not p.exists():
                raise FileNotFoundError(f'Missing column file {table}.{old}')
            data = load_json(p)
            data['name'] = new
            fmt = COLUMN_FORMATS.get((table, new))
            if fmt:
                data['formatString'] = fmt
            dump_json(p, data)
            target = cdir / f'{new}.json'
            if p != target:
                if target.exists():
                    target.unlink()
                p.rename(target)

    for dax in (ROOT / 'Model' / 'tables').glob('*/measures/*.dax'):
        text = dax.read_text(encoding='utf-8')
        for table, mapping in COLUMN_RENAMES.items():
            for old, new in mapping.items():
                text = text.replace(f'{table}[{old}]', f'{table}[{new}]')
        dax.write_text(text, encoding='utf-8')

    dbp = ROOT / 'Model' / 'database.json'
    db = load_json(dbp)
    for rel in db.get('model', {}).get('relationships', []):
        ft, tt = rel.get('fromTable'), rel.get('toTable')
        if ft in COLUMN_RENAMES:
            rel['fromColumn'] = COLUMN_RENAMES[ft].get(rel.get('fromColumn'), rel.get('fromColumn'))
        if tt in COLUMN_RENAMES:
            rel['toColumn'] = COLUMN_RENAMES[tt].get(rel.get('toColumn'), rel.get('toColumn'))
    dump_json(dbp, db)


def rename_ref(ref: str) -> str:
    if not isinstance(ref, str) or '.' not in ref:
        return ref
    table, field = ref.split('.', 1)
    new = COLUMN_RENAMES.get(table, {}).get(field)
    return f'{table}.{new}' if new else ref


def update_expr_columns(node, alias_map):
    if isinstance(node, dict):
        for kind in ('Column', 'Measure'):
            obj = node.get(kind)
            if isinstance(obj, dict):
                src = (((obj.get('Expression') or {}).get('SourceRef') or {}).get('Source'))
                table = alias_map.get(src)
                prop = obj.get('Property')
                if kind == 'Column' and table in COLUMN_RENAMES and prop in COLUMN_RENAMES[table]:
                    obj['Property'] = COLUMN_RENAMES[table][prop]
        for v in node.values():
            update_expr_columns(v, alias_map)
    elif isinstance(node, list):
        for v in node:
            update_expr_columns(v, alias_map)


def update_visual_refs(cfg):
    sv = cfg.get('singleVisual', {})
    pq = sv.get('prototypeQuery', {})
    alias_map = {x.get('Name'): x.get('Entity') for x in pq.get('From', [])}
    for vals in sv.get('projections', {}).values():
        for x in vals:
            if 'queryRef' in x:
                x['queryRef'] = rename_ref(x['queryRef'])
    for sel in pq.get('Select', []):
        for kind in ('Column', 'Measure'):
            obj = sel.get(kind)
            if not isinstance(obj, dict):
                continue
            src = (((obj.get('Expression') or {}).get('SourceRef') or {}).get('Source'))
            table = alias_map.get(src)
            prop = obj.get('Property')
            if kind == 'Column' and table in COLUMN_RENAMES and prop in COLUMN_RENAMES[table]:
                new = COLUMN_RENAMES[table][prop]
                obj['Property'] = new
                sel['Name'] = f'{table}.{new}'
                sel['NativeReferenceName'] = new
    update_expr_columns(pq.get('OrderBy', []), alias_map)
    return cfg


def set_title(sv, text, font=11, align='left'):
    vc = sv.setdefault('vcObjects', {})
    vc['title'] = [{'properties': {
        'show': lit(True), 'text': lit(text), 'fontSize': lit(font, 'D'), 'alignment': lit(align)
    }}]


def style_card(sv, title, display_units=1, precision=1, value_font=28, title_font=9):
    objs = sv.setdefault('objects', {})
    objs['labels'] = [{'properties': {
        'fontSize': lit(value_font, 'D'), 'labelDisplayUnits': lit(display_units, 'D'),
        'labelPrecision': lit(precision, 'L')
    }}]
    objs['categoryLabels'] = [{'properties': {'show': lit(False)}}]
    set_title(sv, title, font=title_font, align='center')


def queryref_of_card(sv):
    vals = sv.get('projections', {}).get('Values', [])
    return vals[0].get('queryRef') if vals else None

def style_slicer(sv):
    vals = sv.get('projections', {}).get('Values', [])
    ref = vals[0].get('queryRef') if vals else None
    title = ref.split('.', 1)[1] if isinstance(ref, str) and '.' in ref else (ref or 'Filter')
    objs = sv.setdefault('objects', {})
    objs['header'] = [{'properties': {
        'show': lit(True),
        'text': lit(title),
        'textSize': lit(9, 'D'),
        'bold': lit(True),
    }}]
    objs['items'] = [{'properties': {
        'textSize': lit(8, 'D'),
        'padding': lit(2, 'D'),
    }}]
    objs['data'] = [{'properties': {
        'mode': lit('Dropdown'),
    }}]




def prune_table(sv, keep_refs):
    keep = set(keep_refs)
    vals = sv.get('projections', {}).get('Values', [])
    sv['projections']['Values'] = [x for x in vals if x.get('queryRef') in keep]
    pq = sv.get('prototypeQuery', {})
    pq['Select'] = [x for x in pq.get('Select', []) if x.get('Name') in keep]


def sort_table(sv, table, field, descending=True, secondary=None):
    pq = sv.setdefault('prototypeQuery', {})
    alias = next((x.get('Name') for x in pq.get('From', []) if x.get('Entity') == table), None)
    if alias:
        order = [{'Direction': 2 if descending else 1, 'Expression': {
            'Column': {'Expression': {'SourceRef': {'Source': alias}}, 'Property': field}
        }}]
        if secondary:
            secondary_field, secondary_desc = secondary
            order.append({'Direction': 2 if secondary_desc else 1, 'Expression': {
                'Column': {'Expression': {'SourceRef': {'Source': alias}}, 'Property': secondary_field}
            }})
        pq['OrderBy'] = order


def rebind_card(sv, table, old_measure, new_measure):
    old_ref, new_ref = f'{table}.{old_measure}', f'{table}.{new_measure}'
    for x in sv.get('projections', {}).get('Values', []):
        if x.get('queryRef') == old_ref:
            x['queryRef'] = new_ref
    for sel in sv.get('prototypeQuery', {}).get('Select', []):
        m = sel.get('Measure')
        if isinstance(m, dict) and m.get('Property') == old_measure:
            m['Property'] = new_measure
            sel['Name'] = new_ref
            sel['NativeReferenceName'] = new_measure


def polish_report():
    sections = ROOT / 'Report' / 'sections'
    for cfg_path in sections.glob('*/visualContainers/*/config.json'):
        cfg = load_json(cfg_path)
        update_visual_refs(cfg)
        sv = cfg.get('singleVisual', {})
        vt = sv.get('visualType')
        page = cfg_path.parents[2].name
        ref = queryref_of_card(sv) if vt == 'card' else None

        # Keep every report filter in the compact dropdown format used by the
        # original working PBIX. Without an explicit data.mode Power BI Desktop
        # can reopen generated slicers as checkbox lists.
        if vt == 'slicer':
            style_slicer(sv)

        # Scenario parameters are intentionally single-select. SELECTEDVALUE
        # falls back to the model default when multiple values are selected,
        # which can otherwise make the displayed scenario appear inconsistent
        # with the slicer state.
        if vt == 'slicer' and 'Scenario Planning' in page:
            refs = [
                x.get('queryRef')
                for values in sv.get('projections', {}).values()
                for x in values
            ]
            scenario_parameter_refs = {
                'ScenarioLeadTime.Lead Time (Days)',
                'ScenarioReviewPeriod.Review Period (Days)',
                'ScenarioServiceLevel.Service Level',
            }
            if scenario_parameter_refs.intersection(refs):
                objs = sv.setdefault('objects', {})
                objs['selection'] = [{'properties': {
                    'singleSelect': lit(True),
                    'selectAllCheckboxEnabled': lit(False),
                }}]

        if vt == 'card':
            card_specs = {
                'PlannerActionCenter.Forecast Units 28D': ('Forecast 28D', 1000000, 2, 30, 9),
                'PlannerActionCenter.Prior Units 28D': ('Prior 28D', 1000000, 2, 30, 9),
                'PlannerActionCenter.Forecast Growth %': ('Growth vs Prior', 1, 2, 30, 9),
                'PlannerActionCenter.A-Class Revenue Share': ('A-Class Revenue Share', 1, 1, 30, 9),
                'PlannerActionCenter.High-Risk Item-Store Count': ('High-Risk Item-Store', 1, 0, 30, 9),
                'PriorityModelHoldout.Priority LightGBM WAPE': ('LightGBM WAPE', 1, 2, 28, 9),
                'PriorityModelHoldout.Priority WAPE Improvement %': ('WAPE Improvement', 1, 2, 28, 9),
                'PriorityModelHoldout.Priority LightGBM Bias %': ('Forecast Bias', 1, 2, 28, 9),
                'PlannerActionCenter.Revenue 365D': ('Revenue 365D', 1000000, 1, 30, 9),
                'PlannerActionCenter.Units 365D': ('Units 365D', 1000000, 1, 30, 9),
                'PlannerActionCenter.Item-Store Count': ('Item-Store Count', 1000, 1, 30, 9),
                'PlannerActionCenter.Growth Review Count': ('Growth Review', 1000, 1, 30, 9),
                'PlannerActionCenter.Decline Review Count': ('Decline Review', 1000, 1, 30, 9),
                'PlannerActionCenter.High-Risk Revenue Share': ('High-Risk Revenue Share', 1, 1, 30, 9),
                'PlannerActionCenter.Average Risk Score': ('Average Risk Score', 1, 1, 30, 9),
                'PlannerActionCenter.Baseline Safety Stock Units': ('Baseline Safety Stock', 1000, 0, 28, 9),
                'PlannerActionCenter.Scenario Safety Stock Units': ('Scenario Safety Stock', 1000, 0, 28, 9),
                'PlannerActionCenter.Scenario Safety Stock Delta': ('Safety Stock Δ', 1000, 1, 28, 9),
                'PlannerActionCenter.Scenario Reorder Point Units': ('Scenario Reorder Point', 1000, 0, 28, 9),
                'PlannerActionCenter.Scenario Target Stock Units': ('Scenario Target Stock', 1000000, 2, 28, 9),
                'PlannerActionCenter.Scenario Target Stock Delta %': ('Target Stock Change %', 1, 1, 28, 9),
            }
            if ref in card_specs:
                style_card(sv, *card_specs[ref])
            if 'Scenario Planning' in page and ref == 'PlannerActionCenter.Scenario Safety Stock Delta':
                rebind_card(sv, 'PlannerActionCenter', 'Scenario Safety Stock Delta', 'Scenario Target Stock Delta')
                style_card(sv, 'Target Stock Change (Units)', 1, 0, 28, 9)

        if vt in {'clusteredColumnChart', 'clusteredBarChart', 'lineChart', 'donutChart', 'tableEx'}:
            refs = [x.get('queryRef') for vals in sv.get('projections', {}).values() for x in vals]
            rset = set(refs)
            title = None
            if 'Executive Planning Overview' in page:
                if 'PlannerActionCenter.Department' in rset and 'PlannerActionCenter.Forecast Units 28D' in rset:
                    title = 'Forecast vs Prior by Department'
                elif 'PlannerActionCenter.State' in rset and 'PlannerActionCenter.Forecast Units 28D' in rset:
                    title = '28-Day Forecast by State'
                elif 'PlannerActionCenter.Demand Pattern' in rset and 'PlannerActionCenter.Item-Store Count' in rset:
                    title = 'Demand Pattern Mix'
                elif vt == 'tableEx' and 'PlannerActionCenter.Planner Action' in rset:
                    title = 'Planner Action Queue'
                elif vt == 'tableEx' and 'PlannerActionCenter.Revenue 365D' in rset:
                    title = 'ABC-XYZ Portfolio Matrix'
            elif 'Demand Forecast & Model Performance' in page:
                if 'PriorityModelHoldout.Model WAPE' in rset: title = 'Priority Holdout WAPE by Model'
                elif 'BaselineModelSummary.Baseline WAPE' in rset: title = 'Rolling Baseline WAPE by Demand Pattern'
                elif 'FeatureImportance.Feature Importance Share' in rset: title = 'Forecast Driver Importance'
                elif 'ForecastWeekly.Weekly Forecast Units' in rset:
                    title = 'Weekly Routed Forecast'
                    sort_table(sv, 'ForecastWeekly', 'Week Start', False)
            elif 'Merchandise & Assortment Planning' in page:
                if vt == 'tableEx': title = 'Merchandise Priority Detail'
                elif 'PlannerActionCenter.Revenue 365D' in rset and 'PlannerActionCenter.Department' in rset: title = 'Revenue by Department'
                elif 'PlannerActionCenter.ABC Class' in rset and 'PlannerActionCenter.Revenue 365D' in rset: title = 'Revenue Mix by ABC Class'
                elif 'PlannerActionCenter.XYZ Class' in rset and 'PlannerActionCenter.Item-Store Count' in rset: title = 'Item-Store Mix by XYZ Class'
                elif 'PlannerActionCenter.Category' in rset and 'PlannerActionCenter.Forecast Units 28D' in rset: title = 'Forecast Units by Category'
            elif 'Planner Action Center' in page and vt == 'tableEx': title = 'Planner Action Queue'
            elif 'Scenario Planning' in page:
                if vt == 'clusteredColumnChart': title = 'Baseline vs Scenario Target Stock by ABC Class'
                elif vt == 'clusteredBarChart': title = 'Scenario Target Stock by Department'
                elif vt == 'tableEx': title = 'Scenario Detail by Department and ABC Class'
            if title:
                set_title(sv, title, font=11, align='left')

        if vt == 'tableEx':
            if 'Planner Action Center' in page:
                prune_table(sv, [
                    'PlannerActionCenter.Item', 'PlannerActionCenter.Store', 'PlannerActionCenter.ABC-XYZ',
                    'PlannerActionCenter.Demand Pattern', 'PlannerActionCenter.Forecast (28D)',
                    'PlannerActionCenter.Planning Change %', 'PlannerActionCenter.Risk Score',
                    'PlannerActionCenter.Planner Action'
                ])
                sort_table(sv, 'PlannerActionCenter', 'Risk Score', True, secondary=('Revenue ($, 365D)', True))
            elif 'Executive Planning Overview' in page and 'PlannerActionCenter.Planner Action' in {x.get('queryRef') for x in sv.get('projections', {}).get('Values', [])}:
                prune_table(sv, [
                    'PlannerActionCenter.Item', 'PlannerActionCenter.Store', 'PlannerActionCenter.ABC-XYZ',
                    'PlannerActionCenter.Demand Pattern', 'PlannerActionCenter.Risk Score',
                    'PlannerActionCenter.Planner Action'
                ])
                sort_table(sv, 'PlannerActionCenter', 'Risk Score', True)
            elif 'Merchandise & Assortment Planning' in page:
                prune_table(sv, [
                    'PlannerActionCenter.Item', 'PlannerActionCenter.Store', 'PlannerActionCenter.Department',
                    'PlannerActionCenter.ABC Class', 'PlannerActionCenter.XYZ Class',
                    'PlannerActionCenter.Revenue ($, 365D)', 'PlannerActionCenter.Forecast (28D)',
                    'PlannerActionCenter.Planning Change %', 'PlannerActionCenter.Risk Score'
                ])
                sort_table(sv, 'PlannerActionCenter', 'Risk Score', True, secondary=('Revenue ($, 365D)', True))

        if vt == 'card' and 'Demand Forecast & Model Performance' in page:
            pos = cfg.get('layouts', [{}])[0].get('position', {})
            newpos = {820: (805, 145), 965: (955, 145), 1110: (1105, 145)}
            if pos.get('x') in newpos:
                pos['x'], pos['width'] = newpos[pos['x']]

        dump_json(cfg_path, cfg)



def align_scenario_default_baseline():
    """Keep the unfiltered/default scenario numerically identical to the stored baseline.

    This avoids a small artificial delta caused by rounded exported planner fields.
    Non-default what-if selections are still recalculated dynamically.
    """
    mdir = ROOT / 'Model' / 'tables' / 'PlannerActionCenter' / 'measures'
    dax = {
        'Scenario Safety Stock Units.dax': '''VAR LeadTime = [Scenario Lead Time Days]
VAR ScenarioLabel = [Scenario Service Label]
VAR OverrideZ = [Scenario Z Override]
RETURN
IF (
    LeadTime = 14 && ScenarioLabel = "ABC default",
    [Baseline Safety Stock Units],
    SUMX (
        PlannerActionCenter,
        VAR ClassZ =
            SWITCH (
                'PlannerActionCenter'[ABC Class],
                "A", 1.645,
                "B", 1.282,
                "C", 1.036,
                1.282
            )
        VAR ZValue = IF ( ScenarioLabel = "ABC default", ClassZ, OverrideZ )
        RETURN ZValue * 'PlannerActionCenter'[Demand Sigma 90D] * SQRT ( LeadTime )
    )
)
''',
        'Scenario Reorder Point Units.dax': '''VAR LeadTime = [Scenario Lead Time Days]
VAR ScenarioLabel = [Scenario Service Label]
VAR OverrideZ = [Scenario Z Override]
RETURN
IF (
    LeadTime = 14 && ScenarioLabel = "ABC default",
    [Baseline Reorder Point Units],
    SUMX (
        PlannerActionCenter,
        VAR ClassZ =
            SWITCH (
                'PlannerActionCenter'[ABC Class],
                "A", 1.645,
                "B", 1.282,
                "C", 1.036,
                1.282
            )
        VAR ZValue = IF ( ScenarioLabel = "ABC default", ClassZ, OverrideZ )
        VAR Safety = ZValue * 'PlannerActionCenter'[Demand Sigma 90D] * SQRT ( LeadTime )
        RETURN 'PlannerActionCenter'[Avg Daily Forecast] * LeadTime + Safety
    )
)
''',
        'Scenario Target Stock Units.dax': '''VAR LeadTime = [Scenario Lead Time Days]
VAR ReviewDays = [Scenario Review Period Days]
VAR ScenarioLabel = [Scenario Service Label]
VAR OverrideZ = [Scenario Z Override]
RETURN
IF (
    LeadTime = 14 && ReviewDays = 7 && ScenarioLabel = "ABC default",
    [Baseline Target Stock Units],
    SUMX (
        PlannerActionCenter,
        VAR ClassZ =
            SWITCH (
                'PlannerActionCenter'[ABC Class],
                "A", 1.645,
                "B", 1.282,
                "C", 1.036,
                1.282
            )
        VAR ZValue = IF ( ScenarioLabel = "ABC default", ClassZ, OverrideZ )
        VAR Safety = ZValue * 'PlannerActionCenter'[Demand Sigma 90D] * SQRT ( LeadTime )
        RETURN 'PlannerActionCenter'[Avg Daily Forecast] * ( LeadTime + ReviewDays ) + Safety
    )
)
''',
    }
    for name, text in dax.items():
        p = mdir / name
        if not p.exists():
            raise FileNotFoundError(p)
        p.write_text(text, encoding='utf-8')


def fix_measure_formats():
    fixes = {
        'PlannerActionCenter': {
            'Scenario Safety Stock Delta.xml': '#,##0;-#,##0;0',
            'Scenario Target Stock Delta.xml': '#,##0;-#,##0;0',
            'Scenario Target Stock Delta %.xml': '0.0%;-0.0%;0.0%',
        },
        'PriorityModelHoldout': {
            'Priority LightGBM WAPE.xml': '0.00%',
            'Priority WAPE Improvement %.xml': '0.00%',
            'Priority LightGBM Bias %.xml': '0.00%;-0.00%;0.00%',
        },
    }
    for table, table_fixes in fixes.items():
        mdir = ROOT / 'Model' / 'tables' / table / 'measures'
        for name, fmt in table_fixes.items():
            p = mdir / name
            if not p.exists():
                continue
            text = p.read_text(encoding='utf-8')
            if '<FormatString>' in text:
                text = re.sub(r'<FormatString>.*?</FormatString>', f'<FormatString>{fmt}</FormatString>', text, flags=re.S)
            else:
                text = text.replace('</Measure>', f'  <FormatString>{fmt}</FormatString>\n</Measure>')
            p.write_text(text, encoding='utf-8')


def validate():
    cols = {}
    for tdir in (ROOT / 'Model' / 'tables').iterdir():
        cdir = tdir / 'columns'; cols[tdir.name] = set()
        if cdir.exists():
            for p in cdir.glob('*.json'):
                cols[tdir.name].add(load_json(p)['name'])
            assert len(cols[tdir.name]) == len(list(cdir.glob('*.json')))

    assert 'Baseline Service Level' in cols.get('PlannerActionCenter', set())
    assert 'Service Level' not in cols.get('PlannerActionCenter', set())
    assert 'Item-Store Forecast Growth %' in cols.get('PlannerActionCenter', set())
    assert 'Forecast Growth %' not in cols.get('PlannerActionCenter', set())

    # Power BI rejects a table when a column and a measure share the same name.
    # Check source-project names before compilation so this cannot regress.
    for tdir in (ROOT / 'Model' / 'tables').iterdir():
        mdir = tdir / 'measures'
        measures = {p.stem for p in mdir.glob('*.dax')} if mdir.exists() else set()
        overlap = cols.get(tdir.name, set()) & measures
        assert not overlap, (tdir.name, sorted(overlap))

    for dax in (ROOT / 'Model' / 'tables').glob('*/measures/*.dax'):
        text = dax.read_text(encoding='utf-8')
        for table, col in re.findall(r'([A-Za-z0-9_]+)\[([^\]]+)\]', text):
            if table in cols:
                assert col in cols[table], (dax, table, col)

    count = 0
    slicer_count = 0
    scenario_parameter_slicers = 0
    for cfg_path in (ROOT / 'Report' / 'sections').glob('*/visualContainers/*/config.json'):
        cfg = load_json(cfg_path); sv = cfg.get('singleVisual', {}); count += 1
        refs = [x.get('queryRef') for xs in sv.get('projections', {}).values() for x in xs if x.get('queryRef')]
        sels = {x.get('Name') for x in sv.get('prototypeQuery', {}).get('Select', [])}
        assert not [r for r in refs if r not in sels], cfg_path

        page = cfg_path.parents[2].name
        if sv.get('visualType') == 'slicer':
            slicer_count += 1
            objs = sv.get('objects', {})
            data_props = objs.get('data', [{}])[0].get('properties', {})
            header_props = objs.get('header', [{}])[0].get('properties', {})
            item_props = objs.get('items', [{}])[0].get('properties', {})
            assert data_props.get('mode') == lit('Dropdown'), cfg_path
            assert header_props.get('show') == lit(True), cfg_path
            assert header_props.get('bold') == lit(True), cfg_path
            assert header_props.get('textSize') == lit(9, 'D'), cfg_path
            assert item_props.get('textSize') == lit(8, 'D'), cfg_path
            assert item_props.get('padding') == lit(2, 'D'), cfg_path

        if sv.get('visualType') == 'slicer' and 'Scenario Planning' in page:
            scenario_refs = {
                'ScenarioLeadTime.Lead Time (Days)',
                'ScenarioReviewPeriod.Review Period (Days)',
                'ScenarioServiceLevel.Service Level',
            }
            if scenario_refs.intersection(refs):
                scenario_parameter_slicers += 1
                props = (
                    sv.get('objects', {})
                    .get('selection', [{}])[0]
                    .get('properties', {})
                )
                assert props.get('singleSelect') == lit(True), cfg_path
                assert props.get('selectAllCheckboxEnabled') == lit(False), cfg_path

    assert slicer_count == 24, slicer_count
    assert scenario_parameter_slicers == 3, scenario_parameter_slicers
    assert count == 67, count
    print('Power BI report validation passed:', count, 'visuals')


if __name__ == '__main__':
    rename_semantic_columns()
    align_scenario_default_baseline()
    polish_report()
    fix_measure_formats()
    validate()
