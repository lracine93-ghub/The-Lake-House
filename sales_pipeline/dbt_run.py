import os
import subprocess
import keyring 
from dotenv import load_dotenv

# 1. Load the non-sensitive configuration from .env
load_dotenv(".env")

# 2. Fetch the highly sensitive passphrase from the OS Keyring
os.environ["DBT_ENV_SECRET_KEY_PASSPHRASE"] = keyring.get_password("snowflake_metadata", "dbt_passphrase")

# Optional: Clean the dbt environment before running (use with caution)
# print("..::..DBT CLEANING..::..")
# subprocess.run(["dbt", "clean"])

# 3. Safely execute dbt
print("..::..DBT DEBUGGING..::..")
subprocess.run(["dbt", "debug"])

# 4. Optionally, you can also run dbt models or tests
 
bypass_tests = str(os.environ.get('BYPASS_TESTS', 'false')).strip().lower()

if bypass_tests == 'true':
    print("Bypassing Tests...")
else:
    print("Testing...")
    subprocess.run(["dbt", "test"]) 
    

generate_full_refresh = str(os.environ.get('GENERATE_FULL_REF', 'false')).strip().lower()

if generate_full_refresh == 'true':
    print("Generating dbt models with full refresh...")
    subprocess.run(["dbt", "run", "--full-refresh"])  
else: 
    print("Generating dbt models...") 
    subprocess.run(["dbt", "run"])

# 5. Generate docs 

generate_docs = str(os.environ.get('GENERATE_DOCS', 'false')).strip().lower()
# print(f'DEBUG: The raw env variable is: '{os.environ.get('GENERATE_DOCS')}'"')

# Check for environtment variable
# Returns None if no variable is set
if generate_docs == 'true': 
    print("Generating dbt docs...")
    subprocess.run(["dbt", "docs", "generate"], check = True)
else:
    print("Skipping dbt doc generation...")

print("Generating Data Lineage...")
subprocess.run(["dbt", "docs", "serve", "--port 8085"])