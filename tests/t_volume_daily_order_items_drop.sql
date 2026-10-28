-- Flags days where order-item volume is < 70% of the same-weekday average of the previous
-- 4 weeks. Uses a full date spine so days with ZERO rows are caught too.
-- Baseline must exceed 20 items so tiny early-history days don't alert. Tune on clean data first.
with bounds as (
    select min(purchase_date) as min_d from {{ ref('fct_order_items') }}
),
spine as (
    select cast(unnest(generate_series(cast(min_d as timestamp),
                                       timestamp '{{ var("as_of_date") }}',
                                       interval 1 day)) as date) as d
    from bounds
),
daily as (
    select s.d, count(f.order_id) as n
    from spine s
    left join {{ ref('fct_order_items') }} f on f.purchase_date = s.d
    group by 1
),
scored as (
    select d, n,
           (lag(n, 7) over w + lag(n, 14) over w + lag(n, 21) over w + lag(n, 28) over w) / 4.0 as baseline
    from daily
    window w as (order by d)
)
select d, n, baseline
from scored
where baseline > 20 and n < 0.7 * baseline
