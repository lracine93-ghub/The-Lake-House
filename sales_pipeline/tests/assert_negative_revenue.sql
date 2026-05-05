SELECT sales.sales_id, 
        sales.revenue
FROM {{ ref('fct_revenue') }} as sales
WHERE sales.revenue < 0