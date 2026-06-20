#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

# 1. Activate the dbt environment
source dbt-env/bin/activate

# 2. Define your project path
PROJECT_DIR="/mnt/c/Users/lucie/Documents/GitHub/The-Lake-House/sales_pipeline"
cd $PROJECT_DIR

# 3. Load the new raw data into PostgreSQL
echo "--- Starting Data Extraction (to AWS S3 ) & Loading (to Snowflake) ---"
python3 extract_data.py

# 4. Run dbt source freshness check
echo "--- Starting Data Transformation ---"
python3 dbt_run.py

echo "--- Pipeline completed successfully! ---"