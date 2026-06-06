import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def stock_status_pie(enriched: pd.DataFrame) -> go.Figure:
    counts = enriched["status"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    color_map = {
        "🔴 OUT OF STOCK": "#e74c3c",
        "🟠 CRITICAL":     "#e67e22",
        "🟡 REORDER NOW":  "#f1c40f",
        "🟢 ADEQUATE":     "#2ecc71",
        "🔵 OVERSTOCKED":  "#3498db",
    }
    fig = px.pie(counts, names="Status", values="Count",
                 color="Status", color_discrete_map=color_map,
                 title="📊 Stock Status Distribution", hole=0.4)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig

def demand_trend(df: pd.DataFrame, product_id: str) -> go.Figure:
    pdata = df[df["product_id"] == product_id].copy()
    pdata = pdata.groupby("date")["demand"].mean().reset_index()
    pdata["7d_avg"] = pdata["demand"].rolling(7).mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=pdata["date"], y=pdata["demand"],
        name="Daily Demand", marker_color="rgba(52,152,219,0.5)"
    ))
    fig.add_trace(go.Scatter(
        x=pdata["date"], y=pdata["7d_avg"],
        name="7-Day Moving Avg",
        line=dict(color="#e74c3c", width=2)
    ))
    fig.update_layout(
        title=f"📈 Demand Trend — {product_id}",
        xaxis_title="Date", yaxis_title="Units",
        legend=dict(orientation="h"),
    )
    return fig

def stock_vs_rop_bar(enriched: pd.DataFrame) -> go.Figure:
    df = enriched.sort_values("current_stock")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["product_name"], y=df["current_stock"],
        name="Current Stock", marker_color="#3498db"
    ))
    fig.add_trace(go.Scatter(
        x=df["product_name"], y=df["reorder_point"],
        name="Reorder Point", mode="markers+lines",
        marker=dict(color="#e74c3c", size=10, symbol="diamond"),
        line=dict(color="#e74c3c", dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=df["product_name"], y=df["safety_stock"],
        name="Safety Stock", mode="markers+lines",
        marker=dict(color="#f39c12", size=8, symbol="triangle-up"),
        line=dict(color="#f39c12", dash="dot")
    ))
    fig.update_layout(
        title="📦 Stock vs Reorder Point vs Safety Stock",
        xaxis_title="Product", yaxis_title="Units",
        legend=dict(orientation="h"),
    )
    return fig

def stock_value_treemap(enriched: pd.DataFrame) -> go.Figure:
    fig = px.treemap(
        enriched, path=["category", "product_name"],
        values="stock_value", color="days_of_stock",
        color_continuous_scale="RdYlGn",
        title="💰 Stock Value Treemap (color = Days of Stock)",
    )
    return fig

def category_demand_bar(df: pd.DataFrame) -> go.Figure:
    avg = df.groupby("product_id")["demand"].mean().reset_index()
    avg.columns = ["Product", "Avg Daily Demand"]
    fig = px.bar(
        avg.sort_values("Avg Daily Demand", ascending=True),
        x="Avg Daily Demand", y="Product", orientation="h",
        title="🏭 Avg Daily Demand by Product",
        color="Avg Daily Demand", color_continuous_scale="Blues",
    )
    return fig
