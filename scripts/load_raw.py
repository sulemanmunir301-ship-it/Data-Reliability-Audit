"""Load Olist CSVs into DuckDB schema `raw`, adding a _loaded_at audit column.

usage: python scripts/load_raw.py <csv_dir> <out.duckdb>
"""
import pathlib
import sys

import duckdb

csv_dir, db = pathlib.Path(sys.argv[1]), sys.argv[2]
TABLES = {  # raw table -> Kaggle file name (only the tables this repo uses)
    "orders": "olist_orders_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
}
con = duckdb.connect(db)
con.execute("create schema if not exists raw")
for t, f in TABLES.items():
    path = (csv_dir / f).as_posix()
    con.execute(
        f"create or replace table raw.{t} as "
        f"select *, current_timestamp::timestamp as _loaded_at "
        f"from read_csv_auto('{path}', header=true)"
    )
    print(t, con.execute(f"select count(*) from raw.{t}").fetchone()[0], "rows")
