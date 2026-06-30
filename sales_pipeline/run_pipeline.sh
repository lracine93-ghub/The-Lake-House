#!/bin/bash
# set -e # Exit immediately if a command exits with a non-zero status

ENV_FILE=".env"

# 1. Check if .env file exists, if it does, load the environment variables
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE..."
    
    while IFS= read -r line || [ -n "$line" ]; do
        # 1. Remove trailing Windows carriage returns (\r) if they exist
        line=$(echo "$line" | tr -d '\r')
        
        # 2. Strip out inline comments and leading/trailing whitespace
        line=$(echo "$line" | sed 's/#.*//' | xargs)
        
        # 3. Skip lines that are empty or were completely commented out
        [ -z "$line" ] && continue
        
        # 4. Export the clean key=value pair
        export "$line"
    done < "$ENV_FILE"
else
    echo "❌ Error: $ENV_FILE file not found!"
    exit 1
fi

# 2. Verify AWS_S3_PROFILE was actually loaded
if [ -z "$AWS_S3_PROFILE" ]; then
    echo "❌ Error: AWS_S3_PROFILE is not set in your $ENV_FILE file."
    exit 1
fi

echo "Using AWS Profile: $AWS_S3_PROFILE"

# 3. Activate the dbt environment
source dbt-env/bin/activate

# 4. Define your project path
PROJECT_DIR="/mnt/c/Users/lucie/Documents/GitHub/The-Lake-House/sales_pipeline"
cd $PROJECT_DIR


# 5. Check AWS authentication status

echo "Checking AWS authentication status..."

# Run the identity check silently; redirect both standard output and errors to null
if aws sts get-caller-identity > /dev/null 2>&1; then
    echo "✔ Active AWS session detected. Skipping to next step in pipeline..."
else
    echo "❌ AWS session missing or expired. Invoking login command..."
    
    # Replace this with your specific login command (e.g., aws sso login)
    aws sso login  --profile $AWS_S3_PROFILE --use-device-code

    # 2. PAUSE THE SCRIPT: Give yourself time to authorize in the browser
    echo "--------------------------------------------------------"
    echo "👉 ACTION REQUIRED:"
    echo "1. Copy the URL above into your Windows browser."
    echo "2. Enter the code provided by the AWS CLI."
    echo "3. Once you see 'Successfully logged in' in your browser,"
    echo "   come back here and press [ENTER] to continue."
    echo "--------------------------------------------------------"
    read -p "Press [ENTER] after completing browser authentication..."
    
    # Optional: Verify if the login actually succeeded before moving forward
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        echo "Error: AWS login failed. Aborting pipeline."
        exit 1
    fi
fi

echo "Running next pipeline step: Extraction & Loading..."


# 6. Run the data extraction and loading script
echo "--- Starting Data Extraction (to AWS S3 ) & Loading (to Snowflake) ---"
python3 main.py

# 7. Run dbt transformations
echo "--- Starting Data Transformation ---"
export GENERATE_FULL_REF="Y" GENERATE_DOCS="Y" CLEAN_ENV="Y" BYPASS_TESTS="N"
if python3 dbt_run.py; then
    echo "Pipeline completed successfully!"
    PIPELINE_STATUS=1
else
    echo "❌ Error: dbt transformations failed. Aborting pipeline."
    PIPELINE_STATUS=0
    exit 1
fi


# 8. Force logout of AWS SSO session to prevent lingering sessions
echo "--- Logging out of AWS SSO session ---"
if aws sso logout; then
    echo "✔ AWS SSO session logged out for $AWS_S3_PROFILE successfully."
else
    echo "❌ Error: Failed to log $AWS_S3_PROFILE out of AWS SSO session. Please check manually."
fi

# Final Pipeline Exit
if [ $PIPELINE_STATUS -eq 0 ]; then
    echo "--- Pipeline completed successfully! ---"
    return 0 > 2 > /dev/null || exit 0
else
    echo "❌ Pipeline encountered errors. Please check logs for details."
    return 1 > 2 > /dev/null || exit 1
    
fi
echo " --- Session logged out successfully. ---"
echo "--- Pipeline completed successfully! ---"