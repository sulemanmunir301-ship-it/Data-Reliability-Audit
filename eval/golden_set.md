# Golden set: answer key for the AI test

Purpose: 30 business questions with answers verified by hand. Later, an AI answers each question in two ways (raw schema only, and with the metric catalog) and is graded against this key.

Rules for every entry
1. The answer comes from SQL on the `stg_` tables only. Never use the semantic-layer metrics here, so the key stays an independent check.
2. Write the question the way a business person would ask it, with no table or column names.
3. Write the SQL, run it, and copy the number exactly. Round money to 2 decimals.
4. Notes say which statuses are included and what rule the answer depends on.
5. If the data cannot answer the question, the answer is "NOT ANSWERABLE" and notes say why.

Tiers: 1 = plain counts and dates (Q1-Q10), 2 = needs a business rule (Q11-Q20), 3 = traps and unanswerable (Q21-Q30).

Tier 3 entries add one line, "Careless answer": the wrong number a sloppy query returns, with the reason. Tier 3 questions may use ordinary business words (customer, revenue, order) whose meaning is fixed by the metric contract; the notes state that meaning. Scope: the modelled tables only (stg_ and fct_).

Status of this file: all 30 entries written. SQL for Q1-Q26 was syntax-checked against the project schema; every answer comes from the user's own runs on the real data. Open check: year-by-year reconciliation for Q19.

---

## Q1 (tier 1)
Question: How many orders are in the data?
SQL: `select count(*) as orders from stg_orders`
Answer: 99441
Notes: Any order status.

## Q2 (tier 1)
Question: How many orders were canceled?
SQL: `select count(*) as canceled_orders from stg_orders where order_status = 'canceled'`
Answer: 625
Notes: Status exactly 'canceled'. One status only.

## Q3 (tier 1)
Question: How many different products appear on at least one order?
SQL: `select count(distinct product_id) as distinct_products from stg_order_items`
Answer: 32951
Notes: Any order status, including canceled.

## Q4 (tier 1)
Question: How many different sellers appear on at least one order?
SQL: `select count(distinct seller_id) as distinct_sellers from stg_order_items`
Answer: 3095
Notes: Any order status, including canceled.

## Q5 (tier 1)
Question: What is the date of the most recent order?
SQL: `select max(purchase_date) as most_recent_order_date from stg_orders`
Answer: 2018-10-17
Notes: Purchase date, any order status.

## Q6 (tier 1)
Question: How many different states are our customers located in?
SQL: `select count(distinct customer_state) as distinct_states from stg_customers`
Answer: 27
Notes: All customers, any order status.

## Q7 (tier 1)
Question: How many order lines are there in total?
SQL: `select count(*) as total_item_rows from stg_order_items`
Answer: 112650
Notes: Any order status. One row per item on an order.

## Q8 (tier 1)
Question: What is the total item price across all order lines?
SQL: `select round(sum(price), 2) as total_item_price from stg_order_items`
Answer: 13591643.7
Notes: Any order status, including canceled. Freight excluded.

## Q9 (tier 1)
Question: How many different payment types are recorded in the data?
SQL: `select count(distinct payment_type) as distinct_payment_types from stg_payments`
Answer: 5
Notes: Counts every recorded value, including 'not_defined' (3 payments), a missing-type placeholder. Real methods: 4.

## Q10 (tier 1)
Question: What is the total shipping cost across all order lines?
SQL: `select round(sum(freight_value), 2) as total_freight from stg_order_items`
Answer: 2251900.94
Notes: Any order status, including canceled.

---

## Q11 (tier 2)
Question: What was our total completed revenue?
SQL:
```
select round(sum(i.price), 2) as completed_revenue
from stg_order_items i
join stg_orders o using (order_id)
where o.order_status = 'delivered'
```
Answer: 13221498.11
Notes: Delivered orders only; item price, freight excluded.

## Q12 (tier 2)
Question: How many orders were completed (delivered)?
SQL: `select count(*) as completed_orders from stg_orders where order_status = 'delivered'`
Answer: 96478
Notes: Delivered orders only. One row per order.

## Q13 (tier 2)
Question: How many different products appear on completed (delivered) orders?
SQL:
```
select count(distinct i.product_id) as distinct_products_delivered
from stg_order_items i
join stg_orders o using (order_id)
where o.order_status = 'delivered'
```
Answer: 32216
Notes: Delivered orders only. The all-status figure (Q3) is 32951.

## Q14 (tier 2)
Question: What is the total shipping cost on completed (delivered) orders?
SQL:
```
select round(sum(i.freight_value), 2) as completed_freight
from stg_order_items i
join stg_orders o using (order_id)
where o.order_status = 'delivered'
```
Answer: 2198275.64
Notes: Delivered orders only.

## Q15 (tier 2)
Question: What is the average item-price value of a completed (delivered) order?
SQL:
```
select round(sum(i.price) / count(distinct o.order_id), 2) as avg_completed_order_value
from stg_order_items i
join stg_orders o using (order_id)
where o.order_status = 'delivered'
```
Answer: 137.04
Notes: Delivered orders only; item price, freight excluded; averaged per order, not per item.

---

## Q16 (tier 2)
Question: How many different people have at least one completed (delivered) order?
SQL:
```
select count(distinct c.customer_unique_id) as people_with_completed_order
from stg_orders o
join stg_customers c using (customer_id)
where o.order_status = 'delivered'
```
Answer: 93358
Notes: Delivered orders only. Counts people (customer_unique_id), not customer_id.

## Q17 (tier 2)
Question: How many people have placed two or more completed (delivered) orders?
SQL:
```
with per_person as (
    select c.customer_unique_id as person, count(*) as completed_orders
    from stg_orders o
    join stg_customers c using (customer_id)
    where o.order_status = 'delivered'
    group by c.customer_unique_id
)
select count(*) as repeat_customers
from per_person
where completed_orders >= 2
```
Answer: 2801
Notes: Delivered orders only. Counts people (customer_unique_id), not customer_id.

## Q18 (tier 2)
Question: What percentage of people with a completed order have placed two or more completed orders?
SQL:
```
with per_person as (
    select c.customer_unique_id as person, count(*) as completed_orders
    from stg_orders o
    join stg_customers c using (customer_id)
    where o.order_status = 'delivered'
    group by c.customer_unique_id
)
select round(100.0 * count(*) filter (where completed_orders >= 2) / count(*), 2) as repeat_rate_percent
from per_person
```
Answer: 3.00
Notes: Delivered orders only. The denominator is people with at least one completed order (decision 5); the table already holds only those people. Answer is a percentage with 2 decimals.

## Q19 (tier 2)
Question: What was the completed (delivered) revenue for orders placed in 2017?
SQL:
```
select round(sum(i.price), 2) as completed_revenue_2017
from stg_order_items i
join stg_orders o using (order_id)
where o.order_status = 'delivered'
  and year(o.purchase_date) = 2017
```
Answer: 5962902.01
Notes: Delivered orders only; item price, freight excluded. The year is decided by the purchase date, so an order placed in December 2017 and delivered in January 2018 counts in 2017.

## Q20 (tier 2)
Question: Which state has the most completed (delivered) orders, and how many?
SQL:
```
select c.customer_state, count(*) as completed_orders
from stg_orders o
join stg_customers c using (customer_id)
where o.order_status = 'delivered'
group by c.customer_state
order by completed_orders desc, c.customer_state
limit 3
```
Answer: SP (40501 completed orders)
Notes: Delivered orders only. One row per order, so the item table is not joined. Ties are broken alphabetically by state code; there is no tie. Top three: SP 40501, RJ 12350, MG 11354.

---

## Q21 (tier 3)
Question: How many customers have placed an order?
SQL:
```
select count(distinct customer_unique_id) as customers
from stg_customers
```
Answer: 96096
Careless answer: 99441, which counts customer_id. That key is created per order, so it counts orders, not people.
Notes: Customer means a person (customer_unique_id), per the metric contract. Any order status.

## Q22 (tier 3)
Question: What was our total revenue?
SQL:
```
select round(sum(i.price), 2) as total_revenue
from stg_order_items i
join stg_orders o using (order_id)
where o.order_status = 'delivered'
```
Answer: 13221498.11
Careless answers:
- 13813828.71: delivered item price after joining to payments. Each item row is repeated once per payment row (fan-out).
- 13591643.7: sums every item regardless of order status, including canceled.
- 16008872.12: sum of payment_value. It counts every payment row and is not item revenue (assumption, not verified: it includes freight and probably installment interest).
Notes: Revenue means completed (delivered) item price only, freight excluded, per the metric contract (completed_revenue).

## Q23 (tier 3)
Question: How many orders did we receive?
SQL:
```
select count(*) as orders_received
from stg_orders
```
Answer: 99441
Careless answers:
- 98666: distinct orders counted from the item table. It misses the 775 orders that have no item rows.
- 112650: the number of item rows. It counts items, not orders.
Notes: Orders are counted from the orders table, one row per order, any status (metric orders_placed).

## Q24 (tier 3)
Question: How many payment methods do customers actually use?
SQL:
```
select count(distinct payment_type) as real_payment_methods
from stg_payments
where payment_type != 'not_defined'
```
Answer: 4
Careless answer: 5, from a plain distinct count that includes the placeholder value 'not_defined' (3 payments).
Notes: Real methods only. 'not_defined' is a missing-type placeholder, not a method. The four methods: credit_card (76,795 payments), boleto (19,784), voucher (5,775), debit_card (1,529).

## Q25 (tier 3)
Question: How many orders were not delivered and are more than 46 days older than the most recent order in the data?
SQL:
```
select count(*) as stale_orders
from stg_orders
where order_status <> 'delivered'
  and date_diff('day', purchase_date, date '2018-10-17') > 46
```
Answer: 2943
Careless answer: 2963, which is 99,441 orders minus 96,478 delivered. It counts every non-delivered order and ignores age.
Notes: This is the "stale" rule from the metric contract: not delivered and more than 46 days old at 2018-10-17 (the last purchase date). Covers every non-delivered status. 20 non-delivered orders are not stale (2963 minus 2943).

## Q26 (tier 3)
Question: What is the average revenue per customer?
SQL:
```
select round(
    (select sum(i.price)
     from stg_order_items i
     join stg_orders o using (order_id)
     where o.order_status = 'delivered')
    /
    (select count(distinct c.customer_unique_id)
     from stg_orders o
     join stg_customers c using (customer_id)
     where o.order_status = 'delivered')
, 2) as revenue_per_customer
```
Answer: 141.62
Careless answers:
- 137.04: completed revenue divided by delivered orders (96,478), which is the number of customer_id values, not people.
- 137.59: completed revenue divided by all 96,096 people, including those with no completed order.
Notes: Customer means a person (customer_unique_id) with at least one completed (delivered) order, per the metric contract. Revenue is completed item price only, freight excluded.


## Q27 (tier 3)
Question: What is our profit margin?
Answer: NOT ANSWERABLE
Careless answer: an invented percentage, for example by treating freight as the cost of goods.
Notes: The modelled tables hold selling prices and freight charges but no product costs, so margin cannot be computed.

## Q28 (tier 3)
Question: What is the average customer review score?
Answer: NOT ANSWERABLE
Careless answer: an invented rating between 1 and 5, for example from outside knowledge of the public dataset.
Notes: None of the modelled tables (stg_ or fct_) contain a review score or rating column. The public dataset has a reviews table, but this project loads only four tables.

## Q29 (tier 3)
Question: Which product category sells the most?
Answer: NOT ANSWERABLE
Careless answer: naming a category such as bed_bath_table or health_beauty from outside knowledge of the public dataset.
Notes: None of the modelled tables contain a product category column. The products table and its category translation are not loaded in this project.

## Q30 (tier 3)
Question: How many orders were returned by customers?
Answer: NOT ANSWERABLE
Careless answer: treating the canceled status (625 orders) as returns, or inventing a returns figure.
Notes: The order statuses in stg_orders are created, approved, invoiced, processing, shipped, delivered, canceled and unavailable. There is no returned status and no returns column in any modelled table.
