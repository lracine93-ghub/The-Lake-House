
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select quantity
from LUCIEN_MIGRATION.analytics.fct_sales
where quantity is null



  
  
      
    ) dbt_internal_test