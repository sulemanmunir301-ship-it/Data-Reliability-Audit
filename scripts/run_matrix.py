"""Inject one failure at a time into a COPY of the clean database, run all checks, and
build a detection matrix (which checks caught which failure, and which failures were missed).

usage: python scripts/run_matrix.py <clean.duckdb>
writes: results/detection_matrix.md and results/detection_matrix.json

Injected failures are SYNTHETIC. The matrix shows what these checks can catch; it is not a
measurement of how often such failures occur in real businesses.
"""
import json
import os
import pathlib
import shutil
import sys

import duckdb

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run_checks  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
clean = pathlib.Path(sys.argv[1]).resolve()
work = ROOT / "data" / "scenario.duckdb"

# Each injection is one SQL script. Windows use order purchase date.
FAILURES = {
    "A_partial_item_loss": (
        "40% of order_items missing for orders placed 2018-03-01..2018-03-10",
        """delete from raw.order_items where order_id in (
             select order_id from raw.orders
             where cast(order_purchase_timestamp as date) between date '2018-03-01' and date '2018-03-10')
           and hash(order_id) % 100 < 40;""",
    ),
    "B_null_customer_ids": (
        "15% of orders from 2018-04-01 lose customer_id",
        """update raw.orders set customer_id = null
           where cast(order_purchase_timestamp as date) >= date '2018-04-01' and hash(order_id) % 100 < 15;""",
    ),
    "C_duplicated_payments": (
        "All payments for orders placed 2018-02-14 loaded twice (retry)",
        """insert into raw.order_payments
           select * from raw.order_payments where order_id in (
             select order_id from raw.orders where cast(order_purchase_timestamp as date) = date '2018-02-14');""",
    ),
    "D_schema_drift": (
        "order_items.price silently changes type DOUBLE -> VARCHAR",
        "alter table raw.order_items alter column price type varchar;",
    ),
    "E_loader_stopped": (
        "Loader stops: no data after 2018-05-31 and _loaded_at is 5 days old",
        """delete from raw.order_payments where order_id in (select order_id from raw.orders where cast(order_purchase_timestamp as date) > date '2018-05-31');
           delete from raw.order_items    where order_id in (select order_id from raw.orders where cast(order_purchase_timestamp as date) > date '2018-05-31');
           delete from raw.orders where cast(order_purchase_timestamp as date) > date '2018-05-31';
           update raw.orders         set _loaded_at = _loaded_at - interval 5 day;
           update raw.customers      set _loaded_at = _loaded_at - interval 5 day;
           update raw.order_items    set _loaded_at = _loaded_at - interval 5 day;
           update raw.order_payments set _loaded_at = _loaded_at - interval 5 day;""",
    ),
    "F_silent_value_shift": (
        "price x100 (cents vs reais) for orders placed 2018-05-01..2018-05-07; counts and keys unchanged",
        """update raw.order_items set price = price * 100
           where order_id in (select order_id from raw.orders
             where cast(order_purchase_timestamp as date) between date '2018-05-01' and date '2018-05-07');""",
    ),
}


def run_scenario(sql):
    shutil.copy(clean, work)
    if sql:
        con = duckdb.connect(str(work))
        for stmt in [s for s in sql.split(";") if s.strip()]:
            con.execute(stmt)
        con.close()
    os.environ["OLIST_DB"] = str(work)
    return run_checks.collect()


baseline = run_scenario(None)
base_set = {p["check"] for p in baseline}
print("baseline problems on CLEAN data:", sorted(base_set) or "none")

results = {"baseline_on_clean": baseline, "scenarios": {}}
for key, (desc, sql) in FAILURES.items():
    probs = run_scenario(sql)
    base_fail = {p["check"]: p["failures"] for p in baseline}
    # new problem, OR a baseline WARN whose failing-row count grew >1.5x (a worsening known issue)
    new = [p for p in probs if p["check"] not in base_set
           or (p["failures"] and base_fail.get(p["check"]) and p["failures"] > 1.5 * base_fail[p["check"]])]
    results["scenarios"][key] = {"description": desc, "detected_by": new}
    print(key, "->", [p["check"] for p in new] or "MISSED")

(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "detection_matrix.json").write_text(json.dumps(results, indent=2, default=str))

md = ["# Detection matrix", "",
      "Failures are synthetic and injected one at a time into a copy of the clean database.",
      "'Caught by' lists checks that failed/errored on the broken copy but not on the clean baseline.", "",
      f"Baseline on clean data: {', '.join(sorted(base_set)) or 'no problems'}", "",
      "| Failure | Injected | Caught? | Caught by (failing rows) |", "|---|---|---|---|"]
for key, v in results["scenarios"].items():
    caught = v["detected_by"]
    cell = "<br>".join(f"`{p['check']}`" + (f" ({p['failures']})" if p["failures"] is not None else "")
                       + f" [{p['status']}]" for p in caught) or "**MISSED**"
    md.append(f"| {key} | {v['description']} | {'yes' if caught else 'NO'} | {cell} |")
(ROOT / "results" / "detection_matrix.md").write_text("\n".join(md) + "\n")
print("wrote results/detection_matrix.md")
