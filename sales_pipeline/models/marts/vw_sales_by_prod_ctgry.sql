{{ config(materialized='view') }}

-- models/marts/vw_sales_by_prod_ctgry.sql
WITH sales AS (
    SELECT * FROM {{ ref('stg_sales') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
)

SELECT 
    products.category,
    SUM(sales.quantity * products.price) AS total_sales
FROM sales
LEFT JOIN products ON sales.product_id = products.product_id
GROUP BY 1