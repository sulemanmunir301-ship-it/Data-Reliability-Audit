"""Profile the raw tables BEFORE trusting any check. Prints and saves results/profile.md.

usage: python scripts/profile_raw.py <db.duckdb>

Look at this output first on real data: column types, null counts, date range, duplicate keys,
status values. Set `as_of_date` in dbt_project.yml from the 'newest order date' line.
"""
import pathlib
import sys

import duckdb

db = sys.argv[1]
con = duckdb.connect(db, read_only=True)
lines = []


def out(s=""):
    print(s)
    lines.append(s)


tables = [r[0] for r in con.execute(
    "select table_name from information_schema.tables where table_schema='raw' order by 1").fetchall()]

for t in tables:
    n = con.execute(f"select count(*) from raw.{t}").fetchone()[0]
    out(f"## raw.{t}  ({n:,} rows)")
    cols = con.execute(
        "select column_name, data_type from information_schema.columns "
        f"where table_schema='raw' and table_name='{t}' order by ordinal_position").fetchall()
    out("| column | type | nulls | distinct |")
    out("|---|---|---|---|")
    for c, ty in cols:
        nulls, dist = con.execute(f'select count(*) - count("{c}"), count(distinct "{c}") from raw.{t}').fetchone()
        out(f"| {c} | {ty} | {nulls:,} | {dist:,} |")
    out()

if "orders" in tables:
    mn, mx = con.execute(
        "select min(cast(order_purchase_timestamp as date)), max(cast(order_purchase_timestamp as date)) from raw.orders").fetchone()
    out(f"## Orders date range\noldest order date: {mn}\nnewest order date: {mx}  <- set as_of_date near this")
    out()
    out("## order_status counts")
    for s, c in con.execute("select order_status, count(*) from raw.orders group by 1 order by 2 desc").fetchall():
        out(f"- {s}: {c:,}")
    out()
    d = con.execute("select count(*) - count(distinct order_id) from raw.orders").fetchone()[0]
    out(f"duplicate order_id rows in orders: {d:,}")
    out()
    out("## Months with fewest orders (sparse history makes the volume check noisy)")
    for m, c in con.execute(
            "select strftime(cast(order_purchase_timestamp as date), '%Y-%m'), count(*) from raw.orders "
            "group by 1 order by 2 limit 5").fetchall():
        out(f"- {m}: {c:,}")
    out()

if "order_items" in tables and "orders" in tables:
    a = con.execute("select count(*) from raw.orders where order_status='delivered' and order_id not in "
                    "(select order_id from raw.order_items)").fetchone()[0]
    b = con.execute("select count(*) from raw.order_items where order_id not in (select order_id from raw.orders)").fetchone()[0]
    out(f"delivered orders with no items: {a:,}")
    out(f"items whose order_id is missing from orders: {b:,}")
    out()

if "order_payments" in tables:
    d = con.execute("select count(*) from (select order_id, payment_sequential from raw.order_payments "
                    "group by 1,2 having count(*)>1)").fetchone()[0]
    out(f"duplicated (order_id, payment_sequential) pairs: {d:,}")
    types = con.execute("select payment_type, count(*) from raw.order_payments group by 1 order by 2 desc").fetchall()
    out("payment types: " + ", ".join(f"{k}={v:,}" for k, v in types))

pathlib.Path("results").mkdir(exist_ok=True)
pathlib.Path("results/profile.md").write_text("\n".join(lines) + "\n")
print("\nwrote results/profile.md")
