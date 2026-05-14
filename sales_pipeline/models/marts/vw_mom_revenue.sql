{{ config(materialized='view') }}

-- models/marts/vw_mom_revenue.sql
WITH revenue_data AS (
    SELECT * FROM {{ ref('fct_revenue') }}
)

SELECT 
    DATE_TRUNC('month', date::date) AS order_month,
    SUM(revenue_net_tax) AS total_revenue
FROM revenue_data
GROUP BY 1
ORDER BY 1