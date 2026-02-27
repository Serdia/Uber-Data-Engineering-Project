import io
import pandas as pd
import requests
from google.cloud import bigquery


if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    client = bigquery.Client()

    watermark_query = """
    SELECT MAX(tpep_pickup_datetime) as last_load_time
    FROM `uber-data-pipeline-487320.ds_uber_project.fact`
    """
    try:
        result = client.query(watermark_query).to_dataframe()
        last_load_time = '2016-03-01'  #result['last_load_time'][0]

        
        if pd.isna(last_load_time):
            # if no data exists yet, set very old date
            last_load_time = pd.Timestamp('1900-01-01')
            print("First run - loading all data")
        else:
            print(f"Loading data after {last_load_time}")

    except Exception as e: # catches the error from try block
        # First run - table doesnt exists
        print(f"Table not found (first run): {e}")
        last_load_time = pd.Timestamp('1900-01-01')
        
    
    # Load csv from google cloud storage
    url = 'https://storage.googleapis.com/os-gcp-bucket/uber_data.csv'
    response = requests.get(url)

    #Returns a DataFrame. Loading ALL records from .csv
    df = pd.read_csv(io.StringIO(response.text), sep=',').head(10) # only return 100 rows 

    # convert to datetime
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])

    # Filter for only new records
    df_new = df[df['tpep_pickup_datetime'] > last_load_time]

    print(f"Total records in CSV: {len(df)}")
    print(f"New records to process: {len(df_new)}")

    if len(df_new) == 0:
        print("No new data to process")
        return pd.DataFrame() # retrurn empty dataframe

    # otherwise
    return df_new
