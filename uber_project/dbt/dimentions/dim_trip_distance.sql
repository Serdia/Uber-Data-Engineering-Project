WITH source AS (
    SELECT
        trip_distance
    FROM {{ ref('stg_raw_data') }}
    WHERE trip_distance IS NOT NULL
),
unique_distances AS (
    SELECT DISTINCT
        trip_distance
    FROM source
),
final AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['trip_distance']) }} AS trip_distance_id,
        trip_distance
    FROM unique_distances
)

SELECT * FROM final