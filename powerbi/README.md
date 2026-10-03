# Power BI Report

The canonical portfolio report is **[Walmart_M5_Demand_Planning_Portfolio.pbix](https://raw.githubusercontent.com/maryamzlf/walmart-demand-planning-analytics/main/powerbi/Walmart_M5_Demand_Planning_Portfolio.pbix)**.

Open the `.pbix` directly in Power BI Desktop. It is a ready-to-open five-page report and is the file shown in the dashboard screenshots in the repository README.

## Pages

1. Executive Planning Overview
2. Demand Forecast & Model Performance
3. Merchandise & Assortment Planning
4. Planner Action Center
5. Scenario Planning

## Portfolio snapshot values

The included PBIX is a fixed working snapshot. Its unfiltered dashboard displays approximately:

- Forecast 28D: **1.24M**
- Prior 28D: **1.23M**
- Aggregate growth: **+0.9%**
- LightGBM WAPE: **45.14%**
- WAPE improvement vs MA28: **8.74%**
- High-risk item-store count: **3,876**
- Routes: **26,150 MA28 / 3,000 LightGBM / 1,340 WeekdayAvg8**

These values correspond to the included PBIX and its screenshots.

## Current analytical validation

The Python/CI pipeline has continued to be revalidated after the fixed PBIX snapshot. Current pipeline metrics and QA evidence are maintained in the root `README.md` and `docs/validation_report.md`.

CI still compiles and validates a PBIT as a **test artifact**, but that template is no longer published as the primary portfolio download. This avoids replacing the known-working PBIX with a generated template.

## Scope

M5 does not contain observed inventory, open purchase orders, supplier lead times, lost sales, or Walmart replenishment decisions. Inventory quantities are explicit planning scenarios rather than observed Walmart inventory.
