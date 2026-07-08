import pandas as pd
from config import Config, get_snowflake_connection
import logging
import os
from sqlalchemy import create_engine, exc as SQLAlchemyError


# Set up logging for a clean, professional output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Define paths to  local CSVs
SALES_CSV_PATH = Config.DATA_DIR / "sales_raw.csv"
PRODUCTS_CSV_PATH = Config.DATA_DIR / "products_raw.csv"


if __name__ == "__main__":
    logging.info("Starting Extraction/Loading process...")
    
   
def load_csv_to_postgres(file_path: str, table_name: str, conn_string: str) -> None:
    """
    Reads a CSV file and loads it into a PostgreSQL table.
    """
    try:
        logging.info(f"Reading {file_path}...")
        df = pd.read_csv(file_path)
        
        # Create database engine
        engine = create_engine(conn_string)
        
        logging.info(f"Loading data into table '{table_name}'...")
        # 'replace' will drop and recreate the table with the new CSV schema
        df.to_sql(
            name=table_name, 
            con=engine, 
            schema='public', 
            if_exists='replace', 
            index=False,
            chunksize=10000 # Good for large datasets
        )
        logging.info(f"Successfully loaded table '{table_name}' with {len(df)} rows.")
        
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except SQLAlchemyError as e:
        logging.error(f"Database error occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    
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
                    FROM @LUCIEN_MIGRATION.RAW.RAW_S3_STAGE/{table_name}
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
                    FROM @LUCIEN_MIGRATION.RAW.RAW_S3_STAGE/{table_name}
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
    logging.info("Extraction/Loading process completed.")

     # 1. Load Sales Raw Table
    # load_csv_to_postgres(SALES_CSV_PATH, "raw_sales", Config.DATABASE_URL)
    

    # 2. Load Products Raw Table
   #  load_csv_to_postgres(PRODUCTS_CSV_PATH, "raw_products", Config.DATABASE_URL)