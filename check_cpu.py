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
cur.execute("SELECT cpu, COUNT(*) FROM listings WHERE cpu IS NOT NULL GROUP BY cpu ORDER BY COUNT(*) DESC")
for row in cur.fetchall():
    print(row)
conn.close()