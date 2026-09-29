
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  SELECT sales.order_id, 
        sales.revenue
FROM LUCIEN_MIGRATION.analytics.fct_revenue as sales
WHERE sales.revenue < 0
  
  
      
    ) dbt_internal_test