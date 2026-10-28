-- Retry/double-load symptom: same (order_id, payment_sequential) more than once.
select order_id, payment_sequential, count(*) as copies
from {{ ref('stg_payments') }}
group by 1, 2
having count(*) > 1
