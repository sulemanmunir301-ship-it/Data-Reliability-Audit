"""Generate Olist-SHAPED synthetic CSVs (same file names + columns as the Kaggle dataset).

Purpose: lets the whole repo run and be tested offline / without a Kaggle login.
It is NOT the real data, and findings on it say nothing about Olist.
Swap in the real CSVs (see README) and every other script works unchanged.
"""
import pathlib
import sys

import numpy as np
import pandas as pd

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "data/synthetic")
out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)

days = pd.date_range("2017-01-01", "2018-06-30", freq="D")
weekday_factor = {0: 1.1, 1: 1.1, 2: 1.05, 3: 1.05, 4: 1.0, 5: 0.8, 6: 0.7}
orders, customers, items, pays = [], [], [], []
oid = 0
for d in days:
    n = rng.poisson(120 * weekday_factor[d.weekday()])
    for _ in range(n):
        oid += 1
        order_id = f"o{oid:08d}"
        cust_id = f"c{oid:08d}"
        ts = d + pd.Timedelta(seconds=int(rng.integers(0, 86400)))
        r = rng.random()
        status = ("delivered" if r < 0.965 else "canceled" if r < 0.975
                  else "unavailable" if r < 0.985 else "shipped")
        orders.append((order_id, cust_id, status, ts, ts + pd.Timedelta(hours=2),
                       ts + pd.Timedelta(days=2), ts + pd.Timedelta(days=9),
                       ts + pd.Timedelta(days=15)))
        customers.append((cust_id, f"u{int(rng.integers(1, 80000)):08d}",
                          int(rng.integers(1000, 99999)), "sao paulo",
                          str(rng.choice(["SP", "RJ", "MG", "RS", "PR"]))))
        if status in ("canceled", "unavailable"):
            continue
        total = 0.0
        for k in range(1, int(rng.choice([1, 2, 3], p=[0.8, 0.15, 0.05])) + 1):
            price = round(float(rng.lognormal(4.3, 0.8)), 2)
            freight = round(float(rng.uniform(8, 40)), 2)
            total += price + freight
            items.append((order_id, k, f"p{int(rng.integers(1, 30000)):06d}",
                          f"s{int(rng.integers(1, 3000)):05d}",
                          ts + pd.Timedelta(days=3), price, freight))
        pv = round(total * (1.1 if rng.random() < 0.01 else 1.0), 2)  # ~1% mismatch
        pays.append((order_id, 1,
                     str(rng.choice(["credit_card", "boleto", "voucher", "debit_card"],
                                    p=[.74, .19, .05, .02])),
                     int(rng.integers(1, 9)), pv))

pd.DataFrame(orders, columns=[
    "order_id", "customer_id", "order_status", "order_purchase_timestamp",
    "order_approved_at", "order_delivered_carrier_date",
    "order_delivered_customer_date", "order_estimated_delivery_date",
]).to_csv(out / "olist_orders_dataset.csv", index=False)
pd.DataFrame(customers, columns=[
    "customer_id", "customer_unique_id", "customer_zip_code_prefix",
    "customer_city", "customer_state",
]).to_csv(out / "olist_customers_dataset.csv", index=False)
pd.DataFrame(items, columns=[
    "order_id", "order_item_id", "product_id", "seller_id",
    "shipping_limit_date", "price", "freight_value",
]).to_csv(out / "olist_order_items_dataset.csv", index=False)
pd.DataFrame(pays, columns=[
    "order_id", "payment_sequential", "payment_type",
    "payment_installments", "payment_value",
]).to_csv(out / "olist_order_payments_dataset.csv", index=False)
print(f"wrote {len(orders)} orders, {len(items)} items, {len(pays)} payments to {out}")
