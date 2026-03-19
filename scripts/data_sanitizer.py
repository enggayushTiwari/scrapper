import pandas as pd
import os

def sanitize_data():
    print("=========================================================")
    print("        BYTCO DATA SANITIZER ENGINE")
    print("=========================================================\n")
    
    # Load Raw Data
    raw_file = 'data/bytco_modern_leads_raw.csv'
    if not os.path.exists(raw_file):
        print(f"Error: {raw_file} not found.")
        return
    
    df = pd.read_csv(raw_file)
    initial_count = len(df)
    
    # Clean Headers
    df.columns = df.columns.str.strip()
    
    # Keyword Purge List
    purge_keywords = ['mandir', 'temple', 'college road', 'gangapur', 'satpur', 'ashok bakery', 'ground']
    
    print(f"Initial leads: {initial_count}")
    print(f"Purging keywords (case-insensitive): {purge_keywords}")
    
    # Filter out rows containing any of the purge keywords
    mask = df['Business Name'].str.contains('|'.join(purge_keywords), case=False, na=False)
    df_clean = df[~mask].copy()
    
    purged_count = initial_count - len(df_clean)
    print(f"Purged {purged_count} rows from the dataset.")
    print(f"Clean leads remaining: {len(df_clean)}")
    
    # Export Clean Data
    clean_file = 'data/bytco_modern_leads_clean.csv'
    df_clean.to_csv(clean_file, index=False, encoding='utf-8-sig')
    print(f"\n[EXPORT] Scrubbed data saved to: {clean_file}")
    
    print("\n=========================================================")
    print("        SANITIZATION COMPLETED SUCCESSFULLY")
    print("=========================================================")

if __name__ == "__main__":
    sanitize_data()
