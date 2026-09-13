# Power BI Build Kit

The Power BI phase uses the validated planning pipeline outputs rather than rebuilding forecasting logic inside the report.

## Data sources

- `data/processed/planner_action_center.csv` — 30,490 item-store rows
- `data/processed/forecast_weekly_item_store.csv` — four forecast weeks per item-store
- `outputs/baseline_model_summary.csv`
- `outputs/priority_model_holdout.csv`
- `outputs/priority_feature_importance.csv`

The planner output now exposes `avg_daily_forecast` and `demand_sigma_90d` so the Scenario Planning page can recalculate safety stock, reorder point, and target stock from transparent base inputs.

## Build order

1. Import the five CSV files into Power BI Desktop.
2. Rename tables exactly to `PlannerActionCenter`, `ForecastWeekly`, `BaselineModelSummary`, `PriorityModelHoldout`, and `FeatureImportance`.
3. Create a one-to-many relationship from `PlannerActionCenter[item_store_key]` to `ForecastWeekly[item_store_key]`. The local Power BI preparation step creates `item_store_key = item_id & "|" & store_id` in both tables.
4. Create the three disconnected what-if tables in `scenario_tables.dax`.
5. Create the measures in `measures.dax` (or use `measures.tmdl` after the imported tables exist).
6. Import `theme.json`.
7. Build the Executive Overview using `page_1_build.md`, then continue through the remaining pages in `docs/dashboard_spec.md`.

## QA targets

Before formatting visuals, the unfiltered model should reproduce:

- Forecast units: **1,242,423.1**
- Prior 28-day units: **1,231,764**
- Aggregate forecast growth: **+0.865%**
- Priority LightGBM WAPE: **45.14%**
- Relative WAPE improvement vs MA28: **8.74%**
- Routes: **26,150 MA28 / 3,000 LightGBM / 1,340 WeekdayAvg8**

The public repository intentionally does not store the large processed CSVs; they are regenerated locally from the public M5 source files.
