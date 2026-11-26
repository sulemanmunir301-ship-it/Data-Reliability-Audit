# Olist metric contract

Every business number in this project is defined once, in `models/semantic/semantic_models.yml`, and queried with MetricFlow (`mf query --metrics <name>`). This page says what each metric means, which orders count, and which traps it avoids.

Data: "Brazilian E-Commerce Public Dataset by Olist" (Kaggle), listed under CC BY-NC-SA 4.0. 99,441 orders; the last purchase date is 2018-10-17. Four of the nine tables are modelled.

## Which orders count

| Status | Orders | Counts as revenue | Counts as an order placed | Counts as completed |
|---|---|---|---|---|
| delivered | 96,478 | yes | yes | yes |
| shipped | 1,107 | no | yes | no |
| canceled | 625 | no | yes | no |
| unavailable | 609 | no | yes | no |
| invoiced | 314 | no | yes | no |
| processing | 301 | no | yes | no |
| approved | 2 | no | yes | no |
| created | 5 | no | yes | no |

Why only `delivered` counts as revenue: canceled orders still carry 95,235.27 of item price, and all non-delivered statuses together carry 370,145.59 (2.80% of delivered revenue).

Stale orders: a non-delivered order is flagged stale when it is more than 46 days old at 2018-10-17, which is the same as "purchased on or before 2018-08-31" and matches the repo's `AS_OF_DATE`. 46 days is the 99th percentile of delivery time among delivered orders (median 10 days, 95th percentile 29). At least 1,059 of 1,107 shipped, 291 of 314 invoiced, all 301 processing, all 5 created and both approved orders were purchased before 2018-08-01, so they are far past the line. Assumption, not verified: these statuses were never updated or the orders were lost.

## Metrics

| Metric | Definition | Built on | Verified result |
|---|---|---|---|
| `completed_revenue` | Sum of item price (freight excluded) on delivered orders | `fct_order_items`, one row per item | 13,221,498.11 |
| `freight_total` | Sum of freight charged on delivered orders | `fct_order_items` | 2,198,275.64 |
| `orders_placed` | Distinct orders of any status | `fct_orders`, one row per order | 99,441 |
| `completed_orders` | Distinct delivered orders | `fct_orders` | 96,478 |
| `repeat_purchase_rate` | People with 2 or more delivered orders, divided by people with at least 1 delivered order | `fct_customers`, one row per person | 2,801 / 93,358 = 3.00% |

Supporting metrics: `repeat_customers` (2,801) and `customers_with_delivered_order` (93,358).

## The three traps this contract avoids

1. **Payment fan-out.** 2,961 of 99,440 orders with payments (3.0%) have two or more payment rows, up to 29. Joining payments to item rows counts each item once per payment row. On delivered orders, 13,221,498.11 becomes 13,813,828.71 after the join. The pure fan-out is 592,465.57 (4.48%); the net difference is 592,330.60 because the same join also drops one delivered order with no payment row (134.97). The inflation comes from repetition, not from larger orders: multi-payment orders average 140.78 against 136.93 for single-payment orders, but their item price is counted about 2.46 times.
2. **`customer_id` is not a person.** It is created per order. There are 99,441 `customer_id` values and 96,096 people (`customer_unique_id`). A repeat rate built on `customer_id` is 0%. The person-level rate is 3.00% under this contract's definition; other definitions give 3.12% (any status, all people) and 2.92% (delivered only, all people).
3. **The item table lacks orders.** `fct_order_items` holds 98,666 of the 99,441 orders; 775 orders (603 unavailable, 164 canceled, 5 created, 2 invoiced, 1 shipped) have no item rows. Order counts therefore come from `fct_orders`, not from the item table.

## Decisions

- Revenue comes from item price, not payments. Payments will not reconcile to item revenue: 249 orders disagree (232 are overpayments, median +6.98 BRL). Assumption, not verified: payments include freight and probably installment interest.
- Freight is excluded from revenue and reported separately as `freight_total`.
- The one delivered order with no payment row (3 item rows, 134.97) stays in revenue and is logged as a data-quality exception.

## Known data-quality exceptions

- 1 delivered order has no payment row.
- 8 delivered orders have no delivery date.
- Stale non-delivered orders, as defined above.
- 3 payments are typed `not_defined`.

## Where each rule is enforced

- `t_fct_reconciles_to_staging`: total item price in `fct_order_items` must equal staging.
- `not_null` on `customer_unique_id` in `fct_order_items`; `unique` and `not_null` on the key of `fct_order_items`, `fct_orders` and `fct_customers`.
- `mf validate-configs` checks every metric against the warehouse.

## Not done yet

- The comparison of AI answers with and without these definitions.
