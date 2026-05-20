import os
import subprocess
import keyring 
from dotenv import load_dotenv

# 1. Load the non-sensitive configuration from .env
load_dotenv(".env")

# 2. Fetch the highly sensitive passphrase from the OS Keyring
os.environ["DBT_ENV_SECRET_KEY_PASSPHRASE"] = keyring.get_password("snowflake_metadata", "dbt_passphrase")

# 3. Safely execute dbt
subprocess.run(["dbt", "debug"])

# 4. Optionally, you can also run dbt models or tests
# subprocess.run(["dbt", "test"])    

subprocess.run(["dbt", "run", "--full-refresh"])   