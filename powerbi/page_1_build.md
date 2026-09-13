# Page 1 — Executive Planning Overview

**Canvas:** 16:9. Use the included theme. Keep a light neutral page background and white visual cards.

## Header

Title: **Retail Demand Planning | Executive Overview**  
Subtitle: **28-Day Forecast • Merchandise Priority • Replenishment Risk**

Place slicers in a compact row below the title: `state_id`, `store_id`, `cat_id`, `dept_id`, `abc_class`, `demand_segment`.

## KPI row

Use six card visuals, left to right:

1. `Forecast Units 28D`
2. `Prior Units 28D`
3. `Forecast Growth %`
4. `A-Class Revenue Share`
5. `High-Risk Item-Store Count`
6. `Priority LightGBM WAPE`

Use display units K/M where appropriate. Forecast Growth and WAPE are percentages. Avoid decorative icons unless they communicate direction or risk.

## Main visuals

### A. Forecast vs Prior by Department
Clustered bar chart. Axis: `dept_id`. Values: `Forecast Units 28D`, `Prior Units 28D`. Sort by Forecast Units descending.

### B. Forecast by Store
Bar chart. Axis: `store_id`. Value: `Forecast Units 28D`.

### C. ABC–XYZ Matrix
Matrix visual. Rows: `abc_class`. Columns: `xyz_class`. Values: `Revenue 365D`, `Item-Store Count`. Apply conditional background formatting to Revenue 365D.

### D. Demand Pattern Mix
Horizontal 100% stacked bar using `demand_segment` and `Item-Store Count`.

### E. Top Planner Actions
Table columns: `item_id`, `store_id`, `abc_xyz`, `demand_segment`, `forecast_28d_units`, `planning_change_signal_pct`, `demand_risk_score`, `planner_action`.

Visual filter: top 15 by `demand_risk_score`, then sort by `revenue_365d` descending. Apply conditional formatting only to risk score and planning-change signal.

## Required note

> Inventory quantities shown in this report are scenario-based decision-support calculations. Public M5 data does not contain observed on-hand inventory, purchase orders, or vendor lead times.
