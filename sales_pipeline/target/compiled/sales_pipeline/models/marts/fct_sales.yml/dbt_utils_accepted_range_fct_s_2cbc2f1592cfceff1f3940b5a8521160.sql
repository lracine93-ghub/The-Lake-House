

with meet_condition as(
  select *
  from LUCIEN_MIGRATION.analytics.fct_sales
),

validation_errors as (
  select *
  from meet_condition
  where
    -- never true, defaults to an empty result set. Exists to ensure any combo of the `or` clauses below succeeds
    1 = 2
    -- records with a value >= min_value are permitted. The `not` flips this to find records that don't meet the rule.
    or not unit_price >= 0
    -- records with a value <= max_value are permitted. The `not` flips this to find records that don't meet the rule.
    or not unit_price <= 99999999999999
)

select *
from validation_errors

