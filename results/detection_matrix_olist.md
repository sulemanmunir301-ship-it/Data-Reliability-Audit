# Detection matrix

Failures are synthetic and injected one at a time into a copy of the clean database.
'Caught by' lists checks that failed/errored on the broken copy but not on the clean baseline.

Baseline on clean data: t_data_freshness_last_healthy_day, t_early_hours_gap, t_orders_without_payments, t_payment_vs_item_total, t_volume_drop_moderate, t_volume_drop_severe

| Failure | Injected | Caught? | Caught by (failing rows) |
|---|---|---|---|
| A_partial_item_loss | 40% of order_items missing for orders placed 2018-03-01..2018-03-10 | yes | `t_delivered_orders_without_items` (945) [fail]<br>`t_volume_drop_moderate` (42) [warn] |
| B_null_customer_ids | 15% of orders from 2018-04-01 lose customer_id | yes | `not_null_stg_orders_customer_id` (4820) [fail] |
| C_duplicated_payments | All payments for orders placed 2018-02-14 loaded twice (retry) | yes | `t_duplicate_payment_rows` (314) [fail]<br>`t_payment_vs_item_total` (540) [warn] |
| D_schema_drift | order_items.price silently changes type DOUBLE -> VARCHAR | yes | `t_raw_schema_drift` (1) [fail] |
| E_loader_stopped | Loader stops: no data after 2018-05-31 and _loaded_at is 5 days old | yes | `source_freshness.raw.customers` [error]<br>`source_freshness.raw.order_payments` [error]<br>`source_freshness.raw.order_items` [error]<br>`source_freshness.raw.orders` [error]<br>`t_data_freshness_orders` (1) [fail]<br>`t_early_hours_gap` (20) [fail]<br>`t_volume_drop_severe` (43) [fail] |
| F_silent_value_shift | price x100 (cents vs reais) for orders placed 2018-05-01..2018-05-07; counts and keys unchanged | yes | `t_payment_vs_item_total` (2143) [warn] |
| G_partial_day_gap | All orders placed before 09:00 on 2018-04-10 missing (intra-day gap, daily total only ~-37%) | yes | `t_early_hours_gap` (7) [fail]<br>`t_volume_drop_moderate` (35) [warn] |
| H_stalled_feed_with_stragglers | Feed stalls after 2018-05-31 but ~1% of orders keep trickling in (so newest-order-date still looks fresh) | yes | `t_early_hours_gap` (19) [fail]<br>`t_volume_drop_severe` (43) [fail] |

Note: on real data the baseline is already red, so "caught" for a check that was failing on the baseline
means its failing-row count INCREASED (baseline counts: severe 24, moderate 34, early-hours gap 6, payment mismatch 249).
