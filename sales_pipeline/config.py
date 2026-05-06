import os
import logging
import pandas as pd
import urllib
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
from dotenv import load_dotenv
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.backends import default_backend

# LOCATE THE DIRECTORY OF THIS FILE TO FIND THE .ENV
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Centralized configuration management for the ETL pipeline."""
    
    # POSTGRES SETTINGS
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD') # Change if your password contains special characters
    POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_DB = os.getenv('POSTGRES_DB')

    # Safely read and convert the port with a default fallback
    try:
        POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    except ValueError:
        POSTGRES_PORT = 5432  # Fallback to the standard port
        
    

    # API SETTINGS
    encoded_password = urllib.parse.quote(POSTGRES_PASSWORD)
    DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # LOCAL PATHS
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data/raw"
    # SAMPLE_DIR = BASE_DIR / "sample_data" 
    
    # CREATE DATA DIRECTORY IF IT DOESN'T EXIST
    DATA_DIR.mkdir(exist_ok=True)
    # SAMPLE_DIR.mkdir(exist_ok=True)
# INSTANTIATE CONFIG FOR USE IN OTHER FILES
config = Config()

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

def header():
    """Return a standard header for API requests."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }