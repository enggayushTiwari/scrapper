import pandas as pd
import numpy as np
import os

def run_psychological_analytics():
    print("=========================================================================================")
    print("                      PSYCHOLOGICAL SALES ANALYTICS ENGINE")
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
            # Handle cases where it might be a float string like "485.0"
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
    
    # Create boolean columns
    df['Has_Website'] = df['Website URL'].apply(lambda x: False if pd.isna(x) or str(x).lower() == 'n/a' or str(x).strip() == '' else True)
    df['Has_Phone'] = df['Phone Number'].apply(lambda x: False if pd.isna(x) or str(x).lower() == 'n/a' or str(x).strip() == '' else True)

    # --- 1. The 'Competitor Envy' Matrix (Envy_Matrix.csv) ---
    print("Generating 'Competitor Envy' Matrix...")
    
    # Max reviews for businesses WITH website
    online_max = df[df['Has_Website'] == True].groupby('Category')['Reviews'].max().rename('Max Online Reviews')
    
    # Max reviews for businesses WITHOUT website
    offline_max = df[df['Has_Website'] == False].groupby('Category')['Reviews'].max().rename('Max Offline Reviews')
    
    envy_matrix = pd.merge(online_max, offline_max, on='Category', how='outer').fillna(0)
    envy_matrix['Missed Traffic Gap'] = envy_matrix['Max Online Reviews'] - envy_matrix['Max Offline Reviews']
    
    # Filter for top 10 categories with biggest gaps
    top_10_envy = envy_matrix.sort_values(by='Missed Traffic Gap', ascending=False).head(10)
    envy_matrix.head(10).to_csv('exports/Envy_Matrix.csv', index=False)
    
    # --- 2. The 'Hidden Gem' Hitlist (Hidden_Gems_Hitlist.csv) ---
    print("Generating 'Hidden Gem' Hitlist...")
    hidden_gems = df[
        (df['Rating'] >= 4.8) & 
        (df['Reviews'] <= 50) & 
        (df['Has_Website'] == False) & 
        (df['Has_Phone'] == True)
    ].sort_values(by='Rating', ascending=False)
    
    hidden_gems.to_csv('exports/Hidden_Gems_Hitlist.csv', index=False)
    
    # --- 3. The 'High-Ticket' Hitlist (High_Ticket_Hitlist.csv) ---
    print("Generating 'High-Ticket' Hitlist...")
    high_ticket_keywords = ['studio', 'boutique', 'premium', 'luxury', 'clinic', 'speciality', 'fine dine', 'spa']
    
    # Create a regex pattern for case-insensitive matching
    pattern = '|'.join(high_ticket_keywords)
    
    high_ticket = df[
        (df['Business Name'].str.contains(pattern, case=False, na=False)) &
        (df['Has_Website'] == False) &
        (df['Has_Phone'] == True)
    ].sort_values(by='Reviews', ascending=False)
    
    high_ticket.to_csv('exports/High_Ticket_Hitlist.csv', index=False)

    # --- Summary ---
    print("\n=========================================================================================")
    print("                                  LEAD SUMMARY")
    print("=========================================================================================")
    print(f"1. Competitor Envy Categories (Top 10): Exported to Envy_Matrix.csv")
    print(f"2. Hidden Gems Found:                  {len(hidden_gems)} leads")
    print(f"3. High-Ticket Targets Found:          {len(high_ticket)} leads")
    print("=========================================================================================\n")

if __name__ == "__main__":
    run_psychological_analytics()
