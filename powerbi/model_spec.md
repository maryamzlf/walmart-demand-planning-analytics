# Power BI Semantic Model

## Tables

| Table | Grain | Purpose |
|---|---|---|
| `PlannerActionCenter` | 1 row per item × store | Primary planning snapshot and slicer dimension |
| `ForecastWeekly` | 4 rows per item × store | Weekly 28-day routed forecast |
| `BaselineModelSummary` | segment × model | Rolling backtest comparison |
| `PriorityModelHoldout` | model | Leakage-safe 3,000-series holdout metrics |
| `FeatureImportance` | feature | LightGBM gain importance |

## Relationship

Create exactly one active relationship:

`PlannerActionCenter[item_store_key]` **1 → many** `ForecastWeekly[item_store_key]`

Cross-filter direction: **Single**, from `PlannerActionCenter` to `ForecastWeekly`.

Keep the three model-diagnostic tables disconnected. They describe benchmark/model diagnostics and should not inherit merchandise slicers.

## Data types

Set `forecast_start_date`, `forecast_end_date`, `week_start_date`, and `week_end_date` to **Date**. Keep item/store/department/category/state identifiers as **Text**. Keep sales, revenue, risk, ADI/CV², volatility and scenario fields as numeric.

## Scenario parameter tables

Create the three disconnected tables in `scenario_tables.dax`. Do not create relationships from these tables. They intentionally filter only the scenario measures through `SELECTEDVALUE`.

## Critical aggregation rule

Do not average or sum row-level `forecast_growth_pct` to create the executive growth KPI. Executive growth must be calculated from aggregated units:

`(SUM(forecast_28d_units) - SUM(prior_28d_units)) / SUM(prior_28d_units)`.
