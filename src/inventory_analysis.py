import pandas as pd
import numpy as np

SERVICE_LEVEL_Z = {
    "90%": 1.28,
    "95%": 1.645,
    "99%": 2.326,
}

def calculate_safety_stock(std_demand, lead_time, z=1.645):
    return z * std_demand * np.sqrt(lead_time)

def calculate_reorder_point(avg_demand, lead_time, safety_stock):
    return (avg_demand * lead_time) + safety_stock

def calculate_eoq(annual_demand, order_cost=50.0,
                  holding_cost_rate=0.2, unit_cost=1.0):
    H = holding_cost_rate * unit_cost
    if H <= 0 or annual_demand <= 0:
        return 0
    return np.sqrt((2 * annual_demand * order_cost) / H)

def classify_stock_status(row):
    stock  = row["current_stock"]
    rop    = row["reorder_point"]
    safety = row["safety_stock"]

    if stock <= 0:
        return "🔴 OUT OF STOCK"
    elif stock <= safety:
        return "🟠 CRITICAL"
    elif stock <= rop:
        return "🟡 REORDER NOW"
    elif stock <= rop * 1.5:
        return "🟢 ADEQUATE"
    else:
        return "🔵 OVERSTOCKED"

def enrich_summary(summary: pd.DataFrame,
                   service_level: str = "95%") -> pd.DataFrame:
    z = SERVICE_LEVEL_Z[service_level]
    df = summary.copy()

    df["safety_stock"] = df.apply(
        lambda r: calculate_safety_stock(
            r["std_daily_demand"], r["lead_time_days"], z),
        axis=1
    ).round(1)

    df["reorder_point"] = df.apply(
        lambda r: calculate_reorder_point(
            r["avg_daily_demand"], r["lead_time_days"], r["safety_stock"]),
        axis=1
    ).round(1)

    df["eoq"] = df.apply(
        lambda r: calculate_eoq(
            r["total_demand"] * 2, unit_cost=r["unit_cost"]),
        axis=1
    ).round(1)

    df["days_of_stock"] = (
        df["current_stock"] /
        df["avg_daily_demand"].replace(0, np.nan)
    ).round(1)

    df["stock_value"] = (
        df["current_stock"] * df["unit_cost"]
    ).round(2)

    df["status"] = df.apply(classify_stock_status, axis=1)

    return df
