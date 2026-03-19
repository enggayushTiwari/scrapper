import pandas as pd
import os
import numpy as np

def run_diagnostics():
    print("=========================================================")
    print("        BYTCO ADVANCED DIAGNOSTICS ENGINE")
    print("=========================================================\n")
    
    # Load Data
    file_path = 'data/bytco_modern_leads_clean.csv'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    
    df = pd.read_csv(file_path)
    
    # Clean Headers
    df.columns = df.columns.str.strip()
    
    # Create Boolean Columns
    df['Has_Website'] = df['Website URL'].apply(lambda x: str(x).strip().lower() not in ['n/a', 'nan', '', 'none'])
    df['Has_Phone'] = df['Phone Number'].apply(lambda x: str(x).strip().lower() not in ['n/a', 'nan', '', 'none'])
    
    # Clean Rating/Reviews
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(0)
    df['Review Count'] = pd.to_numeric(df['Review Count'], errors='coerce').fillna(0)
    
    # Extract Micro-Zone
    df['Micro-Zone'] = df['Location'].apply(lambda x: str(x).split(',')[0].strip())
    
    # --- 1. Reputation Rescue Hitlist ---
    print("--- 1. REPUTATION RESCUE HITLIST ---")
    reputation_rescue = df[
        (df['Review Count'] > 50) & 
        (df['Rating'] <= 4.2) & 
        (df['Has_Website'] == False) & 
        (df['Has_Phone'] == True)
    ].sort_values(by='Review Count', ascending=False)
    
    print(f"Identified {len(reputation_rescue)} Reputation Rescue targets.")
    if not reputation_rescue.empty:
        print(reputation_rescue[['Business Name', 'Category', 'Rating', 'Review Count']].head(10))
    
    os.makedirs('exports', exist_ok=True)
    reputation_rescue.to_csv('exports/Bytco_Reputation_Rescue.csv', index=False)
    print(f"Exported to: exports/Bytco_Reputation_Rescue.csv\n")
    
    # --- 2. Micro-Zone Turf War ---
    print("--- 2. MICRO-ZONE TURF WAR (Pivot Table) ---")
    # Filter for Cafes and Specialty Coffee Shops
    turf_df = df[df['Category'].str.lower().isin(['cafe', 'specialty coffee shop'])]
    
    # Calculate % Missing Website by Micro-Zone
    pivot_table = turf_df.pivot_table(
        index='Micro-Zone',
        columns='Category',
        values='Has_Website',
        aggfunc=lambda x: f"{(1 - x.mean()) * 100:.1f}% Missing"
    )
    print("Visibility Gap Analysis (% Missing Website):")
    print(pivot_table)
    print("\n")
    
    # --- 3. Sleeping Giants Index ---
    print("--- 3. SLEEPING GIANTS INDEX (Elite Potential) ---")
    rev_80th = df['Review Count'].quantile(0.8)
    print(f"80th Percentile for Reviews: {rev_80th}")
    
    sleeping_giants = df[
        (df['Review Count'] >= rev_80th) & 
        (df['Rating'] >= 4.5) & 
        (df['Has_Website'] == False) & 
        (df['Has_Phone'] == True)
    ].sort_values(by='Review Count', ascending=False)
    
    print(f"Identified {len(sleeping_giants)} Sleeping Giant targets.")
    if not sleeping_giants.empty:
        print(sleeping_giants[['Business Name', 'Category', 'Rating', 'Review Count']].head(10))
    
    sleeping_giants.to_csv('exports/Bytco_Sleeping_Giants.csv', index=False)
    print(f"Exported to: exports/Bytco_Sleeping_Giants.csv\n")
    
    print("=========================================================")
    print("        DIAGNOSTICS COMPLETED SUCCESSFULLY")
    print("=========================================================")

if __name__ == "__main__":
    run_diagnostics()
