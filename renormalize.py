import psycopg2
import os
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
from scraper.normalizer import extract_gpu, extract_cpu, extract_ram, extract_storage, extract_brand, extract_condition, extract_device_type

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=int(os.getenv('DB_PORT', 5432))
)
cur = conn.cursor()

# Fetch all listings
cur.execute("SELECT id, title FROM listings")
rows = cur.fetchall()
print(f"Re-normalizing {len(rows)} listings...")

updated = 0
for listing_id, title in rows:
    gpu = extract_gpu(title)
    cpu = extract_cpu(title)
    ram = extract_ram(title)
    storage = extract_storage(title)
    brand = extract_brand(title)
    condition = extract_condition(title)
    device_type = extract_device_type(title)

    cur.execute("""
        UPDATE listings SET
            gpu = %s,
            cpu = %s,
            ram_gb = %s,
            storage_gb = %s,
            brand = %s,
            condition = %s,
            device_type = %s
        WHERE id = %s
    """, (gpu, cpu, ram, storage, brand, condition, device_type, listing_id))
    updated += 1

conn.commit()
print(f"Updated {updated} listings")

# Show new stats
cur.execute("SELECT COUNT(*) FROM listings WHERE gpu IS NOT NULL")
print(f"Listings with GPU: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM listings WHERE cpu IS NOT NULL")
print(f"Listings with CPU: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM listings WHERE ram_gb IS NOT NULL")
print(f"Listings with RAM: {cur.fetchone()[0]}")

cur.close()
conn.close()