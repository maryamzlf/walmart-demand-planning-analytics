# QA and Reproducibility Report

**Review date:** 2026-10-03  
**Canonical report:** `powerbi/Walmart_M5_Demand_Planning_Portfolio.pbit`

## Review scope

This review checks data integrity, leakage controls, forecast and planning calculations, reproducibility, and consistency between analytical outputs and the Power BI report.

## Data integrity

A clean GitHub Actions rebuild verified:

- **30,490** item-store series
- **3,049** items
- **10** stores across **3** states
- **3** categories and **7** departments
- **1,941** observed sales days
- **66,927,173** total units
- **67.9978%** zero-demand observations
- no negative or missing sales
- no duplicate series IDs or calendar-day keys
- **6,841,121** sell-price records
- no missing or non-positive sell prices
- unique store × item × week price keys
- validation history exactly matches `d_1 ... d_1913` in the evaluation file

Price histories are forward-filled only. A later observed price is never backfilled into an earlier period.

Demand-pattern counts reproduce exactly:

| Pattern | Series |
|---|---:|
| Intermittent | 23,096 |
| Lumpy | 3,761 |
| Smooth | 2,939 |
| Erratic | 694 |

ABC classification uses trailing estimated revenue. XYZ variability is calculated from complete Walmart business weeks to avoid partial-week distortion.

## Forecast validation

The statistical baselines use three chronological 28-day folds. The best baseline route by demand pattern is:

- Smooth → **WeekdayAvg8**
- Intermittent → **MA28**
- Erratic → **MA28**
- Lumpy → **MA28**

The LightGBM challenger is evaluated on a separate leakage-safe 28-day holdout for the 3,000 highest-value item-store series selected using pre-holdout information only.

| Model | WAPE | MAE | RMSE | Bias |
|---|---:|---:|---:|---:|
| LightGBM | **45.38%** | **2.52** | **4.34** | **-1.46%** |
| MA28 | 49.46% | 2.74 | 4.86 | -1.28% |
| WeekdayAvg8 | 49.54% | 2.75 | 4.78 | -1.06% |
| SeasonalNaive7 | 56.77% | 3.15 | 5.43 | -6.16% |

Relative WAPE improvement of LightGBM versus MA28: **8.25%**.

Final forecast routing:

- MA28: **26,150** series
- LightGBM: **3,000** series
- WeekdayAvg8: **1,340** series

## Planning reconciliation

The final routed plan reconciles to:

- 28-day forecast: **1,246,980.1 units**
- prior 28-day units: **1,231,764**
- aggregate forecast growth: **+1.235%**
- trailing-365-day estimated revenue: **$45,163,441.24**
- A-class revenue share: **79.999%**
- high-risk item-store records, risk ≥ 70: **3,712**
- high-risk revenue share: **15.693%**
- growth-review records: **5,038**
- decline-review records: **4,371**
- average risk score: **56.038**

Four weekly forecast rows are generated for every item-store series. Weekly values are rounded to two decimals and any residual is allocated within the four-week row set so each item-store series reconciles exactly to its published 28-day forecast. In the compiled report, the maximum residual is only floating-point epsilon (about **2.3 × 10⁻¹³ units**) and the aggregate difference is **0.0**.

Default inventory-scenario totals:

- safety stock: **225,815.5 units**
- reorder point: **849,307.4 units**
- target stock: **1,161,040.0 units**

The default scenario uses a 14-day lead time, 7-day review period, and ABC service levels of 95% / 90% / 85%.

## Power BI consistency

The compiled template was validated after the analytical rebuild:

- **8 tables**
- **1 active relationship**
- **5 report pages**
- **67 visuals**
- **30,490** Planner Action Center rows
- **121,960** weekly forecast rows
- embedded trailing revenue: **$45,163,441.24**
- embedded 28-day forecast: **1,246,980.1 units**
- exact weekly-to-28-day reconciliation
- chronological weekly-forecast ordering
- business-facing report field names
- planner queues sorted by risk
- default scenario reconciles to the stored baseline

### Interaction behavior

On **Demand Forecast & Model Performance**, Item / Store / Demand Pattern filters apply to the routed weekly forecast. Holdout metrics, baseline backtests, and feature-importance visuals remain fixed because they are validation summaries rather than merchandise-level operating metrics.

On **Scenario Planning**, the lead-time, review-period, and service-level parameter slicers are single-select. Leaving them unselected uses the model defaults: 14-day lead time, 7-day review period, and ABC service levels. The stored row-level assumption is labeled **Baseline Service Level** so it cannot be mistaken for a selected scenario override.

### Display rounding

Power BI cards use display units and presentation rounding. Exact values in this report and in the analytical outputs are the reconciliation source. For example, the LightGBM WAPE is **45.3753%** and is displayed as **45.38%** in the report.

## Scope limitations

The public M5 data does not contain observed on-hand inventory, open purchase orders, supplier lead times, lost sales, or Walmart's actual replenishment decisions. Inventory quantities in this project are explicit planning scenarios, not observed Walmart inventory or actual reorder decisions.

The official M5 competition metric is WRMSSE. This project uses WAPE, MAE, RMSE, and bias as planner-facing diagnostics and does not present them as leaderboard-equivalent scores.

## Automated checks

The repository contains **10 unit/regression tests** covering baseline forecast behavior, metric calculations, all four demand-pattern quadrants, planning-scenario constraints, zero-baseline handling, and planner-action threshold reconciliation.

## Build evidence

- Latest analytical / Power BI build: **37141918605 — success**
- Latest code-quality run for the same source change: **37141918556 — success**
- Published PBIT blob: **f725ebeccc6a69e3d7c093b14f1a7647f54577ac**
- Published PBIT size: **3,857,765 bytes**
- Build validation: **8 tables / 1 relationship / 5 pages / 67 visuals**
