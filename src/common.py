from pathlib import Path
import numpy as np
import pandas as pd

META_COLS = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]


def load_m5(raw_dir: str | Path):
    raw_dir = Path(raw_dir)
    sales = pd.read_csv(raw_dir / "sales_train_evaluation.csv")
    calendar = pd.read_csv(raw_dir / "calendar.csv")
    prices = pd.read_csv(raw_dir / "sell_prices.csv")
    dcols = [c for c in sales.columns if c.startswith("d_")]
    return sales, calendar, prices, dcols


def sales_array(sales: pd.DataFrame, dcols: list[str]) -> np.ndarray:
    return sales[dcols].to_numpy(dtype=np.float32)


def forecast_snaive7(history: np.ndarray, horizon: int = 28) -> np.ndarray:
    pattern = history[:, -7:]
    return np.tile(pattern, (1, int(np.ceil(horizon / 7))))[:, :horizon]


def forecast_moving_average(history: np.ndarray, window: int = 28, horizon: int = 28) -> np.ndarray:
    mean = history[:, -window:].mean(axis=1, keepdims=True)
    return np.repeat(mean, horizon, axis=1)


def forecast_weekday_average(history: np.ndarray, weeks: int = 8, horizon: int = 28) -> np.ndarray:
    days = weeks * 7
    pattern = history[:, -days:].reshape(history.shape[0], weeks, 7).mean(axis=1)
    return np.tile(pattern, (1, int(np.ceil(horizon / 7))))[:, :horizon]


def forecast_trend56(history: np.ndarray, horizon: int = 28) -> np.ndarray:
    y = history[:, -56:].astype(np.float32)
    x = np.arange(56, dtype=np.float32)
    xmean = x.mean()
    ymean = y.mean(axis=1, keepdims=True)
    slope = ((y - ymean) * (x - xmean)).sum(axis=1) / ((x - xmean) ** 2).sum()
    intercept = ymean[:, 0] - slope * xmean
    future_x = np.arange(56, 56 + horizon, dtype=np.float32)
    return np.clip(intercept[:, None] + slope[:, None] * future_x[None, :], 0, None)


def metrics(actual: np.ndarray, pred: np.ndarray) -> dict:
    denom = float(actual.sum())
    error = pred - actual
    abs_error = np.abs(error)
    return {
        "wape": float(abs_error.sum() / denom) if denom else np.nan,
        "mae": float(abs_error.mean()),
        "rmse": float(np.sqrt((error ** 2).mean())),
        "bias_pct": float(error.sum() / denom) if denom else np.nan,
    }
