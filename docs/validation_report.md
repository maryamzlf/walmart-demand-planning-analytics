# Final Three-Pass Validation Report

**Validation date:** 2026-09-28  
**Scope:** Data, forecasting, planning logic, tracked evidence, Power BI model, and presentation consistency.

## Final status

**PASS — canonical deliverable: `powerbi/Walmart_M5_Demand_Planning_Portfolio.pbit`.**

The project was reviewed in three separate passes. The audit found two stale presentation artifacts from an older Power BI snapshot: its LightGBM bias card showed **-0.2%** instead of the current **-0.86%**, and its default scenario showed a **43-unit** target-stock delta even though the default scenario is the baseline. That stale `.pbix` and the two affected screenshots were removed from the current repository. The canonical `.pbit` uses the current model metrics and forces the default scenario to reconcile exactly to baseline.

## Pass 1 — Data, leakage, and reproducibility

**Status: PASS**

A fresh GitHub Actions build downloaded the public M5 source data and regenerated the analysis from scratch.

Validated:
- 30,490 unique item-store series
- 3,049 items; 10 stores; 3 states; 3 categories; 7 departments
- 1,941 observed sales days
- 66,927,173 total units
- 67.9978% zero-demand observations
- no negative or missing sales values
- 6,841,121 sell-price rows; no missing or non-positive sell prices
- unique store × item × week price keys
- validation history is an exact prefix of the evaluation history
- price preparation is forward-fill only; no future-price backfill
- priority-series selection for the holdout uses only pre-holdout data

Demand-pattern counts reproduced:
- Intermittent: **23,096**
- Lumpy: **3,761**
- Smooth: **2,939**
- Erratic: **694**

## Pass 2 — Forecasting, planning logic, and numerical reconciliation

**Status: PASS**

Three chronological 28-day baseline folds continue to support:
- Smooth → **WeekdayAvg8**
- Intermittent → **MA28**
- Erratic → **MA28**
- Lumpy → **MA28**

Priority holdout metrics:

| Model | WAPE | RMSE | Bias |
|---|---:|---:|---:|
| LightGBM | **45.14%** | **4.30** | **-0.86%** |
| MA28 | 49.46% | 4.86 | -1.25% |
| WeekdayAvg8 | 49.53% | 4.78 | -1.07% |
| SeasonalNaive7 | 56.75% | 5.44 | -6.12% |

Relative WAPE improvement vs MA28: **8.74%**.

Final routing:
- MA28: **26,150**
- LightGBM: **3,000**
- WeekdayAvg8: **1,340**

Verified unfiltered planning totals:
- Forecast 28D: **1,242,423.1 units**
- Prior 28D: **1,231,764 units**
- Aggregate growth: **+0.865%**
- Revenue 365D: **$45,163,441.21**
- Units 365D: **14,585,821**
- A-class revenue share: **~80.0%**
- High-risk item-store count (risk >= 70): **3,876**
- Growth review count (planning signal >= 20): **5,028**
- Decline review count (planning signal <= -20): **4,358**
- Average risk score: **56.293**
- Baseline safety stock: **225,815.5 units**
- Baseline reorder point: **847,028.3 units**
- Baseline target stock: **1,157,623.9 units**

Weekly forecast totals:
- 2016-05-23: **304,629.23**
- 2016-05-30: **313,010.08**
- 2016-06-06: **317,923.50**
- 2016-06-13: **306,863.57**

Weekly item-store forecasts reconcile to the 28-day item-store totals within the expected two-decimal export tolerance.

## Pass 3 — Power BI, documentation, and presentation consistency

**Status: PASS**

The compiled Power BI template is validated automatically after every build:
- **8 tables**
- **1 active relationship**
- **5 report pages**
- **67 visuals**
- 30,490 Planner Action Center rows
- 121,960 weekly forecast rows
- 4 weekly rows per item-store series
- no infinite numeric values in the embedded planner data
- embedded holdout metrics exactly match regenerated source metrics
- business-facing field names are used in report visuals
- default scenario measures resolve to the stored baseline
- priority queues use deterministic risk-first, revenue-second sorting

The page-2 diagnostic tables are intentionally disconnected. Merchandise slicers can change the routed weekly forecast, while fixed holdout/backtest charts remain validation summaries.

### Presentation corrections made during this audit
- Removed the stale `.pbix` snapshot that no longer matched the validated model.
- Removed two stale screenshots that contained the old bias/default-scenario values.
- Made the validated `.pbit` the canonical downloadable report.
- Standardized visible labels such as **Growth vs Prior**, **High-Risk Item-Store**, **Planner Action Queue**, **Top 8 Forecast Drivers**, and **Target Stock Change**.
- Synchronized generated evidence files with the fresh CI build.
- Removed the earlier synthetic dashboard preview; the README uses only screenshots captured from Power BI.

## AI / authorship presentation check

Repository content was searched for explicit AI-assistant markers including **ChatGPT**, **OpenAI**, **LLM**, **prompt**, and **assistant**. No such markers are present in project code or documentation. GitHub Actions bot commits are standard CI automation and are not presented as analytical authorship.

## Interpretation boundary

M5 does not contain observed on-hand inventory, open purchase orders, vendor lead times, or actual Walmart replenishment decisions. Safety stock, reorder point, and target stock are therefore scenario-based decision-support calculations, not claims about Walmart's actual inventory policy.

## Conclusion

The analytical results, tracked evidence, and canonical Power BI template are internally consistent. The project is suitable for portfolio use with the validated `.pbit` as the source of truth.
