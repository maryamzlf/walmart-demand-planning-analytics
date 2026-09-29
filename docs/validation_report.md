# Final Three-Pass Validation Report

**Validation date:** 2026-09-29  
**Canonical deliverable:** `powerbi/Walmart_M5_Demand_Planning_Portfolio.pbit`

## Final status

**PASS**

The project was rerun from public M5 source files and reviewed in three independent passes: source/reproducibility, model/planning calculations, and Power BI/presentation consistency.

## Pass 1 — Data integrity, leakage, and reproducibility

**Status: PASS**

Verified in a fresh CI build:
- 30,490 item-store series
- 1,941 observed sales days
- 66,927,173 total units
- 67.9978% zero-demand observations
- no negative or missing sales
- no duplicate series IDs or calendar-day keys
- 6,841,121 price rows
- no missing or non-positive sell prices
- unique store × item × week price keys
- validation history exactly matches `d_1 ... d_1913` in the evaluation file for all 30,490 series
- forward-fill only for price histories; no future-price backfill
- exact trailing pre-holdout revenue for ML priority selection

Demand-pattern counts reproduced:
- Intermittent: **23,096**
- Lumpy: **3,761**
- Smooth: **2,939**
- Erratic: **694**

Code quality passed syntax checks, **9 tests**, and a repository-content check for obvious assistant/AI attribution language.

## Pass 2 — Forecasting and planning calculations

**Status: PASS**

Three rolling 28-day baseline folds still select:
- Smooth → **WeekdayAvg8**
- Intermittent → **MA28**
- Erratic → **MA28**
- Lumpy → **MA28**

The priority holdout cohort was corrected to use the same value definition as final routing: exact trailing revenue rather than unit volume × average price.

| Model | WAPE | MAE | RMSE | Bias |
|---|---:|---:|---:|---:|
| LightGBM | **45.03%** | **2.50** | **4.26** | **-0.67%** |
| MA28 | 49.46% | 2.74 | 4.86 | -1.28% |
| WeekdayAvg8 | 49.54% | 2.75 | 4.78 | -1.06% |
| SeasonalNaive7 | 56.77% | 3.15 | 5.43 | -6.16% |

Relative WAPE improvement vs MA28: **8.96%**.

Final routing:
- MA28: **26,150**
- LightGBM: **3,000**
- WeekdayAvg8: **1,340**

Verified planning totals:
- Forecast 28D: **1,242,423.1**
- Prior 28D: **1,231,764**
- Growth: **+0.865%**
- Estimated revenue 365D: **$45,163,441.21**
- Units 365D: **14,585,821**
- A-class revenue share: **79.999%**
- High-risk records (risk ≥ 70): **3,876**
- High-risk estimated-revenue share: **16.63%**
- Growth review: **5,028**
- Decline review: **4,358**
- Average risk score: **56.293**
- Baseline safety stock: **225,815.5**
- Baseline reorder point: **847,028.3**
- Baseline target stock: **1,157,623.9**

Weekly forecast totals:
- 2016-05-23: **304,629.23**
- 2016-05-30: **313,010.08**
- 2016-06-06: **317,923.50**
- 2016-06-13: **306,863.57**

At item-store level, the four exported weekly values reconcile to the 28-day forecast within **0.06 units**, consistent with two-decimal weekly rounding.

## Pass 3 — Power BI and presentation consistency

**Status: PASS**

The compiled template is checked for:
- **8 tables**
- **1 active relationship**
- **5 pages**
- **67 visuals**
- 30,490 Planner Action Center rows
- 121,960 weekly forecast rows
- four weekly rows per item-store
- no infinite values in embedded planner data
- embedded model metrics equal the regenerated CSV metrics
- chronological weekly-chart sort
- business-facing field names in report visuals
- deterministic risk-first action queues
- default Scenario Planning values equal stored baseline
- feature-importance visual bound to the full feature table

Corrections made in this review:
- replaced the holdout revenue proxy with exact pre-holdout trailing revenue
- updated reported model metrics to the corrected holdout
- added raw-source duplicate/price/history checks to CI
- removed the stale Executive screenshot because its WAPE card showed the previous holdout result
- kept older PBIX snapshots out of the canonical deliverables
- removed an unused Top-8 feature-filter transformation
- simplified internal build-tool and workflow names

Only screenshots whose KPIs still match the current run remain in the README.

## Interpretation boundary

M5 does not provide observed on-hand inventory, open purchase orders, supplier lead times, lost sales, or Walmart's actual replenishment decisions. Inventory quantities in the report are planning scenarios, not statements about Walmart's real inventory policy.
