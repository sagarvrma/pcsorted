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

# Overall counts
cur.execute("SELECT COUNT(*) FROM listings")
print(f"Total listings: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM listings WHERE source='ebay'")
print(f"eBay listings: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM listings WHERE source='bestbuy'")
print(f"Best Buy listings: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM listings WHERE source='newegg'")
print(f"Newegg listings: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM listings WHERE source='antonline'")
print(f"Antonline listings: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM price_history")
print(f"Total price history rows: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM pipeline_runs")
print(f"Total pipeline runs: {cur.fetchone()[0]}")

# Spec extraction quality
print("\n--- Spec Extraction Quality ---")
cur.execute("SELECT COUNT(*) FROM listings WHERE gpu IS NOT NULL")
print(f"Listings with GPU: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM listings WHERE cpu IS NOT NULL")
print(f"Listings with CPU: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM listings WHERE ram_gb IS NOT NULL")
print(f"Listings with RAM: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM listings WHERE storage_gb IS NOT NULL")
print(f"Listings with Storage: {cur.fetchone()[0]}")

# Per source spec quality
print("\n--- Spec Quality by Source ---")
for source in ['ebay', 'bestbuy', 'newegg', 'antonline']:
    cur.execute(f"""
        SELECT 
            COUNT(*) as total,
            COUNT(gpu) as has_gpu,
            COUNT(cpu) as has_cpu,
            COUNT(ram_gb) as has_ram
        FROM listings WHERE source='{source}'
    """)
    row = cur.fetchone()
    total, has_gpu, has_cpu, has_ram = row
    print(f"{source}: {total} total | GPU: {has_gpu} ({int(has_gpu/total*100) if total else 0}%) | CPU: {has_cpu} ({int(has_cpu/total*100) if total else 0}%) | RAM: {has_ram} ({int(has_ram/total*100) if total else 0}%)")

# Price ranges by source
print("\n--- Price Ranges by Source ---")
for source in ['ebay', 'bestbuy', 'newegg', 'antonline']:
    cur.execute(f"""
        SELECT MIN(current_price), MAX(current_price), AVG(current_price)
        FROM listings WHERE source='{source}' AND current_price IS NOT NULL
    """)
    row = cur.fetchone()
    if row[0]:
        print(f"{source}: ${row[0]:.0f} - ${row[1]:.0f} (avg ${row[2]:.0f})")

# Condition breakdown
print("\n--- Condition Breakdown ---")
cur.execute("""
    SELECT condition, COUNT(*) 
    FROM listings 
    GROUP BY condition 
    ORDER BY COUNT(*) DESC
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# GPU distribution
print("\n--- Top GPUs in DB ---")
cur.execute("""
    SELECT gpu, COUNT(*) 
    FROM listings 
    WHERE gpu IS NOT NULL 
    GROUP BY gpu 
    ORDER BY COUNT(*) DESC 
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Sample listings per source
for source in ['bestbuy', 'newegg', 'ebay']:
    cur.execute(f"""
        SELECT title, current_price, gpu, cpu, ram_gb 
        FROM listings 
        WHERE source='{source}' 
        ORDER BY RANDOM()
        LIMIT 3
    """)
    rows = cur.fetchall()
    print(f"\n--- {source.capitalize()} Sample ---")
    for row in rows:
        print(f"  {row[0][:55]} | ${row[1]} | GPU:{row[2]} | CPU:{row[3]} | RAM:{row[4]}GB")

# Recent pipeline runs
print("\n--- Recent Pipeline Runs ---")
cur.execute("""
    SELECT source, rows_ingested, rows_rejected, duration_seconds, status, ran_at
    FROM pipeline_runs
    ORDER BY ran_at DESC
    LIMIT 12
""")
for row in cur.fetchall():
    print(f"  {row[5].strftime('%m/%d %H:%M')} | {row[0]} | ingested:{row[1]} rejected:{row[2]} | {row[3]:.1f}s | {row[4]}")

cur.close()
conn.close()