-- clean and standardize the raw data for further transformations
-- rename columns 
-- convert data types
-- add surrogate keys
-- filter out bad data

{{ config(
    materialized = 'view',  
    schema = 'staging' 
) }}
/*
materialized = 'view':   view name in BigQuery will be the same as the .sql file name, which is "stg_raw_data". 
schema = 'staging':   this will create seperate dataset in BigQuery for all staging models, which is good for organization and access control.
*/


SELECT 
    {{ dbt_utils.generate_surrogate_key(['VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']) }} AS trip_id, --creates a unique hash key from one or more columns
    VendorID AS vendor_id,
    tpep_pickup_datetime AS pickup_datetime,
    PARSE_DATETIME('%m/%d/%Y %H:%M', tpep_dropoff_datetime) AS dropoff_datetime,
    passenger_count AS passenger_count,
    trip_distance AS trip_distance,
    pickup_longitude AS pickup_longitude,
    pickup_latitude AS pickup_latitude,
    ratecodeid AS ratecode_id,
    store_and_fwd_flag AS store_and_fwd_flag,
    dropoff_longitude AS dropoff_longitude,
    dropoff_latitude AS dropoff_latitude,
    payment_type AS payment_type,
    fare_amount AS fare_amount,
    extra AS extra,
    mta_tax AS mta_tax,
    tip_amount AS tip_amount,
    tolls_amount AS tolls_amount,
    improvement_surcharge AS improvement_surcharge,
    total_amount AS total_amount
FROM {{ source('ds_uber_project', 'stg_uber_raw_data') }} -- reference the source name  and source table name defined in sources.yml
WHERE VendorID IS NOT NULL
   
