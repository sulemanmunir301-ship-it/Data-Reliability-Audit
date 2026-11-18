-- Fails if the fact table's total price differs from staging, or if either total is missing.
with fct as (
    select sum(price) as total from {{ ref('fct_order_items') }}
),
stg as (
    select sum(price) as total from {{ ref('stg_order_items') }}
)
select fct.total as fct_total, stg.total as stg_total
from fct cross join stg
where fct.total is null
   or stg.total is null
   or abs(fct.total - stg.total) > 0.01
