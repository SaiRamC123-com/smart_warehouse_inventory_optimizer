import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import warnings
warnings.filterwarnings("ignore")

print("=" * 70)
print("SMART WAREHOUSE INVENTORY OPTIMIZER - EXPLORATION NOTEBOOK")
print("=" * 70)

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv("../data/inventory_demand_forecasting_dataset.csv")

print("\nDataset Shape:", df.shape)
print("\nFirst 5 Records")
print(df.head())

print("\nDataset Information")
print(df.info())

print("\nMissing Values")
print(df.isnull().sum())

print("\nDuplicate Rows:", df.duplicated().sum())

print("\nStatistical Summary")
print(df.describe())


df["date"] = pd.to_datetime(df["date"])

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["week"] = df["date"].dt.isocalendar().week
df["quarter"] = df["date"].dt.quarter
df["dayofweek"] = df["date"].dt.dayofweek

# ==========================================================
# DEMAND DISTRIBUTION
# ==========================================================

plt.figure(figsize=(10,5))
sns.histplot(df["demand"], bins=30, kde=True)
plt.title("Demand Distribution")
plt.show()

# ==========================================================
# PRICE DISTRIBUTION
# ==========================================================

plt.figure(figsize=(10,5))
sns.histplot(df["price"], bins=30, kde=True)
plt.title("Price Distribution")
plt.show()

# ==========================================================
# DAILY DEMAND TREND
# ==========================================================

daily_demand = df.groupby("date")["demand"].sum()

plt.figure(figsize=(14,5))
daily_demand.plot()
plt.title("Daily Demand Trend")
plt.xlabel("Date")
plt.ylabel("Demand")
plt.show()

# ==========================================================
# PROMOTION IMPACT
# ==========================================================

promotion_demand = df.groupby("promotion")["demand"].mean()

plt.figure(figsize=(6,4))
promotion_demand.plot(kind="bar")
plt.title("Promotion Impact on Demand")
plt.ylabel("Average Demand")
plt.show()

print("\nPromotion Analysis")
print(promotion_demand)

# ==========================================================
# STORE DEMAND ANALYSIS
# ==========================================================

store_demand = df.groupby("store_id")["demand"].sum()

plt.figure(figsize=(10,5))
store_demand.plot(kind="bar")
plt.title("Store Wise Demand")
plt.show()

# ==========================================================
# PRODUCT DEMAND ANALYSIS
# ==========================================================

product_demand = df.groupby("product_id")["demand"].sum()

plt.figure(figsize=(12,5))
product_demand.plot(kind="bar")
plt.title("Product Wise Demand")
plt.show()

# ==========================================================
# PRICE VS DEMAND
# ==========================================================

plt.figure(figsize=(10,5))
sns.scatterplot(
    x="price",
    y="demand",
    hue="promotion",
    data=df
)
plt.title("Price vs Demand")
plt.show()

# ==========================================================
# CORRELATION HEATMAP
# ==========================================================

numeric_cols = df.select_dtypes(include=np.number)

plt.figure(figsize=(10,6))
sns.heatmap(
    numeric_cols.corr(),
    annot=True,
    cmap="coolwarm"
)
plt.title("Correlation Matrix")
plt.show()

# ==========================================================
# LABEL ENCODING
# ==========================================================

data = df.copy()

store_encoder = LabelEncoder()
product_encoder = LabelEncoder()

data["store_id"] = store_encoder.fit_transform(data["store_id"])
data["product_id"] = product_encoder.fit_transform(data["product_id"])

# ==========================================================
# FEATURE SELECTION
# ==========================================================

X = data[
    [
        "store_id",
        "product_id",
        "price",
        "promotion",
        "year",
        "month",
        "day",
        "week",
        "quarter",
        "dayofweek"
    ]
]

y = data["demand"]

# ==========================================================
# TRAIN TEST SPLIT
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining Shape:", X_train.shape)
print("Testing Shape:", X_test.shape)

# ==========================================================
# LINEAR REGRESSION
# ==========================================================

lr = LinearRegression()

lr.fit(X_train, y_train)

lr_predictions = lr.predict(X_test)

print("\nLINEAR REGRESSION RESULTS")
print("MAE :", mean_absolute_error(y_test, lr_predictions))
print("RMSE :", np.sqrt(mean_squared_error(y_test, lr_predictions)))
print("R2 :", r2_score(y_test, lr_predictions))

# ==========================================================
# RANDOM FOREST
# ==========================================================

rf = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    max_depth=15
)

rf.fit(X_train, y_train)

rf_predictions = rf.predict(X_test)

print("\nRANDOM FOREST RESULTS")
print("MAE :", mean_absolute_error(y_test, rf_predictions))
print("RMSE :", np.sqrt(mean_squared_error(y_test, rf_predictions)))
print("R2 :", r2_score(y_test, rf_predictions))

# ==========================================================
# FEATURE IMPORTANCE
# ==========================================================

importance = pd.DataFrame(
    {
        "Feature": X.columns,
        "Importance": rf.feature_importances_
    }
)

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

print("\nTop Important Features")
print(importance)

plt.figure(figsize=(10,6))
sns.barplot(
    data=importance,
    x="Importance",
    y="Feature"
)
plt.title("Feature Importance")
plt.show()

# ==========================================================
# ACTUAL VS PREDICTED
# ==========================================================

plt.figure(figsize=(8,6))
plt.scatter(
    y_test,
    rf_predictions,
    alpha=0.5
)
plt.xlabel("Actual Demand")
plt.ylabel("Predicted Demand")
plt.title("Actual vs Predicted Demand")
plt.show()

# ==========================================================
# INVENTORY OPTIMIZATION
# ==========================================================

inventory_analysis = (
    df.groupby("product_id")["demand"]
    .mean()
    .reset_index()
)

inventory_analysis.columns = [
    "product_id",
    "avg_demand"
]

inventory_analysis["reorder_level"] = (
    inventory_analysis["avg_demand"] * 1.20
)

inventory_analysis["safety_stock"] = (
    inventory_analysis["avg_demand"] * 0.50
)

inventory_analysis = inventory_analysis.sort_values(
    by="avg_demand",
    ascending=False
)

print("\nTop Products to Stock")
print(inventory_analysis.head(10))

# ==========================================================
# FORECAST SAMPLE
# ==========================================================

forecast_df = pd.DataFrame(
    {
        "Actual_Demand": y_test.values,
        "Predicted_Demand": rf_predictions
    }
)

print("\nDemand Forecast Sample")
print(forecast_df.head(20))

# ==========================================================
# BUSINESS INSIGHTS
# ==========================================================

print("\n")
print("=" * 70)
print("SMART WAREHOUSE BUSINESS INSIGHTS")
print("=" * 70)

print("1. Identify high-demand products.")
print("2. Maintain safety stock for critical products.")
print("3. Promotion campaigns increase demand.")
print("4. Price impacts inventory movement.")
print("5. Random Forest provides accurate forecasting.")
print("6. Prioritize stock allocation to high-demand stores.")
print("7. Use reorder levels for inventory replenishment.")
print("8. Reduce stock-outs using demand prediction.")
print("9. Optimize warehouse storage planning.")
print("10. Improve supply chain efficiency.")

print("=" * 70)
print("PROJECT COMPLETED SUCCESSFULLY")
print("=" * 70)
