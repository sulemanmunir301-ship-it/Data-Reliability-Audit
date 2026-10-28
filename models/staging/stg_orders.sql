select
    order_id,
    customer_id,
    order_status,
    cast(order_purchase_timestamp as timestamp) as purchased_at,
    cast(order_purchase_timestamp as date)      as purchase_date
from {{ source('raw', 'orders') }}
