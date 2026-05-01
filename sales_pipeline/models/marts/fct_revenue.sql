{{ config(materialized='table') }}

WITH sales AS (

    SELECT * FROM {{ ref('stg_sales') }}

)

SELECT
    *
FROM sales