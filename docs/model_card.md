# Model Card: Priority-Series LightGBM

## Intended use
Forecast the next 28 days of unit demand for the highest-value item-store combinations in the M5 retail dataset. The model is a planning-support challenger, not an autonomous ordering system.

## Training design
- Global model across 3,000 priority item-store series
- Trailing daily history with lag and rolling-window features
- Tweedie regression objective
- Recursive 28-day forecast
- Calendar, event, SNAP, and price covariates

## Leakage controls
For the reported holdout result, priority series were ranked using only data available before the holdout. Lag and rolling features are shifted so the target day is never included in its own predictors.

## Holdout performance
- WAPE: 45.31%
- MAE: 2.52 units/day-series
- RMSE: 4.33
- Bias: -0.89%

Compared with the 28-day moving-average challenger (49.46% WAPE), the model improved WAPE by 8.4% on the priority holdout.

## Most influential feature groups
The fitted model is dominated by recent demand level and recency signals, particularly 7-day and 28-day rolling demand, followed by lagged demand, item identity, weekday, variability, and price.

## Known limitations
- Demand is zero-heavy and forecast errors remain material at the individual item-store-day level.
- The public dataset ends in 2016; the project demonstrates methodology, not current Walmart performance.
- Price is observed weekly, so intra-week price variation cannot be modeled.
- No on-hand inventory or supplier constraints are available.
- Recursive forecasting can compound error across the 28-day horizon.

## Governance choice
A simpler forecast is retained for the long tail unless the ML challenger demonstrates sufficient value. This limits unnecessary complexity and makes the model-routing logic explainable to planners.
