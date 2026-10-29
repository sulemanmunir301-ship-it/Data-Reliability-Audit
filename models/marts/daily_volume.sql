-- One row per calendar day (full spine, so empty days exist) with a same-weekday baseline.
-- Shared by the volume, freshness and early-hours tests so the logic lives in one place.
with bounds as (
    select min(purchase_date) as min_d from {{ ref('fct_order_items') }}
),
spine as (
    select cast(unnest(generate_series(cast(min_d as timestamp),
                                       timestamp '{{ var("as_of_date") }}',
                                       interval 1 day)) as date) as d
    from bounds
),
items as (
    select purchase_date as d, count(*) as n from {{ ref('fct_order_items') }} group by 1
),
early as (
    select purchase_date as d, count(*) filter (where hour(purchased_at) < 9) as early_orders
    from {{ ref('stg_orders') }} group by 1
),
daily as (
    select s.d, coalesce(i.n, 0) as n, coalesce(e.early_orders, 0) as early_orders
    from spine s
    left join items i on i.d = s.d
    left join early e on e.d = s.d
),
scored as (
    select d, n, early_orders,
           (lag(n, 7) over w + lag(n, 14) over w + lag(n, 21) over w + lag(n, 28) over w) / 4.0 as baseline,
           avg(early_orders) over (order by d rows between 28 preceding and 1 preceding) as early_baseline,
           -- slow baseline: median of the previous 180 days. Unlike the same-weekday baseline above, a
           -- multi-week outage barely moves it, so a long outage cannot become the "new normal".
           median(n) over (order by d rows between 180 preceding and 1 preceding) as long_baseline
    from daily
    window w as (order by d)
)
select d, n, baseline, n / nullif(baseline, 0) as ratio, early_orders, early_baseline, long_baseline
from scored
