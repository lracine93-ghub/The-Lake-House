{{ config(materialized='table') }}

WITH source_data AS (
    SELECT
        *
    FROM {{ source('external_source', 'raw_products') }}
), 
renamed as (
    SELECT
        id as product_id,
        upper(title) as product_name,
        description as product_description,
        price ,
        category ,
        updated_at as last_updated,
        {{ dbt.current_timestamp() }} as dbt_updated_at
    FROM source_data
)

select * from renamed


