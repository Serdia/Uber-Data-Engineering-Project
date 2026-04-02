



SELECT
    {{ dbt_utils.generate_surrogate_key(['pickup_datetime', 'dropoff_datetime']) }} AS datetime_id, 

    pickup_datetime,
    EXTRACT(HOUR FROM pickup_datetime)      AS pick_hour,
    EXTRACT(DAY FROM pickup_datetime)       AS pick_day,
    EXTRACT(MONTH FROM pickup_datetime)     AS pick_month,
    EXTRACT(YEAR FROM pickup_datetime)      AS pick_year,
    EXTRACT(DAYOFWEEK FROM pickup_datetime) AS pick_weekday,

    dropoff_datetime,
    EXTRACT(HOUR FROM dropoff_datetime)      AS drop_hour,
    EXTRACT(DAY FROM dropoff_datetime)       AS drop_day,
    EXTRACT(MONTH FROM dropoff_datetime)     AS drop_month,
    EXTRACT(YEAR FROM dropoff_datetime)      AS drop_year,
    EXTRACT(DAYOFWEEK FROM dropoff_datetime) AS drop_weekday

FROM (
    SELECT DISTINCT
        pickup_datetime,
        dropoff_datetime
    FROM {{ ref('stg_raw_data') }}
    WHERE pickup_datetime IS NOT NULL
      AND dropoff_datetime IS NOT NULL
)

