import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

st.set_page_config(page_title="Retail Analytics", layout="wide")
st.title("Retail Sales & Inventory Analytics")
st.caption("Data extraction • integrity checks • SQL-ready analysis • forecasting • scenario analysis • allocation optimization")

df = pd.read_csv("retail_sales.csv", parse_dates=["date"])

# Data integrity checks
missing = int(df.isna().sum().sum())
duplicates = int(df.duplicated().sum())
if missing == 0 and duplicates == 0:
    st.success("Data integrity checks passed: no missing values or duplicate rows.")
else:
    st.warning(f"Data checks: {missing} missing values, {duplicates} duplicate rows.")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Revenue", f"${df.revenue.sum():,.0f}")
c2.metric("Units Sold", f"{df.units_sold.sum():,.0f}")
c3.metric("Products", df.product.nunique())
c4.metric("Regions", df.region.nunique())

st.subheader("Revenue Trend")
monthly = df.assign(month=df.date.dt.to_period("M").astype(str)).groupby("month").revenue.sum()
st.line_chart(monthly)

st.subheader("Product & Regional Analysis")
a,b = st.columns(2)
with a:
    st.bar_chart(df.groupby("product").revenue.sum().sort_values(ascending=False))
with b:
    st.bar_chart(df.groupby("region").revenue.sum().sort_values(ascending=False))

st.subheader("Demand Scenario Analysis")
daily = df.groupby(["date","product"]).units_sold.sum().reset_index()
latest = daily.date.max()
recent = daily[daily.date > latest - pd.Timedelta(days=30)]
baseline = recent.groupby("product").units_sold.mean()
scenario = st.slider("Demand change", -30, 30, 10, 5)
projected = baseline.sum() * (1 + scenario/100) * 30
st.metric("Projected 30-day units", f"{projected:,.0f}")

st.subheader("Replenishment Allocation")
margin = {"Laptop": .18, "Monitor": .22, "Keyboard": .30, "Mouse": .32,
          "Headset": .28, "Printer": .20, "Router": .25, "Webcam": .27}
products = baseline.index.tolist()
price = df.groupby("product").unit_price.first().reindex(products).values
profit = price * np.array([margin[p] for p in products])
capacity = max(1, int(baseline.sum() * .20))
res = linprog(-profit, A_ub=[np.ones(len(products))], b_ub=[capacity],
              bounds=list(zip(np.zeros(len(products)), baseline.values*1.2)), method="highs")
alloc = pd.DataFrame({"Product":products, "Recommended Units":np.round(res.x).astype(int)})
st.dataframe(alloc, use_container_width=True)
