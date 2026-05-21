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
    "CyberPowerPC gaming desktop",
    "iBUYPOWER gaming desktop",
    "gaming desktop RTX 4060",
    "gaming desktop RTX 4070",
    "gaming desktop RTX 4080",
    "gaming desktop RTX 3060",
    "gaming desktop RTX 3070",
    "gaming desktop RTX 5070",
    "gaming desktop RTX 5060",
    "prebuilt gaming PC tower",
    "gaming desktop AMD Ryzen",
    "gaming desktop RX 7800",
]

def get_scrapeops_url(url):
    return f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={quote(url)}&render=true&render_wait=5000"

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

        if 'CyberPowerPC' in query:
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
    seen_urls = set()

    # Only grab real product links: /ip/product-name/12345678
    product_links = [
        a for a in soup.select('a[href*="/ip/"]')
        if re.search(r'/ip/.+/\d+', a.get('href', ''))
    ]
    print(f"  Found {len(product_links)} real product links")

    for link in product_links:
        try:
            href = link.get('href', '')
            url = f"https://www.walmart.com{href}" if href.startswith('/') else href
            base_url = url.split('?')[0]

            if base_url in seen_urls:
                continue
            seen_urls.add(base_url)

            # Extract product ID from URL
            m = re.search(r'/ip/.+/(\d+)', base_url)
            product_id = m.group(1) if m else base_url.split('/')[-1]

            # Title from img alt or aria-label
            img = link.find('img')
            title = ''
            if img:
                title = img.get('alt', '')
            if not title:
                title = link.get('aria-label', '')
            if not title:
                title = link.get_text(strip=True)
            if not title or len(title) < 10:
                continue

            # Skip nav/category links
            if any(s in title.lower() for s in ['shop all', 'browse', 'view all', 'see all']):
                continue

            # Price
            price = None
            parent = link.parent
            for _ in range(8):
                if parent is None:
                    break
                price_text = parent.find(string=re.compile(r'\$[\d,]+\.?\d*'))
                if price_text:
                    price = clean_price(str(price_text))
                    if price:
                        break
                parent = parent.parent

            image_url = img.get('src') if img else None

            items.append({
                'external_id': product_id,
                'title': title,
                'url': base_url,
                'image_url': image_url,
                'price': price,
                'in_stock': True,
            })

        except Exception as e:
            continue

    print(f"  Parsed {len(items)} Walmart listings")
    return items

def scrape():
    all_items = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        html = scrape_page(query)
        if not html:
            continue

        if 'captcha' in html.lower() and len(html) < 50000:
            print(f"  Captcha detected, skipping")
            continue

        items = parse_listings(html)
        new_count = 0
        for item in items:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                all_items.append(item)
                new_count += 1
        print(f"  Added {new_count} new Walmart listings")

        time.sleep(random.uniform(3, 5))

    print(f"Walmart: scraped {len(all_items)} unique listings")
    return all_items