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
    "prebuilt gaming computer",
    "CyberPowerPC gaming desktop",
    "iBUYPOWER gaming desktop",
    "gaming PC tower",
]

def get_scrapeops_url(url):
    # render_wait=5000 tells ScrapeOps to wait 5 seconds after page load
    return f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={quote(url)}&render=true&render_wait=5000"

def clean_price(price_str):
    if not price_str:
        return None
    match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
    try:
        val = float(match.group(0))
        return val if 100 <= val <= 10000 else None
    except:
        return None

def scrape_page(query, page=1):
    url = f"https://www.bestbuy.com/site/searchpage.jsp?st={query.replace(' ', '+')}&cp={page}"
    proxy_url = get_scrapeops_url(url)
    print(f"  Requesting: {url}")

    try:
        resp = requests.get(proxy_url, timeout=120)
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

    cards = soup.select('li.product-list-item')
    print(f"  Found {len(cards)} product cards")

    for card in cards:
        try:
            # Skip skeleton/loading placeholder cards
            if card.select_one('.skeleton-product-grid-view'):
                continue

            link_elem = card.select_one('a.product-list-item-link')
            title_elem = card.select_one('h3.product-title')

            if not link_elem or not title_elem:
                continue

            href = link_elem.get('href', '')
            url = f"https://www.bestbuy.com{href}" if href.startswith('/') else href
            base_url = url.split('?')[0]

            title = title_elem.get('title') or title_elem.get_text(strip=True)
            if not title or len(title) < 10:
                continue

            # Price — find dollar amount in card
            price = None
            price_text = card.find(string=re.compile(r'\$[\d,]+'))
            if price_text:
                price = clean_price(str(price_text))

            # Image
            img_elem = card.select_one('img')
            image_url = img_elem.get('src') if img_elem else None

            items.append({
                'external_id': href.rstrip('/').split('/')[-1],
                'title': title,
                'url': base_url,
                'image_url': image_url,
                'price': price,
                'in_stock': True,
            })

        except Exception as e:
            continue

    print(f"  Parsed {len(items)} valid listings")
    return items

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
                print(f"  Captcha detected for '{query}' page {page}, skipping")
                break

            items = parse_listings(html)
            if not items:
                print(f"  No items parsed for '{query}' page {page}")
                break

            for item in items:
                if item['url'] not in seen_urls:
                    seen_urls.add(item['url'])
                    all_items.append(item)

            time.sleep(random.uniform(3, 6))

        time.sleep(random.uniform(4, 7))

    print(f"Best Buy: scraped {len(all_items)} unique listings")
    return all_items