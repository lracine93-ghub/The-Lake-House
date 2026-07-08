-- models/marts/fct_revenue.sql
{{ config(materialized='view') }}

WITH sales AS (
    SELECT * FROM {{ ref('stg_sales') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
)

SELECT 
    sales.order_id,
    sales.product_id,
    sales.dt_ordered AS date,
    sales.quantity,
    products.price,
    (sales.quantity * products.price) AS revenue
FROM sales
LEFT JOIN products ON sales.product_id = products.product_id