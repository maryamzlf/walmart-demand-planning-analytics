# Data

This project uses the **Walmart M5 Forecasting - Accuracy** competition data from Kaggle.

Raw files are not committed to this repository because of size and redistribution considerations. Download the competition data from Kaggle and place these files under `data/raw/`:

- `calendar.csv`
- `sales_train_evaluation.csv`
- `sell_prices.csv`
- `sample_submission.csv` (optional)
- `sales_train_validation.csv` (not required by this pipeline)

The pipeline uses `sales_train_evaluation.csv` as the single sales-history source to avoid duplicating the validation history already contained in the evaluation file.
