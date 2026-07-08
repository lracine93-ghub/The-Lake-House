from data_xtractor import migrate_table
from data_loadr import PRODUCTS_CSV_PATH, SALES_CSV_PATH, load_products_dim_tbl, load_sales_fact_tbl
from config import Config, get_s3_client, header, get_snowflake_connection
import logging

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    print("Migrating tables from PostgreSQL to AWS S3...")

    # Migrate raw_products and raw_sales tables
    print(f'--- Starting migration for raw_products ---')
    migrate_table('raw_products')
    print(f'--- Finished migration for raw_products ---')

    print(f'--- Starting migration for raw_sales ---')
    migrate_table('raw_sales')
    print(f'--- Finished migration for raw_sales ---')

    print("Migration to S3 completed. Starting loading to Snowflake...")

    print(f'--- Starting dimension table loading for raw_products ---')
    load_products_dim_tbl('raw_products')
    print(f'--- Finished dimension table loading for raw_products ---')

    print(f'--- Starting fact table loading for raw_sales ---')
    load_sales_fact_tbl('raw_sales')
    print(f'--- Finished fact table loading for raw_sales ---')

    print("Data migration & loading completed.")

    # 1. Load Sales Raw Table
    # load_csv_to_postgres(SALES_CSV_PATH, "raw_sales", Config.DATABASE_URL)
    

    # 2. Load Products Raw Table
    # load_csv_to_postgres(PRODUCTS_CSV_PATH, "raw_products", Config.DATABASE_URL)