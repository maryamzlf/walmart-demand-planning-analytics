# Power BI Dashboard Specification

The final report is designed for a merchandise / demand / inventory planning audience rather than as a generic analytics dashboard.

## Page 1 — Executive Planning Overview
**KPIs**
- Forecast Units — Next 28 Days
- Prior 28-Day Units
- Forecast Growth %
- A-Class Revenue Share
- High-Risk Item-Store Count
- Priority Forecast WAPE

**Visuals**
- Forecast vs prior demand by department
- Forecast by state/store
- ABC-XYZ matrix
- Demand-pattern mix
- Top planner actions table

## Page 2 — Demand Forecast & Model Performance
- Actual vs backtest forecast
- WAPE / RMSE / Bias by model
- Error by demand segment
- Forecast by week for selected item/store
- Feature importance for priority LightGBM

## Page 3 — Merchandise & Assortment Planning
- Revenue and units by category / department
- A/B/C contribution
- X/Y/Z variability
- High-value growth / decline items
- Price movement vs unit movement

## Page 4 — Planner Action Center
Table grain: item × store.

Recommended columns:
- Item
- Store
- Department
- ABC-XYZ
- Demand segment
- Prior 28D Units
- Forecast 28D Units
- Growth %
- Demand Risk Score
- Scenario Safety Stock
- Scenario Reorder Point
- Planner Action

Conditional formatting should emphasize high-value and high-risk records, not decorate every field.

## Page 5 — Scenario Planning
Slicers / what-if parameters:
- Lead time
- Service level
- Review period

Outputs:
- Safety stock scenario
- Reorder point scenario
- Target stock scenario

A visible note must state that these are scenario calculations because public M5 data does not contain actual on-hand inventory or Walmart replenishment decisions.
