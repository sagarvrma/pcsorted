import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=int(os.getenv('DB_PORT', 5432))
    )

def upsert_listing(conn, listing: dict) -> bool:
    sql = """
        INSERT INTO listings (
            source, external_id, title, url, image_url, brand,
            device_type, condition, in_stock, cpu, gpu,
            ram_gb, storage_gb, current_price, last_seen_at
        ) VALUES (
            %(source)s, %(external_id)s, %(title)s, %(url)s, %(image_url)s, %(brand)s,
            %(device_type)s, %(condition)s, %(in_stock)s, %(cpu)s, %(gpu)s,
            %(ram_gb)s, %(storage_gb)s, %(current_price)s, NOW()
        )
        ON CONFLICT (url) DO UPDATE SET
            current_price = EXCLUDED.current_price,
            in_stock = EXCLUDED.in_stock,
            last_seen_at = NOW()
        RETURNING id, (xmax = 0) AS inserted
    """
    cur = conn.cursor()
    cur.execute(sql, listing)
    row = cur.fetchone()
    listing_id, inserted = row

    # Always write price history
    cur.execute(
        "INSERT INTO price_history (listing_id, price) VALUES (%s, %s)",
        (listing_id, listing['current_price'])
    )
    cur.close()
    return inserted

def log_pipeline_run(conn, source, rows_ingested, rows_rejected, duration, status):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pipeline_runs (source, rows_ingested, rows_rejected, duration_seconds, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (source, rows_ingested, rows_rejected, duration, status))
    cur.close()