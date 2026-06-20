with staged_sales as (
    select
       *
    from {{ ref('stg_sales') }}
),
final as (
    select
        order_id,
        product_id,
        customer_id,
        quantity,
        unit_price,
        total_amt,
        dt_ordered,
        last_updated
    from staged_sales
)
select * from final