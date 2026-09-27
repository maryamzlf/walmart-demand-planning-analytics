# Power BI Portfolio Report

This folder contains the final Power BI portfolio template for the Walmart M5 Demand Planning Analytics project.

## Open the report

Download `Walmart_M5_Demand_Planning_Portfolio.pbit` and open it with Power BI Desktop. The portfolio template contains embedded analytical outputs, so it does not depend on a local CSV folder path for initial review. Use **File → Save As** to create a `.pbix` copy on your computer if desired.

## Report pages

1. **Executive Planning Overview** — 28-day forecast, prior-period comparison, high-risk series, state/department views, demand-pattern mix, and planner queue.
2. **Demand Forecast & Model Performance** — LightGBM holdout metrics, rolling baseline comparison, forecast drivers, and weekly routed forecast.
3. **Merchandise & Assortment Planning** — revenue, units, ABC/XYZ mix, category outlook, and prioritized merchandise detail.
4. **Planner Action Center** — item-store recommendations ranked by demand risk and planning movement.
5. **Scenario Planning** — lead-time, review-period, and service-level what-if analysis for safety stock, reorder point, and target stock.

## Important interpretation note

The M5 public dataset does not contain observed Walmart inventory, purchase orders, supplier lead times, or actual replenishment decisions. The inventory page therefore presents **explicit planning scenarios**, not actual Walmart inventory recommendations.

## QA targets

The unfiltered report should reproduce approximately:

- Forecast units: **1.24M**
- Prior 28-day units: **1.23M**
- Aggregate forecast growth: **+0.9%**
- Priority LightGBM WAPE: **45.14%**
- Relative WAPE improvement vs MA28: **8.74%**
- Routes: **26,150 MA28 / 3,000 LightGBM / 1,340 WeekdayAvg8**

## Build reproducibility

The repository includes `tools/build_real_pbit_source.py.gz`, `tools/polish_powerbi_project.py`, and a GitHub Actions workflow that rebuilds and validates the template from the analytical pipeline outputs.
