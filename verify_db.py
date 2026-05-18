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

cur.execute("SELECT COUNT(*) FROM listings")
print(f"Total listings: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM listings WHERE source='bestbuy'")
print(f"Best Buy listings: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM listings WHERE source='antonline'")
print(f"Antonline listings: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM price_history")
print(f"Total price history rows: {cur.fetchone()[0]}")

cur.execute("""
    SELECT title, current_price, gpu, cpu, ram_gb 
    FROM listings 
    WHERE source='bestbuy' 
    LIMIT 5
""")
rows = cur.fetchall()
print("\nBest Buy sample:")
for row in rows:
    print(f"  {row[0][:60]} | ${row[1]} | GPU:{row[2]} | CPU:{row[3]} | RAM:{row[4]}GB")

cur.close()
conn.close()