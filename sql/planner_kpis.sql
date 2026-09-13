/* Assumption: planner_action_center.csv has been loaded to a table named planner_action_center. SQL Server-compatible portfolio queries. */

-- Executive KPI summary
SELECT
    SUM(forecast_28d_units) AS forecast_units_next_28d,
    SUM(prior_28d_units) AS prior_units_28d,
    100.0 * (SUM(forecast_28d_units) - SUM(prior_28d_units)) / NULLIF(SUM(prior_28d_units), 0) AS forecast_growth_pct,
    SUM(CASE WHEN abc_class = 'A' THEN revenue_365d ELSE 0 END) / NULLIF(SUM(revenue_365d), 0) AS a_class_revenue_share,
    SUM(CASE WHEN demand_risk_score >= 75 THEN 1 ELSE 0 END) AS high_risk_item_store_count
FROM planner_action_center;

-- Department planning view
SELECT dept_id, SUM(revenue_365d) AS revenue_365d, SUM(prior_28d_units) AS prior_28d_units,
       SUM(forecast_28d_units) AS forecast_28d_units,
       100.0 * (SUM(forecast_28d_units) - SUM(prior_28d_units)) / NULLIF(SUM(prior_28d_units), 0) AS growth_pct,
       AVG(demand_risk_score) AS avg_demand_risk_score
FROM planner_action_center
GROUP BY dept_id
ORDER BY revenue_365d DESC;

-- ABC-XYZ matrix
SELECT abc_xyz, COUNT(*) AS item_store_count, SUM(revenue_365d) AS revenue_365d,
       SUM(forecast_28d_units) AS forecast_28d_units, AVG(demand_risk_score) AS avg_demand_risk_score
FROM planner_action_center
GROUP BY abc_xyz
ORDER BY abc_xyz;

-- Planner action queue
SELECT TOP 100 item_id, store_id, dept_id, cat_id, abc_xyz, demand_segment, revenue_365d,
       preceding_28d_units, prior_28d_units, forecast_28d_units, forecast_growth_pct,
       recent_run_rate_change_pct, planning_change_signal_pct, demand_risk_score,
       safety_stock_scenario_units, reorder_point_scenario_units, forecast_model_route, planner_action
FROM planner_action_center
ORDER BY demand_risk_score DESC, revenue_365d DESC;

-- High-value planning inflections. Use the planning signal rather than literal
-- forecast growth so MA28-routed series are not structurally hidden at 0%.
SELECT item_id, store_id, dept_id, abc_xyz, preceding_28d_units, prior_28d_units,
       forecast_28d_units, forecast_growth_pct, planning_change_signal_pct, planner_action
FROM planner_action_center
WHERE abc_class = 'A' AND ABS(planning_change_signal_pct) >= 20
ORDER BY ABS(planning_change_signal_pct) DESC;
