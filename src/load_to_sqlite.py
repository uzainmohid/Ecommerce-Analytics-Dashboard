
# Load raw CSVs into a SQLite database with simple indexes.
# Creates: data/db/ecom.db
import pandas as pd
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DBP = ROOT / "data" / "db" / "ecom.db"

conn = sqlite3.connect(DBP)

customers = pd.read_csv(RAW / "customers.csv")
products = pd.read_csv(RAW / "products.csv")
transactions = pd.read_csv(RAW / "transactions.csv", parse_dates=["order_date"])

customers.to_sql("customers", conn, if_exists="replace", index=False)
products.to_sql("products", conn, if_exists="replace", index=False)
transactions.to_sql("transactions", conn, if_exists="replace", index=False)

cur = conn.cursor()
cur.execute("CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(order_date);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_txn_customer ON transactions(customer_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_txn_product ON transactions(product_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_cust_id ON customers(customer_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_prod_id ON products(product_id);")
conn.commit()
conn.close()

print("Loaded data into data/db/ecom.db")
