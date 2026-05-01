{{ config(materialized='view') }}

WITH source_data AS (
    SELECT
        *
    FROM read_csv_auto('data/raw/sales_raw.csv')
)
SELECT *
FROM source_data

