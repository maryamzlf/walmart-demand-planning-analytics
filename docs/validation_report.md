# Final Three-Stage Validation Report

**Validation date:** 2026-09-13  
**Scope:** Full pre-Power-BI review of the Walmart M5 demand-planning portfolio project.

## Result

**PASS — ready for the Power BI build.**

The full workflow was rerun from the raw M5 ZIP through final planner outputs. Two substantive issues were found during the review and corrected before this report was finalized:

1. **Potential price look-ahead:** early missing weekly prices were previously backfilled from later weeks. Price preparation now forward-fills only and encodes initial missing/pre-launch prices as unavailable (`0`).
2. **Zero-baseline planning signal:** flat MA28 forecasts and zero-denominator periods could suppress meaningful planner movement. The action layer now uses recent run-rate movement plus a finite symmetric zero-baseline fallback.

The documentation, SQL, tests, and reproducible portfolio outputs were then synchronized to the corrected logic.

## Stage 1 — Data integrity & reproducibility

Status: **PASS**

Validated directly from `m5-forecasting-accuracy.zip`:

- 30,490 unique item-store series
- 3,049 items, 10 stores, 3 states, 3 categories, 7 departments
- 1,941 observed sales days; 66,927,173 total units
- 68.0% zero-demand observations
- no negative sales values
- no missing sales values
- 6,841,121 price rows with no missing or non-positive prices
- no duplicate `store_id × item_id × wm_yr_wk` price keys
- 1,969 unique and contiguous calendar day keys (`d_1 ... d_1969`)
- no duplicate item-store series IDs
- full chunkwise equality check confirms all 30,490 validation rows and all `d_1 ... d_1913` values are exactly contained in the evaluation file after normalizing the official `_validation` / `_evaluation` ID suffixes
- segmentation regenerated successfully with no missing ABC / XYZ / demand-pattern classes
- ABC modeled-revenue shares reproduce approximately 80% / 15% / 5%

Demand-pattern counts reproduced exactly:

| Segment | Series |
|---|---:|
| Intermittent | 23,096 |
| Lumpy | 3,761 |
| Smooth | 2,939 |
| Erratic | 694 |

## Stage 2 — Forecasting, leakage controls & planner logic

Status: **PASS**

### Rolling baseline backtests
Three chronological 28-day folds were rerun. The evidence-based routing remains:

- Smooth → `WeekdayAvg8` (48.26% average WAPE)
- Intermittent → `MA28` (92.18%)
- Erratic → `MA28` (66.56%)
- Lumpy → `MA28` (94.25%)

### Priority LightGBM holdout
The leakage-safe 3,000-series holdout was rerun twice with deterministic settings and reproduced the same metrics:

| Model | WAPE | RMSE | Bias |
|---|---:|---:|---:|
| LightGBM | **45.14%** | **4.30** | **-0.86%** |
| MA28 | 49.46% | 4.86 | -1.25% |
| WeekdayAvg8 | 49.53% | 4.78 | -1.07% |
| SeasonalNaive7 | 56.75% | 5.44 | -6.12% |

Relative WAPE improvement vs MA28: **8.74%**.

### Leakage review
- Priority-series ranking uses only pre-holdout sales and prices.
- Lag and rolling features do not include the target day.
- Weekly price preparation no longer backfills from future weeks.
- Before the fix, 4,191 training-day price cells across 44 priority series lacked a contemporaneous price; all corresponding target units were zero. These cells are now encoded as unavailable rather than filled with a future price.
- No selected priority series has missing price coverage in the 28-day holdout or final 28-day M5 forecast horizon.

### Final routed forecast & planner outputs
Routes reproduced exactly:

- MA28: 26,150 series
- LightGBM: 3,000 series
- WeekdayAvg8: 1,340 series

Final planning-horizon totals:

- Forecast units: **1,242,423.1**
- Prior 28-day units: **1,231,764**
- Aggregate planning change: **+0.87%**

Output invariants all passed:

- no negative forecasts
- risk score always finite and between 0 and 100
- planning-change signal finite for all 30,490 series
- safety stock non-negative
- reorder point ≥ safety stock
- target stock ≥ reorder point
- service-level mapping matches ABC classes
- only approved planner-action labels are emitted
- four weekly forecast rows exist for every item-store series
- weekly and 28-day forecasts reconcile within expected CSV rounding tolerance (maximum absolute difference 0.06 units)

## Stage 3 — Engineering, documentation & portfolio consistency

Status: **PASS**

- all Python source and test files pass `py_compile`
- **9/9** lightweight regression/unit tests pass
- baseline forecast utilities and all four ADI/CV² demand-pattern quadrants are tested
- zero-baseline and MA28 planning-signal edge cases are tested
- invalid planning horizon and invalid lead-time inputs are rejected
- raw and large processed files remain excluded from Git
- scripts now regenerate the tracked portfolio evidence files for baseline summaries, priority-model metrics, feature importance, segment summaries, and planner-action samples
- data dictionary documents the current planner-output schema
- SQL action queries use the planning-change signal so MA28-routed series are not structurally hidden at 0% literal forecast growth
- Power BI specification references the corrected fields and current model outputs
- all model-performance numbers in README, methodology, model card, and executive findings are aligned to the final leakage-safe run

## Two additional independent repeat passes

After the final three-stage validation above, the analytical pipeline was independently recomputed **two more times in fresh Python processes** from the raw M5 evaluation, calendar, and price files. Each repeat separately executed the data checks, demand segmentation, three rolling baseline folds, leakage-safe LightGBM holdout, final LightGBM route, scenario-planning logic, and output invariants.

Both repeats returned **PASS** and were numerically identical:

- zero-demand share: **67.9978%**
- demand-pattern counts: 23,096 Intermittent; 3,761 Lumpy; 2,939 Smooth; 694 Erratic
- baseline routing: Smooth → WeekdayAvg8; all other demand segments → MA28
- LightGBM holdout WAPE: **45.1408%**
- MA28 holdout WAPE: **49.4629%**
- relative WAPE improvement: **8.7379%**
- final route counts: 26,150 MA28; 3,000 LightGBM; 1,340 WeekdayAvg8
- final 28-day forecast: **1,242,423.125 units**
- prior 28-day units: **1,231,764**
- aggregate planning change: **+0.8654%**
- maximum weekly-to-28-day reconciliation difference: **0.0601 units**
- deterministic final-output fingerprint was identical in both runs: `587214ccbf0dc2865059e4f31ee1b46233766dd3c9be77b982431a8ac58c8364`

This repeatability check provides an additional control against transient execution differences or accidental non-determinism before the Power BI layer is built.

## Pre-Power-BI conclusion

The analytical foundation is internally consistent, reproducible, and suitable for portfolio presentation. Remaining work is the **Power BI visualization/data-model layer**, not a correction to the forecasting or planning foundation.
