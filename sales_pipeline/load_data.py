import logging
import pandas as pd
import urllib
# from scripts.config import Config
from sqlalchemy import create_engine

from  config import Config, load_csv_to_postgres

# Set up logging for a clean, professional output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Define paths to  local CSVs
SALES_CSV_PATH = Config.DATA_DIR / "sales_raw.csv"
PRODUCTS_CSV_PATH = Config.DATA_DIR / "products_raw.csv"


if __name__ == "__main__":
    logging.info("Starting Extraction/Loading process...")
    
    # 1. Load Sales Raw Table
    load_csv_to_postgres(SALES_CSV_PATH, "raw_sales", Config.DATABASE_URL)
    

    # 2. Load Products Raw Table
    load_csv_to_postgres(PRODUCTS_CSV_PATH, "raw_products", Config.DATABASE_URL)
    
    logging.info("Extraction/Loading process completed.")