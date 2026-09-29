# Data

This project uses the **Walmart M5 Forecasting - Accuracy** competition dataset.

Raw files are not committed because of size and redistribution considerations. For local reproduction, place these files under `data/raw/`:

- `calendar.csv`
- `sales_train_evaluation.csv`
- `sell_prices.csv`
- `sales_train_validation.csv` (optional for the modeling pipeline; used by the CI integrity check)
- `sample_submission.csv` (optional)

The modeling pipeline uses `sales_train_evaluation.csv` as the canonical sales-history source because it already contains the full validation history.

CI independently confirms that `sales_train_validation.csv` matches the first 1,913 days of the evaluation file for all 30,490 series. It also checks calendar-key uniqueness, price-key uniqueness, and that sell prices are present and positive.

For unattended CI, GitHub Actions downloads the same M5 competition archive from a public Zenodo mirror so the build does not require Kaggle authentication.
