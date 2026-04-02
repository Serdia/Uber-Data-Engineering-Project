WITH source AS (
    SELECT DISTINCT
        pickup_latitude,
        pickup_longitude
    FROM {{ ref('stg_raw_data') }}
    WHERE pickup_latitude IS NOT NULL
      AND pickup_longitude IS NOT NULL
),

final AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['pickup_latitude', 'pickup_longitude']) }} AS pickup_location_id,
        pickup_latitude,
        pickup_longitude
    FROM source
)

SELECT * FROM final