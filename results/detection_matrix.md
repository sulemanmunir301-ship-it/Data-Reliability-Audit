# Detection matrix

Failures are synthetic and injected one at a time into a copy of the clean database.
'Caught by' lists checks that failed/errored on the broken copy but not on the clean baseline.

Baseline on clean data: t_payment_vs_item_total

| Failure | Injected | Caught? | Caught by (failing rows) |
|---|---|---|---|
| A_partial_item_loss | 40% of order_items missing for orders placed 2018-03-01..2018-03-10 | yes | `t_delivered_orders_without_items` (430) [fail]<br>`t_volume_daily_order_items_drop` (8) [fail] |
| B_null_customer_ids | 15% of orders from 2018-04-01 lose customer_id | yes | `not_null_stg_orders_customer_id` (1637) [fail] |
| C_duplicated_payments | All payments for orders placed 2018-02-14 loaded twice (retry) | yes | `t_duplicate_payment_rows` (116) [fail] |
| D_schema_drift | order_items.price silently changes type DOUBLE -> VARCHAR | yes | `t_raw_schema_drift` (1) [fail] |
| E_loader_stopped | Loader stops: no data after 2018-05-31 and _loaded_at is 5 days old | yes | `source_freshness.raw.order_items` [error]<br>`source_freshness.raw.order_payments` [error]<br>`source_freshness.raw.customers` [error]<br>`source_freshness.raw.orders` [error]<br>`t_data_freshness_orders` (1) [fail]<br>`t_volume_daily_order_items_drop` (28) [fail] |
| F_silent_value_shift | price x100 (cents vs reais) for orders placed 2018-05-01..2018-05-07; counts and keys unchanged | yes | `t_payment_vs_item_total` (1479) [warn] |
