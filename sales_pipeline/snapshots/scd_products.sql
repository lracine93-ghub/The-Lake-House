{% snapshot scd_products %}

{{
    config(
        target_schema='main',
        unique_key='id', 
        strategy='check',
        check_cols=['title', 'price'],
        invalidate_harddeletes=True
    )
}}

SELECT * FROM {{ ref('stg_products') }}

{% endsnapshot %}