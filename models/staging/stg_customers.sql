select
    customer_id,
    customer_unique_id,
    customer_state
from {{ source('raw', 'customers') }}
