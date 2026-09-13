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
| `forecast_28d_units` | Routed 28-day unit forecast |
| `forecast_growth_pct` | Forecast vs prior 28-day units |
| `service_level_scenario` | Service-level assumption by ABC class |
| `safety_stock_scenario_units` | Scenario-based safety stock |
| `reorder_point_scenario_units` | Scenario-based reorder point |
| `target_stock_scenario_units` | Scenario-based target stock |
| `demand_risk_score` | Heuristic 0-100 prioritization score |
| `planner_action` | Rule-based next-action recommendation |

## Important limitation
The M5 public data does **not** include on-hand stock, open purchase orders, vendor lead times, or true Walmart replenishment records. Inventory fields produced by this project are explicitly scenario outputs and must not be described as observed Walmart inventory.
