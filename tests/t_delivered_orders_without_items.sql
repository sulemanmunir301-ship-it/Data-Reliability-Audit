-- A relationships test (items -> orders) cannot see orders that LOST their items.
-- This is the reverse check.
select o.order_id, o.purchase_date
from {{ ref('stg_orders') }} o
left join (select distinct order_id from {{ ref('stg_order_items') }}) i using (order_id)
where o.order_status = 'delivered' and i.order_id is null
