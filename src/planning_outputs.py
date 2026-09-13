from pathlib import Path
import numpy as np
import pandas as pd

Z = {"A": 1.645, "B": 1.282, "C": 1.036}


def _safe_change(current, reference):
    """Percent change with an explicit zero-base policy.

    A zero reference is left undefined rather than reported as an infinite
    growth rate. The action engine uses the absolute unit change as a fallback.
    """
    current = np.asarray(current, dtype=float)
    reference = np.asarray(reference, dtype=float)
    return np.divide(
        current - reference,
        reference,
        out=np.full(current.shape, np.nan, dtype=float),
        where=reference > 0,
    )


def _symmetric_change(current, reference):
    """Finite directional change signal in [-2, 2].

    Unlike conventional percent change, this remains defined when one side of
    the comparison is zero. It is used only for planner prioritization fallbacks,
    not as the reported forecast-growth percentage.
    """
    current = np.asarray(current, dtype=float)
    reference = np.asarray(reference, dtype=float)
    denom = np.abs(current) + np.abs(reference)
    return np.divide(
        2.0 * (current - reference),
        denom,
        out=np.zeros(current.shape, dtype=float),
        where=denom > 0,
    )


def add_planning_scenarios(
    segmentation: pd.DataFrame,
    sales_array: np.ndarray,
    forecast: np.ndarray,
    lead_time_days=14,
    review_period_days=7,
):
    if lead_time_days <= 0 or review_period_days < 0:
        raise ValueError("lead_time_days must be > 0 and review_period_days must be >= 0")
    if forecast.ndim != 2 or forecast.shape[1] != 28:
        raise ValueError("forecast must contain exactly 28 daily forecast columns")
    if len(segmentation) != sales_array.shape[0] or len(segmentation) != forecast.shape[0]:
        raise ValueError("segmentation, sales history, and forecast must have the same series count")

    out = segmentation.copy()
    forecast_28 = np.clip(forecast, 0, None).sum(axis=1)
    prior_28 = sales_array[:, -28:].sum(axis=1)
    preceding_28 = sales_array[:, -56:-28].sum(axis=1)
    avg_daily = forecast_28 / 28.0

    forecast_growth = _safe_change(forecast_28, prior_28)
    recent_run_rate_change = _safe_change(prior_28, preceding_28)
    forecast_unit_change = forecast_28 - prior_28

    sigma90 = sales_array[:, -90:].std(axis=1, ddof=1)
    z = out.abc_class.map(Z).to_numpy(float)
    if np.isnan(z).any():
        raise ValueError("abc_class must contain only A, B, or C")
    safety = z * sigma90 * np.sqrt(lead_time_days)

    out["preceding_28d_units"] = preceding_28.astype(int)
    out["prior_28d_units"] = prior_28.astype(int)
    out["forecast_28d_units"] = np.round(forecast_28, 1)
    out["forecast_unit_change"] = np.round(forecast_unit_change, 1)
    out["forecast_growth_pct"] = np.round(forecast_growth * 100, 1)
    out["recent_run_rate_change_pct"] = np.round(recent_run_rate_change * 100, 1)
    out["avg_daily_forecast"] = np.round(avg_daily, 2)
    out["demand_sigma_90d"] = np.round(sigma90, 4)
    out["service_level_scenario"] = out.abc_class.map({"A": "95%", "B": "90%", "C": "85%"})
    out["lead_time_scenario_days"] = lead_time_days
    out["review_period_scenario_days"] = review_period_days
    out["safety_stock_scenario_units"] = np.round(safety, 1)
    out["reorder_point_scenario_units"] = np.round(avg_daily * lead_time_days + safety, 1)
    out["target_stock_scenario_units"] = np.round(
        avg_daily * (lead_time_days + review_period_days) + safety, 1
    )

    # Decision signal: retain ordinary forecast growth when informative. If the
    # forecast is mechanically flat (notably MA28), use recent run-rate movement.
    # Symmetric change is used as the zero-baseline fallback so activations and
    # drop-to-zero cases remain finite instead of disappearing as NaN.
    forecast_signal = _symmetric_change(forecast_28, prior_28)
    run_rate_signal = _symmetric_change(prior_28, preceding_28)
    planning_change = forecast_growth.copy()
    flat_forecast = np.isfinite(forecast_growth) & (np.abs(forecast_growth) < 1e-9)
    planning_change[flat_forecast] = run_rate_signal[flat_forecast]
    zero_base_forecast = (~np.isfinite(forecast_growth)) & (forecast_28 > 0)
    planning_change[zero_base_forecast] = forecast_signal[zero_base_forecast]
    remaining_missing = ~np.isfinite(planning_change)
    planning_change[remaining_missing] = run_rate_signal[remaining_missing]
    out["planning_change_signal_pct"] = np.round(planning_change * 100, 1)

    abc_score = out.abc_class.map({"A": 40, "B": 25, "C": 10}).to_numpy(float)
    xyz_score = out.xyz_class.map({"X": 5, "Y": 15, "Z": 25}).to_numpy(float)
    seg_score = out.demand_segment.map(
        {"Smooth": 5, "Intermittent": 10, "Erratic": 15, "Lumpy": 20}
    ).to_numpy(float)
    change_score = np.clip(
        np.nan_to_num(np.abs(planning_change), nan=0, posinf=2, neginf=2) * 20,
        0,
        15,
    )
    out["demand_risk_score"] = np.round(
        np.clip(abc_score + xyz_score + seg_score + change_score, 0, 100), 1
    )

    actions = []
    signal = np.nan_to_num(planning_change, nan=0, posinf=2, neginf=-2)
    for a, x, s, g, unit_delta in zip(
        out.abc_class, out.xyz_class, out.demand_segment, signal, forecast_unit_change
    ):
        zero_base_growth = g == 0 and unit_delta > 0
        if a == "A" and (g > 0.20 or zero_base_growth):
            actions.append("Protect availability; validate supply and raise coverage")
        elif a == "A" and g < -0.20:
            actions.append("Review excess-risk exposure before replenishment")
        elif a == "A" and x == "Z":
            actions.append("High-value volatile demand; use frequent planner review")
        elif a == "A":
            actions.append("Prioritize service level and monitor forecast bias")
        elif x == "Z" or s == "Lumpy":
            actions.append("Use conservative buys and shorter review cycles")
        elif a == "C":
            actions.append("Lean replenishment; minimize long-tail inventory exposure")
        else:
            actions.append("Standard replenishment cadence; monitor trend changes")
    out["planner_action"] = actions
    return out


def save_planning_outputs(frame: pd.DataFrame, output_path="data/processed/planner_action_center.csv"):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
