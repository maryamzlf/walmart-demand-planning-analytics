# Methodology

## 1. Business objective
The project converts historical Walmart unit sales, price, calendar, event, and SNAP information into a planner-facing workflow for four questions:

1. What is likely to sell during the next 28 days?
2. Which item-store combinations deserve the most planning attention?
3. Which demand patterns require different forecasting approaches?
4. What inventory coverage would be appropriate under explicit service-level and lead-time scenarios?

The repository deliberately separates **observed Walmart data** from **scenario-based planning outputs**. M5 does not provide on-hand inventory, purchase orders, supplier lead times, or actual Walmart replenishment decisions. Safety stock, reorder point, and target stock are therefore planning scenarios, not claims about Walmart's internal inventory.

## 2. Data grain and scope
The bottom-level forecasting grain is **item × store × day**.

- 30,490 item-store series
- 3,049 unique items
- 10 stores
- 3 states: CA, TX, WI
- 3 categories and 7 departments
- 1,941 observed selling days from 2011-01-29 through 2016-05-22

The evaluation sales file is used as the canonical source because it already contains the full validation history. A full chunkwise equality check confirms that all 30,490 validation series and all `d_1 ... d_1913` values are identical to the corresponding prefix of the evaluation file.

## 3. Demand segmentation
A one-model-fits-all approach performs poorly on sparse retail demand, so each item-store series is classified using the last 365 observed days.

Two statistics are calculated:
- **ADI (Average Demand Interval)** = number of days / number of non-zero demand days
- **CV²** = squared coefficient of variation of non-zero demand sizes

| Segment | ADI | CV² |
|---|---:|---:|
| Smooth | < 1.32 | < 0.49 |
| Intermittent | >= 1.32 | < 0.49 |
| Erratic | < 1.32 | >= 0.49 |
| Lumpy | >= 1.32 | >= 0.49 |

This dataset is strongly intermittent: roughly 68% of daily item-store observations are zero.

## 4. Value and variability segmentation
### ABC
Item-store combinations are ranked by trailing-365-day estimated revenue. Cumulative revenue defines A as approximately the first 80%, B as the next 15%, and C as the final 5%.

### XYZ
Weekly demand variability is measured with coefficient of variation: X <= 0.50; Y > 0.50 and <= 1.00; Z > 1.00.

ABC-XYZ is used for prioritization rather than as a forecasting target.

## 5. Forecast backtesting
Forecasts use a 28-day horizon with rolling-origin backtests. Candidates are 7-day seasonal naive, 28-day moving average, 4-week weekday average, 8-week weekday average, 56-day trend, and Croston SBA.

Across three rolling 28-day folds, the strongest simple rules were:
- **Smooth:** 8-week weekday average
- **Intermittent / Erratic / Lumpy:** 28-day moving average

Croston SBA remains in the benchmark even though it was not selected; model choice is evidence-driven.

## 6. Priority-series machine learning challenger
The highest-value 3,000 item-store series receive a global LightGBM challenger. Priority series for the holdout test are selected only from the trailing period available before the holdout, preventing target leakage.

Features: 1/7/14/28/56-day lags; 7/28/56-day rolling means; 28-day volatility; current price and 7-day price change; weekday/month/year; event and SNAP indicators; and item/store/department/category/state identifiers.

The model uses a Tweedie objective for non-negative, zero-heavy demand.

Price handling is explicitly leakage-safe. Weekly prices are forward-filled only; an initial missing price is encoded as `0` (unavailable) rather than backfilled from a later week. For the 28-day future M5 horizon, the competition-provided future weekly prices are treated as known planning covariates.

| Model | WAPE | RMSE | Bias |
|---|---:|---:|---:|
| LightGBM | 45.14% | 4.30 | -0.86% |
| 28-day moving average | 49.46% | 4.86 | -1.25% |
| 8-week weekday average | 49.53% | 4.78 | -1.07% |
| 7-day seasonal naive | 56.75% | 5.44 | -6.12% |

LightGBM reduced WAPE by **8.7% relative to the 28-day moving-average challenger**.

## 7. Forecast routing
- Top 3,000 priority item-store series: LightGBM
- Remaining Smooth series: 8-week weekday average
- Remaining Intermittent, Erratic, and Lumpy series: 28-day moving average

This concentrates model complexity where it creates the most business value.

## 8. Scenario-based inventory planning
Because M5 contains no on-hand inventory or supplier lead time, the project does not calculate actual order quantities.

Assumptions: 14-day lead time, 7-day review period, 95% service for A, 90% for B, and 85% for C. Daily demand volatility uses the trailing 90 observed days.

`Safety Stock = z × sigma_daily × sqrt(lead_time)`

`Reorder Point = average_daily_forecast × lead_time + safety_stock`

`Target Stock = average_daily_forecast × (lead_time + review_period) + safety_stock`

These are decision-support scenarios only.

## 9. Planner Action Center
Each item-store record receives a demand-risk score from value class, variability, demand pattern, and a planning-change signal. Ordinary forecast growth is retained when informative. When a forecast is mechanically flat (notably the MA28 route), the signal uses recent 28-day run-rate movement instead. A symmetric-change fallback keeps zero-baseline activations and drop-to-zero cases finite rather than silently turning them into missing values.

Rule-based actions direct attention toward high-value growth, potential excess exposure, volatile/lumpy demand, and long-tail inventory risk. This turns forecast output into a planning workflow rather than stopping at prediction accuracy.

## 10. Reproducibility
The scripts regenerate the portfolio evidence files:
- `backtest.py` writes both fold-level results and `outputs/baseline_model_summary.csv`.
- `priority_model.py` writes holdout metrics and feature importance.
- `final_forecast.py` writes the Power BI-ready large tables plus `outputs/segment_summary.csv` and `outputs/planner_action_sample.csv`.

Raw and large processed data remain excluded from Git and are regenerated from the public M5 source files.
