{% snapshot scd_products %}

{{
    config(
        target_schema='snapshots',
        unique_key='product_id',
        strategy='check',
        check_cols=[
            'product_name',
            'product_description',
            'price',
            'category'
        ],
        hard_deletes='invalidate'
    )
}}

SELECT * FROM {{ ref('stg_products') }}

{% endsnapshot %}
