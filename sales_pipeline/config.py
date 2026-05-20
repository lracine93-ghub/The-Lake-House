import os
import logging
import pandas as pd
import urllib
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
from dotenv import load_dotenv
import datetime 
import boto3
from botocore.exceptions import ProfileNotFound, ClientError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import snowflake.connector

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
        
    # SNOWFLAKE SETTINGS
    SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
    SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
    SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
    SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
    SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
    SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')
    SNOWFLAKE_ROLE = os.getenv('SNOWFLAKE_ROLE')
    DBT_ENV_SECRET_KEY_FILE_PATH = os.getenv('DBT_ENV_SECRET_KEY_FILE_PATH')
    DBT_ENV_SECRET_KEY_PASSPHRASE = os.getenv('DBT_ENV_SECRET_KEY_PASSPHRASE') 

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

    # Boto3 S3 SETTINGS (if needed in the future)
   #  AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
   #  AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
    AWS_REGION = os.getenv('AWS_REGION')

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


def get_s3_client(profile_name='lucien-dev'):
    """
    Creates a Boto3 client using a secure Named Profile.
    This pattern ensures credentials are never hardcoded.
    """
    try:
        # Create a session tied to your SSO profile
        session = boto3.Session(profile_name=profile_name)
        
        # Create the client from that session
        return session.client('s3')
    
    except ProfileNotFound:
        print(f"Error: AWS Profile '{profile_name}' not found. Run 'aws configure sso'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
def get_snowflake_connection():
    """Establish a connection to Snowflake using credentials from the config and Key Pair Authentication."""
    try:
        with open(Config.DBT_ENV_SECRET_KEY_FILE_PATH, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=Config.DBT_ENV_SECRET_KEY_PASSPHRASE.encode(),
            )
        private_key_der = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        conn = snowflake.connector.connect(
            user=Config.SNOWFLAKE_USER,
            account=Config.SNOWFLAKE_ACCOUNT,
            warehouse=Config.SNOWFLAKE_WAREHOUSE,
            database=Config.SNOWFLAKE_DATABASE,
            schema=Config.SNOWFLAKE_SCHEMA,
            role=Config.SNOWFLAKE_ROLE,
            # PRIVATE_KEY_CONTENT=CONFIG.SNOW_PKEY_PATH,
            # PRIVATE_KEY_PASSPHRASE=CONFIG.SNOW_PKEY_PASSPHRASE,
            private_key=private_key_der
        )
        return conn
    except Exception as e:
        logging.error(f"Error connecting to Snowflake: {e}")
        return None


