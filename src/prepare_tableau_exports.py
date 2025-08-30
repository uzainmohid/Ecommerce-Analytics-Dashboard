
# Prepare aggregated facts for Tableau + RFM & churn flags.
# Outputs:
# - data/processed/tableau_sales_facts.csv
# - data/processed/tableau_customer_kpis.csv
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

tx = pd.read_csv(RAW / "transactions.csv", parse_dates=["order_date"])

# Monthly facts
sales_facts = (
    tx.assign(order_month=tx["order_date"].values.astype('datetime64[M]'))
      .groupby(["order_month","country","state","category","subcategory","channel"], as_index=False)
      .agg(orders=("order_id","nunique"),
           customers=("customer_id","nunique"),
           units=("quantity","sum"),
           revenue=("revenue","sum"))
)
sales_facts.to_csv(PROC / "tableau_sales_facts.csv", index=False)

# RFM per customer
max_date = tx["order_date"].max().normalize()
cust_grp = tx.groupby("customer_id", as_index=False).agg(
    last_purchase=("order_date","max"),
    frequency=("order_id","nunique"),
    monetary=("revenue","sum")
)
cust_grp["recency"] = (max_date - cust_grp["last_purchase"]).dt.days
# Quantile scores (1 low .. 5 high) — invert recency so lower days => higher score
cust_grp["R"] = pd.qcut(-cust_grp["recency"], 5, labels=[1,2,3,4,5])
cust_grp["F"] = pd.qcut(cust_grp["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5])
cust_grp["M"] = pd.qcut(cust_grp["monetary"].rank(method="first"), 5, labels=[1,2,3,4,5])
cust_grp["RFM_Score"] = cust_grp["R"].astype(int)*100 + cust_grp["F"].astype(int)*10 + cust_grp["M"].astype(int)

# Churn flag = no purchase in last 90 days
cust_grp["recency_days"] = cust_grp["recency"]
cust_grp["churn_flag"] = (cust_grp["recency_days"] > 90).astype(int)

# Join geography for slicing
cust_geo = tx[["customer_id","country","state","city"]].drop_duplicates("customer_id")
cust_kpis = cust_grp.merge(cust_geo, on="customer_id", how="left")

# Rename and export
cust_kpis = cust_kpis.rename(columns={
    "last_purchase": "last_purchase_date",
    "frequency": "orders",
    "monetary": "revenue"
})
cust_kpis.to_csv(PROC / "tableau_customer_kpis.csv", index=False)

print("Exports written to data/processed/")
