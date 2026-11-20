-- Grain: one row per order.
select
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    o.order_status,
    o.purchased_at,
    o.purchase_date
from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c using (customer_id)
