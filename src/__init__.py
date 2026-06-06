# src/__init__.py

from .data_loader import load_data, get_product_summary
from .inventory_analysis import (
    calculate_safety_stock,
    calculate_reorder_point,
    calculate_eoq,
    classify_stock_status,
    enrich_summary,
    SERVICE_LEVEL_Z,
)
from .visualizations import (
    stock_status_pie,
    demand_trend,
    stock_vs_rop_bar,
    stock_value_treemap,
    category_demand_bar,
)

__version__ = "1.0.0"
__author__  = "Pragyan AI Hackathon Team"
__project__ = "Smart Warehouse Inventory Optimizer"

__all__ = [
    # Data
    "load_data",
    "get_product_summary",
    # Analysis
    "calculate_safety_stock",
    "calculate_reorder_point",
    "calculate_eoq",
    "classify_stock_status",
    "enrich_summary",
    "SERVICE_LEVEL_Z",
    # Visualizations
    "stock_status_pie",
    "demand_trend",
    "stock_vs_rop_bar",
    "stock_value_treemap",
    "category_demand_bar",
]
