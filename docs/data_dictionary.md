# Data Dictionary

## Raw M5 inputs

### `sales_train_evaluation.csv`
| Field | Meaning |
|---|---|
| `id` | Bottom-level series identifier |
| `item_id` | Product identifier |
| `dept_id` | Department |
| `cat_id` | Category |
| `store_id` | Store |
| `state_id` | State |
| `d_1 ... d_1941` | Daily units sold |

### `calendar.csv`
Contains date, Walmart week, weekday, month, year, event names/types, and state-specific SNAP participation flags.

### `sell_prices.csv`
Weekly sell price at `store_id × item_id × wm_yr_wk` grain.

## Derived planner fields
| Field | Definition |
|---|---|
| `units_365d` | Units sold in trailing 365 days |
| `revenue_365d` | Estimated trailing revenue using weekly units × weekly sell price |
| `active_days_365d` | Number of non-zero-demand days |
| `zero_share_365d` | Share of trailing days with zero units |
| `adi` | Average demand interval |
| `cv2_nonzero_demand` | Squared CV of non-zero demand sizes |
| `demand_segment` | Smooth / Intermittent / Erratic / Lumpy |
| `abc_class` | Revenue-priority class A/B/C |
| `xyz_class` | Weekly-demand variability X/Y/Z |
| `preceding_28d_units` | Units in the 28 days before the most recent 28-day observed window |
| `prior_28d_units` | Units in the most recent 28 observed days |
| `forecast_28d_units` | Routed 28-day unit forecast |
| `forecast_unit_change` | Forecast units minus prior-28-day units |
| `forecast_growth_pct` | Conventional forecast vs prior-28-day percent change; blank when the prior period is zero |
| `recent_run_rate_change_pct` | Conventional prior-28 vs preceding-28 percent change; blank when the preceding period is zero |
| `planning_change_signal_pct` | Planner prioritization signal: forecast growth when informative, otherwise recent run-rate movement with a finite symmetric zero-baseline fallback |
| `avg_daily_forecast` | Routed 28-day forecast divided by 28; base demand-rate input for scenario calculations |
| `demand_sigma_90d` | Sample standard deviation of daily unit demand over the latest 90 observed days; exposed so Power BI what-if measures can recalculate safety stock transparently |
| `service_level_scenario` | Service-level assumption by ABC class |
| `lead_time_scenario_days` | Assumed replenishment lead time |
| `review_period_scenario_days` | Assumed review cycle |
| `safety_stock_scenario_units` | Scenario safety stock using trailing-90-day demand volatility |
| `reorder_point_scenario_units` | Scenario reorder point |
| `target_stock_scenario_units` | Scenario target stock |
| `demand_risk_score` | Heuristic 0-100 prioritization score |
| `planner_action` | Rule-based next-action recommendation |
| `forecast_model_route` | LightGBM / WeekdayAvg8 / MA28 |
| `forecast_start_date` | First day of the 28-day planning horizon |
| `forecast_end_date` | Last day of the 28-day planning horizon |

## Important limitation
The M5 public data does **not** include on-hand stock, open purchase orders, vendor lead times, or true Walmart replenishment records. Inventory fields produced by this project are explicitly scenario outputs and must not be described as observed Walmart inventory.
