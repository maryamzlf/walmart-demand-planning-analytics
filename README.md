# Walmart Demand Planning Analytics

**End-to-end retail demand forecasting, merchandise prioritization, and scenario-based replenishment analytics using Python, SQL, LightGBM, and Power BI-ready outputs.**

This project was built as a planning workflow, not as a generic Kaggle notebook. It combines demand-pattern segmentation, value prioritization, time-based forecast validation, machine-learning model routing, and planner-facing actions at the **item × store** level.

## Business questions

- What will likely sell during the next 28 days?
- Which item-store combinations deserve the most planner attention?
- Which demand patterns need different forecasting methods?
- Where is demand accelerating or declining?
- What safety-stock / reorder-point coverage would be reasonable under explicit lead-time and service-level assumptions?

## Why this project is different

A large share of retail demand is sparse and intermittent, so forcing one forecasting model across every SKU-store combination is inefficient and often inaccurate. This project uses a **value-aware forecast router**:

1. **Top 3,000 high-value item-store series** → global LightGBM challenger
2. **Remaining Smooth demand** → 8-week weekday average
3. **Remaining Intermittent / Erratic / Lumpy demand** → 28-day moving average

The model architecture is driven by backtest evidence rather than by model complexity for its own sake.

## Dataset audit

| Metric | Result |
|---|---:|
| Item-store series | 30,490 |
| Unique items | 3,049 |
| Stores | 10 |
| States | 3 |
| Categories | 3 |
| Departments | 7 |
| Observed days | 1,941 |
| Date range | 2011-01-29 to 2016-05-22 |
| Total units | 66,927,173 |
| Zero-demand observations | 68.0% |

The public M5 data includes unit sales, weekly sell prices, calendar events, and SNAP indicators. It does **not** include Walmart on-hand inventory, purchase orders, vendor lead times, or actual replenishment decisions.

## Demand segmentation

Each item-store series is classified over the trailing 365 days using **ADI** and **CV²**:

| Demand pattern | Series | Share |
|---|---:|---:|
| Intermittent | 23,096 | 75.7% |
| Lumpy | 3,761 | 12.3% |
| Smooth | 2,939 | 9.6% |
| Erratic | 694 | 2.3% |

The project also applies **ABC revenue segmentation** and **XYZ weekly-demand variability**, giving planners a combined value/volatility view.

## Forecast validation

All forecasting tests use time-based holdouts. Statistical challengers are evaluated across three rolling 28-day folds.

For the leakage-safe priority-series holdout, LightGBM delivered:

| Model | WAPE | RMSE | Bias |
|---|---:|---:|---:|
| **LightGBM** | **45.31%** | **4.33** | **-0.89%** |
| 28-day moving average | 49.46% | 4.86 | -1.25% |
| 8-week weekday average | 49.53% | 4.78 | -1.07% |
| 7-day seasonal naive | 56.75% | 5.44 | -6.12% |

**Result:** the priority LightGBM challenger reduced WAPE by **8.4% relative to the 28-day moving-average baseline**.

The ML feature set includes recent demand lags, rolling demand level/volatility, weekly sell price, price change, weekday/month, event flags, state SNAP indicators, and product/store hierarchy identifiers.

## Planner Action Center

The final item-store output translates the forecast into business-facing fields:

- ABC-XYZ class
- demand pattern
- trailing revenue and demand
- next-28-day forecast
- forecast growth vs prior 28 days
- demand-risk score
- service-level scenario
- safety-stock scenario
- reorder-point scenario
- target-stock scenario
- planner action recommendation

Example actions include:

- **Protect availability; validate supply and raise coverage**
- **Review excess-risk exposure before replenishment**
- **High-value volatile demand; use frequent planner review**
- **Lean replenishment; minimize long-tail inventory exposure**

## Inventory-scenario integrity

M5 does not contain observed inventory. To avoid overstating what the public data can support, the project treats inventory metrics as explicit scenarios:

- lead time: 14 days
- review period: 7 days
- A-class service level: 95%
- B-class service level: 90%
- C-class service level: 85%

These calculations are decision-support outputs, **not actual Walmart stock or order quantities**.

## Repository structure

```text
.
├── data/
│   └── README.md
├── docs/
│   ├── project_charter.md
│   ├── methodology.md
│   ├── data_dictionary.md
│   ├── model_card.md
│   └── dashboard_spec.md
├── outputs/
│   ├── data_audit.json
│   ├── baseline_model_summary.csv
│   ├── priority_model_holdout.csv
│   ├── priority_feature_importance.csv
│   ├── segment_summary.csv
│   ├── planner_action_sample.csv
│   └── executive_findings.md
├── sql/
│   └── planner_kpis.sql
├── src/
│   ├── common.py
│   ├── data_audit.py
│   ├── segmentation.py
│   ├── backtest.py
│   ├── priority_model.py
│   ├── planning_outputs.py
│   └── run_pipeline.py
├── tests/
│   └── test_planning_logic.py
├── config.yaml
└── requirements.txt
```

## Reproduce the analysis

1. Download the **M5 Forecasting - Accuracy** files from Kaggle.
2. Put `calendar.csv`, `sales_train_evaluation.csv`, and `sell_prices.csv` in `data/raw/`.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the core pipeline: `python src/run_pipeline.py`
5. Evaluate the priority ML challenger: `python src/priority_model.py`

## Power BI design

The planned report contains five decision-oriented pages: Executive Planning Overview; Demand Forecast & Model Performance; Merchandise & Assortment Planning; Planner Action Center; and Scenario Planning. See [`docs/dashboard_spec.md`](docs/dashboard_spec.md).

## Tools demonstrated

**Python:** pandas, NumPy, LightGBM, Numba  
**Forecasting:** rolling-origin validation, intermittent-demand benchmarking, global ML forecasting  
**Planning:** ABC-XYZ, ADI/CV² segmentation, service-level scenarios, safety stock / reorder point  
**SQL:** planner KPI and action-queue queries  
**BI:** Power BI-ready data model and dashboard specification

## Notes on responsible interpretation

This is an independent portfolio analysis using public competition data. It is not affiliated with Walmart and does not represent current Walmart operations. The dataset ends in 2016; the project demonstrates analytical and planning methodology rather than current business performance.
