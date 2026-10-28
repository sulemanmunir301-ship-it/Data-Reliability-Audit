-- Data-level freshness (what the business sees), not loader-level (see sources.yml).
-- Fails when newest order is more than 2 days older than as_of_date.
select max(purchase_date) as newest_order,
       date_diff('day', max(purchase_date), date '{{ var("as_of_date") }}') as lag_days
from {{ ref('stg_orders') }}
having date_diff('day', max(purchase_date), date '{{ var("as_of_date") }}') > 2
