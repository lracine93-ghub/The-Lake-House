#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

# 1. Activate the dbt environment
source dbt-env/bin/activate

# 2. Define your project path
PROJECT_DIR="/mnt/c/Users/lucie/Documents/GitHub/The-Lake-House/sales_pipeline"
cd $PROJECT_DIR

# 3. Load the new raw data into PostgreSQL
echo "--- Starting Data Ingestion ---"
python3 load_data.py

# 4. Run dbt source freshness check
echo "--- Checking Source Freshness ---"
dbt source freshness

# 5. Run dbt models
echo "--- Running Transformations ---"
dbt run

# 6. Test dbt models
echo "--- Running Data Tests ---"
dbt test

echo "--- Pipeline completed successfully! ---"