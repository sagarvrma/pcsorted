import time
import os
import json
import boto3
from datetime import datetime
from dotenv import load_dotenv

from scraper.sources import ebay, bestbuy, antonline
from scraper.normalizer import normalize
from scraper.upsert import get_conn, upsert_listing, log_pipeline_run

load_dotenv()

S3_BUCKET = os.getenv('S3_BUCKET', 'pcsorted-data')

def upload_raw_to_s3(source, data):
    try:
        s3 = boto3.client('s3')
        key = f"raw/{source}/{datetime.utcnow().strftime('%Y-%m-%d')}.json"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        print(f"Uploaded raw {source} data to s3://{S3_BUCKET}/{key}")
    except Exception as e:
        print(f"S3 upload failed for {source}: {e}")

def run_source(source_name, scrape_fn, conn):
    print(f"\n--- Running {source_name} scraper ---")
    start = time.time()
    rows_ingested = 0
    rows_rejected = 0

    try:
        raw = scrape_fn()
        upload_raw_to_s3(source_name, raw)

        for item in raw:
            try:
                normalized = normalize(item, source_name)

                if not normalized['current_price'] or not normalized['url']:
                    rows_rejected += 1
                    continue

                if normalized['current_price'] < 100 or normalized['current_price'] > 10000:
                    rows_rejected += 1
                    continue

                upsert_listing(conn, normalized)
                rows_ingested += 1

            except Exception as e:
                print(f"  Row error: {e}")
                rows_rejected += 1

        conn.commit()
        duration = round(time.time() - start, 2)
        log_pipeline_run(conn, source_name, rows_ingested, rows_rejected, duration, 'success')
        conn.commit()
        print(f"{source_name} done: {rows_ingested} ingested, {rows_rejected} rejected in {duration}s")

    except Exception as e:
        duration = round(time.time() - start, 2)
        log_pipeline_run(conn, source_name, 0, 0, duration, f'error: {str(e)}')
        conn.commit()
        print(f"{source_name} failed: {e}")

def main():
    print(f"PCSorted pipeline starting at {datetime.utcnow().isoformat()}")
    conn = get_conn()

    run_source('antonline', antonline.scrape, conn)
    run_source('bestbuy', bestbuy.scrape, conn)
    # run_source('ebay', ebay.scrape, conn)  # works in CI, blocked locally

    conn.close()
    print("\nPipeline complete.")

if __name__ == "__main__":
    main()