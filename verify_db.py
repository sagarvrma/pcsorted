import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=int(os.getenv('DB_PORT', 5432))
)
cur = conn.cursor()

# Count listings
cur.execute("SELECT COUNT(*) FROM listings")
print(f"Total listings: {cur.fetchone()[0]}")

# Count price history
cur.execute("SELECT COUNT(*) FROM price_history")
print(f"Total price history rows: {cur.fetchone()[0]}")

# Count pipeline runs
cur.execute("SELECT COUNT(*) FROM pipeline_runs")
print(f"Total pipeline runs: {cur.fetchone()[0]}")

# Show sample listings
cur.execute("SELECT title, current_price, brand, gpu, cpu, ram_gb FROM listings LIMIT 5")
rows = cur.fetchall()
print("\nSample listings:")
for row in rows:
    print(f"  {row[0][:50]} | ${row[1]} | {row[2]} | GPU:{row[3]} | CPU:{row[4]} | RAM:{row[5]}GB")

cur.close()
conn.close()