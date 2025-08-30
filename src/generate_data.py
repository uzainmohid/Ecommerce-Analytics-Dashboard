
# Generate realistic e-commerce data (customers, products, transactions).
# Outputs:
# - data/raw/customers.csv
# - data/raw/products.csv
# - data/raw/transactions.csv
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

# Customers
n_customers = 5000
countries = ["USA", "Canada", "UK", "Germany", "India", "Australia"]
states_by_country = {
    "USA": ["CA","NY","TX","FL","WA","IL"],
    "Canada": ["ON","BC","QC","AB"],
    "UK": ["England","Scotland","Wales","NI"],
    "Germany": ["BE","BW","BY","HH","HE","NW"],
    "India": ["TN","KA","MH","DL","GJ","WB"],
    "Australia": ["NSW","VIC","QLD","WA"]
}
cities_sample = ["CityA","CityB","CityC","CityD","CityE","CityF"]

cust_ids = np.arange(100000, 100000 + n_customers)
cust_country = np.random.choice(countries, size=n_customers, p=[0.45,0.08,0.08,0.07,0.25,0.07])
cust_state = [np.random.choice(states_by_country[c]) for c in cust_country]
cust_city = np.random.choice(cities_sample, size=n_customers)

signup_start = np.datetime64("2023-01-01")
signup_end = np.datetime64("2025-06-30")
signup_dates = signup_start + (signup_end - signup_start) * np.random.rand(n_customers)
customers = pd.DataFrame({
    "customer_id": cust_ids,
    "signup_date": pd.to_datetime(signup_dates).date,
    "country": cust_country,
    "state": cust_state,
    "city": cust_city
})

# Products
categories = {
    "Electronics": ["Phones","Laptops","Accessories"],
    "Fashion": ["Men","Women","Accessories"],
    "Home": ["Kitchen","Decor","Furniture"],
    "Sports": ["Outdoor","Fitness","Apparel"]
}
product_rows = []
pid = 200000
for cat, subs in categories.items():
    for sub in subs:
        for i in range(1, 21):  # 20 products per subcategory
            base = np.random.randint(10, 500) * 1.0
            product_rows.append((pid, f"{cat} {sub} {i}", cat, sub, base))
            pid += 1
products = pd.DataFrame(product_rows, columns=["product_id","product_name","category","subcategory","base_price"])

# Transactions
n_orders = 100_000
order_start = np.datetime64("2023-01-01")
order_end = np.datetime64("2025-08-01")
order_dates = order_start + (order_end - order_start) * np.random.rand(n_orders)
order_dates = pd.to_datetime(order_dates)

# seasonality multipliers (Nov-Dec peak, June dip)
month_mult = {m:1.0 for m in range(1,13)}
for m in [11,12]:
    month_mult[m] = 1.25
month_mult[6] = 0.9

channels = ["Web","Mobile","Marketplace","Social"]
channel_p = [0.45,0.35,0.15,0.05]

cust_choices = np.random.choice(cust_ids, size=n_orders)
prod_choices = products.sample(n_orders, replace=True).reset_index(drop=True)
qty = np.random.choice([1,2,3,4], size=n_orders, p=[0.65,0.25,0.08,0.02])

base_price = prod_choices["base_price"].values
noise = np.random.normal(loc=1.0, scale=0.1, size=n_orders)
price = np.clip(base_price * noise, 5, None)
discount = np.where(np.random.rand(n_orders) < 0.15, np.random.uniform(0.05, 0.30, n_orders), 0.0)
rev = qty * price * (1 - discount)

trans = pd.DataFrame({
    "order_id": np.arange(500000, 500000 + n_orders),
    "order_date": order_dates,
    "customer_id": cust_choices,
    "product_id": prod_choices["product_id"].values,
    "category": prod_choices["category"].values,
    "subcategory": prod_choices["subcategory"].values,
    "quantity": qty,
    "price": price.round(2),
    "discount": np.round(discount, 3),
    "revenue": rev.round(2),
    "channel": np.random.choice(channels, size=n_orders, p=channel_p)
})

# Join geo for slicing
trans = trans.merge(customers[["customer_id","country","state","city"]], on="customer_id", how="left")

# Apply seasonality to revenue by month
trans["month"] = trans["order_date"].dt.month
trans["revenue"] = (trans["revenue"] * trans["month"].map(month_mult)).round(2)

# Save
customers.to_csv(RAW / "customers.csv", index=False)
products.to_csv(RAW / "products.csv", index=False)
trans.drop(columns=["month"], inplace=True)
trans.to_csv(RAW / "transactions.csv", index=False)

print("Generated data in data/raw/")
