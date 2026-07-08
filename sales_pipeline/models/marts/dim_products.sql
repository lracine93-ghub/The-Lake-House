
with staged_products as (
    select * from {{ ref('stg_products') }}
),
final as (
    select
        product_id,
        product_name,
        product_description,
        price,  
        category,
        case 
            when price < 20 then 'Low'
            when price >= 20 and price < 100 then 'Medium'
            else 'High'
        end as price_level,
        last_updated
    from staged_products
)
select * from final