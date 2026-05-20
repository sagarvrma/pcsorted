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

# Delete low price eBay junk
cur.execute("DELETE FROM listings WHERE source = 'ebay' AND current_price < 200")
print(f'Deleted {cur.rowcount} low-price eBay listings')

# Delete junk titles
junk_titles = [
    '%read description%',
    '%build service%',
    '%parts only%',
    '%for parts%',
    '%not working%',
    '%as is%',
    '%broken%',
    '%untested%',
    '%barebone%',
    '%case only%',
    '%gpu only%',
    '%cpu only%',
]

for pattern in junk_titles:
    cur.execute(f"DELETE FROM listings WHERE source = 'ebay' AND LOWER(title) LIKE '{pattern}'")
    if cur.rowcount > 0:
        print(f'Deleted {cur.rowcount} listings matching: {pattern}')

conn.commit()

cur.execute("SELECT COUNT(*) FROM listings")
print(f'\nTotal listings remaining: {cur.fetchone()[0]}')

cur.execute("SELECT COUNT(*) FROM listings WHERE source = 'ebay'")
print(f'eBay listings remaining: {cur.fetchone()[0]}')

cur.close()
conn.close()