import pandas as pd
from google.cloud import bigquery

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



@data_exporter
def export_raw_to_bigquery(df, **kwargs):
    """
    Load raw incremental data to BigQuery staging table
    dbt will transform it later
    """
    
    if len(df) == 0:
        print("No new data to export")
        return
    
    # Just load the raw DataFrame as-is
    # No transformations!
    # Uses pandas-gbq library directly
    # Uses credentials from environment variable (GOOGLE_APPLICATION_CREDENTIALS) or VM's service account
    # Standard pandas method (works anywhere, not just Mage)
    # More control over options
    df.to_gbq(
        # creates table if not exists
        destination_table='uber-data-pipeline-487320.ds_uber_project.stg_uber_raw_data',
        project_id='uber-data-pipeline-487320',
        if_exists='append',  # Incremental append
        progress_bar=False
    )
    
    print(f" Loaded {len(df)} raw records to staging table")
