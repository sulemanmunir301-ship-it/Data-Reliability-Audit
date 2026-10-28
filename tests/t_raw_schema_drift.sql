-- Compares raw column types to the expected contract. Staging casts can silently
-- absorb a type change, so the build passes while the source is no longer what you think.
with expected(table_name, column_name, data_type) as (
    values
    ('order_items', 'price', 'DOUBLE'),
    ('order_items', 'freight_value', 'DOUBLE'),
    ('order_payments', 'payment_value', 'DOUBLE'),
    ('orders', 'order_purchase_timestamp', 'TIMESTAMP')
),
actual as (
    select table_name, column_name, data_type
    from information_schema.columns where table_schema = 'raw'
)
select e.table_name, e.column_name, e.data_type as expected_type, a.data_type as actual_type
from expected e
left join actual a using (table_name, column_name)
where a.data_type is distinct from e.data_type
