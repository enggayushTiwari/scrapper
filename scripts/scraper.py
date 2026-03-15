import time
import random
import pandas as pd
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# ============================================================
# MICRO-TEST CONFIG: Set to True for full run, False for test
# ============================================================
MICRO_TEST = False
MICRO_TEST_LIMIT = 3  # Stop after this many leads

def scrape_google_maps():
    if MICRO_TEST:
        locations = ['Nashik']
        categories = ['international school']
        print("[MICRO-TEST MODE] Running with 1 location, 1 category, limit 3 leads.\n")
    else:
        locations = ['Nashik Road']
        categories = [
            # Food & Cafe (Owner is usually on-site, needs high visual appeal)
            'cafe', 'restro bar', 'fine dining restaurant', 'premium bakery', 'specialty coffee shop',

            # Independent Healthcare (Solo practitioners with high patient value)
            'dentist', 'physiotherapist', 'chiropractor', 'homeopathy clinic', 'veterinary clinic',
            
            # Aesthetics & Grooming (High competition, instant decisions)
            'premium salon', 'unisex salon', 'tattoo studio', 'bridal makeup studio', 'nail bar',
            
            # Automotive (High ticket, single owner)
            'car detailing studio', 'ceramic coating', 'premium bike modification', 'used car dealer',
            
            # Solo Professional Services
            'chartered accountant', 'tax consultant', 'interior designer', 'boutique architect',
            
            # Boutique Retail
            'designer boutique', 'pet shop', 'custom jewelry designer', 'modular furniture studio',
            
            # Fitness
            'crossfit box', 'yoga studio', 'martial arts academy'
        ]
    
    results = []
    total_extracted = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Correctly apply stealth for playwright-stealth 2.0.2
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
                
                print(f"\n--- Navigating to: {search_url} ---")
                
                try:
                    page.goto(search_url, timeout=60000)
                    
                    # Cookie Consent Handler
                    try:
                        consent_btn = page.locator('button:has-text("Accept all"), button:has-text("I agree"), button:has-text("Accept")').first
                        if consent_btn.count() > 0:
                            print("Handling cookie consent overlay...")
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
                    print(f"Could not find the results feed for {category} in {location}.")
                    continue
                
                # Dynamic Scrolling
                print(f"Scrolling for {category} in {location}...")
                max_scrolls = 60
                target_listings = 120  # Google Maps typically caps a single search scroll at around 120 listings
                
                for _ in range(max_scrolls):
                    feed_element.hover()
                    page.mouse.wheel(delta_x=0, delta_y=random.randint(800, 1200))
                    time.sleep(random.uniform(2, 4))
                    current_count = page.locator('a[href*="/maps/place/"]').count()
                    if current_count >= target_listings:
                        break
                
                time.sleep(random.uniform(3, 5))
                
                # Extraction
                cards = page.locator('a[href*="/maps/place/"]').all()
                listing_urls = [card.get_attribute('href') for card in cards if card.get_attribute('href')]
                
                print(f"Extracting data for up to {len(listing_urls)} listings...")

                # Track the previous h1 text to detect stale reads
                prev_h1_text = ""

                for url in listing_urls:
                    if MICRO_TEST and total_extracted >= MICRO_TEST_LIMIT:
                        print(f"[MICRO-TEST] Reached limit of {MICRO_TEST_LIMIT} leads. Stopping.")
                        break

                    try:
                        time.sleep(random.uniform(3, 6))
                        page.goto(url, timeout=30000)
                        
                        # Check for popups again on detail view
                        try:
                            consent_btn = page.locator('button:has-text("Accept all"), button:has-text("I agree"), button:has-text("Accept")').first
                            if consent_btn.count() > 0: consent_btn.click(timeout=2000)
                        except Exception: pass

                        # ============================================================
                        # FIX 1: STRICT WAIT — Wait for the h1 title to fully render
                        # and change from the previous listing's title.
                        # This prevents reading stale data from the prior page.
                        # ============================================================
                        try:
                            page.wait_for_selector('h1.DUwDvf', timeout=10000)
                        except Exception:
                            # Fallback: wait for any h1
                            try:
                                page.wait_for_selector('h1', timeout=5000)
                            except Exception:
                                print(f"  [SKIP] h1 title never appeared for {url[:60]}...")
                                continue

                        # Extra wait for all DOM elements to settle
                        time.sleep(random.uniform(2, 3))

                        # Verify h1 has actually changed (anti-stale-read)
                        current_h1 = ""
                        try:
                            h1_el = page.locator('h1.DUwDvf').first
                            if h1_el.count() > 0:
                                current_h1 = h1_el.inner_text(timeout=3000)
                        except Exception:
                            pass

                        if current_h1 and current_h1 == prev_h1_text:
                            # Same h1 as last listing — page didn't update. Wait more.
                            print(f"  [STALE] h1 unchanged ('{current_h1[:40]}'). Waiting extra...")
                            time.sleep(3)
                            try:
                                current_h1 = page.locator('h1.DUwDvf').first.inner_text(timeout=3000)
                            except Exception:
                                pass

                        prev_h1_text = current_h1
                        
                        # ============================================================
                        # FIX 2: UPDATED SELECTORS (from live DOM inspection)
                        # ============================================================
                        name = "N/A"
                        rating = "N/A"
                        reviews = "N/A"
                        website = "N/A"
                        phone = "N/A"
                        
                        # --- Business Name ---
                        try:
                            name_loc = page.locator('h1.DUwDvf').first
                            if name_loc.count() > 0:
                                name = name_loc.inner_text(timeout=3000)
                        except Exception:
                            pass
                        
                        # --- Rating & Reviews (using div.F7nice and aria-label) ---
                        try:
                            # Rating: first span inside div.F7nice with aria-hidden
                            rating_el = page.locator('div.F7nice span[aria-hidden="true"]').first
                            if rating_el.count() > 0:
                                rating = rating_el.inner_text(timeout=2000)
                            
                            # Reviews: span with aria-label containing "review"
                            review_el = page.locator('span[aria-label*="review"]').first
                            if review_el.count() > 0:
                                review_aria = review_el.get_attribute('aria-label', timeout=2000)
                                if review_aria:
                                    # aria-label is like "4 reviews" or "524 reviews"
                                    reviews = review_aria.split(' ')[0].replace(',', '')
                        except Exception:
                            pass
                            
                        # --- Website (using data-item-id="authority") ---
                        try:
                            website_el = page.locator('a[data-item-id="authority"]').first
                            if website_el.count() > 0:
                                website = website_el.get_attribute('href', timeout=2000) or "N/A"
                        except Exception:
                            pass
                            
                        # --- Phone (using data-item-id containing "phone") ---
                        try:
                            phone_el = page.locator('button[data-item-id*="phone"]').first
                            if phone_el.count() > 0:
                                phone_aria = phone_el.get_attribute('aria-label', timeout=2000)
                                if phone_aria and 'Phone:' in phone_aria:
                                    phone = phone_aria.replace('Phone:', '').strip()
                                else:
                                    phone_text = phone_el.inner_text(timeout=2000)
                                    if phone_text:
                                        phone = phone_text.strip().split('\n')[-1]
                        except Exception:
                            pass
                            
                        if name != "N/A" and name.strip() != "":
                            results.append({
                                'Location': location, 'Category': category,
                                'Business Name': name, 'Phone Number': phone,
                                'Website URL': website, 'Rating': rating, 'Review Count': reviews
                            })
                            total_extracted += 1
                            print(f"  [{total_extracted}] ✅ {name}")
                            print(f"       Rating: {rating} | Reviews: {reviews} | Phone: {phone}")
                            print(f"       Website: {website[:60] if website != 'N/A' else 'N/A'}")
                    except Exception as e:
                        print(f"Error extracting listing: {e}")
                        continue

            if MICRO_TEST and total_extracted >= MICRO_TEST_LIMIT:
                break
                        
        browser.close()
        
    if results:
        df = pd.DataFrame(results).drop_duplicates(subset=['Business Name', 'Phone Number'], keep='first')
        df.to_csv('data/nashik_road_leads_raw.csv', index=False, encoding='utf-8-sig')
        print(f"\n--- SUCCESS! Total leads: {len(df)} ---")
        
        # Print summary table for micro-test
        if MICRO_TEST:
            print("\n========== MICRO-TEST RESULTS ==========")
            for i, row in df.iterrows():
                print(f"\n  Lead {i+1}: {row['Business Name']}")
                print(f"    Category:  {row['Category']}")
                print(f"    Rating:    {row['Rating']}")
                print(f"    Reviews:   {row['Review Count']}")
                print(f"    Phone:     {row['Phone Number']}")
                print(f"    Website:   {row['Website URL']}")
            print("\n=========================================")
    else:
        print("\n--- No data extracted. ---")

if __name__ == "__main__":
    scrape_google_maps()
