SELECT sales.order_id, 
        sales.revenue
FROM {{ ref('fct_revenue') }} as sales
WHERE sales.revenue < 0