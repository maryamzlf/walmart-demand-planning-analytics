# Methodology

## 1. Business objective

The analysis addresses four planning questions:
1. What is likely to sell during the next 28 days?
2. Which item-store combinations deserve the most attention?
3. Which demand patterns need different forecasting approaches?
4. How do lead time, review period, and service level change inventory coverage scenarios?

Observed M5 data and modeled planning outputs are kept separate. M5 does not provide on-hand inventory, purchase orders, supplier lead times, or lost-sales data.

## 2. Data grain and source checks

Forecasting grain: **item × store × day**.

- 30,490 item-store series
- 3,049 items
- 10 stores
- 3 states
- 3 categories / 7 departments
- 1,941 observed days, 2011-01-29 through 2016-05-22

The evaluation file is the canonical sales history. CI confirms that all 30,490 validation rows and all `d_1 ... d_1913` values exactly match the corresponding prefix of the evaluation file.

Additional checks cover duplicate keys, missing/negative sales, missing/non-positive prices, and duplicate store-item-week price records.

## 3. Demand segmentation

Each item-store series is classified over the last 365 observed days.

- **ADI** = days / non-zero demand days
- **CV²** = squared coefficient of variation of non-zero demand sizes

| Segment | ADI | CV² |
|---|---:|---:|
| Smooth | < 1.32 | < 0.49 |
| Intermittent | ≥ 1.32 | < 0.49 |
| Erratic | < 1.32 | ≥ 0.49 |
| Lumpy | ≥ 1.32 | ≥ 0.49 |

About 68% of bottom-level daily observations are zero.

## 4. ABC-XYZ

**ABC:** item-store records are ranked by trailing-365-day estimated revenue. Weekly units are multiplied by that week's sell price. Cumulative revenue defines approximately 80% A, 15% B, and 5% C.

**XYZ:** weekly demand coefficient of variation defines X ≤ 0.50, Y > 0.50 and ≤ 1.00, Z > 1.00.

## 5. Baseline backtests

Forecast horizon: 28 days. Candidate models:
- SeasonalNaive7
- MA28
- WeekdayAvg4
- WeekdayAvg8
- Trend56
- Croston SBA

Three chronological rolling folds select:
- Smooth → **WeekdayAvg8**
- Intermittent / Erratic / Lumpy → **MA28**

## 6. Priority LightGBM challenger

The highest-value 3,000 item-store series receive a global LightGBM challenger.

For the reported holdout, the priority cohort is determined **before the split** using exact trailing revenue: weekly units × the sell price for that same item-store-week, summed over the trailing 365 days. Holdout sales are never used for cohort selection.

Features include 1/7/14/28/56-day lags; 7/28/56-day rolling means; 28-day volatility; weekly sell price and 7-day price change; weekday/month/year; event and SNAP indicators; and hierarchy identifiers.

Prices are forward-filled only. Initial pre-launch prices remain unavailable (encoded as 0), rather than being filled from later weeks. Competition-provided prices for the 28-day planning horizon are treated as known covariates.

| Model | WAPE | MAE | RMSE | Bias |
|---|---:|---:|---:|---:|
| LightGBM | **45.03%** | **2.50** | **4.26** | **-0.67%** |
| MA28 | 49.46% | 2.74 | 4.86 | -1.28% |
| WeekdayAvg8 | 49.54% | 2.75 | 4.78 | -1.06% |
| SeasonalNaive7 | 56.77% | 3.15 | 5.43 | -6.16% |

Relative WAPE improvement vs MA28: **8.96%**.

## 7. Final model routing

- top 3,000 priority series → LightGBM
- remaining Smooth → WeekdayAvg8
- remaining Intermittent / Erratic / Lumpy → MA28

Final route counts: 3,000 LightGBM; 1,340 WeekdayAvg8; 26,150 MA28.

## 8. Planning scenarios

Default assumptions:
- 14-day lead time
- 7-day review period
- A/B/C service levels: 95% / 90% / 85%
- trailing-90-day daily demand volatility

`Safety Stock = z × sigma_daily × sqrt(lead_time)`

`Reorder Point = average_daily_forecast × lead_time + safety_stock`

`Target Stock = average_daily_forecast × (lead_time + review_period) + safety_stock`

These are transparent decision-support scenarios, not actual order quantities. The safety-stock calculation uses a normal-volatility approximation; for intermittent and lumpy demand it is a sensitivity tool rather than a calibrated service-level guarantee.

## 9. Planner Action Center

Risk combines ABC value, XYZ variability, demand pattern, and a planning-change signal. **Risk ≥ 70** is the report's high-risk threshold.

Forecast growth is used when informative. If a route is mechanically flat (especially MA28), recent 28-day run-rate movement is used instead. A symmetric fallback handles zero-baseline activations and drop-to-zero cases without infinite growth rates.

## 10. Evaluation scope

The official M5 competition uses WRMSSE. This project uses WAPE, MAE, RMSE, and aggregate bias because they are easier to interpret in a planning workflow. They are not presented as leaderboard-equivalent scores.

The LightGBM result is one leakage-safe 28-day priority holdout; the baseline router uses three rolling folds. A production implementation should add more rolling ML holdouts and monitoring.
