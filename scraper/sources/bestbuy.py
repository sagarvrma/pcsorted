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

CATEGORY_URLS = [
    "https://www.bestbuy.com/site/pc-gaming/gaming-desktops/pcmcat287600050002.c?cp=1",
    "https://www.bestbuy.com/site/pc-gaming/gaming-desktops/pcmcat287600050002.c?cp=2",
    "https://www.bestbuy.com/site/pc-gaming/gaming-desktops/pcmcat287600050002.c?cp=3",
    "https://www.bestbuy.com/site/pc-gaming/gaming-desktops/pcmcat287600050002.c?cp=4",
    "https://www.bestbuy.com/site/pc-gaming/gaming-desktops/pcmcat287600050002.c?cp=5",
]

def get_scrapeops_url(url):
    return f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={quote(url)}&render=true&render_wait=8000"

def clean_price(price_str):
    if not price_str:
        return None
    match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
    try:
        val = float(match.group(0))
        return val if 100 <= val <= 10000 else None
    except:
        return None

def scrape_page(url):
    proxy_url = get_scrapeops_url(url)
    print(f"  Requesting: {url}")

    try:
        resp = requests.get(proxy_url, timeout=120)
        resp.raise_for_status()
        print(f"  Response: {resp.status_code}, length={len(resp.text)}")

        if 'cp=1' in url:
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
        print(f"  BestBuy request failed for {url}: {e}")
        return None

def parse_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    cards = soup.select('li.product-list-item')
    real_cards = [c for c in cards if not c.select_one('.skeleton-product-grid-view')]
    print(f"  Found {len(cards)} cards, {len(real_cards)} real")

    for card in real_cards:
        try:
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

            price_text = card.find(string=re.compile(r'\$[\d,]+'))
            price = clean_price(str(price_text)) if price_text else None

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

    for url in CATEGORY_URLS:
        html = scrape_page(url)
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

        print(f"  Added {new_count} new listings")

        if not items:
            print("  No items — stopping pagination")
            break

        time.sleep(random.uniform(4, 7))

    print(f"Best Buy: scraped {len(all_items)} unique listings")
    return all_items