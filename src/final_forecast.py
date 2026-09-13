from pathlib import Path
import numpy as np
import pandas as pd

from common import load_m5, sales_array, forecast_moving_average, forecast_weekday_average
from segmentation import build_segmentation
from priority_model import _prepare_subset, _encodings, _training_frame, _fit, _recursive
from planning_outputs import add_planning_scenarios, save_planning_outputs


def generate_final_forecast(raw_dir="data/raw", processed_dir="data/processed",
                            portfolio_output_dir="outputs", horizon=28, n_priority=3000):
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    sales, calendar, prices, dcols = load_m5(raw_dir)
    arr = sales_array(sales, dcols)

    seg_path = processed_dir / "segmentation.csv"
    segmentation = pd.read_csv(seg_path) if seg_path.exists() else build_segmentation(raw_dir, seg_path)
    priority_idx = segmentation.nlargest(n_priority, "revenue_365d").index.to_numpy()

    forecast = forecast_moving_average(arr, 28, horizon)
    smooth = segmentation.demand_segment.eq("Smooth").to_numpy()
    forecast[smooth] = forecast_weekday_average(arr[smooth], 8, horizon)

    meta, y, cal, daily_price = _prepare_subset(priority_idx, sales, calendar, prices, arr, max_day=1969)
    codes, event, snap = _encodings(meta, cal)
    X, target = _training_frame(y, cal, daily_price, codes, event, snap, 1478, 1941)
    model = _fit(X, target)
    priority_forecast = _recursive(model, y, cal, daily_price, codes, event, snap, 1941, horizon)
    forecast[priority_idx] = priority_forecast

    planning = add_planning_scenarios(segmentation, arr, forecast)
    route = np.full(len(planning), "MA28", dtype=object)
    route[smooth] = "WeekdayAvg8"
    route[priority_idx] = "LightGBM"
    planning["forecast_model_route"] = route
    planning["forecast_start_date"] = str(calendar.loc[calendar.d == "d_1942", "date"].iloc[0])
    planning["forecast_end_date"] = str(calendar.loc[calendar.d == "d_1969", "date"].iloc[0])
    save_planning_outputs(planning, processed_dir / "planner_action_center.csv")

    weekly = []
    future_dates = calendar.set_index("d").loc[[f"d_{i}" for i in range(1942, 1970)], "date"].to_numpy()
    for week in range(4):
        block = forecast[:, week*7:(week+1)*7].sum(axis=1)
        frame = sales[["id","item_id","dept_id","cat_id","store_id","state_id"]].copy()
        frame["forecast_week"] = week + 1
        frame["week_start_date"] = future_dates[week*7]
        frame["forecast_units"] = np.round(block, 2)
        weekly.append(frame)
    pd.concat(weekly, ignore_index=True).to_csv(processed_dir / "forecast_weekly_item_store.csv", index=False)

    portfolio_output_dir = Path(portfolio_output_dir)
    portfolio_output_dir.mkdir(parents=True, exist_ok=True)
    segment_summary = (
        planning.groupby("demand_segment", as_index=False)
        .agg(
            series=("id", "count"),
            units_365d=("units_365d", "sum"),
            revenue_365d=("revenue_365d", "sum"),
            forecast_28d_units=("forecast_28d_units", "sum"),
            avg_demand_risk_score=("demand_risk_score", "mean"),
        )
    )
    segment_summary["revenue_share_pct"] = (
        100.0 * segment_summary.revenue_365d / segment_summary.revenue_365d.sum()
    )
    segment_summary.to_csv(portfolio_output_dir / "segment_summary.csv", index=False)

    sample_cols = [
        "item_id", "store_id", "dept_id", "cat_id", "abc_xyz", "demand_segment",
        "revenue_365d", "preceding_28d_units", "prior_28d_units", "forecast_28d_units",
        "forecast_growth_pct", "recent_run_rate_change_pct", "planning_change_signal_pct",
        "demand_risk_score", "safety_stock_scenario_units", "reorder_point_scenario_units",
        "forecast_model_route", "planner_action",
    ]
    (
        planning.sort_values(["demand_risk_score", "revenue_365d"], ascending=[False, False])
        .head(20)[sample_cols]
        .to_csv(portfolio_output_dir / "planner_action_sample.csv", index=False)
    )
    return planning, forecast


if __name__ == "__main__":
    planning, _ = generate_final_forecast()
    print(planning[["forecast_28d_units","prior_28d_units"]].sum())
    print(planning.forecast_model_route.value_counts())
