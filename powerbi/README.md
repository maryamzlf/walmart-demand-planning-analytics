# Power BI Report

The canonical report is **`Walmart_M5_Demand_Planning_Portfolio.pbit`**.

Open it in Power BI Desktop. The template contains the five report pages and embedded analytical outputs, so no local CSV path is required for initial review. Use **File → Save As** in Power BI Desktop if a `.pbix` copy is needed.

## Pages

1. Executive Planning Overview
2. Demand Forecast & Model Performance
3. Merchandise & Assortment Planning
4. Planner Action Center
5. Scenario Planning

Page-2 validation tables are intentionally disconnected from merchandise slicers. The slicers can change the routed weekly forecast; holdout and backtest summaries stay fixed.

## Verified unfiltered values

- Forecast 28D: **1,242,423.1**
- Prior 28D: **1,231,764**
- Aggregate growth: **+0.87%**
- LightGBM WAPE: **45.03%**
- LightGBM bias: **-0.67%**
- WAPE improvement vs MA28: **8.96%**
- High-risk item-store count (risk ≥ 70): **3,876**
- Growth review: **5,028**
- Decline review: **4,358**
- Average risk score: **56.293**
- Baseline safety stock: **225,815.5**
- Baseline reorder point: **847,028.3**
- Baseline target stock: **1,157,623.9**
- Routes: **26,150 MA28 / 3,000 LightGBM / 1,340 WeekdayAvg8**

With default settings (14-day lead time, 7-day review period, ABC service levels), scenario values equal the stored baseline and target-stock delta is **0**.

## Scope

M5 does not contain observed inventory, open POs, supplier lead times, or Walmart replenishment decisions. Inventory quantities are explicit planning scenarios.

GitHub Actions rebuilds the analytics from public M5 source files, compiles the PBIT, and validates embedded data, model structure, measures, visual bindings, page order, and key KPI reconciliations.
