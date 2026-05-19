import re
import time
import random
import os
import requests
import boto3
import json
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
    "prebuilt gaming computer",
    "CyberPowerPC gaming desktop",
    "iBUYPOWER gaming desktop",
    "gaming PC tower",
]

def get_scrapeops_url(url):
    return f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={quote(url)}&render=false"

def clean_price(price):
    if not price:
        return None
    try:
        val = float(str(price).replace(',', '').replace('$', ''))
        return val if 100 <= val <= 10000 else None
    except:
        return None

def scrape_page(query, page=1):
    url = f"https://www.bestbuy.com/site/searchpage.jsp?st={query.replace(' ', '+')}&cp={page}"
    proxy_url = get_scrapeops_url(url)
    print(f"  Requesting: {url}")

    try:
        resp = requests.get(proxy_url, timeout=60)
        resp.raise_for_status()
        print(f"  Response: {resp.status_code}, length={len(resp.text)}")

        if page == 1 and 'RTX+4060' in url:
            try:
                s3 = boto3.client('s3')
                bucket = os.getenv('S3_BUCKET', 'pcsorted-data')
                s3.put_object(
                    Bucket=bucket,
                    Key='debug/bestbuy_page.html',
                    Body=resp.text.encode('utf-8'),
                    ContentType='text/html'
                )
                print("  Saved HTML to S3 debug/bestbuy_page.html")
            except Exception as e:
                print(f"  S3 save failed: {e}")

        return resp.text
    except Exception as e:
        print(f"  BestBuy request failed for '{query}' page {page}: {e}")
        return None

def parse_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    # Extract JSON from script tags
    scripts = soup.find_all('script', type='application/json')
    print(f"  Found {len(scripts)} JSON script tags")

    all_products = []

    for script in scripts:
        try:
            data = json.loads(script.string)
            # Recursively find product arrays
            find_products(data, all_products)
        except:
            continue

    print(f"  Found {len(all_products)} products in JSON")

    for product in all_products:
        try:
            name = product.get('name') or product.get('title')
            sku = str(product.get('sku') or product.get('skuId') or '')
            price = clean_price(product.get('regularPrice') or product.get('salePrice') or product.get('currentPrice'))
            image = product.get('image') or product.get('thumbnailImage')
            if not name or not sku or not price:
                continue
            url = f"https://www.bestbuy.com/site/{sku}.p?skuId={sku}"

            items.append({
                'external_id': sku,
                'title': name,
                'url': url,
                'image_url': image,
                'price': price,
                'in_stock': product.get('inStoreAvailability', True),
            })
        except:
            continue

    # Fallback to CSS selectors if JSON parsing found nothing
    if not items:
        print("  JSON parsing found nothing, trying CSS selectors")
        cards = soup.select('li.product-list-item')
        real_cards = [c for c in cards if not c.select_one('.skeleton-product-grid-view')]
        print(f"  Found {len(real_cards)} real cards via CSS")
        for card in real_cards:
            try:
                link_elem = card.select_one('a.product-list-item-link')
                title_elem = card.select_one('h3.product-title')
                if not link_elem or not title_elem:
                    continue
                href = link_elem.get('href', '')
                url = f"https://www.bestbuy.com{href}" if href.startswith('/') else href
                title = title_elem.get('title') or title_elem.get_text(strip=True)
                price_text = card.find(string=re.compile(r'\$[\d,]+'))
                price = clean_price(str(price_text)) if price_text else None
                img_elem = card.select_one('img')
                image_url = img_elem.get('src') if img_elem else None
                if not title or len(title) < 10:
                    continue
                items.append({
                    'external_id': href.rstrip('/').split('/')[-1],
                    'title': title,
                    'url': url.split('?')[0],
                    'image_url': image_url,
                    'price': price,
                    'in_stock': True,
                })
            except:
                continue

    print(f"  Parsed {len(items)} valid listings")
    return items

def find_products(data, results, depth=0):
    if depth > 10:
        return
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and ('sku' in item or 'skuId' in item) and ('name' in item or 'title' in item):
                results.append(item)
            else:
                find_products(item, results, depth + 1)
    elif isinstance(data, dict):
        if ('sku' in data or 'skuId' in data) and ('name' in data or 'title' in data):
            results.append(data)
        else:
            for val in data.values():
                find_products(val, results, depth + 1)

def scrape():
    all_items = []
    seen_urls = set()

    print(f"  SCRAPEOPS_KEY set: {bool(SCRAPEOPS_KEY)}")

    for query in SEARCH_QUERIES:
        print(f"  Scraping Best Buy: {query}")
        for page in range(1, 3):
            html = scrape_page(query, page)
            if not html:
                break

            if 'captcha' in html.lower() and len(html) < 50000:
                print(f"  Captcha detected, skipping")
                break

            items = parse_listings(html)
            if not items:
                print(f"  No items for '{query}' page {page}")
                break

            for item in items:
                if item['url'] not in seen_urls:
                    seen_urls.add(item['url'])
                    all_items.append(item)

            time.sleep(random.uniform(2, 4))

        time.sleep(random.uniform(3, 5))

    print(f"Best Buy: scraped {len(all_items)} unique listings")
    return all_items