import numpy as np
import pandas as pd
from src.planning_outputs import add_planning_scenarios


def test_scenario_outputs_nonnegative():
    seg = pd.DataFrame({
        "abc_class":["A","B"], "xyz_class":["X","Z"],
        "demand_segment":["Smooth","Lumpy"]
    })
    sales = np.ones((2,90),dtype=float)
    forecast = np.ones((2,28),dtype=float)
    out = add_planning_scenarios(seg,sales,forecast)
    assert (out.safety_stock_scenario_units >= 0).all()
    assert (out.reorder_point_scenario_units >= 0).all()
    assert (out.target_stock_scenario_units >= out.reorder_point_scenario_units).all()
