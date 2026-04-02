WITH source AS (
    SELECT
        payment_type
    FROM {{ ref('stg_raw_data') }}
    WHERE payment_type IS NOT NULL
),

unique_payment_types AS (
    SELECT DISTINCT
        payment_type
    FROM source
),

final AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['payment_type']) }} AS payment_type_id,
        payment_type,
        CASE payment_type
            WHEN 0 THEN 'Flex Fare trip'
            WHEN 1 THEN 'Credit card'
            WHEN 2 THEN 'Cash'
            WHEN 3 THEN 'No charge'
            WHEN 4 THEN 'Dispute'
            WHEN 5 THEN 'Unknown'
            WHEN 6 THEN 'Voided trip'
            ELSE 'Unknown'
        END AS payment_type_name
    FROM unique_payment_types
)

SELECT * FROM final