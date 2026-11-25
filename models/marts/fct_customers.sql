-- Grain: one row per person (customer_unique_id).
with per_person as (
    select
        customer_unique_id,
        min(purchase_date) as first_order_date,
        count(*) filter (where order_status = 'delivered') as delivered_orders
    from {{ ref('fct_orders') }}
    group by customer_unique_id
)
select
    customer_unique_id,
    first_order_date,
    delivered_orders,
    case when delivered_orders >= 2 then 1 else 0 end as is_repeat_customer,
    case when delivered_orders >= 1 then 1 else 0 end as has_delivered_order
from per_person
