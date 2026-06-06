import pandas as pd
import numpy as np
import os

def load_data(filepath: str = None) -> pd.DataFrame:
    if filepath is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(BASE_DIR, "data",
                    "inventory_demand_forecasting_dataset.csv")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at: {filepath}")

    df = pd.read_csv(filepath, parse_dates=["date"])
    df = df.sort_values(["product_id", "date"]).reset_index(drop=True)

    # Add helper columns
    df["month"]      = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["dayofweek"]  = df["date"].dt.day_name()

    return df


def get_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Works with real CSV: date, store_id, product_id, price, promotion, demand"""

    summary = df.groupby("product_id").agg(
        avg_daily_demand = ("demand", "mean"),
        std_daily_demand = ("demand", "std"),
        total_demand     = ("demand", "sum"),
        current_stock    = ("demand", "last"),   # proxy
        avg_price        = ("price",  "mean"),
    ).reset_index()

    summary["std_daily_demand"] = summary["std_daily_demand"].fillna(0)

    # Add required columns for inventory analysis
    summary["product_name"]   = summary["product_id"]
    summary["category"]       = "General"
    summary["unit_cost"]      = summary["avg_price"]
    summary["lead_time_days"] = 7
    summary["stock_level"]    = summary["current_stock"]
    summary["restock_qty"]    = 0
    summary["avg_stock_level"]= summary["current_stock"]
    summary["total_restock_qty"] = 0

    return summary
