import time
import random
import pandas as pd
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# ============================================================
# MICRO-TEST CONFIG: Set to True for full run, False for test
# ============================================================
MICRO_TEST = False
MICRO_TEST_LIMIT = 5  # Stop after this many leads

def scrape_google_maps():
    if MICRO_TEST:
        locations = ['Nashik']
        categories = ['international school']
        print("[MICRO-TEST MODE] Running with 1 location, 1 category, limit 5 leads.\n")
    else:
        # UPDATED FOR BYTCO HYPER-LOCAL SCRAPE
        locations = ['Bytco Point, Nashik Road', 'Bytco College, Nashik Road', 'Muktidham, Nashik Road']
        categories = [
            'specialty coffee shop', 'cafe', 'lounge', 'restro bar', 
            'unisex salon', 'nail salon', 'aesthetic clinic', 
            'pilates studio', 'crossfit', 'coworking space'
        ]
        print(f"Starting Hyper-local Scrape for {len(locations)} locations and {len(categories)} categories...")
    
    results = []
    total_extracted = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Correctly apply stealth
        stealth_obj = Stealth()
        stealth_obj.use_sync(page)
        
        for location in locations:
            for category in categories:
                if MICRO_TEST and total_extracted >= MICRO_TEST_LIMIT:
                    break

                # Fixed URL Format
                category_query = category.replace(' ', '+')
                location_query = location.replace(' ', '+')
                search_url = f'https://www.google.com/maps/search/{category_query}+in+{location_query}'
                
                print(f"\n--- Searching: {category} in {location} ---")
                
                try:
                    page.goto(search_url, timeout=60000)
                    
                    # Cookie Consent Handler
                    try:
                        consent_btn = page.locator('button:has-text("Accept all"), button:has-text("I agree"), button:has-text("Accept")').first
                        if consent_btn.count() > 0:
                            consent_btn.click(timeout=3000)
                            time.sleep(random.uniform(1, 2))
                    except Exception:
                        pass
                    
                    time.sleep(random.uniform(5, 8))
                except Exception as e:
                    print(f"Failed to load search results: {e}")
                    continue
                
                try:
                    page.wait_for_selector('div[role="feed"]', timeout=20000)
                    feed_element = page.locator('div[role="feed"]')
                except Exception:
                    print(f"No results feed found for {category} in {location}.")
                    continue
                
                # Dynamic Scrolling
                print(f"Scrolling for leads...")
                max_scrolls = 20 # Reduced for hyper-local focus
                target_listings = 50
                
                for _ in range(max_scrolls):
                    feed_element.hover()
                    page.mouse.wheel(delta_x=0, delta_y=random.randint(800, 1200))
                    time.sleep(random.uniform(2, 3))
                    current_count = page.locator('a[href*="/maps/place/"]').count()
                    if current_count >= target_listings:
                        break
                
                time.sleep(2)
                
                # Extraction
                cards = page.locator('a[href*="/maps/place/"]').all()
                listing_urls = [card.get_attribute('href') for card in cards if card.get_attribute('href')]
                
                print(f"Found {len(listing_urls)} potential leads. Extracting details...")

                prev_h1_text = ""

                for url in listing_urls:
                    if MICRO_TEST and total_extracted >= MICRO_TEST_LIMIT:
                        break

                    try:
                        time.sleep(random.uniform(3, 5))
                        page.goto(url, timeout=30000)
                        
                        # Wait for title
                        try:
                            page.wait_for_selector('h1.DUwDvf', timeout=10000)
                        except Exception:
                            continue

                        current_h1 = ""
                        try:
                            h1_el = page.locator('h1.DUwDvf').first
                            if h1_el.count() > 0:
                                current_h1 = h1_el.inner_text(timeout=3000)
                        except Exception:
                            pass

                        if current_h1 and current_h1 == prev_h1_text:
                            time.sleep(3)
                            current_h1 = page.locator('h1.DUwDvf').first.inner_text(timeout=3000)

                        prev_h1_text = current_h1
                        
                        name = current_h1 or "N/A"
                        rating = "N/A"
                        reviews = "N/A"
                        website = "N/A"
                        phone = "N/A"
                        
                        # Rating & Reviews
                        try:
                            rating_el = page.locator('div.F7nice span[aria-hidden="true"]').first
                            if rating_el.count() > 0:
                                rating = rating_el.inner_text(timeout=2000)
                            
                            review_el = page.locator('span[aria-label*="review"]').first
                            if review_el.count() > 0:
                                review_aria = review_el.get_attribute('aria-label', timeout=2000)
                                if review_aria:
                                    reviews = review_aria.split(' ')[0].replace(',', '')
                        except Exception:
                            pass
                            
                        # Website
                        try:
                            website_el = page.locator('a[data-item-id="authority"]').first
                            if website_el.count() > 0:
                                website = website_el.get_attribute('href', timeout=2000) or "N/A"
                        except Exception:
                            pass
                            
                        # Phone
                        try:
                            phone_el = page.locator('button[data-item-id*="phone"]').first
                            if phone_el.count() > 0:
                                phone_aria = phone_el.get_attribute('aria-label', timeout=2000)
                                if phone_aria and 'Phone:' in phone_aria:
                                    phone = phone_aria.replace('Phone:', '').strip()
                        except Exception:
                            pass
                            
                        if name != "N/A":
                            results.append({
                                'Location': location, 'Category': category,
                                'Business Name': name, 'Phone Number': phone,
                                'Website URL': website, 'Rating': rating, 'Review Count': reviews
                            })
                            total_extracted += 1
                            print(f"  [{total_extracted}] ✅ {name} ({rating} stars, {reviews} reviews)")
                    except Exception as e:
                        print(f"Error: {e}")
                        continue

            if MICRO_TEST and total_extracted >= MICRO_TEST_LIMIT:
                break
                        
        browser.close()
        
    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['Business Name', 'Phone Number'], keep='first')
        df.to_csv('data/bytco_modern_leads_raw.csv', index=False, encoding='utf-8-sig')
        print(f"\n--- SCRAPE COMPLETE! {len(df)} High-ticket leads saved to data/bytco_modern_leads_raw.csv ---")
    else:
        print("\n--- No leads found. ---")

if __name__ == "__main__":
    scrape_google_maps()
