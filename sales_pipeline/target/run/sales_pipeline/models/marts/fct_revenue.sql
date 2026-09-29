
  create or replace   view LUCIEN_MIGRATION.analytics.fct_revenue
  
  
  
  
  as (
    -- models/marts/fct_revenue.sql


WITH sales AS (
    SELECT * FROM LUCIEN_MIGRATION.staging.stg_sales
),

products AS (
    SELECT * FROM LUCIEN_MIGRATION.staging.stg_products
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
  );

