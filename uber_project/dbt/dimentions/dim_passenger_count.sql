WITH source AS (
    SELECT
        passenger_count
    FROM {{ ref('stg_raw_data') }}
    WHERE passenger_count IS NOT NULL
),

unique_passengers AS (
    SELECT DISTINCT
        passenger_count
    FROM source
),

final AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['passenger_count']) }} AS passenger_count_id,
        passenger_count
    FROM unique_passengers
)

SELECT * FROM final