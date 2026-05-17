import re
import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

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

def scrape():
    items = []
    seen_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)

        for query in SEARCH_QUERIES:
            encoded = query.replace(' ', '+')
            url = f"https://www.ebay.com/sch/i.html?_nkw={encoded}&_sacat=179&_sop=12&_ipg=60"

            try:
                print(f"  Scraping eBay: {query}")
                page.goto(url, timeout=60000, wait_until='domcontentloaded')

                time.sleep(random.uniform(2, 4))

                try:
                    page.wait_for_selector('.s-item', timeout=10000)
                except:
                    print(f"  No results for: {query}")
                    continue

                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                for card in soup.select('li.s-item'):
                    try:
                        title_elem = card.select_one('.s-item__title')
                        price_elem = card.select_one('.s-item__price')
                        link_elem = card.select_one('a.s-item__link')
                        img_elem = card.select_one('.s-item__image img')

                        if not all([title_elem, price_elem, link_elem]):
                            continue

                        title = title_elem.get_text(strip=True)

                        if 'Shop on eBay' in title:
                            continue

                        url_link = link_elem.get('href', '')
                        clean_url = url_link.split('?')[0] if '?' in url_link else url_link

                        if clean_url in seen_urls:
                            continue
                        seen_urls.add(clean_url)

                        price = clean_price(price_elem.get_text(strip=True))
                        if not price:
                            continue

                        image_url = None
                        if img_elem:
                            image_url = img_elem.get('src') or img_elem.get('data-src')
                            if image_url and 'placeholder' in image_url.lower():
                                image_url = None

                        items.append({
                            'external_id': clean_url.split('/')[-1],
                            'title': title,
                            'url': clean_url,
                            'image_url': image_url,
                            'price': price,
                            'in_stock': True,
                        })

                    except Exception as e:
                        continue

                time.sleep(random.uniform(3, 6))

            except Exception as e:
                print(f"  eBay query failed for '{query}': {e}")
                continue

        browser.close()

    print(f"eBay: scraped {len(items)} unique listings")
    return items