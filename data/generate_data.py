import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

PRODUCTS = {
    "P001": ("Laptop",        "Electronics",  800, 50),
    "P002": ("Office Chair",  "Furniture",    120, 200),
    "P003": ("USB Hub",       "Electronics",   25, 500),
    "P004": ("Desk Lamp",     "Furniture",     35, 300),
    "P005": ("Monitor",       "Electronics",  250,  80),
    "P006": ("Keyboard",      "Electronics",   45, 400),
    "P007": ("Webcam",        "Electronics",   75, 150),
    "P008": ("Headphones",    "Electronics",   90, 120),
    "P009": ("Filing Cabinet","Furniture",    180,  60),
    "P010": ("Whiteboard",    "Supplies",      55,  90),
}

def generate_inventory_data(days=180):
    records = []
    start_date = datetime.today() - timedelta(days=days)

    for product_id, (name, category, unit_cost, avg_daily_demand) in PRODUCTS.items():
        current_stock = int(avg_daily_demand * random.uniform(10, 30))
        lead_time = random.randint(3, 14)

        for day in range(days):
            date = start_date + timedelta(days=day)
            # Simulate seasonal demand variation
            season_factor = 1 + 0.3 * np.sin(2 * np.pi * day / 90)
            demand = max(0, int(np.random.normal(
                avg_daily_demand * season_factor,
                avg_daily_demand * 0.2
            )))
            # Random restocking
            restock = int(avg_daily_demand * random.randint(10, 20)) if current_stock < avg_daily_demand * 5 else 0
            current_stock = max(0, current_stock + restock - demand)

            records.append({
                "date":          date.strftime("%Y-%m-%d"),
                "product_id":    product_id,
                "product_name":  name,
                "category":      category,
                "daily_demand":  demand,
                "stock_level":   current_stock,
                "unit_cost":     unit_cost,
                "restock_qty":   restock,
                "lead_time_days":lead_time,
            })

    df = pd.DataFrame(records)
    df.to_csv("inventory_data.csv", index=False)
    print(f"✅ Generated {len(df)} records → inventory_data.csv")
    return df

if __name__ == "__main__":
    generate_inventory_data()
