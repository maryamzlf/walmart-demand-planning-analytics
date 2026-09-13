from pathlib import Path
import json
import numpy as np
import pandas as pd
import lightgbm as lgb
from common import load_m5, sales_array, forecast_moving_average, forecast_weekday_average, forecast_snaive7, metrics

FEATURES = [
    "lag1","lag7","lag14","lag28","lag56","rmean7","rmean28","rmean56","rstd28",
    "sell_price","price_change_7d","wday","month","year","event_flag","snap",
    "item_code","store_code","dept_code","cat_code","state_code"
]
CATEGORICAL = ["item_code","store_code","dept_code","cat_code","state_code"]


def _priority_indices_pre_holdout(sales, calendar, prices, arr, dcols, train_end=1913, n_priority=3000):
    start = train_end - 365
    units = arr[:, start:train_end].sum(axis=1)
    weeks = pd.unique(calendar.set_index("d").loc[dcols[start:train_end], "wm_yr_wk"])
    avg_price = prices[prices.wm_yr_wk.isin(weeks)].groupby(["item_id","store_id"]).sell_price.mean()
    keys = pd.MultiIndex.from_frame(sales[["item_id","store_id"]])
    p = avg_price.reindex(keys).to_numpy()
    fallback = prices.groupby(["item_id","store_id"]).sell_price.mean().reindex(keys).to_numpy()
    p = np.where(np.isnan(p), fallback, p)
    revenue_proxy = units * p
    return np.argsort(-revenue_proxy)[:n_priority]


def _prepare_subset(indices, sales, calendar, prices, arr, max_day=1969):
    meta = sales.iloc[indices].reset_index(drop=True)
    y = arr[indices].astype(np.float32)
    all_d = [f"d_{i}" for i in range(1, max_day + 1)]
    cal = calendar.set_index("d").loc[all_d].reset_index()
    keep = meta[["item_id","store_id"]].drop_duplicates().assign(_keep=1)
    p = prices.merge(keep, on=["item_id","store_id"], how="inner").drop(columns="_keep")
    weeks = pd.unique(cal.wm_yr_wk)
    pivot = p.pivot_table(index=["item_id","store_id"], columns="wm_yr_wk", values="sell_price", aggfunc="last")
    key = pd.MultiIndex.from_frame(meta[["item_id","store_id"]])
    pivot = pivot.reindex(index=key, columns=weeks).ffill(axis=1).bfill(axis=1)
    pw = pivot.to_numpy(np.float32)
    week_map = {w:i for i,w in enumerate(weeks)}
    daily_price = np.column_stack([pw[:,week_map[w]] for w in cal.wm_yr_wk.to_numpy()]).astype(np.float32)
    return meta, y, cal, daily_price


def _encodings(meta, cal):
    codes = {
        "item_code": pd.Categorical(meta.item_id).codes.astype(np.int32),
        "store_code": pd.Categorical(meta.store_id).codes.astype(np.int16),
        "dept_code": pd.Categorical(meta.dept_id).codes.astype(np.int16),
        "cat_code": pd.Categorical(meta.cat_id).codes.astype(np.int8),
        "state_code": pd.Categorical(meta.state_id).codes.astype(np.int8),
    }
    event = ((cal.event_name_1.notna()) | (cal.event_name_2.notna())).astype(np.int8).to_numpy()
    snap = np.empty((len(meta), len(cal)), dtype=np.int8)
    for state in ["CA","TX","WI"]:
        mask = meta.state_id.to_numpy() == state
        snap[mask,:] = cal[f"snap_{state}"].to_numpy(np.int8)[None,:]
    return codes, event, snap


def _training_frame(y, cal, daily_price, codes, event, snap, start, end):
    times = np.arange(start, end)
    n, nt = y.shape[0], len(times)
    cs = np.concatenate([np.zeros((n,1), np.float32), np.cumsum(y, axis=1, dtype=np.float32)], axis=1)
    cs2 = np.concatenate([np.zeros((n,1), np.float32), np.cumsum(y**2, axis=1, dtype=np.float32)], axis=1)
    def mean(w): return (cs[:,times] - cs[:,times-w]) / w
    def std(w):
        m = mean(w); sq = (cs2[:,times] - cs2[:,times-w]) / w
        return np.sqrt(np.maximum(sq - m**2, 0))
    X = pd.DataFrame({
        "lag1":y[:,times-1].ravel(), "lag7":y[:,times-7].ravel(), "lag14":y[:,times-14].ravel(),
        "lag28":y[:,times-28].ravel(), "lag56":y[:,times-56].ravel(),
        "rmean7":mean(7).ravel(), "rmean28":mean(28).ravel(), "rmean56":mean(56).ravel(), "rstd28":std(28).ravel(),
        "sell_price":daily_price[:,times].ravel(),
        "price_change_7d":(daily_price[:,times] / np.maximum(daily_price[:,times-7],0.01) - 1).ravel(),
        "wday":np.tile(cal.wday.to_numpy(np.int8)[times],n), "month":np.tile(cal.month.to_numpy(np.int8)[times],n),
        "year":np.tile((cal.year.to_numpy(np.int16)[times]-2011).astype(np.int8),n),
        "event_flag":np.tile(event[times],n), "snap":snap[:,times].ravel(),
    })
    for name, values in codes.items(): X[name] = np.repeat(values, nt)
    return X[FEATURES], y[:,times].ravel()


def _fit(X, y):
    model = lgb.LGBMRegressor(
        objective="tweedie", tweedie_variance_power=1.1, n_estimators=350, learning_rate=0.05,
        num_leaves=64, min_child_samples=50, subsample=0.85, colsample_bytree=0.85,
        reg_lambda=0.1, random_state=42, n_jobs=-1, verbosity=-1, deterministic=True, force_col_wise=True,
    )
    model.fit(X, y, categorical_feature=CATEGORICAL)
    return model


def _recursive(model, history, cal, daily_price, codes, event, snap, start_t, horizon=28):
    ext = np.concatenate([history.copy(), np.zeros((history.shape[0], horizon), np.float32)], axis=1)
    pred = np.zeros((history.shape[0], horizon), np.float32)
    for h, t in enumerate(range(start_t, start_t + horizon)):
        v28 = ext[:,t-28:t]
        X = pd.DataFrame({
            "lag1":ext[:,t-1],"lag7":ext[:,t-7],"lag14":ext[:,t-14],"lag28":ext[:,t-28],"lag56":ext[:,t-56],
            "rmean7":ext[:,t-7:t].mean(axis=1),"rmean28":v28.mean(axis=1),"rmean56":ext[:,t-56:t].mean(axis=1),
            "rstd28":v28.std(axis=1),"sell_price":daily_price[:,t],
            "price_change_7d":daily_price[:,t]/np.maximum(daily_price[:,t-7],0.01)-1,
            "wday":np.full(history.shape[0],cal.wday.iloc[t],np.int8),"month":np.full(history.shape[0],cal.month.iloc[t],np.int8),
            "year":np.full(history.shape[0],cal.year.iloc[t]-2011,np.int8),"event_flag":np.full(history.shape[0],event[t],np.int8),
            "snap":snap[:,t], **codes,
        })
        p = np.clip(model.predict(X[FEATURES]), 0, None).astype(np.float32)
        pred[:,h] = p; ext[:,t] = p
    return pred


def evaluate_priority_model(raw_dir="data/raw", output_path="outputs/priority_model_holdout.json"):
    sales, calendar, prices, dcols = load_m5(raw_dir); arr = sales_array(sales, dcols)
    idx = _priority_indices_pre_holdout(sales, calendar, prices, arr, dcols)
    meta, y, cal, price = _prepare_subset(idx, sales, calendar, prices, arr)
    codes, event, snap = _encodings(meta, cal)
    X, target = _training_frame(y, cal, price, codes, event, snap, 1450, 1913)
    model = _fit(X, target)
    pred = _recursive(model, y[:,:1913], cal, price, codes, event, snap, 1913, 28)
    actual = y[:,1913:1941]
    result = {
        "LightGBM": metrics(actual,pred),
        "MA28": metrics(actual,forecast_moving_average(y[:,:1913],28,28)),
        "WeekdayAvg8": metrics(actual,forecast_weekday_average(y[:,:1913],8,28)),
        "SeasonalNaive7": metrics(actual,forecast_snaive7(y[:,:1913],28)),
    }
    result["relative_wape_improvement_vs_MA28"] = (result["MA28"]["wape"]-result["LightGBM"]["wape"])/result["MA28"]["wape"]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True); Path(output_path).write_text(json.dumps(result,indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(evaluate_priority_model(), indent=2))
