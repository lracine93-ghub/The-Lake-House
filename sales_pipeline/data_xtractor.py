import pandas as pd
from sqlalchemy import create_engine
import os
from config import Config, get_s3_client
import datetime

def migrate_table(table_name):

    # 1. Connect to your local Postgres (The "Silly" Server)
    pg_engine = create_engine(Config.DATABASE_URL)

    try:
        pg_engine.connect()
        print("Successfully connected to PostgreSQL.")

        s3 = get_s3_client()
        print("Successfully connected to AWS S3.")
    except Exception as e:
        print(f"Error connecting to PostgreSQL or S3: {e}")
        return


    print(f"--- Starting migration for {table_name} ---")
    
    # 2. Extract: Use chunking for large tables 
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, pg_engine)
    
    # 3. Save as Parquet for efficient upload to S3
    parquet_file = f"{table_name}_{datetime.datetime.now().strftime('%Y%m%d')}_{datetime.datetime.now().strftime('%H%M%S')}.parquet"
    df.to_parquet(parquet_file, index=False, engine='pyarrow')
   
    try:
        s3.upload_file(parquet_file, Config.AWS_S3_BUCKET_NAME, f"raw/{table_name}/{datetime.datetime.now().strftime('%Y-%m-%d')}/{parquet_file}")
        print(f"Loaded {parquet_file} into {Config.AWS_S3_BUCKET_NAME} S3 bucket.")
    except Exception as e:
        print(f"Error uploading to S3: {e}")
    finally:
        if os.path.exists(parquet_file):
            os.remove(parquet_file)


 