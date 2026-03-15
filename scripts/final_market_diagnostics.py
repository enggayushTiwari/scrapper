import pandas as pd
import numpy as np
import os
import math

def run_final_diagnostics():
    print("=========================================================================================")
    print("                        FINAL MARKET DIAGNOSTICS ENGINE")
    print("=========================================================================================\n")
    
    raw_file = 'data/nashik_road_leads_raw.csv'
    
    if not os.path.exists(raw_file):
        print(f"Error: {raw_file} not found.")
        return

    try:
        df = pd.read_csv(raw_file)
        # Clean headers
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # --- Data Cleaning ---
    def clean_reviews(val):
        if pd.isna(val) or str(val).lower() == 'n/a' or str(val).strip() == '':
            return 0
        try:
            return int(float(str(val).replace(',', '')))
        except:
            return 0

    def clean_rating(val):
        if pd.isna(val) or str(val).lower() == 'n/a' or str(val).strip() == '':
            return 0.0
        try:
            return float(val)
        except:
            return 0.0

    df['Reviews'] = df['Review Count'].apply(clean_reviews)
    df['Rating'] = df['Rating'].apply(clean_rating)
    
    # Enrichment for hitlist
    df['Has_Website'] = df['Website URL'].apply(lambda x: False if pd.isna(x) or str(x).lower() == 'n/a' or str(x).strip() == '' else True)
    df['Has_Phone'] = df['Phone Number'].apply(lambda x: False if pd.isna(x) or str(x).lower() == 'n/a' or str(x).strip() == '' else True)

    # --- 1. The Franchise Filter ---
    print("--- Phase 1: The Franchise Filter ---")
    name_counts = df['Business Name'].value_counts()
    chains = name_counts[name_counts > 1].index.tolist()
    
    total_locations = len(df)
    chain_locations_count = df[df['Business Name'].isin(chains)].shape[0]
    
    print(f"Total Businesses Found: {total_locations}")
    print(f"Corporate/Franchise Locations Found: {chain_locations_count} (across {len(chains)} unique brands)")
    
    df_independent = df[~df['Business Name'].isin(chains)].copy()
    print(f"Independent Businesses Remaining: {len(df_independent)}\n")

    # --- 2. The Monopoly Index ---
    print("--- Phase 2: The Monopoly Index (Independent Data) ---")
    category_counts = df_independent['Category'].value_counts()
    top_10_categories = category_counts.head(10).index.tolist()
    
    for cat in top_10_categories:
        cat_df = df_independent[df_independent['Category'] == cat].sort_values(by='Reviews', ascending=False)
        total_cat_reviews = cat_df['Reviews'].sum()
        
        if total_cat_reviews == 0:
            print(f"{cat:<25}: No reviews found in this category.")
            continue
            
        # Top 10% of businesses by count
        num_businesses = len(cat_df)
        top_10_count = max(1, math.ceil(num_businesses * 0.10))
        
        top_10_reviews = cat_df.head(top_10_count)['Reviews'].sum()
        percentage = (top_10_reviews / total_cat_reviews) * 100
        
        print(f"{cat[:24]:<25}: The top 10% ({top_10_count} business/es) own {percentage:.1f}% of all reviews.")
    print("\n")

    # --- 3. The True Hitlist ---
    print("--- Phase 3: The True Hitlist (Exporting to Independent_Owner_Hitlist.csv) ---")
    true_hitlist = df_independent[
        (df_independent['Has_Website'] == False) & 
        (df_independent['Has_Phone'] == True)
    ].sort_values(by='Reviews', ascending=False).head(150)
    
    true_hitlist.to_csv('exports/Independent_Owner_Hitlist.csv', index=False)
    print(f"Successfully exported top {len(true_hitlist)} independent targets to Independent_Owner_Hitlist.csv")
    print("Diagnostics Complete.")

if __name__ == "__main__":
    run_final_diagnostics()
