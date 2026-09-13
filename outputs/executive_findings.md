# Executive Findings

- The M5 evaluation data contains **30,490 item-store time series**, **3,049 items**, and **10 stores** across California, Texas, and Wisconsin.
- Daily demand is highly sparse: **68.0%** of bottom-level daily observations are zero.
- In the trailing 365-day planning window, **75.7%** of series are classified as intermittent and **12.3%** as lumpy.
- High-value priority forecasting benefits from a global ML challenger: leakage-safe LightGBM achieved **45.14% WAPE** versus **49.46%** for the 28-day moving-average challenger, an **8.7% relative WAPE improvement** on the priority holdout.
- LightGBM holdout bias was **-0.86%**, indicating little systematic over/under-forecasting at the aggregate priority-series level.
- The final forecasting design routes model complexity by business value: ML for the top 3,000 priority item-store series, an 8-week weekday average for remaining Smooth demand, and a 28-day moving average for the remaining sparse/volatile long tail.
- The final 28-day planning horizon totals about **1.242 million forecast units** versus **1.232 million units** in the prior 28 days, or roughly **+0.9%** at the aggregate level. This is a planning output, not an out-of-sample accuracy claim.
- Scenario inventory outputs use explicit assumptions (14-day lead time, 7-day review period, ABC-based service levels) and are **not** presented as Walmart on-hand inventory or actual reorder decisions.
