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
    return f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={quote(url)}&render=true"

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

        # Save first RTX 4060 page HTML to S3 for inspection
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

    # Try different selectors for Best Buy's current HTML
    cards = soup.select('li.sku-item')
    if not cards:
        cards = soup.select('[class*="sku-item"]')
    if not cards:
        cards = soup.select('li[class*="product"]')
    if not cards:
        # Last resort — find all li elements containing product links
        cards = [li for li in soup.find_all('li') 
                 if li.find('a', href=lambda h: h and '/product/' in str(h))]

    print(f"  Found {len(cards)} product cards")

    for card in cards:
        try:
            # Find product link
            link_elem = card.find('a', href=lambda h: h and '/product/' in str(h))
            if not link_elem:
                continue

            title = link_elem.get_text(strip=True)
            href = link_elem.get('href', '')
            url = f"https://www.bestbuy.com{href}" if href.startswith('/') else href

            # Price — look for any element with dollar amount
            price_elem = card.find(string=re.compile(r'\$[\d,]+'))
            price = clean_price(str(price_elem)) if price_elem else None

            # Image
            img_elem = card.find('img')
            image_url = img_elem.get('src') if img_elem else None

            if not title or len(title) < 10:
                continue

            items.append({
                'external_id': href.split('/')[-1],
                'title': title,
                'url': url,
                'image_url': image_url,
                'price': price,
                'in_stock': True,
            })

        except Exception as e:
            continue

    return items

def scrape():
    all_items = []
    seen_urls = set()

    print(f"  SCRAPEOPS_KEY set: {bool(SCRAPEOPS_KEY)}")

    # Debug first page
    first_html = scrape_page("gaming desktop RTX 4060", 1)
    if first_html:
        print(f"  DEBUG: Got HTML length={len(first_html)}")
        if 'sku-item' in first_html:
            print("  DEBUG: Found sku-item elements — selectors should work")
        elif 'captcha' in first_html.lower():
            print("  DEBUG: Got captcha page")
        elif 'access denied' in first_html.lower():
            print("  DEBUG: Got access denied")
        else:
            soup = BeautifulSoup(first_html, 'html.parser')
            body = soup.find('body')
            if body:
                print(f"  DEBUG: Body preview: {body.get_text()[:500]}")
    else:
        print("  DEBUG: Got no HTML at all — request failed")
        return []

    for query in SEARCH_QUERIES:
        print(f"  Scraping Best Buy: {query}")
        for page in range(1, 4):
            html = scrape_page(query, page)
            if not html:
                break

            items = parse_listings(html)
            if not items:
                print(f"  No items parsed for '{query}' page {page}")
                break

            for item in items:
                if item['url'] not in seen_urls:
                    seen_urls.add(item['url'])
                    all_items.append(item)

            time.sleep(random.uniform(2, 4))

        time.sleep(random.uniform(3, 5))

    print(f"Best Buy: scraped {len(all_items)} unique listings")
    return all_items