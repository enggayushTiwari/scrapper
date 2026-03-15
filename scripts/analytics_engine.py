import pandas as pd
import numpy as np
import os

def run_analytics():
    print("=========================================================================================")
    print("                           NASHIK MARKET OPPORTUNITY ANALYTICS")
    print("=========================================================================================\n")
    
    raw_file = 'data/nashik_leads_raw_RUN_1.csv'
    # Fallback to the micro-test file if the massive run hasn't occurred yet
    if not os.path.exists(raw_file):
        raw_file = 'data/nashik_leads_raw.csv'
        print(f"[INFO] '{raw_file}' substituted since massive run file not found.\n")

    tier1_file = 'data/Tier_1_No_Website.csv'
    
    try:
        raw_df = pd.read_csv(raw_file)
        tier1_df = pd.read_csv(tier1_file)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # 1. Clean Review Count
    raw_df['Review Count'] = raw_df['Review Count'].replace(['N/A', 'None', 'nan'], np.nan)
    if raw_df['Review Count'].dtype == object:
        raw_df['Review Count'] = raw_df['Review Count'].str.replace(',', '', regex=False)
    raw_df['Review Count'] = pd.to_numeric(raw_df['Review Count'], errors='coerce')

    # 2. Clean Rating
    raw_df['Rating'] = raw_df['Rating'].replace(['N/A', 'None', 'nan'], np.nan)
    raw_df['Rating'] = pd.to_numeric(raw_df['Rating'], errors='coerce')

    # 3. Market Distribution
    total_per_category = raw_df.groupby('Category').size().reset_index(name='Total Businesses')

    # 4. Foot Traffic Analysis
    foot_traffic = raw_df.groupby('Category')['Review Count'].agg(['mean', 'median']).reset_index()
    foot_traffic.rename(columns={'mean': 'Average Reviews', 'median': 'Median Reviews'}, inplace=True)
    
    # 5. Opportunity Matrix calculation using Tier_1_No_Website.csv
    # Count how many leads from each category are in Tier 1
    if not tier1_df.empty and 'Category' in tier1_df.columns:
        no_website_counts = tier1_df.groupby('Category').size().reset_index(name='No Website Count')
    else:
        no_website_counts = pd.DataFrame(columns=['Category', 'No Website Count'])
    
    # Merge all DataFrames together
    report_df = pd.merge(total_per_category, foot_traffic, on='Category', how='left')
    report_df = pd.merge(report_df, no_website_counts, on='Category', how='left')
    
    # Fill missing values for No Website Count with 0
    report_df['No Website Count'] = report_df['No Website Count'].fillna(0)
    report_df['% No Website'] = (report_df['No Website Count'] / report_df['Total Businesses']) * 100
    
    # 6. Scoring: High Reviews (Activity) + High % Missing Websites (Need)
    max_avg_reviews = report_df['Average Reviews'].max() if not report_df['Average Reviews'].isna().all() else 0
    max_pct_no_web = report_df['% No Website'].max() if not report_df['% No Website'].isna().all() else 0
    
    # Normalize with safety checks to avoid div zero
    if max_avg_reviews > 0:
        norm_reviews = report_df['Average Reviews'].fillna(0) / max_avg_reviews
    else:
        norm_reviews = 0
        
    if max_pct_no_web > 0:
        norm_no_website = report_df['% No Website'].fillna(0) / max_pct_no_web
    else:
        norm_no_website = 0
        
    # The Opportunity Score (10-point scale)
    report_df['Opportunity Score'] = ((norm_reviews * 0.4) + (norm_no_website * 0.6)) * 10
    
    # Sort
    report_df = report_df.sort_values(by='Opportunity Score', ascending=False)
    
    # Format and Print
    print(f"{'Rank':<5} | {'Category':<22} | {'Total':<6} | {'Avg Rev':<8} | {'Med Rev':<8} | {'Missing Web':<12} | {'% Missing':<10} | {'Score / 10'}")
    print("-" * 115)
    
    rank = 1
    for idx, row in report_df.iterrows():
        cat = row['Category'][:20]
        tot = int(row['Total Businesses'])
        avg_rev = f"{row['Average Reviews']:.1f}" if pd.notna(row['Average Reviews']) else "N/A"
        med_rev = f"{row['Median Reviews']:.1f}" if pd.notna(row['Median Reviews']) else "N/A"
        no_web = int(row['No Website Count'])
        pct_no_web = f"{row['% No Website']:.1f}%"
        score = f"{row['Opportunity Score']:.2f}"
        
        print(f"{rank:<5} | {cat:<22} | {tot:<6} | {avg_rev:<8} | {med_rev:<8} | {no_web:<12} | {pct_no_web:<10} | {score}")
        rank += 1

if __name__ == "__main__":
    run_analytics()
