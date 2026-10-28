{{ config(severity='warn') }}
-- Reconciliation: payments should equal items + freight. Some legitimate mismatches exist
-- (vouchers, installment interest), so this is a WARN with a 1.00 tolerance.
with items as (
    select order_id, sum(price + freight_value) as item_total
    from {{ ref('stg_order_items') }} group by 1
),
pay as (
    select order_id, sum(payment_value) as paid
    from {{ ref('stg_payments') }} group by 1
)
select order_id, item_total, paid
from items join pay using (order_id)
where abs(item_total - paid) > 1.00
