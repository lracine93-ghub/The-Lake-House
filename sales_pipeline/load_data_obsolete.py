import os
import pandas as pd
import urllib
from sqlalchemy import create_engine, text
import datetime


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
engine = create_engine(DATABASE_URL)

# 2. Base path to your project files on your Windows machine (accessed through WSL)
base_path = r"/mnt/c/Users/lucie/Documents/GitHub/The-Lake-House/sales_pipeline"


# Set up logging for a clean, professional output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    # Replace with your actual PostgreSQL credentials
    # Format: postgresql://username:password@host:port/database_name
    DATABASE_URL = "postgresql://racinel:password@localhost:5432/sales_db"
    
    # Define paths to your local CSVs (adjust paths if they are in a /data directory)
    SALES_CSV_PATH = "data/raw_sales.csv"
    PRODUCTS_CSV_PATH = "data/raw_products.csv"
    
    logging.info("Starting EL process...")
    
    # 1. Load Sales Raw Table
    load_csv_to_postgres(SALES_CSV_PATH, "raw_sales", DATABASE_URL)
    
    # 2. Load Products Raw Table
    load_csv_to_postgres(PRODUCTS_CSV_PATH, "raw_products", DATABASE_URL)
    
    logging.info("EL process completed.")

# 3. Define the CSV files to load (Update these file names to match your actual CSV files!)
files_to_load = {
    'raw_sales': 'data/raw/sales_raw.csv', 
    'raw_products': 'data/raw/products_raw.csv'
}

for table_name, file_path in files_to_load.items():
    full_path = os.path.join(base_path, file_path)
    
    print(f"Loading {full_path} into table {table_name}...")

    with engine.connect() as conn:
        try:
            # Truncate stg_sales and drop dependencies if necessary
            conn.execute(text(f"ALTER TABLE public.{table_name} ADD COLUMN IF NOT EXISTS loaded_at TIMESTAMP;"))
            conn.commit()
            print("Ensured 'loaded_at' column exists in the database.")

            conn.execute(text(f"TRUNCATE TABLE public.{table_name} CASCADE;"))
            conn.commit()    

            df = pd.read_csv(full_path)
            df['loaded_at'] = datetime.datetime.now()  # Add a timestamp column for tracking when the data was loaded    
            
            # Load the DataFrame into the database (replaces the table if it exists)
            df.to_sql(table_name, con=engine, schema='public', if_exists='append', index=False)
          
            print(f"Successfully loaded {table_name}!")
        except Exception as e:
            print(f"Error loading {table_name}: {e}")
        
# Add a timestamp column for tracking when the data was loaded

