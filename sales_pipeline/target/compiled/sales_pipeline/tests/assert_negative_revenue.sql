SELECT sales.order_id, 
        sales.revenue
FROM LUCIEN_MIGRATION.analytics.fct_revenue as sales
WHERE sales.revenue < 0