import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from src.data_loader import load_data, get_product_summary
from src.inventory_analysis import enrich_summary
from src.visualizations import (
    stock_status_pie, demand_trend,
    stock_vs_rop_bar, stock_value_treemap, category_demand_bar
)

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Warehouse Optimizer",
    page_icon="🏭",
    layout="wide",
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 12px; padding: 16px; color: white;
        text-align: center; margin: 4px;
    }
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
@st.cache_data
def load_all():
    df = load_data("data/inventory_data.csv")
    summary = get_product_summary(df)
    return df, summary

df, summary = load_all()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/warehouse.png", width=80)
st.sidebar.title("⚙️ Settings")

service_level = st.sidebar.selectbox(
    "Service Level", ["90%", "95%", "99%"], index=1,
    help="Higher service level → more safety stock buffered"
)
category_filter = st.sidebar.multiselect(
    "Filter by Category",
    options=df["category"].unique().tolist(),
    default=df["category"].unique().tolist()
)

enriched = enrich_summary(summary, service_level)
enriched_filtered = enriched[enriched["category"].isin(category_filter)]
df_filtered = df[df["category"].isin(category_filter)]

# ── Header ────────────────────────────────────────────────────
st.title("🏭 Smart Warehouse Inventory Optimizer")
st.caption("Pragyan AI Hackathon | Real-time Stock Intelligence Dashboard")

# ── KPI Row ───────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
total_products   = len(enriched_filtered)
out_of_stock     = (enriched_filtered["status"] == "🔴 OUT OF STOCK").sum()
critical         = (enriched_filtered["status"] == "🟠 CRITICAL").sum()
reorder_needed   = (enriched_filtered["status"] == "🟡 REORDER NOW").sum()
total_stock_val  = enriched_filtered["stock_value"].sum()

k1.metric("📦 Total Products",   total_products)
k2.metric("🔴 Out of Stock",     out_of_stock,    delta=f"-{out_of_stock}" if out_of_stock else None, delta_color="inverse")
k3.metric("🟠 Critical Stock",   critical,        delta=f"-{critical}" if critical else None, delta_color="inverse")
k4.metric("🟡 Reorder Needed",   reorder_needed)
k5.metric("💰 Total Stock Value",f"${total_stock_val:,.0f}")

st.divider()

# ── Alerts Panel ──────────────────────────────────────────────
alerts = enriched_filtered[enriched_filtered["status"].isin(["🔴 OUT OF STOCK","🟠 CRITICAL","🟡 REORDER NOW"])]

if not alerts.empty:
    with st.expander(f"🚨 Active Alerts ({len(alerts)} products need attention)", expanded=True):
        for _, row in alerts.iterrows():
            css_class = "alert-box" if "OUT" in row["status"] or "CRITICAL" in row["status"] else "warn-box"
            st.markdown(
                f'<div class="{css_class}">'
                f'<b>{row["status"]} — {row["product_name"]}</b><br>'
                f'Current Stock: <b>{int(row["current_stock"])}</b> units | '
                f'Reorder Point: <b>{row["reorder_point"]}</b> | '
                f'Safety Stock: <b>{row["safety_stock"]}</b> | '
                f'Days Remaining: <b>{row["days_of_stock"]}</b> | '
                f'Suggested Order (EOQ): <b>{int(row["eoq"])}</b> units'
                f'</div>',
                unsafe_allow_html=True
            )
else:
    st.success("✅ All products are at healthy stock levels!")

st.divider()

# ── Charts Row 1 ──────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(stock_status_pie(enriched_filtered), use_container_width=True)
with col2:
    st.plotly_chart(category_demand_bar(df_filtered), use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────
st.plotly_chart(stock_vs_rop_bar(enriched_filtered), use_container_width=True)
st.plotly_chart(stock_value_treemap(enriched_filtered), use_container_width=True)

# ── Demand Trend ──────────────────────────────────────────────
st.subheader("📈 Product Demand Trend")
product_options = enriched_filtered.set_index("product_id")["product_name"].to_dict()
selected_pid = st.selectbox(
    "Select Product",
    options=list(product_options.keys()),
    format_func=lambda x: f"{x} — {product_options[x]}"
)
st.plotly_chart(demand_trend(df_filtered, selected_pid), use_container_width=True)

# ── Full Inventory Table ──────────────────────────────────────
st.subheader("📋 Full Inventory Intelligence Table")
display_cols = [
    "product_name","category","current_stock","avg_daily_demand",
    "safety_stock","reorder_point","eoq","days_of_stock","stock_value","status"
]
st.dataframe(
    enriched_filtered[display_cols].rename(columns={
        "product_name":     "Product",
        "category":         "Category",
        "current_stock":    "Stock",
        "avg_daily_demand": "Avg Daily Demand",
        "safety_stock":     "Safety Stock",
        "reorder_point":    "Reorder Point",
        "eoq":              "EOQ",
        "days_of_stock":    "Days Left",
        "stock_value":      "Stock Value ($)",
        "status":           "Status",
    }),
    use_container_width=True,
    height=400,
)

# ── Footer ────────────────────────────────────────────────────
st.divider()
st.caption("🏭 Smart Warehouse Inventory Optimizer | Built with Python + Streamlit | Pragyan AI Hackathon")
