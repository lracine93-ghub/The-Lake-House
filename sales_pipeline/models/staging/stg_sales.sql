{{ config(materialized='table') }}

WITH source_sales AS (
    SELECT
        *
    FROM {{ source('external_source', 'raw_sales') }}
),
RENAMED AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['sales_id', 'product_id']) }} as order_id,
        product_id,
        cust_id as customer_id,
        qty as quantity,
        case when unit_price IS NULL then 0
            else cast(unit_price as decimal(10,2))
        end as unit_price,
        case when total_amt IS NULL then 0
            else cast(total_amt as decimal(10,2))
        end as total_amt,
        cast(sale_date as timestamp) as dt_ordered,
        updated_at as last_updated,
        {{ dbt.current_timestamp() }} as dbt_updated_at
    FROM source_sales
)
SELECT *
FROM RENAMED

