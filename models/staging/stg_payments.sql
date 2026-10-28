select
    order_id,
    payment_sequential,
    payment_type,
    cast(payment_value as double) as payment_value
from {{ source('raw', 'order_payments') }}
