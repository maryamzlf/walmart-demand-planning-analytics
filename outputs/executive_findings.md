# Executive Findings

- The M5 evaluation data contains **30,490 item-store time series**, **3,049 items**, and **10 stores** across California, Texas, and Wisconsin.
- **68.0%** of bottom-level daily observations are zero.
- Over the trailing 365-day planning window, **75.7%** of series are Intermittent and **12.3%** are Lumpy.
- On the leakage-safe priority holdout, LightGBM reached **45.03% WAPE** versus **49.46%** for MA28, an **8.96% relative improvement**. The 3,000-series cohort is selected using exact trailing pre-holdout revenue.
- LightGBM holdout bias was **-0.67%**.
- Final routing uses LightGBM for 3,000 priority series, WeekdayAvg8 for 1,340 remaining Smooth series, and MA28 for 26,150 remaining series.
- The final 28-day plan is **1,242,423.1 forecast units** versus **1,231,764 prior-period units**, about **+0.87%** overall.
- **3,876** item-store records have risk ≥ 70 and account for **16.63%** of trailing estimated revenue.
- Inventory quantities are scenarios based on a 14-day lead time, 7-day review period, and ABC service levels; they are not observed Walmart inventory or actual reorder decisions.
