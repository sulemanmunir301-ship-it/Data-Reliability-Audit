## raw.customers  (63,912 rows)
| column | type | nulls | distinct |
|---|---|---|---|
| customer_id | VARCHAR | 0 | 63,912 |
| customer_unique_id | VARCHAR | 0 | 43,883 |
| customer_zip_code_prefix | BIGINT | 0 | 47,064 |
| customer_city | VARCHAR | 0 | 1 |
| customer_state | VARCHAR | 0 | 5 |
| _loaded_at | TIMESTAMP | 0 | 1 |

## raw.order_items  (78,196 rows)
| column | type | nulls | distinct |
|---|---|---|---|
| order_id | VARCHAR | 0 | 62,658 |
| order_item_id | BIGINT | 0 | 3 |
| product_id | VARCHAR | 0 | 27,806 |
| seller_id | VARCHAR | 0 | 2,999 |
| shipping_limit_date | TIMESTAMP | 0 | 62,607 |
| price | DOUBLE | 0 | 24,240 |
| freight_value | DOUBLE | 0 | 3,201 |
| _loaded_at | TIMESTAMP | 0 | 1 |

## raw.order_payments  (62,658 rows)
| column | type | nulls | distinct |
|---|---|---|---|
| order_id | VARCHAR | 0 | 62,658 |
| payment_sequential | BIGINT | 0 | 1 |
| payment_type | VARCHAR | 0 | 4 |
| payment_installments | BIGINT | 0 | 8 |
| payment_value | DOUBLE | 0 | 27,378 |
| _loaded_at | TIMESTAMP | 0 | 1 |

## raw.orders  (63,912 rows)
| column | type | nulls | distinct |
|---|---|---|---|
| order_id | VARCHAR | 0 | 63,912 |
| customer_id | VARCHAR | 0 | 63,912 |
| order_status | VARCHAR | 0 | 4 |
| order_purchase_timestamp | TIMESTAMP | 0 | 63,860 |
| order_approved_at | TIMESTAMP | 0 | 63,860 |
| order_delivered_carrier_date | TIMESTAMP | 0 | 63,860 |
| order_delivered_customer_date | TIMESTAMP | 0 | 63,860 |
| order_estimated_delivery_date | TIMESTAMP | 0 | 63,860 |
| _loaded_at | TIMESTAMP | 0 | 1 |

## Orders date range
oldest order date: 2017-01-01
newest order date: 2018-06-30  <- set as_of_date near this

## order_status counts
- delivered: 61,704
- shipped: 954
- unavailable: 643
- canceled: 611

duplicate order_id rows in orders: 0

## Months with fewest orders (sparse history makes the volume check noisy)
- 2017-02: 3,215
- 2018-02: 3,314
- 2017-04: 3,420
- 2018-06: 3,469
- 2017-09: 3,526

delivered orders with no items: 0
items whose order_id is missing from orders: 0

duplicated (order_id, payment_sequential) pairs: 0
payment types: credit_card=46,429, boleto=11,790, voucher=3,149, debit_card=1,290
