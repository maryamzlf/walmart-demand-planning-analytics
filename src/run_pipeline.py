"""Reproducible entry point for the open-source portions of the project.

The full priority-series LightGBM is intentionally a separate step because it is the most
computationally expensive stage. Run it after audit/segmentation/backtesting.
"""
from data_audit import run_audit
from segmentation import build_segmentation
from backtest import run_backtest

if __name__ == "__main__":
    print("1/3 Data audit")
    run_audit()
    print("2/3 Demand/value segmentation")
    build_segmentation()
    print("3/3 Rolling-origin baseline backtest")
    run_backtest()
    print("Core pipeline complete. Run priority_model.py for the ML challenger.")
