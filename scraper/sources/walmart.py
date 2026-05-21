import re
import time
import random
import os
import requests
import boto3
from urllib.parse import quote
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

SCRAPEOPS_KEY = os.getenv('SCRAPEOPS_API_KEY')

SEARCH_QUERIES = [
    "gaming desktop RTX 4060",
    "gaming desktop RTX 4070",
    "gaming desktop RTX 4080",
    "gaming desktop RTX 3060",
    "gaming desktop RTX 3070",
    "gaming desktop RTX 5070",
    "gaming desktop RTX 5060",
    "CyberPowerPC gaming desktop",
    "iBUYPOWER gaming desktop",
    "prebuilt gaming PC",
    "gaming desktop AMD Ryzen",
    "gaming desktop RX 7800",
]

def get_scrapeops_url(url):
    return f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={quote(url)}&render=true&render_wait=4000"

def clean_price(price_str):
    if not price_str:
        return None
    match = re.search(r'[\d,]+\.?\d*', str(price_str).replace(',', ''))
    try:
        val = float(match.group(0))
        return val if 100 <= val <= 10000 else None
    except:
        return None

def scrape_page(query):
    encoded = query.replace(' ', '+')
    url = f"https://www.walmart.com/search?q={encoded}&cat_id=3944"
    proxy_url = get_scrapeops_url(url)
    print(f"  Requesting Walmart: {query}")

    try:
        resp = requests.get(proxy_url, timeout=120)
        resp.raise_for_status()
        print(f"  Response: {resp.status_code}, length={len(resp.text)}")

        # Save first query for debugging
        if 'RTX+4060' in encoded:
            try:
                s3 = boto3.client('s3')
                s3.put_object(
                    Bucket=os.getenv('S3_BUCKET', 'pcsorted-data'),
                    Key='debug/walmart_page.html',
                    Body=resp.text.encode('utf-8'),
                    ContentType='text/html'
                )
                print("  Saved Walmart HTML to S3")
            except Exception as e:
                print(f"  S3 save failed: {e}")

        return resp.text
    except Exception as e:
        print(f"  Walmart request failed for '{query}': {e}")
        return None

def parse_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    # Try multiple selectors
    cards = soup.select('[data-item-id]')
    print(f"  [data-item-id]: {len(cards)}")

    cards2 = soup.select('div[data-testid="item-stack"]')
    print(f"  [data-testid=item-stack]: {len(cards2)}")

    cards3 = soup.select('a[href*="/ip/"]')
    print(f"  a[href*=/ip/]: {len(cards3)}")

    cards4 = soup.select('[data-automation-id="product-price"]')
    print(f"  [data-automation-id=product-price]: {len(cards4)}")

    # Print first product link found
    for a in soup.select('a[href*="/ip/"]')[:3]:
        print(f"  Sample link: {a.get('href', '')[:80]}")
        print(f"  Sample text: {a.get_text(strip=True)[:60]}")

    print(f"  Parsed {len(items)} Walmart listings")
    return items

def scrape():
    all_items = []
    seen_urls = set()

    for query in SEARCH_QUERIES[:2]:  # Only run 2 queries for debug
        html = scrape_page(query)
        if not html:
            continue

        items = parse_listings(html)
        for item in items:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                all_items.append(item)

        time.sleep(random.uniform(3, 5))

    print(f"Walmart: scraped {len(all_items)} unique listings")
    return all_items