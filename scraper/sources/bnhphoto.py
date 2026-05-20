import re
import time
import random
import requests
from bs4 import BeautifulSoup

SEARCH_URLS = [
    "https://www.bhphotovideo.com/c/search?Ntt=gaming+desktop+RTX+4060&N=4294539008",
    "https://www.bhphotovideo.com/c/search?Ntt=gaming+desktop+RTX+4070&N=4294539008",
    "https://www.bhphotovideo.com/c/search?Ntt=gaming+desktop+RTX+4080&N=4294539008",
    "https://www.bhphotovideo.com/c/search?Ntt=gaming+desktop+RTX+3070&N=4294539008",
    "https://www.bhphotovideo.com/c/search?Ntt=gaming+desktop+RTX+5070&N=4294539008",
    "https://www.bhphotovideo.com/c/search?Ntt=CyberPowerPC+desktop&N=4294539008",
    "https://www.bhphotovideo.com/c/search?Ntt=iBUYPOWER+desktop&N=4294539008",
    "https://www.bhphotovideo.com/c/search?Ntt=gaming+desktop+RX+7800&N=4294539008",
]

def clean_price(price_str):
    if not price_str:
        return None
    match = re.search(r'[\d,]+\.?\d*', str(price_str).replace(',', ''))
    try:
        val = float(match.group(0))
        return val if 100 <= val <= 10000 else None
    except:
        return None

def scrape_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    print(f"  Requesting B&H: {url.split('Ntt=')[1].split('&')[0].replace('+', ' ')}")
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        print(f"  Response: {resp.status_code}, length={len(resp.text)}")
        return resp.text
    except Exception as e:
        print(f"  B&H request failed: {e}")
        return None

def parse_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    cards = soup.select('[data-selenium="miniProductPage"]')
    if not cards:
        cards = soup.select('.productNameContainer, [class*="product-name"]')
    print(f"  Found {len(cards)} B&H cards")

    for card in cards:
        try:
            link_elem = card.select_one('a[href*="/c/product"]') or card.select_one('a')
            title_elem = card.select_one('[data-selenium="productName"], h3, .name')
            price_elem = card.select_one('[data-selenium="price"], .price')

            if not link_elem or not title_elem:
                continue

            href = link_elem.get('href', '')
            url = f"https://www.bhphotovideo.com{href}" if href.startswith('/') else href
            base_url = url.split('?')[0]

            title = title_elem.get_text(strip=True)
            if not title or len(title) < 10:
                continue

            price = clean_price(price_elem.get_text(strip=True)) if price_elem else None

            img_elem = card.select_one('img')
            image_url = img_elem.get('src') if img_elem else None

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

    print(f"  Parsed {len(items)} B&H listings")
    return items

def scrape():
    all_items = []
    seen_urls = set()

    for url in SEARCH_URLS:
        html = scrape_page(url)
        if not html:
            continue

        items = parse_listings(html)
        new_count = 0
        for item in items:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                all_items.append(item)
                new_count += 1
        print(f"  Added {new_count} new B&H listings")

        time.sleep(random.uniform(2, 4))

    print(f"B&H: scraped {len(all_items)} unique listings")
    return all_items