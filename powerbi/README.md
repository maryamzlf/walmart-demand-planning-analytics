# Power BI Report

The canonical portfolio report is **[Walmart_M5_Demand_Planning_Portfolio.pbit](https://raw.githubusercontent.com/maryamzlf/walmart-demand-planning-analytics/main/powerbi/Walmart_M5_Demand_Planning_Portfolio.pbit)**.

Open the `.pbit` in Power BI Desktop. It contains the validated five-page report and current embedded analytical outputs. Use **File → Save As** if a `.pbix` copy is needed.

## Pages

1. Executive Planning Overview
2. Demand Forecast & Model Performance
3. Merchandise & Assortment Planning
4. Planner Action Center
5. Scenario Planning

## Validated unfiltered values

- Forecast 28D: **1,246,980.1**
- Prior 28D: **1,231,764**
- Aggregate growth: **+1.235%**
- LightGBM WAPE: **45.38%**
- WAPE improvement vs MA28: **8.25%**
- High-risk item-store count: **3,712**
- Trailing-365-day estimated revenue: **$45,163,441.24**
- Routes: **26,150 MA28 / 3,000 LightGBM / 1,340 WeekdayAvg8**

The five dashboard screenshots in the repository README correspond to this final report.

## Validation

The Python/CI pipeline rebuilds the analytical outputs, compiles the report, and validates the embedded model and report structure before publication. See `docs/validation_report.md` for the detailed QA evidence.

## Scope

M5 does not contain observed inventory, open purchase orders, supplier lead times, lost sales, or Walmart replenishment decisions. Inventory quantities are explicit planning scenarios rather than observed Walmart inventory.
