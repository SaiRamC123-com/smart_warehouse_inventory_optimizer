import pandas as pd
import numpy as np

SERVICE_LEVEL_Z = {
    "90%": 1.28,
    "95%": 1.645,
    "99%": 2.326,
}

def calculate_safety_stock(
    std_demand: float,
    lead_time: int,
    z: float = 1.645
) -> float:
    """
    Safety Stock = Z * σ_demand * √(Lead Time)
    """
    return z * std_demand * np.sqrt(lead_time)

def calculate_reorder_point(
    avg_demand: float,
    lead_time: int,
    safety_stock: float
) -> float:
    """
    Reorder Point = (Avg Daily Demand × Lead Time) + Safety Stock
    """
    return (avg_demand * lead_time) + safety_stock

def calculate_eoq(
    annual_demand: float,
    order_cost: float = 50.0,
    holding_cost_rate: float = 0.2,
    unit_cost: float = 1.0
) -> float:
    """
    Economic Order Quantity = √(2DS / H)
    D = annual demand, S = order cost, H = holding cost per unit
    """
    H = holding_cost_rate * unit_cost
    if H <= 0 or annual_demand <= 0:
        return 0
    return np.sqrt((2 * annual_demand * order_cost) / H)

def classify_stock_status(row: pd.Series) -> str:
    """Classify each product's current stock into alert levels."""
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

def enrich_summary(
    summary: pd.DataFrame,
    service_level: str = "95%"
) -> pd.DataFrame:
    """Add Safety Stock, ROP, EOQ, Status to the product summary."""
    z = SERVICE_LEVEL_Z[service_level]

    summary = summary.copy()

    summary["safety_stock"] = summary.apply(
        lambda r: calculate_safety_stock(r["std_daily_demand"], r["lead_time_days"], z),
        axis=1
    ).round(1)

    summary["reorder_point"] = summary.apply(
        lambda r: calculate_reorder_point(r["avg_daily_demand"], r["lead_time_days"], r["safety_stock"]),
        axis=1
    ).round(1)

    summary["eoq"] = summary.apply(
        lambda r: calculate_eoq(r["total_demand"] * 2, unit_cost=r["unit_cost"]),
        axis=1
    ).round(1)

    summary["days_of_stock"] = (
        summary["current_stock"] / summary["avg_daily_demand"].replace(0, np.nan)
    ).round(1)

    summary["stock_value"] = (summary["current_stock"] * summary["unit_cost"]).round(2)

    summary["status"] = summary.apply(classify_stock_status, axis=1)

    return summary
