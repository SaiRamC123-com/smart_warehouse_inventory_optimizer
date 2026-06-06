import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import streamlit as st
import pandas as pd
from src.data_loader import load_data, get_product_summary
from src.inventory_analysis import enrich_summary
from src.visualizations import (
    stock_status_pie, demand_trend,
    stock_vs_rop_bar, stock_value_treemap, category_demand_bar
)

st.set_page_config(
    page_title="Smart Warehouse Optimizer",
    page_icon="🏭", layout="wide"
)

st.markdown("""
<style>
.alert-box {
    border-left: 5px solid #e74c3c;
    background: #fdf2f2; padding: 10px 16px;
    border-radius: 4px; margin: 6px 0;
}
.warn-box {
    border-left: 5px solid #f39c12;
    background: #fef9f0; padding: 10px 16px;
    border-radius: 4px; margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────
DATA_PATH = os.path.join(BASE_DIR, "data",
            "inventory_demand_forecasting_dataset.csv")

@st.cache_data
def load_all(path):
    df      = load_data(path)
    summary = get_product_summary(df)
    return df, summary

try:
    df, summary = load_all(DATA_PATH)
except FileNotFoundError as e:
    st.error(f"❌ {e}")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.image(
    "https://img.icons8.com/fluency/96/warehouse.png", width=80
)
st.sidebar.title("⚙️ Settings")

service_level = st.sidebar.selectbox(
    "Service Level", ["90%", "95%", "99%"], index=1
)
product_filter = st.sidebar.multiselect(
    "Filter by Product",
    options=df["product_id"].unique().tolist(),
    default=df["product_id"].unique().tolist()
)
store_filter = st.sidebar.multiselect(
    "Filter by Store",
    options=df["store_id"].unique().tolist(),
    default=df["store_id"].unique().tolist()
)

df_filtered = df[
    df["product_id"].isin(product_filter) &
    df["store_id"].isin(store_filter)
]
enriched        = enrich_summary(summary, service_level)
enriched_filtered = enriched[enriched["product_id"].isin(product_filter)]

# ── Header ────────────────────────────────────────────────────
st.title("🏭 Smart Warehouse Inventory Optimizer")
st.caption("Pragyan AI Hackathon | Real-time Stock Intelligence Dashboard")

# ── KPIs ──────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📦 Products",       len(enriched_filtered))
k2.metric("🔴 Out of Stock",   (enriched_filtered["status"]=="🔴 OUT OF STOCK").sum())
k3.metric("🟠 Critical",       (enriched_filtered["status"]=="🟠 CRITICAL").sum())
k4.metric("🟡 Reorder Needed", (enriched_filtered["status"]=="🟡 REORDER NOW").sum())
k5.metric("📊 Avg Demand",     f"{df_filtered['demand'].mean():.1f}")

st.divider()

# ── Alerts ────────────────────────────────────────────────────
alerts = enriched_filtered[enriched_filtered["status"].isin([
    "🔴 OUT OF STOCK","🟠 CRITICAL","🟡 REORDER NOW"
])]

if not alerts.empty:
    with st.expander(f"🚨 Alerts ({len(alerts)} products)", expanded=True):
        for _, row in alerts.iterrows():
            css = "alert-box" if "OUT" in row["status"] or "CRITICAL" in row["status"] else "warn-box"
            st.markdown(
                f'<div class="{css}"><b>{row["status"]} — {row["product_name"]}</b><br>'
                f'Stock: <b>{int(row["current_stock"])}</b> | '
                f'Reorder Point: <b>{row["reorder_point"]}</b> | '
                f'Safety Stock: <b>{row["safety_stock"]}</b> | '
                f'Days Left: <b>{row["days_of_stock"]}</b> | '
                f'EOQ: <b>{int(row["eoq"])}</b></div>',
                unsafe_allow_html=True
            )
else:
    st.success("✅ All products at healthy stock levels!")

st.divider()

# ── Charts ────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(stock_status_pie(enriched_filtered),  use_container_width=True)
with col2:
    st.plotly_chart(category_demand_bar(df_filtered),     use_container_width=True)

st.plotly_chart(stock_vs_rop_bar(enriched_filtered),      use_container_width=True)
st.plotly_chart(stock_value_treemap(enriched_filtered),   use_container_width=True)

# ── Demand Trend ──────────────────────────────────────────────
st.subheader("📈 Product Demand Trend")
selected = st.selectbox("Select Product", df["product_id"].unique().tolist())
st.plotly_chart(demand_trend(df_filtered, selected),      use_container_width=True)

# ── Table ─────────────────────────────────────────────────────
st.subheader("📋 Inventory Intelligence Table")
st.dataframe(
    enriched_filtered[[
        "product_name","current_stock","avg_daily_demand",
        "safety_stock","reorder_point","eoq","days_of_stock",
        "stock_value","status"
    ]].rename(columns={
        "product_name":     "Product",
        "current_stock":    "Stock",
        "avg_daily_demand": "Avg Demand",
        "safety_stock":     "Safety Stock",
        "reorder_point":    "Reorder Point",
        "eoq":              "EOQ",
        "days_of_stock":    "Days Left",
        "stock_value":      "Stock Value ($)",
        "status":           "Status",
    }),
    use_container_width=True, height=400
)

st.divider()
st.caption("🏭 Smart Warehouse Optimizer | Pragyan AI Hackathon | Python + Streamlit")
