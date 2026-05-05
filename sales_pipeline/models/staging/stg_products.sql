{{ config(materialized='table') }}

WITH source_data AS (
    SELECT
        *
    FROM {{ source('local_source', 'raw_products') }}
)
SELECT *
FROM source_data

