# Power BI Report

The canonical report is **`Walmart_M5_Demand_Planning_Portfolio.pbit`**.

Open it in Power BI Desktop. The template contains the five report pages and embedded analytical outputs, so no local CSV path is required for initial review. Use **File → Save As** in Power BI Desktop if a `.pbix` copy is needed.

## Pages

1. Executive Planning Overview
2. Demand Forecast & Model Performance
3. Merchandise & Assortment Planning
4. Planner Action Center
5. Scenario Planning

## Interaction behavior

On **Demand Forecast & Model Performance**, the Item / Store / Demand Pattern slicers filter the routed weekly forecast. Holdout metrics, rolling baseline results, and feature importance remain fixed because they summarize model validation rather than item-store operating results.

On **Scenario Planning**, no explicit parameter selection means the default scenario is used:

- lead time: **14 days**
- review period: **7 days**
- service levels: **A 95% / B 90% / C 85%**

Power BI cards use presentation rounding and display units. The exact reconciliation values are listed below.

## Verified unfiltered values

- Forecast 28D: **1,246,980.1**
- Prior 28D: **1,231,764**
- Aggregate growth: **+1.235%**
- LightGBM WAPE: **45.38%**
- LightGBM bias: **-1.46%**
- WAPE improvement vs MA28: **8.25%**
- High-risk item-store count (risk ≥ 70): **3,712**
- High-risk revenue share: **15.693%**
- Growth review: **5,038**
- Decline review: **4,371**
- Average risk score: **56.038**
- Baseline safety stock: **225,815.5**
- Baseline reorder point: **849,307.4**
- Baseline target stock: **1,161,040.0**
- Routes: **26,150 MA28 / 3,000 LightGBM / 1,340 WeekdayAvg8**

With default scenario settings, calculated scenario values reconcile to the stored baseline and target-stock delta is **0**.

## Scope

M5 does not contain observed inventory, open purchase orders, supplier lead times, lost sales, or Walmart replenishment decisions. Inventory quantities are explicit planning scenarios. Safety stock uses a normal-volatility approximation, so intermittent and lumpy demand should be interpreted as sensitivity analysis rather than a calibrated service-level guarantee.

GitHub Actions rebuilds the analytics from public M5 source files, compiles the PBIT, and validates embedded data, model structure, measures, visual bindings, page order, and key KPI reconciliations.
