# Power BI Report

This folder contains the validated Power BI deliverable for the Walmart M5 Demand Planning Analytics project.

## Open the report

Open **`Walmart_M5_Demand_Planning_Portfolio.pbit`** in Power BI Desktop. The template contains the five-page report and embedded analytical outputs, so initial review does not depend on a local CSV path.

If a `.pbix` file is needed, open the validated `.pbit` and use **File → Save As** in Power BI Desktop. The repository intentionally does not keep an older `.pbix` snapshot when it no longer matches the current validated model.

## Report pages

1. **Executive Planning Overview** — 28-day forecast, prior-period comparison, high-risk series, state/department views, demand-pattern mix, and planner queue.
2. **Demand Forecast & Model Performance** — LightGBM holdout metrics, rolling baseline comparison, forecast drivers, and weekly routed forecast.
3. **Merchandise & Assortment Planning** — revenue, units, ABC/XYZ mix, category outlook, and prioritized merchandise detail.
4. **Planner Action Center** — item-store recommendations ranked by demand risk and business value.
5. **Scenario Planning** — lead-time, review-period, and service-level what-if analysis for safety stock, reorder point, and target stock.

The model-diagnostic tables on page 2 are intentionally disconnected from merchandise slicers. The slicers affect the routed weekly forecast, while holdout/backtest metrics remain fixed validation summaries.

## Verified unfiltered values

- Forecast units: **1,242,423.1**
- Prior 28-day units: **1,231,764**
- Aggregate forecast growth: **+0.87%**
- Priority LightGBM WAPE: **45.14%**
- Priority LightGBM bias: **-0.86%**
- Relative WAPE improvement vs MA28: **8.74%**
- High-risk item-store count: **3,876**
- Growth review count: **5,028**
- Decline review count: **4,358**
- Baseline safety stock: **225,815.5 units**
- Baseline reorder point: **847,028.3 units**
- Baseline target stock: **1,157,623.9 units**
- Routes: **26,150 MA28 / 3,000 LightGBM / 1,340 WeekdayAvg8**

With the default scenario (14-day lead time, 7-day review period, ABC service levels), scenario values equal the stored baseline and the target-stock delta is **0**.

## Important interpretation note

The M5 public dataset does not contain observed Walmart inventory, purchase orders, supplier lead times, or actual replenishment decisions. Inventory quantities in the report are explicit planning scenarios, not observed Walmart inventory.

## Build reproducibility

GitHub Actions rebuilds the analytics from the public M5 source files, compiles the `.pbit`, validates the embedded data/model/visual structure, and synchronizes the tracked analytical evidence.
