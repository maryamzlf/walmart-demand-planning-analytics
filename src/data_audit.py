from pathlib import Path
import json
import numpy as np
from common import load_m5, sales_array


def run_audit(raw_dir="data/raw", output_path="outputs/data_audit.json"):
    sales, calendar, prices, dcols = load_m5(raw_dir)
    arr = sales_array(sales, dcols)

    report = {
        "n_series": int(len(sales)),
        "n_items": int(sales.item_id.nunique()),
        "n_stores": int(sales.store_id.nunique()),
        "n_states": int(sales.state_id.nunique()),
        "n_categories": int(sales.cat_id.nunique()),
        "n_departments": int(sales.dept_id.nunique()),
        "n_days": int(len(dcols)),
        "total_units": int(sales[dcols].to_numpy(dtype=np.int32).sum(dtype=np.int64)),
        "zero_share": float((arr == 0).mean()),
        "negative_sales_count": int((arr < 0).sum()),
        "missing_sales_count": int(np.isnan(arr).sum()),
        "price_rows": int(len(prices)),
        "missing_price_count": int(prices.sell_price.isna().sum()),
        "price_min": float(prices.sell_price.min()),
        "price_max": float(prices.sell_price.max()),
        "start_date": str(calendar.loc[calendar.d == dcols[0], "date"].iloc[0]),
        "end_date": str(calendar.loc[calendar.d == dcols[-1], "date"].iloc[0]),
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    print(run_audit())
