from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit, prange
from common import load_m5, sales_array, forecast_snaive7, forecast_moving_average, forecast_weekday_average, forecast_trend56, metrics
from segmentation import demand_pattern_features


@njit
def _croston_sba_one(y, alpha=0.1):
    first = -1
    for i in range(len(y)):
        if y[i] > 0:
            first = i
            break
    if first == -1:
        return 0.0
    z = y[first]
    p = first + 1.0
    last = first
    for t in range(first + 1, len(y)):
        if y[t] > 0:
            z = alpha * y[t] + (1 - alpha) * z
            interval = t - last
            p = alpha * interval + (1 - alpha) * p
            last = t
    return (1 - alpha / 2.0) * (z / p) if p > 0 else 0.0


@njit(parallel=True)
def croston_batch(history, alpha=0.1, lookback=730):
    output = np.empty(history.shape[0], dtype=np.float32)
    start = max(0, history.shape[1] - lookback)
    for i in prange(history.shape[0]):
        output[i] = _croston_sba_one(history[i, start:], alpha)
    return output


def run_backtest(raw_dir="data/raw", output_path="outputs/baseline_backtest.csv", horizon=28):
    sales, _, _, dcols = load_m5(raw_dir)
    arr = sales_array(sales, dcols)
    train_ends = [len(dcols) - 84, len(dcols) - 56, len(dcols) - 28]
    rows = []

    for train_end in train_ends:
        history = arr[:, :train_end]
        actual = arr[:, train_end:train_end + horizon]
        _, _, _, segment = demand_pattern_features(history[:, -365:])
        forecasts = {
            "SeasonalNaive7": forecast_snaive7(history, horizon),
            "MA28": forecast_moving_average(history, 28, horizon),
            "WeekdayAvg4": forecast_weekday_average(history, 4, horizon),
            "WeekdayAvg8": forecast_weekday_average(history, 8, horizon),
            "Trend56": forecast_trend56(history, horizon),
        }
        croston = croston_batch(history, 0.1, 730)
        forecasts["CrostonSBA"] = np.repeat(croston[:, None], horizon, axis=1)

        for group in ["ALL", "Smooth", "Intermittent", "Erratic", "Lumpy"]:
            mask = np.ones(len(sales), dtype=bool) if group == "ALL" else segment == group
            for model_name, pred in forecasts.items():
                score = metrics(actual[mask], pred[mask])
                rows.append({"fold_train_end": train_end, "segment": group, "model": model_name, "n_series": int(mask.sum()), **score})

    out = pd.DataFrame(rows)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    return out


if __name__ == "__main__":
    result = run_backtest()
    print(result.groupby(["segment", "model"]).wape.mean().sort_values().head(20))
