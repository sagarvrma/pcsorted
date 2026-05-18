import re
import time
import random
import os
import requests
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
    return f"https://proxy.scrapeops.io/v1/?api_key={SCRAPEOPS_KEY}&url={url}&render=true"

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

    try:
        resp = requests.get(proxy_url, timeout=60)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  BestBuy request failed for '{query}' page {page}: {e}")
        return None

def parse_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    for card in soup.select('li.sku-item'):
        try:
            title_elem = card.select_one('.sku-title a')
            price_elem = card.select_one('.priceView-customer-price span')
            img_elem = card.select_one('.product-image img')

            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            href = title_elem.get('href', '')
            url = f"https://www.bestbuy.com{href}" if href.startswith('/') else href

            price = clean_price(price_elem.get_text(strip=True)) if price_elem else None
            image_url = img_elem.get('src') if img_elem else None

            add_to_cart = card.select_one('.add-to-cart-button')
            in_stock = add_to_cart is not None and 'sold-out' not in str(add_to_cart).lower()

            items.append({
                'external_id': url.split('/')[-1].split('.')[0],
                'title': title,
                'url': url,
                'image_url': image_url,
                'price': price,
                'in_stock': in_stock,
            })

        except Exception as e:
            continue

    return items

def scrape():
    all_items = []
    seen_urls = set()

    # Debug: dump first page to S3 raw folder via print for CI inspection
    first_html = scrape_page("gaming desktop RTX 4060", 1)
    if first_html:
        print(f"  DEBUG: Got HTML length={len(first_html)}")
        # Check if we got actual product data or a blocked page
        if 'sku-item' in first_html:
            print("  DEBUG: Found sku-item elements")
        elif 'captcha' in first_html.lower():
            print("  DEBUG: Got captcha page")
        elif 'access denied' in first_html.lower():
            print("  DEBUG: Got access denied")
        else:
            # Print first 500 chars of body to see what we got
            from bs4 import BeautifulSoup as BS
            soup = BS(first_html, 'html.parser')
            body = soup.find('body')
            if body:
                print(f"  DEBUG: Body preview: {body.get_text()[:300]}")
    else:
        print("  DEBUG: Got no HTML at all")

    for query in SEARCH_QUERIES:
        print(f"  Scraping Best Buy: {query}")
        for page in range(1, 4):
            html = scrape_page(query, page)
            if not html:
                break

            items = parse_listings(html)
            if not items:
                break

            for item in items:
                if item['url'] not in seen_urls:
                    seen_urls.add(item['url'])
                    all_items.append(item)

            time.sleep(random.uniform(2, 4))

        time.sleep(random.uniform(3, 5))

    print(f"Best Buy: scraped {len(all_items)} unique listings")
    return all_items