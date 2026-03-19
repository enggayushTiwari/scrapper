import pandas as pd
import requests
import time
import whois
from urllib.parse import urlparse

def run_enrichment():
    print("--- Starting Enrichment Engine ---")
    
    # Data Loading
    target_file = 'data/bytco_modern_leads_raw.csv'
    try:
        df = pd.read_csv(target_file)
        print(f"Loaded '{target_file}' successfully.")
    except Exception as e:
        print(f"Error reading '{target_file}': {e}")
        return
    
    # Ensure Website URL column exists and is string type to avoid .str accessor errors
    if 'Website URL' not in df.columns:
        print("Error: 'Website URL' column not found in CSV.")
        return
        
    df['Website URL'] = df['Website URL'].fillna('N/A').astype(str)
    
    # Standardize missing websites
    df['Website URL'] = df['Website URL'].replace(['N/A', 'None', 'nan', ''], pd.NA)
    
    # --- Phase 2: Tier 1 Leads ---
    print("\n[Phase 2] Filtering Tier 1 (No Website) leads...")
    
    # Filter rows where website is NA
    tier_1_mask = df['Website URL'].isna()
    tier_1_df = df[tier_1_mask]
    
    if not tier_1_df.empty:
        tier_1_df.to_csv('exports/Tier_1_Bytco_No_Website.csv', index=False, encoding='utf-8-sig')
        print(f"-> Saved {len(tier_1_df)} leads to 'exports/Tier_1_Bytco_No_Website.csv'")
    else:
        print("-> No Tier 1 leads found (all entries have a website).")
        
    # --- Phase 3: Tier 2 Leads ---
    print("\n[Phase 3] Validating Phase 3 (Tier 2) leads...")
    tier_2_candidates = df[~tier_1_mask].copy()
    
    struggling_sites = []
    valid_sites = []
    
    # Add a User-Agent header so the requests aren't blocked.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html'
    }
    
    if not tier_2_candidates.empty:
        print(f"Pinging {len(tier_2_candidates)} websites...\n")
        
        for idx, row in tier_2_candidates.iterrows():
            url = str(row['Website URL']).strip()
            
            # Ensure URL starts with http
            if not (url.startswith('http://') or url.startswith('https://')):
                url = 'http://' + url
                
            status_code = None
            load_time = None
            error_msg = None
            
            start_time = time.time()
            max_retries = 1
            retries = 0
            
            # Validation Logic with Retry Mechanism
            while retries <= max_retries:
                try:
                    # Set a timeout of 10 seconds
                    response = requests.get(url, headers=headers, timeout=10)
                    load_time = time.time() - start_time
                    status_code = response.status_code
                    error_msg = None  # Clear error msg on success
                    break # Success, escape retry loop
                except requests.exceptions.SSLError:
                    error_msg = 'SSL Error'
                    break # Don't retry SSL errors
                except requests.exceptions.ConnectionError:
                    error_msg = 'Connection Error'
                    if retries < max_retries:
                        print(f"[RETRY] ConnectionError for {url}. Waiting 3 seconds...")
                        time.sleep(3)
                    retries += 1
                except requests.exceptions.Timeout:
                    error_msg = 'Timeout'
                    break # Don't retry Timeouts
                except Exception as e:
                    error_msg = f'Other Error: {e}'
                    break # Don't retry unknown errors
                
            if error_msg:
                # Calculate load time even if it errored out
                load_time = time.time() - start_time
                
            # Scoring/Filtering: throws an error (404, SSL, Connection) OR takes longer than 8 seconds
            is_broken = False
            if error_msg:
                is_broken = True
                print(f"[ERROR] {row['Business Name']} - {url} | Error: {error_msg} | Time: {load_time:.2f}s")
            elif status_code and status_code >= 400:
                is_broken = True
                print(f"[HTTP {status_code}] {row['Business Name']} - {url} | Time: {load_time:.2f}s")
            elif load_time and load_time > 8:
                is_broken = True
                print(f"[SLOW] {row['Business Name']} - {url} | Status: {status_code} | Time: {load_time:.2f}s")
            else:
                print(f"[OK] {row['Business Name']} - {url} | Status: {status_code} | Time: {load_time:.2f}s")
                
            if is_broken:
                broken_lead = row.to_dict()
                broken_lead['Validation URL'] = url
                broken_lead['Status Code'] = status_code if status_code else error_msg
                broken_lead['Load Time (s)'] = round(load_time, 2) if load_time else "N/A"
                struggling_sites.append(broken_lead)
            else:
                valid_lead = row.to_dict()
                valid_lead['Validation URL'] = url
                valid_sites.append(valid_lead)
            
            # Mandatory 2-second sleep between every ping to avoid overwhelming the network
            time.sleep(2)
    else:
        print("-> No Tier 2 leads to validate (none have websites).")
            
    # Output: Save the struggling sites to a new CSV
    if struggling_sites:
        broken_df = pd.DataFrame(struggling_sites)
        broken_df.to_csv('exports/Tier_2_Bytco_Broken_Sites.csv', index=False, encoding='utf-8-sig')
        print(f"\n--- Output Phase 3 ---")
        print(f"-> Saved {len(broken_df)} leads to 'exports/Tier_2_Bytco_Broken_Sites.csv'.")
    elif not tier_2_candidates.empty:
        print("\n-> Zero struggling websites found! All Tier 2 leads are healthy.")

    # --- Phase 4: Tier 3 Outdated Sites ---
    print("\n[Phase 4] Checking domain age for Phase 3 valid leads...")
    outdated_sites = []
    
    if valid_sites:
        print(f"Running WHOIS lookups for {len(valid_sites)} websites...\n")
        
        for lead in valid_sites:
            url = lead['Validation URL']
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Clean domain (remove www., ports, etc.)
            if domain.startswith('www.'):
                domain = domain[4:]
            domain = domain.split(':')[0]
            
            try:
                # Perform WHOIS lookup
                w = whois.whois(domain)
                creation_date = w.creation_date
                
                if not creation_date:
                    print(f"[WHOIS SKIP] {domain} - No creation date found")
                    continue
                    
                # whois can return a list of dates or a single datetime object
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                
                # We attempt to access .year
                year_created = creation_date.year
                
                print(f"[WHOIS OK] {domain} created in {year_created}")
                
                # Flag domains created before 2020
                if year_created < 2020:
                    outdated_lead = lead.copy()
                    outdated_lead['Year Created'] = year_created
                    outdated_sites.append(outdated_lead)
            except Exception as e:
                print(f"[WHOIS ERROR] Failed lookup for {domain}: {e}")
                continue
                
        # Output Phase 4
        if outdated_sites:
            outdated_df = pd.DataFrame(outdated_sites)
            outdated_df.to_csv('exports/Tier_3_Bytco_Outdated_Sites.csv', index=False, encoding='utf-8-sig')
            print(f"\n--- Output Phase 4 ---")
            print(f"-> Saved {len(outdated_df)} leads to 'exports/Tier_3_Bytco_Outdated_Sites.csv'.")
        else:
            print("\n-> Zero outdated websites found! All valid sites were created in 2020 or later.")
    else:
        print("-> No valid Tier 2 leads to check for Phase 4.")

if __name__ == "__main__":
    run_enrichment()
