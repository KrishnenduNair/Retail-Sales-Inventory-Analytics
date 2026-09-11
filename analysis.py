import pandas as pd
import numpy as np
from scipy.optimize import linprog

DATA = "retail_sales.csv"
df = pd.read_csv(DATA, parse_dates=["date"])

# 1) Data quality / integrity checks
checks = {
    "duplicate_rows": int(df.duplicated().sum()),
    "missing_values": int(df.isna().sum().sum()),
    "negative_units": int((df["units_sold"] < 0).sum()),
    "negative_revenue": int((df["revenue"] < 0).sum()),
}
print("DATA QUALITY CHECKS")
for k, v in checks.items():
    print(f"{k}: {v}")

# 2) KPI analysis
monthly = df.assign(month=df["date"].dt.to_period("M").astype(str)).groupby("month").agg(
    revenue=("revenue", "sum"), units=("units_sold", "sum")
).reset_index()
product = df.groupby("product").agg(
    revenue=("revenue", "sum"), units=("units_sold", "sum")
).sort_values("revenue", ascending=False)

print("\nTOP PRODUCTS BY REVENUE")
print(product.head())

# 3) Demand baseline + what-if scenario analysis
daily = df.groupby(["date", "product"])["units_sold"].sum().reset_index()
latest = daily["date"].max()
recent = daily[daily["date"] > latest - pd.Timedelta(days=30)]
forecast = recent.groupby("product")["units_sold"].mean().rename("baseline_daily_demand")

scenarios = pd.DataFrame({
    "scenario": ["Baseline", "Demand +10%", "Demand -10%"],
    "demand_multiplier": [1.00, 1.10, 0.90]
})
scenario_rows = []
for _, s in scenarios.iterrows():
    scenario_rows.append({
        "scenario": s["scenario"],
        "projected_30_day_units": round((forecast.sum() * s["demand_multiplier"] * 30), 0)
    })
print("\nSCENARIO ANALYSIS")
print(pd.DataFrame(scenario_rows))

# 4) Simple allocation optimization: allocate limited replenishment to products
# Objective: maximize expected contribution using a proxy margin and demand coverage.
margin = {"Laptop": .18, "Monitor": .22, "Keyboard": .30, "Mouse": .32,
          "Headset": .28, "Printer": .20, "Router": .25, "Webcam": .27}
products = forecast.index.tolist()
demand = forecast.reindex(products).values
price = df.groupby("product")["unit_price"].first().reindex(products).values
profit_per_unit = price * np.array([margin[p] for p in products])
capacity = max(1, int(demand.sum() * 0.20))

# maximize profit => minimize negative profit; x <= demand*1.2, sum x <= capacity
res = linprog(-profit_per_unit, A_ub=[np.ones(len(products))],
              b_ub=[capacity], bounds=list(zip(np.zeros(len(products)), demand*1.2)),
              method="highs")
allocation = pd.DataFrame({
    "product": products,
    "recommended_replenishment": np.round(res.x, 0).astype(int)
})
print("\nREPLENISHMENT ALLOCATION")
print(allocation)
