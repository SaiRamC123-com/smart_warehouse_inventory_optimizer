import pandas as pd
import numpy as np
import os

def load_data(filepath: str = None) -> pd.DataFrame:
    """Load and preprocess inventory CSV."""

    # Auto-find the file if no path given
    if filepath is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(BASE_DIR, "data", "inventory_demand_forecasting_dataset.csv")

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at: {filepath}\n"
            "Make sure the CSV is inside the 'data/' folder in your GitHub repo."
        )

    df = pd.read_csv(filepath, parse_dates=["date"])
    df = df.sort_values(["product_id", "date"]).reset_index(drop=True)

    # Add helper columns
    df["month"]      = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["week"]       = df["date"].dt.isocalendar().week.astype(int)
    df["dayofweek"]  = df["date"].dt.day_name()

    return df


def get_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-product stats from daily records."""

    summary = df.groupby([
        "product_id", "category", "unit_cost", "lead_time_days"
    ]).agg(
        product_name      = ("product_name",  "first"),
        avg_daily_demand  = ("daily_demand",  "mean"),
        std_daily_demand  = ("daily_demand",  "std"),
        total_demand      = ("daily_demand",  "sum"),
        current_stock     = ("stock_level",   "last"),
        avg_stock_level   = ("stock_level",   "mean"),
        total_restock_qty = ("restock_qty",   "sum"),
    ).reset_index()

    summary["std_daily_demand"] = summary["std_daily_demand"].fillna(0)

    return summary
