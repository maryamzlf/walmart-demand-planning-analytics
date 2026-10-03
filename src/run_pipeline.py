"""Run the data audit, segmentation, and baseline backtests.

The priority-series LightGBM stage remains separate because it is the most
computationally expensive part of the workflow.
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
