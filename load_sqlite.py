import sqlite3
import pandas as pd

df = pd.read_csv("retail_sales.csv")
con = sqlite3.connect("retail_analytics.db")
df.to_sql("retail_sales", con, if_exists="replace", index=False)
print("Loaded", len(df), "rows into retail_analytics.db")
con.close()
