# Power BI Dashboard — Final Implementation

The final report is implemented for a merchandise / demand / inventory planning audience rather than as a generic analytics dashboard.

## Power BI-ready sources

- `data/processed/planner_action_center.csv` — one row per item × store
- `data/processed/forecast_weekly_item_store.csv` — four forecast weeks per item × store
- `outputs/baseline_model_summary.csv` — rolling baseline comparison
- `outputs/priority_model_holdout.csv` — priority holdout model comparison
- `outputs/priority_feature_importance.csv` — LightGBM feature importance

## Page 1 — Executive Planning Overview

**KPIs:** Forecast 28D, Prior 28D, Growth vs Prior, A-Class Revenue Share, High-Risk Item-Store, LightGBM WAPE.

**Visuals:** Forecast vs prior by department, 28-day forecast by state, demand-pattern mix, ABC-XYZ portfolio matrix, and priority planning queue.

## Page 2 — Demand Forecast & Model Performance

**KPIs:** LightGBM WAPE, WAPE Improvement, Forecast Bias.

**Visuals:** Priority holdout WAPE by model, rolling baseline WAPE by demand pattern, Forecast Driver Importance, and weekly routed forecast.

## Page 3 — Merchandise & Assortment Planning

**KPIs:** Revenue 365D, Units 365D, Item-Store Count, Growth Review, Decline Review.

**Visuals:** Revenue by department, revenue mix by ABC class, item-store mix by XYZ class, 28-day forecast by category, and merchandise priority detail. The priority table is sorted by Risk Score descending, then trailing revenue.

## Page 4 — Planner Action Center

Table grain: **item × store**.

**KPIs:** High-Risk Item-Store, High-Risk Revenue Share, Growth Review, Decline Review, Average Risk Score.

**Priority queue fields:** Item, Store, ABC-XYZ, Demand Pattern, Forecast (28D), Planning Change %, Risk Score, Planner Action.

The queue is sorted by **Risk Score descending** so the most consequential records are visible first.

## Page 5 — Scenario Planning

**Slicers / what-if parameters:** Lead Time (Days), Review Period (Days), Service Level, ABC Class, Department.

**KPIs:** Baseline Safety Stock, Scenario Safety Stock, Target Stock Change (Units), Scenario Reorder Point, Scenario Target Stock, Target Stock Change %.

**Visuals:** Baseline vs scenario target stock by ABC class, scenario target stock by department, and scenario detail by department / ABC class.

A visible interpretation note should accompany portfolio discussion: these are planning scenarios because public M5 data does not contain actual on-hand inventory or Walmart replenishment decisions.


## Interaction and reconciliation notes

- Model-diagnostic tables on **Demand Forecast & Model Performance** are intentionally disconnected from merchandise slicers. Holdout/backtest metrics are fixed validation summaries; slicers affect the routed weekly forecast through the PlannerActionCenter → ForecastWeekly relationship.
- The default Scenario Planning state (14-day lead time, 7-day review period, ABC service levels) must equal the stored baseline exactly. Therefore the default **Target Stock Change (Units)** and **Target Stock Change %** are 0.
- Planner queues are sorted by **Risk Score descending**, then **Revenue descending** to make ties deterministic and business-prioritized.
