-- "Newest order date" freshness is fooled by stragglers (real Olist: a few orders in Sep-Oct 2018
-- after volume collapsed in late Aug). This asks: when was the last day with at least 50% of the
-- SLOW (180-day median) baseline? Fails if that is more than 2 days before as_of_date.
-- The same-weekday baseline is NOT used here: after ~4 weeks of outage it adapts and goes quiet.
select max(d) as last_healthy_day,
       date_diff('day', max(d), date '{{ var("as_of_date") }}') as lag_days
from {{ ref('daily_volume') }}
where not (long_baseline > 20 and n < 0.5 * long_baseline)
having date_diff('day', max(d), date '{{ var("as_of_date") }}') > 2
