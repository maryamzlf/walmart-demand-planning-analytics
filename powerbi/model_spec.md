# Power BI Semantic Model

## Tables

| Table | Grain | Purpose |
|---|---|---|
| `PlannerActionCenter` | 1 row per item × store | Primary planning snapshot and slicer dimension |
| `ForecastWeekly` | 4 rows per item × store | Weekly 28-day routed forecast |
| `BaselineModelSummary` | demand pattern × model | Rolling baseline comparison |
| `PriorityModelHoldout` | model | Leakage-safe 3,000-series holdout metrics |
| `FeatureImportance` | feature | LightGBM gain importance |
| `ScenarioLeadTime` | lead-time option | Disconnected scenario parameter |
| `ScenarioReviewPeriod` | review-period option | Disconnected scenario parameter |
| `ScenarioServiceLevel` | service-level option | Disconnected scenario parameter |

## Relationship

Create exactly one active relationship:

`PlannerActionCenter[item_store_key]` **1 → many** `ForecastWeekly[item_store_key]`

Cross-filter direction: **Single**, from `PlannerActionCenter` to `ForecastWeekly`.

Keep the three model-diagnostic tables disconnected. They describe benchmark/model diagnostics and should not inherit merchandise slicers. Keep all three scenario parameter tables disconnected; they affect scenario calculations through measures only.

## Business-facing semantic names

The compiled report exposes business-facing column names while retaining technical source columns underneath. Examples:

- `item_id` → **Item**
- `store_id` → **Store**
- `dept_id` → **Department**
- `cat_id` → **Category**
- `abc_class` → **ABC Class**
- `xyz_class` → **XYZ Class**
- `demand_segment` → **Demand Pattern**
- `forecast_28d_units` → **Forecast (28D)**
- `prior_28d_units` → **Prior (28D)**
- `planning_change_signal_pct` → **Planning Change %**
- `service_level_scenario` → **Baseline Service Level**
- `demand_risk_score` → **Risk Score**
- `planner_action` → **Planner Action**

The reference DAX in `measures.dax` uses these final semantic names.

## Data types

Set forecast dates and weekly dates to **Date**. Keep item/store/department/category/state identifiers as **Text**. Keep sales, revenue, risk, ADI/CV², volatility, and scenario fields as numeric.

## Scenario parameter tables

The final report uses the following disconnected fields:

- `ScenarioLeadTime[Lead Time (Days)]`
- `ScenarioReviewPeriod[Review Period (Days)]`
- `ScenarioServiceLevel[Service Level]`
- `ScenarioServiceLevel[Z]`

Their reference definitions are in `scenario_tables.dax`. The three scenario parameter slicers are configured as single-select controls.

## Critical aggregation rule

Do not average or sum row-level forecast-growth percentages to create the executive growth KPI. Executive growth is calculated from aggregated units:

`(SUM(Forecast (28D)) - SUM(Prior (28D))) / SUM(Prior (28D))`

This reconciles the current canonical report to **+1.235%** aggregate growth.
