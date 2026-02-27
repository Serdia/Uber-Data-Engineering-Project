import pandas as pd
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(df, *args, **kwargs): # 'data' here IS the DataFrame from the data_loader
    """
    Create dim/fact tables from new data.

    df here IS the new data coming from the data_loader.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # If no new data, then return a dictionary of empty dataframes, 
    # so the next block receives the expected structure and wont crush
    if len(df) == 0:
        print("No new data to transform")
        return {
            'fact': pd.DataFrame(),
            'dim_passanger_count': pd.DataFrame(),
            'dim_trip_distance': pd.DataFrame(),
            'dim_rate_code': pd.DataFrame(),
            'dim_pickup_location': pd.DataFrame(),
            'dim_dropoff_location': pd.DataFrame(),
            'dim_payment_type': pd.DataFrame(),
            'dim_datetime': pd.DataFrame(),
        }

    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

    df = df.drop_duplicates().reset_index(drop=True)
    df['trip_id'] = df.index

    dim_datetime = df[['tpep_pickup_datetime','tpep_dropoff_datetime']].drop_duplicates().reset_index(drop=True)

    # create new column in df based on 'tpep_pickup_datetime'
    dim_datetime['pick_hour']=dim_datetime['tpep_pickup_datetime'].dt.hour  
    dim_datetime['pick_day']=dim_datetime['tpep_pickup_datetime'].dt.day 
    dim_datetime['pick_month']=dim_datetime['tpep_pickup_datetime'].dt.month
    dim_datetime['pick_year']=dim_datetime['tpep_pickup_datetime'].dt.year
    dim_datetime['pick_weekday']=dim_datetime['tpep_pickup_datetime'].dt.weekday

    # create new column in df by based on 'tpep_dropoff_datetime'
    dim_datetime['drop_hour']=dim_datetime['tpep_dropoff_datetime'].dt.hour
    dim_datetime['drop_day']=dim_datetime['tpep_dropoff_datetime'].dt.day
    dim_datetime['drop_month']=dim_datetime['tpep_dropoff_datetime'].dt.month
    dim_datetime['drop_year']=dim_datetime['tpep_dropoff_datetime'].dt.year
    dim_datetime['drop_weekday']=dim_datetime['tpep_dropoff_datetime'].dt.weekday

    # create primary key "datetime_id"
    dim_datetime['datetime_id']=dim_datetime.index

    # organize columns in proper order 
    dim_datetime=dim_datetime[['datetime_id','tpep_pickup_datetime','pick_hour','pick_day','pick_month','pick_year','pick_weekday'
                ,'tpep_dropoff_datetime','drop_hour','drop_day','drop_month','drop_year','drop_weekday']]

    # dim_passanger_count
    dim_passanger_count = df[['passenger_count']].drop_duplicates().reset_index(drop=True)
    dim_passanger_count['passenger_count_id']=dim_passanger_count.index # create primary key "datetime_id"
    dim_passanger_count=dim_passanger_count[['passenger_count_id','passenger_count']] # reorder columns

    # dim_trip_distance
    dim_trip_distance = df[['trip_distance']].drop_duplicates().reset_index(drop=True)
    dim_trip_distance['trip_distance_id']=dim_trip_distance.index
    dim_trip_distance=dim_trip_distance[['trip_distance_id','trip_distance']]

    rate_code_type={
        1:"Standard rate",
        2:"JFK",
        3:"Newark",
        4:"Nassau or Westchester",
        5:"Negotiated fare",
        6:"Group ride"
    }

    # Resets the index to start from 0, 1, 2, 3...  drop=True discards the old index (doesn't keep it as a column)
    dim_rate_code = df[['RatecodeID']].drop_duplicates().reset_index(drop=True)                           # creates column 'RatecodeID'
    dim_rate_code['rate_code_id'] = dim_rate_code.index                                     # set primary key. Creates column 'rate_code_id'
    dim_rate_code['rate_code_name'] = dim_rate_code['RatecodeID'].map(rate_code_type)       # translate the numeric RatecodeID values to their descriptive names using the dictionary
    dim_rate_code[['rate_code_id','RatecodeID','rate_code_name']]                           # reorder columns

    dim_pickup_location = df[['pickup_latitude', 'pickup_longitude']].drop_duplicates().reset_index(drop=True)
    dim_pickup_location['pickup_location_id'] = dim_pickup_location.index
    dim_pickup_location[['pickup_location_id','pickup_latitude','pickup_longitude']]

    dim_dropoff_location = df[['dropoff_latitude', 'dropoff_longitude']].drop_duplicates().reset_index(drop=True)
    dim_dropoff_location['dropoff_location_id'] = dim_dropoff_location.index
    dim_dropoff_location[['dropoff_location_id','dropoff_latitude','dropoff_longitude']]


    payment_type_name = {
        0:"Flex Fare trip",
        1:"Credit card",
        2:"Cash",
        3:"No charge",
        4:"Dispute",
        5:"Unknown",
        6:"Voided trip"
    }

    # Resets the index to start from 0, 1, 2, 3...  drop=True discards the old index (doesn't keep it as a column)
    dim_payment_type=df[['payment_type']].drop_duplicates().reset_index(drop=True)
    dim_payment_type['payment_type_id'] = dim_payment_type.index
    dim_payment_type['payment_type_name'] = dim_payment_type['payment_type'].map(payment_type_name)
    dim_payment_type[['payment_type_id', 'payment_type', 'payment_type_name']]

    fact= (df.merge(dim_passanger_count, on='passenger_count', how='left')
            .merge(dim_trip_distance, on='trip_distance', how='left')
            .merge(dim_rate_code, on='RatecodeID', how='left')
            .merge(dim_pickup_location, on=['pickup_latitude', 'pickup_longitude'], how='left')
            .merge(dim_dropoff_location, on=['dropoff_latitude', 'dropoff_longitude'], how='left')
            .merge(dim_payment_type, on='payment_type', how='left')
            .merge(dim_datetime, on='tpep_pickup_datetime', how='left'))

    # # # Drop the original columns since now I have Ids in my fact table 
    # # fact = fact.drop(columns=['passenger_count'])

    # Instead of dropping columns from fact I choose the ones I want to keep
    fact = fact[[
        'trip_id',
        'VendorID',
        'datetime_id',
        'tpep_pickup_datetime',
        'pickup_location_id',
        'dropoff_location_id',
        'rate_code_id',
        'payment_type_id',
        'passenger_count_id',
        'trip_distance_id',
        'fare_amount',
        'extra',
        'mta_tax',
        'tip_amount',
        'tolls_amount',
        'improvement_surcharge',
        'total_amount'
    ]]

    # for more efficiency return dictionary of dataframes directly 
    # and exporter should be able to accept those
    return{
        "dim_datetime":dim_datetime,
        "dim_passanger_count":dim_passanger_count,
        "dim_trip_distance":dim_trip_distance,
        "dim_rate_code":dim_rate_code,
        "dim_pickup_location":dim_pickup_location,
        "dim_dropoff_location":dim_dropoff_location,
        "dim_payment_type":dim_payment_type,
        "fact":fact
    }


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
