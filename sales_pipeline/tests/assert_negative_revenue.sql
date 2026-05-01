SELECT sales.sales_id, 
        sales.total_amt,
FROM {{ ref('fct_revenue') }} as sales
WHERE sales.total_amt < 0