import numpy as np

from src.common import (
    forecast_moving_average, forecast_snaive7, forecast_weekday_average, metrics
)
from src.segmentation import demand_pattern_features


def test_baseline_forecast_shapes_and_values():
    history = np.arange(1, 57, dtype=float)[None, :]
    ma = forecast_moving_average(history, window=28, horizon=28)
    sn = forecast_snaive7(history, horizon=28)
    wd = forecast_weekday_average(history, weeks=8, horizon=28)
    assert ma.shape == sn.shape == wd.shape == (1, 28)
    assert np.allclose(ma, history[:, -28:].mean())
    assert np.array_equal(sn[0, :7], history[0, -7:])


def test_metrics_perfect_prediction():
    actual = np.array([[1.0, 2.0, 3.0]])
    score = metrics(actual, actual.copy())
    assert score["wape"] == 0
    assert score["mae"] == 0
    assert score["rmse"] == 0
    assert score["bias_pct"] == 0


def test_demand_pattern_classification_four_quadrants():
    smooth = np.ones(100)
    intermittent = np.tile([1.0, 0.0], 50)
    erratic = np.tile([1.0, 10.0], 50)
    lumpy = np.zeros(100)
    lumpy[::4] = 1.0
    lumpy[2::4] = 10.0
    recent = np.vstack([smooth, intermittent, erratic, lumpy]).astype(np.float32)
    _, _, _, segment = demand_pattern_features(recent)
    assert segment.tolist() == ["Smooth", "Intermittent", "Erratic", "Lumpy"]
