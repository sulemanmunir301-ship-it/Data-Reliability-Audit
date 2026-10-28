-- Grain: one row per order item.
select
    i.order_id || '-' || cast(i.order_item_id as varchar) as order_item_key,
    i.order_id,
    i.order_item_id,
    o.customer_id,
    c.customer_state,
    o.order_status,
    o.purchased_at,
    o.purchase_date,
    i.product_id,
    i.seller_id,
    i.price,
    i.freight_value
from {{ ref('stg_order_items') }} i
join {{ ref('stg_orders') }} o using (order_id)
left join {{ ref('stg_customers') }} c using (customer_id)
