# 🏭 Smart Warehouse Inventory Optimizer

> **Pragyan AI Hackathon** | Python + Streamlit + Pandas

## 🚀 Quick Start

```bash
# 1. Clone and enter project
git clone https://github.com/YOUR_USERNAME/smart-warehouse-optimizer
cd smart-warehouse-optimizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate dataset
python data/generate_data.py

# 4. Launch dashboard
streamlit run dashboard/app.py
```

## 🧠 Features
- **Safety Stock** = Z × σ_demand × √(Lead Time)
- **Reorder Point** = (Avg Demand × Lead Time) + Safety Stock
- **EOQ** = √(2DS/H) — Economic Order Quantity
- **5-level stock alerts**: Out of Stock → Critical → Reorder → Adequate → Overstocked
- **Interactive charts**: Demand trend, treemap, status pie
- **Adjustable service level** (90%, 95%, 99%)
