{{ config(materialized='table') }}

WITH source_data AS (
    SELECT
        *
    FROM {{ source('local_source', 'raw_sales') }}
)
SELECT *
FROM source_data

