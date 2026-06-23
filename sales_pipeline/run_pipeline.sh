#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

# 1. Activate the dbt environment
source dbt-env/bin/activate

# 2. Define your project path
PROJECT_DIR="/mnt/c/Users/lucie/Documents/GitHub/The-Lake-House/sales_pipeline"
cd $PROJECT_DIR

# log in to AWS using SSO

echo "Checking AWS authentication status..."

# Run the identity check silently; redirect both standard output and errors to null
if aws sts get-caller-identity > /dev/null 2>&1; then
    echo "✔ Active AWS session detected. Skipping to next step in pipeline..."
else
    echo "❌ AWS session missing or expired. Invoking login command..."
    
    # Replace this with your specific login command (e.g., aws sso login)
    aws login
    
    # Optional: Verify if the login actually succeeded before moving forward
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        echo "Error: AWS login failed. Aborting pipeline."
        exit 1
    fi
fi

# --- Your Next Pipeline Step Goes Here ---
echo "Running next pipeline step: Extraction & Loading..."


# 3. Load the new raw data into PostgreSQL
echo "--- Starting Data Extraction (to AWS S3 ) & Loading (to Snowflake) ---"
python3 main.py

echo "--- Starting Data Transformation ---"
export GENERATE_FULL_REF="Y" GENERATE_DOCS="Y" CLEAN_ENV="Y" BYPASS_TESTS="N"
python3 dbt_run.py

echo "--- Pipeline completed successfully! ---"