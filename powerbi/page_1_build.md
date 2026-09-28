# Page 1 — Executive Planning Overview

Reference layout for the final Power BI report.

## Filters
State, Store, Category, Department, ABC Class, Demand Pattern.

## KPIs
1. Forecast 28D
2. Prior 28D
3. Growth vs Prior
4. A-Class Revenue Share
5. High-Risk Item-Store
6. LightGBM WAPE

## Visuals
- **Forecast vs Prior by Department** — Forecast 28D vs Prior 28D.
- **28-Day Forecast by State** — routed forecast by state.
- **Demand Pattern Mix** — item-store count by Smooth / Intermittent / Erratic / Lumpy.
- **ABC-XYZ Portfolio Matrix** — Revenue 365D and Item-Store Count by ABC/XYZ class.
- **Planner Action Queue** — Item, Store, ABC-XYZ, Demand Pattern, Risk Score, Planner Action.

The action queue is sorted by Risk Score descending and Revenue descending.

## Interpretation
Inventory quantities elsewhere in the report are scenario-based decision-support calculations. M5 does not provide observed on-hand inventory, purchase orders, or vendor lead times.
