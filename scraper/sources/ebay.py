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
    "prebuilt gaming pc RTX 4060",
    "prebuilt gaming pc RTX 4070",
    "prebuilt gaming pc RTX 4080",
    "prebuilt gaming pc RTX 3060",
    "prebuilt gaming pc RTX 3070",
    "prebuilt gaming pc RTX 3080",
    "prebuilt desktop computer i7",
    "prebuilt desktop computer i5",
    "gaming desktop CyberPowerPC",
    "gaming desktop iBUYPOWER",
    "prebuilt gaming pc RX 7800",
    "prebuilt gaming pc RX 6700",
    "gaming desktop RTX 4060",
    "gaming desktop RTX 4070",
    "gaming desktop RTX 5070",
    "gaming desktop RTX 5060",
]

def get_scrapeops_url(url):
    return f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={quote(url)}&render=true&render_wait=3000"

def clean_price(price_str):
    if not price_str:
        return None
    match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
    try:
        val = float(match.group(0))
        return val if 100 <= val <= 10000 else None
    except:
        return None

def scrape_page(query):
    encoded = query.replace(' ', '+')
    url = f"https://www.ebay.com/sch/i.html?_nkw={encoded}&_sacat=179&_sop=12&_ipg=60"
    proxy_url = get_scrapeops_url(url)
    print(f"  Requesting eBay: {query}")

    try:
        resp = requests.get(proxy_url, timeout=120)
        resp.raise_for_status()
        print(f"  Response: {resp.status_code}, length={len(resp.text)}")

        if 'RTX+4060' in encoded:
            try:
                s3 = boto3.client('s3')
                s3.put_object(
                    Bucket=os.getenv('S3_BUCKET', 'pcsorted-data'),
                    Key='debug/ebay_page.html',
                    Body=resp.text.encode('utf-8'),
                    ContentType='text/html'
                )
                print("  Saved eBay HTML to S3")
            except Exception as e:
                print(f"  S3 save failed: {e}")

        return resp.text
    except Exception as e:
        print(f"  eBay request failed for '{query}': {e}")
        return None

def parse_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    cards = soup.select('li.s-card')
    print(f"  Found {len(cards)} eBay cards")

    for card in cards:
        try:
            link_elem = card.select_one('a.s-card__link')
            img_elem = card.select_one('img.s-card__image')

            if not link_elem:
                continue

            href = link_elem.get('href', '')
            clean_url = href.split('?')[0] if '?' in href else href
            if not clean_url or 'ebay.com' not in clean_url:
                clean_url = f"https://www.ebay.com{href}" if href.startswith('/') else href

            # Title from img alt text
            title = img_elem.get('alt', '') if img_elem else ''
            if not title or len(title) < 10:
                continue

            if 'Shop on eBay' in title:
                continue

            # Price
            price_text = card.find(string=re.compile(r'\$[\d,]+'))
            price = clean_price(str(price_text)) if price_text else None
            if not price:
                continue

            image_url = img_elem.get('src') if img_elem else None

            items.append({
                'external_id': clean_url.split('/')[-1],
                'title': title,
                'url': clean_url.split('?')[0],
                'image_url': image_url,
                'price': price,
                'in_stock': True,
            })

        except Exception as e:
            continue

    print(f"  Parsed {len(items)} valid eBay listings")
    return items

def scrape():
    all_items = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        html = scrape_page(query)
        if not html:
            continue

        if 'captcha' in html.lower() and len(html) < 50000:
            print(f"  Captcha detected for '{query}', skipping")
            continue

        items = parse_listings(html)
        new_count = 0
        for item in items:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                all_items.append(item)
                new_count += 1
        print(f"  Added {new_count} new eBay listings")

        time.sleep(random.uniform(2, 4))

    print(f"eBay: scraped {len(all_items)} unique listings")
    return all_items