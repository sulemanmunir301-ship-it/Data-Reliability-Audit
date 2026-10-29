{{ config(severity='warn') }}
-- Real Olist has exactly 1 order with no payment row. (Synthetic data: canceled/unavailable orders
-- have no payments by construction, so this warns there.)
select o.order_id, o.order_status, o.purchase_date
from {{ ref('stg_orders') }} o
left join (select distinct order_id from {{ ref('stg_payments') }}) p using (order_id)
where p.order_id is null
