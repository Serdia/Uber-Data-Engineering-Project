WITH source AS (
    SELECT
        ratecode_id
    FROM {{ ref('stg_raw_data') }}
    WHERE ratecode_id IS NOT NULL
),

unique_rate_codes AS (
    SELECT DISTINCT
        ratecode_id
    FROM source
),

final AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['ratecode_id']) }} AS rate_code_id,
        ratecode_id,
        CASE ratecode_id
            WHEN 1 THEN 'Standard rate'
            WHEN 2 THEN 'JFK'
            WHEN 3 THEN 'Newark'
            WHEN 4 THEN 'Nassau or Westchester'
            WHEN 5 THEN 'Negotiated fare'
            WHEN 6 THEN 'Group ride'
            ELSE 'Unknown'
        END AS rate_code_name
    FROM unique_rate_codes
)

SELECT * FROM final