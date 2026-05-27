import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=5432
)
cur = conn.cursor()

cur.execute("DELETE FROM price_history WHERE listing_id IN (SELECT id FROM listings WHERE source = 'antonline')")
print(f'Deleted {cur.rowcount} Antonline price history rows')

cur.execute("DELETE FROM listings WHERE source = 'antonline'")
print(f'Deleted {cur.rowcount} Antonline listings')

conn.commit()
cur.close()
conn.close()