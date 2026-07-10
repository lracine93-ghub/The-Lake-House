import os
import subprocess
import sys
import keyring 
from dotenv import load_dotenv

# 1. Load the non-sensitive configuration from .env
load_dotenv(".env")

# 2. Fetch the highly sensitive passphrase from the OS Keyring
os.environ["DBT_ENV_SECRET_KEY_PASSPHRASE"] = keyring.get_password("snowflake_metadata", "dbt_passphrase")

# Checking Source Freshness (Optional but recommended)
print("--- CHECKING DBT SOURCE FRESHNESS ---")
subprocess.run(["dbt", "source", "freshness"], check=True)

# Optional: Clean the dbt environment before running (use with caution)
clean_environment = str(os.environ.get('CLEAN_ENV', 'N')).strip()

if clean_environment == 'Y':
     print("--- CLEANING DBT ENVIRONMENT ---")
     subprocess.run(["dbt", "clean"], check=True)
else:
    print("--- SKIPPING DBT ENVIRONMENT CLEANING ---")      

# 3. Safely execute dbt
print("--- DEBUGGING ---")
subprocess.run(["dbt", "debug"])

# 4. Optionally, you can also run dbt models or tests
 
bypass_tests = str(os.environ.get('BYPASS_TESTS', 'N')).strip()

if bypass_tests == 'Y':
    print("--- BYPASSING TESTS ---")
else:
    print("--- RUNNING TESTS ---")
    subprocess.run(["dbt", "test"]) 
    

generate_full_refresh = str(os.environ.get('GENERATE_FULL_REF', 'N')).strip().lower()

if generate_full_refresh == 'Y':
    print("--- GENERATING DBT MODELS WITH FULL REFRESH ---")
    subprocess.run(["dbt", "run", "--full-refresh"])  
else: 
    print("--- GENERATING DBT MODELS ---") 
    subprocess.run(["dbt", "run"])

# 5. Generate docs 

generate_docs = str(os.environ.get('GENERATE_DOCS', 'N')).strip()

# Check for environtment variable
# Returns None if no variable is set
if generate_docs == 'Y': 
    print("--- GENERATING DBT DOCUMENTATION ---")
    subprocess.run(["dbt", "docs", "generate"], check = True)

    print("--- SERVING DBT DOCUMENTATION ---")
    try:
        subprocess.run(["dbt", "docs", "serve", "--port", "8085"], check = True)
    except KeyboardInterrupt:
        print("DBT documentation server stopped by user.")
        
        
        sys.exit(0)


