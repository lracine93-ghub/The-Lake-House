import pandas as pd
from sqlalchemy import create_engine
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import os
from config import Config, get_s3_client, get_snowflake_connection
import boto3 
import logging
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

def load_sales_fact_tbl(table_name):
    # Loads the sales fact table from S3 to Snowflake using Snowflake's COPY INTO command.

    conn = get_snowflake_connection()

    # 1. Create the sales fact table in Snowflake
    query = f"""CREATE OR REPLACE TABLE {Config.SNOWFLAKE_SCHEMA}.{table_name} (
                                sales_id INTEGER, 
                                product_id INTEGER, 
                                cust_id INTEGER, 
                                qty INTEGER, 
                                unit_price DECIMAL(10,2), 
                                total_amt DECIMAL(10,2), 
                                sale_date TIMESTAMP_NTZ, 
                                updated_at TIMESTAMP_NTZ, 
                                dbt_updated_at TIMESTAMP_NTZ default current_timestamp());"""

    try:
        conn.cursor().execute(query)
        print(f"Successfully created {table_name} table in Snowflake.")
    except Exception as e:  
        print(f"Error creating {table_name} table in Snowflake: {e}")
        return
    
    # 2. Load data from S3 to Snowflake using Snowflake's COPY INTO command
    
    copy_query = f""" COPY INTO {Config.SNOWFLAKE_SCHEMA}.{table_name}
                    FROM @LUCIEN_MIGRATION.RAW.S3_RAW_STAGE/{table_name}
                    FILE_FORMAT = (TYPE = 'PARQUET')
                    PATTERN = '.*\\.parquet'
                    MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
                    ON_ERROR = 'SKIP_FILE';     """   
    try:
        conn.cursor().execute(copy_query)
        print(f"Successfully loaded data into {table_name} table in Snowflake.")
    except Exception as e:
        print(f"Error loading data into {table_name} table in Snowflake: {e}")
    finally:
        conn.close()

def load_products_dim_tbl(table_name):
    # Loads the products dimension table from S3 to Snowflake using Snowflake's COPY INTO command.

    conn = get_snowflake_connection()

    # 1. Create the products dimension table in Snowflake
    query = f"""CREATE OR REPLACE TABLE {Config.SNOWFLAKE_SCHEMA}.{table_name} (
                                id integer ,
                                title string,
                                price number(10,2),
                                description string,
                                category string, 
                                image string,
                                rating string, 
                                updated_at timestamp_ntz, 
                                ingestion_ts timestamp_ntz default current_timestamp()
                                );"""

    try:
        conn.cursor().execute(query)
        print(f"Successfully created {table_name} table in Snowflake.")
    except Exception as e:  
        print(f"Error creating {table_name} table in Snowflake: {e}")
        return
    # 2. Load data from S3 to Snowflake using Snowflake's COPY INTO command
    
    copy_query = f""" COPY INTO {Config.SNOWFLAKE_SCHEMA}.{table_name}
                    FROM @LUCIEN_MIGRATION.RAW.S3_RAW_STAGE/{table_name}
                    FILE_FORMAT = (TYPE = 'PARQUET')
                    PATTERN = '.*\\.parquet'
                    MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
                    ON_ERROR = 'SKIP_FILE';     """   
    try:
        conn.cursor().execute(copy_query)
        print(f"Successfully loaded data into {table_name} table in Snowflake.")
    except Exception as e:
        print(f"Error loading data into {table_name} table in Snowflake: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
   #  migrate_table('raw_products')
    migrate_table('raw_sales')
    load_sales_fact_tbl('raw_sales')
