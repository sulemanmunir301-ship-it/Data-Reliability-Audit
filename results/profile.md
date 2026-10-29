## raw.customers  (99,441 rows)
| column | type | nulls | distinct |
|---|---|---|---|
| customer_id | VARCHAR | 0 | 99,441 |
| customer_unique_id | VARCHAR | 0 | 96,096 |
| customer_zip_code_prefix | VARCHAR | 0 | 14,994 |
| customer_city | VARCHAR | 0 | 4,119 |
| customer_state | VARCHAR | 0 | 27 |
| _loaded_at | TIMESTAMP | 0 | 1 |

## raw.order_items  (112,650 rows)
| column | type | nulls | distinct |
|---|---|---|---|
| order_id | VARCHAR | 0 | 98,666 |
| order_item_id | BIGINT | 0 | 21 |
| product_id | VARCHAR | 0 | 32,951 |
| seller_id | VARCHAR | 0 | 3,095 |
| shipping_limit_date | TIMESTAMP | 0 | 93,318 |
| price | DOUBLE | 0 | 5,968 |
| freight_value | DOUBLE | 0 | 6,999 |
| _loaded_at | TIMESTAMP | 0 | 1 |

## raw.order_payments  (103,886 rows)
| column | type | nulls | distinct |
|---|---|---|---|
| order_id | VARCHAR | 0 | 99,440 |
| payment_sequential | BIGINT | 0 | 29 |
| payment_type | VARCHAR | 0 | 5 |
| payment_installments | BIGINT | 0 | 24 |
| payment_value | DOUBLE | 0 | 29,077 |
| _loaded_at | TIMESTAMP | 0 | 1 |

## raw.orders  (99,441 rows)
| column | type | nulls | distinct |
|---|---|---|---|
| order_id | VARCHAR | 0 | 99,441 |
| customer_id | VARCHAR | 0 | 99,441 |
| order_status | VARCHAR | 0 | 8 |
| order_purchase_timestamp | TIMESTAMP | 0 | 98,875 |
| order_approved_at | TIMESTAMP | 160 | 90,733 |
| order_delivered_carrier_date | TIMESTAMP | 1,783 | 81,018 |
| order_delivered_customer_date | TIMESTAMP | 2,965 | 95,664 |
| order_estimated_delivery_date | TIMESTAMP | 0 | 459 |
| _loaded_at | TIMESTAMP | 0 | 1 |

## Orders date range
oldest order date: 2016-09-04
newest order date: 2018-10-17  <- set as_of_date near this

## order_status counts
- delivered: 96,478
- shipped: 1,107
- canceled: 625
- unavailable: 609
- invoiced: 314
- processing: 301
- created: 5
- approved: 2

duplicate order_id rows in orders: 0

## Months with fewest orders (sparse history makes the volume check noisy)
- 2016-12: 1
- 2016-09: 4
- 2018-10: 4
- 2018-09: 16
- 2016-10: 324

delivered orders with no items: 0
items whose order_id is missing from orders: 0

duplicated (order_id, payment_sequential) pairs: 0
payment types: credit_card=76,795, boleto=19,784, voucher=5,775, debit_card=1,529, not_defined=3
