
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_amt
from LUCIEN_MIGRATION.analytics.fct_sales
where total_amt is null



  
  
      
    ) dbt_internal_test