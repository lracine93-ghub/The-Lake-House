import logging
import pandas as pd
import urllib
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Set up logging for a clean, professional output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define your raw credentials (put the actual values here)
user = 'postgres'
password = 'p6ssw0rd' # Change if your password contains special characters
host = 'localhost'
port = '5432'
database = 'sales_db'

# 2. Safely encode the credentials
encoded_password = urllib.parse.quote(password)

# DEFINE THE DATABASE CONNECTION
DATABASE_URL = f'postgresql://{user}:{encoded_password}@{host}:{port}/{database}'


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

if __name__ == "__main__":

    # Define paths to  local CSVs
    SALES_CSV_PATH = "data/raw/sales_raw.csv"
    PRODUCTS_CSV_PATH = "data/raw/products_raw.csv"
    
    logging.info("Starting Extraction/Loading process...")
    
    # 1. Load Sales Raw Table
    load_csv_to_postgres(SALES_CSV_PATH, "raw_sales", DATABASE_URL)
    
    # 2. Load Products Raw Table
    load_csv_to_postgres(PRODUCTS_CSV_PATH, "raw_products", DATABASE_URL)
    
    logging.info("Extraction/Loading process completed.")