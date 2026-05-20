import re
import time
import random
import os
import requests
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
    "prebuilt gaming desktop AMD",
    "gaming desktop RX 7800",
    "gaming desktop RX 7900",
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
    url = f"https://www.newegg.com/p/pl?d={encoded}&N=4131"
    proxy_url = get_scrapeops_url(url)
    print(f"  Requesting Newegg: {query}")

    try:
        resp = requests.get(proxy_url, timeout=120)
        resp.raise_for_status()
        print(f"  Response: {resp.status_code}, length={len(resp.text)}")
        return resp.text
    except Exception as e:
        print(f"  Newegg request failed for '{query}': {e}")
        return None

def parse_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    # Newegg product cells
    cards = soup.select('.item-cell')
    print(f"  Found {len(cards)} Newegg cards")

    for card in cards:
        try:
            title_elem = card.select_one('.item-title')
            price_elem = card.select_one('.price-current')
            link_elem = card.select_one('a.item-title')
            img_elem = card.select_one('.item-img img')

            if not title_elem or not link_elem:
                continue

            title = title_elem.get_text(strip=True)
            href = link_elem.get('href', '')
            url = href if href.startswith('http') else f"https://www.newegg.com{href}"
            base_url = url.split('?')[0]

            price = clean_price(price_elem.get_text(strip=True)) if price_elem else None

            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')

            if not title or len(title) < 10:
                continue

            items.append({
                'external_id': base_url.split('/')[-1],
                'title': title,
                'url': base_url,
                'image_url': image_url,
                'price': price,
                'in_stock': True,
            })

        except Exception as e:
            continue

    print(f"  Parsed {len(items)} Newegg listings")
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
        print(f"  Added {new_count} new Newegg listings")

        time.sleep(random.uniform(3, 5))

    print(f"Newegg: scraped {len(all_items)} unique listings")
    return all_items