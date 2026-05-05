-- models/marts/fct_revenue.sql
{{ config(materialized='view') }}

WITH sales AS (
    SELECT * FROM {{ ref('stg_sales') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
)

SELECT 
    sales.sales_id,
    sales.product_id,
    sales.sale_date AS date,
    sales.qty as quantity,
    products.price,
    (sales.qty * products.price) AS revenue
FROM sales
LEFT JOIN products ON sales.product_id = products.id