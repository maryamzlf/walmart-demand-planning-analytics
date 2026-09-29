# Model Card: Priority-Series LightGBM

## Intended use

Forecast 28 days of unit demand for the 3,000 highest-value item-store series in the M5 dataset. The model supports planning analysis; it is not an autonomous ordering system.

## Training design

- one global model across 3,000 priority series
- Tweedie regression objective
- recursive 28-day forecast
- lag and rolling-demand features
- calendar, event, SNAP, price, and hierarchy covariates

## Holdout cohort and leakage controls

Priority series are ranked by **exact trailing revenue available before the holdout**: weekly units × the sell price for the same item-store-week, summed over the trailing 365 days.

Lag/rolling features are shifted so the target day is never included in its predictors. Prices are forward-filled only; later prices are not backfilled into earlier weeks.

## Holdout performance

- WAPE: **45.03%**
- MAE: **2.50** units per item-store-day
- RMSE: **4.26**
- Bias: **-0.67%**
- MA28 WAPE: **49.46%**
- relative WAPE improvement vs MA28: **8.96%**

## Feature behavior

Recent demand dominates feature gain. The largest contributors are the 7-day rolling mean, 28-day rolling mean, lag-1 demand, item identity, 56-day rolling mean, weekday, and recent volatility. Feature importance is descriptive of this fitted model and should not be read as causal effect.

## Validation scope

The ML challenger is reported on one leakage-safe 28-day priority holdout. The simple-model router is evaluated on three rolling 28-day folds. Production use would require additional rolling ML holdouts and ongoing monitoring.

## Limitations

- demand is zero-heavy and item-store-day error remains material
- the public data ends in 2016
- sell price is weekly
- future-horizon M5 prices are treated as known covariates
- on-hand inventory, open POs, vendor lead times, and supplier constraints are unavailable
- recursive forecasting can compound error across the horizon

The official M5 leaderboard uses WRMSSE. WAPE/MAE/RMSE/bias here are planning diagnostics, not leaderboard scores.
