select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    cast(price as double)         as price,
    cast(freight_value as double) as freight_value
from {{ source('raw', 'order_items') }}
