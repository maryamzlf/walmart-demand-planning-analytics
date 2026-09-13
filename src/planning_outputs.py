from pathlib import Path
import numpy as np
import pandas as pd

Z = {"A":1.645, "B":1.282, "C":1.036}


def add_planning_scenarios(segmentation: pd.DataFrame, sales_array: np.ndarray, forecast: np.ndarray,
                           lead_time_days=14, review_period_days=7):
    out = segmentation.copy()
    forecast_28 = forecast.sum(axis=1)
    prior_28 = sales_array[:,-28:].sum(axis=1)
    avg_daily = forecast_28 / 28.0
    growth = np.divide(forecast_28-prior_28, prior_28, out=np.full_like(forecast_28,np.nan), where=prior_28>0)
    sigma90 = sales_array[:,-90:].std(axis=1,ddof=1)
    z = out.abc_class.map(Z).to_numpy(float)
    safety = z * sigma90 * np.sqrt(lead_time_days)

    out["prior_28d_units"] = prior_28.astype(int)
    out["forecast_28d_units"] = np.round(forecast_28,1)
    out["forecast_growth_pct"] = np.round(growth*100,1)
    out["avg_daily_forecast"] = np.round(avg_daily,2)
    out["service_level_scenario"] = out.abc_class.map({"A":"95%","B":"90%","C":"85%"})
    out["lead_time_scenario_days"] = lead_time_days
    out["safety_stock_scenario_units"] = np.round(safety,1)
    out["reorder_point_scenario_units"] = np.round(avg_daily*lead_time_days+safety,1)
    out["target_stock_scenario_units"] = np.round(avg_daily*(lead_time_days+review_period_days)+safety,1)

    abc_score = out.abc_class.map({"A":40,"B":25,"C":10}).to_numpy(float)
    xyz_score = out.xyz_class.map({"X":5,"Y":15,"Z":25}).to_numpy(float)
    seg_score = out.demand_segment.map({"Smooth":5,"Intermittent":10,"Erratic":15,"Lumpy":20}).to_numpy(float)
    growth_score = np.clip(np.nan_to_num(np.abs(growth),nan=0,posinf=2)*20,0,15)
    out["demand_risk_score"] = np.round(np.clip(abc_score+xyz_score+seg_score+growth_score,0,100),1)

    actions=[]
    for a,x,s,g in zip(out.abc_class,out.xyz_class,out.demand_segment,np.nan_to_num(growth,nan=0,posinf=2,neginf=-2)):
        if a=="A" and g>0.20: actions.append("Protect availability; validate supply and raise coverage")
        elif a=="A" and g<-0.20: actions.append("Review excess-risk exposure before replenishment")
        elif a=="A" and x=="Z": actions.append("High-value volatile demand; use frequent planner review")
        elif a=="A": actions.append("Prioritize service level and monitor forecast bias")
        elif x=="Z" or s=="Lumpy": actions.append("Use conservative buys and shorter review cycles")
        elif a=="C": actions.append("Lean replenishment; minimize long-tail inventory exposure")
        else: actions.append("Standard replenishment cadence; monitor trend changes")
    out["planner_action"] = actions
    return out


def save_planning_outputs(frame: pd.DataFrame, output_path="data/processed/planner_action_center.csv"):
    Path(output_path).parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(output_path,index=False)
