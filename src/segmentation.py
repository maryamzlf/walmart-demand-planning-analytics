from pathlib import Path
import numpy as np
import pandas as pd
from common import load_m5, sales_array


def demand_pattern_features(recent: np.ndarray):
    active = (recent > 0).sum(axis=1)
    adi = np.divide(recent.shape[1], active, out=np.full(active.shape, np.inf, dtype=float), where=active > 0)
    cv2 = np.full(recent.shape[0], np.inf, dtype=np.float32)

    for i, row in enumerate(recent):
        nz = row[row > 0]
        if len(nz) >= 2:
            mean = nz.mean()
            cv2[i] = (nz.std(ddof=1) / mean) ** 2 if mean > 0 else np.inf
        elif len(nz) == 1:
            cv2[i] = 0.0

    segment = np.full(recent.shape[0], "Lumpy", dtype=object)
    segment[(adi < 1.32) & (cv2 < 0.49)] = "Smooth"
    segment[(adi >= 1.32) & (cv2 < 0.49)] = "Intermittent"
    segment[(adi < 1.32) & (cv2 >= 0.49)] = "Erratic"
    return active, adi, cv2, segment


def build_segmentation(raw_dir="data/raw", output_path="data/processed/segmentation.csv", recent_days=365):
    sales, calendar, prices, dcols = load_m5(raw_dir)
    arr = sales_array(sales, dcols)
    recent = arr[:, -recent_days:]

    active, adi, cv2, segment = demand_pattern_features(recent)
    units = recent.sum(axis=1)
    zero_share = (recent == 0).mean(axis=1)

    recent_d = dcols[-recent_days:]
    weeks = calendar.set_index("d").loc[recent_d, "wm_yr_wk"].to_numpy()
    unique_weeks = pd.unique(weeks)
    weekly_units = np.zeros((len(sales), len(unique_weeks)), dtype=np.float32)
    for j, week in enumerate(unique_weeks):
        weekly_units[:, j] = recent[:, np.where(weeks == week)[0]].sum(axis=1)

    price_recent = prices[prices.wm_yr_wk.isin(unique_weeks)]
    pivot = price_recent.pivot_table(index=["item_id", "store_id"], columns="wm_yr_wk", values="sell_price", aggfunc="last")
    item_store = pd.MultiIndex.from_frame(sales[["item_id", "store_id"]])
    pivot = pivot.reindex(index=item_store, columns=unique_weeks).ffill(axis=1).bfill(axis=1)
    price_matrix = pivot.to_numpy(dtype=np.float32)
    revenue = (weekly_units * price_matrix).sum(axis=1)

    order = np.argsort(-revenue)
    cumulative = np.cumsum(revenue[order]) / revenue.sum()
    abc = np.empty(len(sales), dtype=object)
    abc[order[cumulative <= 0.80]] = "A"
    abc[order[(cumulative > 0.80) & (cumulative <= 0.95)]] = "B"
    abc[order[cumulative > 0.95]] = "C"

    weekly_mean = weekly_units.mean(axis=1)
    weekly_std = weekly_units.std(axis=1, ddof=1)
    weekly_cv = np.divide(weekly_std, weekly_mean, out=np.full_like(weekly_std, np.inf), where=weekly_mean > 0)
    xyz = np.where(weekly_cv <= 0.5, "X", np.where(weekly_cv <= 1.0, "Y", "Z"))

    out = sales[["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]].copy()
    out["units_365d"] = units.astype(int)
    out["revenue_365d"] = np.round(revenue, 2)
    out["active_days_365d"] = active.astype(int)
    out["zero_share_365d"] = np.round(zero_share, 4)
    out["adi"] = np.round(adi, 3)
    out["cv2_nonzero_demand"] = np.where(np.isfinite(cv2), np.round(cv2, 3), np.nan)
    out["demand_segment"] = segment
    out["weekly_cv"] = np.where(np.isfinite(weekly_cv), np.round(weekly_cv, 3), np.nan)
    out["abc_class"] = abc
    out["xyz_class"] = xyz
    out["abc_xyz"] = out.abc_class + out.xyz_class

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    return out


if __name__ == "__main__":
    frame = build_segmentation()
    print(frame.demand_segment.value_counts())
