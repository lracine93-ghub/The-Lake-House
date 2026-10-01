import duckdb

# Point to your database file
db_path = 'C:/Users/lucie/Documents/GitHub/The-Lake-House/sales_pipeline/data/warehouse.duckdb'

# Connect to the database
conn = duckdb.connect(db_path)

# Query the database
tables = conn.execute("SELECT * FROM information_schema.tables WHERE table_schema='main'").fetchall()

print("Tables found in warehouse.duckdb:")

for table in tables:
    print(f"- {table[0], table[1], table[2]}")

conn.close()