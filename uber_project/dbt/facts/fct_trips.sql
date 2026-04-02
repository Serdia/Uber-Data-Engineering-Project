{{ config(
    materialized='incremental',
    unique_key='trip_id'
) }}

WITH trips AS (
    SELECT *
    FROM {{ ref('stg_raw_data') }}
    -- only processes NEW records on each run
    {% if is_incremental() %}  -- protects the first run
    WHERE pickup_datetime > (SELECT MAX(pickup_datetime) FROM {{ this }})  -- {{ this }} is a dbt special variable that refers to the model itself — the table that already exists (fct_trips) in the database.
    {% endif %}
),

dim_passenger_count AS (
    SELECT *
    FROM {{ ref('dim_passenger_count') }}
),

dim_trip_distance AS (
    SELECT *
    FROM {{ ref('dim_trip_distance') }}
),

dim_rate_code AS (
    SELECT *
    FROM {{ ref('dim_rate_code') }}
),

dim_pickup_location AS (
    SELECT *
    FROM {{ ref('dim_pickup_location') }}
),

dim_dropoff_location AS (
    SELECT *
    FROM {{ ref('dim_dropoff_location') }}
),

dim_payment_type AS (
    SELECT *
    FROM {{ ref('dim_payment_type') }}
),

dim_datetime AS (
    SELECT *
    FROM {{ ref('dim_datetime') }}
),

final AS (
    SELECT
        -- keys
        t.trip_id,
        t.vendor_id,
        dd.datetime_id,
        dpl.pickup_location_id,
        ddl.dropoff_location_id,
        drc.rate_code_id,
        dpt.payment_type_id,
        dpc.passenger_count_id,
        dtd.trip_distance_id,

        -- measures
        t.fare_amount,
        t.extra,
        t.mta_tax,
        t.tip_amount,
        t.tolls_amount,
        t.improvement_surcharge,
        t.total_amount

    FROM trips t
        LEFT JOIN dim_passenger_count   dpc  ON t.passenger_count    = dpc.passenger_count
        LEFT JOIN dim_trip_distance     dtd  ON t.trip_distance      = dtd.trip_distance
        LEFT JOIN dim_rate_code         drc  ON t.ratecode_id        = drc.ratecode_id
        LEFT JOIN dim_pickup_location   dpl  ON t.pickup_latitude    = dpl.pickup_latitude
                                            AND t.pickup_longitude   = dpl.pickup_longitude
        LEFT JOIN dim_dropoff_location  ddl  ON t.dropoff_latitude   = ddl.dropoff_latitude
                                            AND t.dropoff_longitude  = ddl.dropoff_longitude
        LEFT JOIN dim_payment_type      dpt  ON t.payment_type       = dpt.payment_type
        LEFT JOIN dim_datetime          dd   ON t.pickup_datetime    = dd.pickup_datetime
                                            AND t.dropoff_datetime   = dd.dropoff_datetime
)

SELECT * FROM final
