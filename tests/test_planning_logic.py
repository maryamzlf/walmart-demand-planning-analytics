import numpy as np
import pandas as pd
import pytest
from src.planning_outputs import add_planning_scenarios


def _seg():
    return pd.DataFrame({
        "abc_class": ["A", "B"],
        "xyz_class": ["X", "Z"],
        "demand_segment": ["Smooth", "Lumpy"],
    })


def test_scenario_outputs_nonnegative():
    sales = np.ones((2, 90), dtype=float)
    forecast = np.ones((2, 28), dtype=float)
    out = add_planning_scenarios(_seg(), sales, forecast)
    assert (out.safety_stock_scenario_units >= 0).all()
    assert (out.reorder_point_scenario_units >= 0).all()
    assert (out.target_stock_scenario_units >= out.reorder_point_scenario_units).all()


def test_ma28_like_forecast_uses_recent_run_rate_as_planning_signal():
    sales = np.ones((2, 90), dtype=float)
    sales[:, -56:-28] = 0.5
    forecast = np.ones((2, 28), dtype=float)  # equals prior-28 average
    out = add_planning_scenarios(_seg(), sales, forecast)
    assert (out.forecast_growth_pct == 0).all()
    assert (out.planning_change_signal_pct > 0).all()


def test_zero_reference_growth_is_not_reported_as_infinite():
    sales = np.zeros((2, 90), dtype=float)
    forecast = np.ones((2, 28), dtype=float)
    out = add_planning_scenarios(_seg(), sales, forecast)
    assert out.forecast_growth_pct.isna().all()
    assert np.isfinite(out.demand_risk_score).all()


def test_invalid_horizon_is_rejected():
    with pytest.raises(ValueError):
        add_planning_scenarios(_seg(), np.ones((2, 90)), np.ones((2, 14)))


def test_invalid_lead_time_is_rejected():
    with pytest.raises(ValueError):
        add_planning_scenarios(_seg(), np.ones((2, 90)), np.ones((2, 28)), lead_time_days=0)
