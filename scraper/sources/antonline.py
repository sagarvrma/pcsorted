import re
import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

SEARCH_URLS = [
    "https://www.antonline.com/Computers/Desktops",
    "https://www.antonline.com/Search?k=gaming+desktop&s=4",
    "https://www.antonline.com/Search?k=prebuilt+gaming+pc&s=4",
]

def clean_price(price_str):
    if not price_str:
        return None
    match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
    try:
        val = float(match.group(0))
        return val if 100 <= val <= 10000 else None
    except:
        return None

def extract_price(price_elem):
    if not price_elem:
        return None
    # Remove the MSRP strikethrough span first
    for msrp in price_elem.select('span[style*="line-through"]'):
        msrp.decompose()
    # Remove the "MSRP" label span
    for label in price_elem.select('span[style*="font-size:0.5em"]'):
        label.decompose()
    return clean_price(price_elem.get_text(strip=True))

def scrape():
    items = []
    seen_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        for search_url in SEARCH_URLS:
            try:
                print(f"  Scraping Antonline: {search_url}")
                page.goto(search_url, timeout=60000, wait_until='domcontentloaded')
                time.sleep(random.uniform(2, 3))

                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                for card in soup.select('article.product_card'):
                    try:
                        href = card.get('data-href', '')
                        if not href:
                            continue
                        clean_url = f"https://www.antonline.com{href}" if href.startswith('/') else href

                        if clean_url in seen_urls:
                            continue
                        seen_urls.add(clean_url)

                        # Title from h2.title
                        title_elem = card.select_one('h2.title')
                        title = title_elem.get_text(strip=True) if title_elem else None
                        if not title:
                            # Fallback to img alt
                            imgs = card.select('img')
                            for img in imgs:
                                alt = img.get('alt', '')
                                if len(alt) > 20:
                                    title = alt
                                    break
                        if not title:
                            continue

                        # Price from h3.price
                        price_elem = card.select_one('h3.price')
                        price = extract_price(price_elem)

                        # Image — skip badge images, get product image
                        image_url = None
                        imgs = card.select('img')
                        for img in imgs:
                            src = img.get('src', '')
                            if 'Badge' not in src and 'badge' not in src:
                                image_url = src
                                break

                        items.append({
                            'external_id': href.split('/')[-1],
                            'title': title,
                            'url': clean_url,
                            'image_url': image_url,
                            'price': price,
                            'in_stock': True,
                        })

                    except Exception as e:
                        continue

                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"  Antonline failed for {search_url}: {e}")
                continue

        browser.close()

    print(f"Antonline: scraped {len(items)} unique listings")
    return items