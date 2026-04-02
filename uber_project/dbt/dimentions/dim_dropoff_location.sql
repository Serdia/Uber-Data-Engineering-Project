WITH source AS (
    SELECT DISTINCT
        dropoff_latitude,
        dropoff_longitude
    FROM {{ ref('stg_raw_data') }}
    WHERE dropoff_latitude IS NOT NULL
      AND dropoff_longitude IS NOT NULL
),

final AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['dropoff_latitude', 'dropoff_longitude']) }} AS dropoff_location_id,
        dropoff_latitude,
        dropoff_longitude
    FROM source
)

SELECT * FROM final