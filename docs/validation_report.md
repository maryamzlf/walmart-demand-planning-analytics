# Final Three-Pass Validation Report

**Validation date:** 2026-09-29  
**Canonical report:** `powerbi/Walmart_M5_Demand_Planning_Portfolio.pbit`

## Current status

**PASS — CURRENT PBIT PUBLISHED AND VALIDATED**

The analytical pipeline, reported metrics, and Power BI build were reviewed in three separate passes. A stale repository copy of the PBIT was identified and replaced with a fresh build validated against the metrics below.

## Pass 1 — Data integrity, leakage, and reproducibility

**Status: PASS**

Verified from a clean GitHub Actions rebuild:

- 30,490 item-store series
- 3,049 items, 10 stores, 3 states, 3 categories, 7 departments
- 1,941 observed sales days
- 66,927,173 total units
- 67.9978% zero-demand observations
- no negative or missing sales
- no duplicate series IDs or calendar-day keys
- 6,841,121 price rows
- no missing or non-positive sell prices
- unique store × item × week price keys
- validation history exactly matches `d_1 ... d_1913` in the evaluation file
- price histories are forward-filled only; later prices are not backfilled
- LightGBM is configured deterministically with fixed seeds and one thread
- code-quality workflow passes syntax checks and 9 unit/regression tests

Demand-pattern counts reproduce exactly:

| Pattern | Series |
|---|---:|
| Intermittent | 23,096 |
| Lumpy | 3,761 |
| Smooth | 2,939 |
| Erratic | 694 |

## Pass 2 — Forecasting and planning calculations

**Status: PASS**

Three rolling 28-day baseline folds select:

- Smooth → **WeekdayAvg8**
- Intermittent → **MA28**
- Erratic → **MA28**
- Lumpy → **MA28**

Priority-series holdout:

| Model | WAPE | MAE | RMSE | Bias |
|---|---:|---:|---:|---:|
| LightGBM | **45.38%** | **2.52** | **4.34** | **-1.46%** |
| MA28 | 49.46% | 2.74 | 4.86 | -1.28% |
| WeekdayAvg8 | 49.54% | 2.75 | 4.78 | -1.06% |
| SeasonalNaive7 | 56.77% | 3.15 | 5.43 | -6.16% |

Relative WAPE improvement vs MA28: **8.25%**.

Final routed plan:

- MA28: **26,150** series
- LightGBM: **3,000** series
- WeekdayAvg8: **1,340** series
- Forecast 28D: **1,246,980.1 units**
- Prior 28D: **1,231,764 units**
- Aggregate forecast growth: **+1.235%**
- Estimated revenue 365D: **$45,163,441.24**
- A-class revenue share: **79.999%**
- High-risk item-store records (risk ≥ 70): **3,712**
- High-risk revenue share: **15.693%**
- Growth review: **5,038**
- Decline review: **4,371**
- Average risk score: **56.038**

Default inventory-scenario totals:

- Safety stock: **225,815.5**
- Reorder point: **849,307.4**
- Target stock: **1,161,040.0**

The four weekly forecast rows per item-store reconcile to the 28-day forecast with a maximum difference of **0.06 units**, attributable to two-decimal weekly export rounding.

## Pass 3 — Power BI and presentation consistency

**Status: PASS**

The current-head Power BI build completed compilation, package validation, repository publication, and artifact upload successfully:

- **8 tables**
- **1 active relationship**
- **5 pages**
- **67 visuals**
- **30,490** Planner Action Center rows
- **121,960** weekly forecast rows
- business-facing visual field names
- chronological weekly forecast ordering
- fixed validation KPIs intentionally disconnected from merchandise slicers
- default Scenario Planning state reconciles to the stored baseline
- embedded planner revenue: **$45,163,441.24**
- embedded 28-day forecast: **1,246,980.1 units**

The previous PBIT in the repository contained an earlier validated run and therefore did not match the current analytical evidence. It was replaced. Older dashboard screenshots with superseded KPI values are excluded from the canonical report.

## Presentation-language review

No public-facing documentation contains prompt text, assistant-style meta commentary, or generation claims. README and documentation wording was reviewed for specific analytical language rather than generic promotional language.

Technical terms such as **leakage control**, **rolling holdout**, **ABC-XYZ**, **ADI/CV²**, **WAPE**, and **scenario planning** are retained because they describe the methodology.

## Interpretation boundary

M5 does not provide observed on-hand inventory, open purchase orders, supplier lead times, lost sales, or Walmart's actual replenishment decisions. Inventory quantities in this project are planning scenarios, not statements about Walmart's real inventory policy.

The official M5 competition metric is WRMSSE. This project uses WAPE, MAE, RMSE, and bias as planner-facing diagnostics and does not present them as leaderboard-equivalent scores.


## Final build evidence

- GitHub Actions build run: **36620592616 — success**
- Published PBIT blob: **cd3732048d4262fc3340018b8f94347a0bf20a7e**
- Published PBIT size: **3,857,605 bytes**
- Code-quality run on the reviewed source commit: **36620592519 — success**
