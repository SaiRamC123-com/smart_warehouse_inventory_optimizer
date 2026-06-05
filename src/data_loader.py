import pandas as pd
import os

def load_data(filepath: str = "data/inventory_data.csv") -> pd.DataFrame:
    """Load and preprocess inventory CSV."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at '{filepath}'.\n"
            "Run: python data/generate_data.py"
        )
    df = pd.read_csv(filepath, parse_dates=["date"])
    df = df.sort_values(["product_id", "date"]).reset_index(drop=True)
    return df

def get_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-product stats from daily records."""
    summary = df.groupby(["product_id", "product_name", "category", "unit_cost", "lead_time_days"]).agg(
        avg_daily_demand  = ("daily_demand",  "mean"),
        std_daily_demand  = ("daily_demand",  "std"),
        total_demand      = ("daily_demand",  "sum"),
        current_stock     = ("stock_level",   "last"),
        avg_stock_level   = ("stock_level",   "mean"),
        total_restock_qty = ("restock_qty",   "sum"),
    ).reset_index()
    return summary
