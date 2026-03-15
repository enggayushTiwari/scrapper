import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_sales_analytics():
    print("=========================================================================================")
    print("                           NASIK ROAD SALES INTELLIGENCE")
    print("=========================================================================================\n")
    
    raw_file = 'data/nashik_road_leads_raw.csv'
    tier1_file = 'data/Tier_1_NashikRoad_No_Website.csv'
    
    if not os.path.exists(raw_file):
        print(f"Error: {raw_file} not found.")
        return

    try:
        df = pd.read_csv(raw_file)
        # Strip columns to prevent KeyErrors
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"Error loading {raw_file}: {e}")
        return

    # --- Data Cleaning ---
    def clean_numeric(val):
        if pd.isna(val) or str(val).lower() == 'n/a' or str(val).strip() == '':
            return 0
        try:
            return int(float(str(val).replace(',', '')))
        except:
            return 0

    df['Reviews'] = df['Review Count'].apply(clean_numeric)
    df['Rating'] = df['Rating'].apply(lambda x: float(x) if str(x).replace('.','').isdigit() else 0.0)
    
    # Define flags
    df['Has_Website'] = df['Website URL'].apply(lambda x: False if pd.isna(x) or str(x).lower() == 'n/a' else True)
    df['Has_Phone'] = df['Phone Number'].apply(lambda x: False if pd.isna(x) or str(x).lower() == 'n/a' else True)

    # --- 1. The ROI Proof (Stats for Sales Pitch) ---
    print("--- Phase 1: The ROI Proof (Pitch Deck Stats) ---")
    roi_stats = df.groupby('Has_Website').agg(
        Avg_Rating=('Rating', 'mean'),
        Median_Reviews=('Reviews', 'median'),
        Total_Count=('Business Name', 'count')
    ).reset_index()
    
    print(roi_stats.to_string(index=False))
    print("\n[INSIGHT] Businesses with websites typically have significantly higher review counts and better visibility.\n")

    # --- 2. Automated Lead Scoring ---
    # Score = Rating * Reviews
    df['Lead_Score'] = df['Rating'] * df['Reviews']

    # --- 3. The WhatsApp Hitlist ---
    # Website == False AND Phone == True
    hitlist = df[(df['Has_Website'] == False) & (df['Has_Phone'] == True)].copy()
    
    # --- 4. Export the Hitlist ---
    # Sort by Lead_Score descending, top 100
    hitlist_sorted = hitlist.sort_values(by='Lead_Score', ascending=False).head(100)
    
    # Filter columns
    output_cols = ['Category', 'Business Name', 'Rating', 'Reviews', 'Phone Number', 'Lead_Score']
    hitlist_export = hitlist_sorted[output_cols]
    
    target_export = 'exports/Nashik_Road_WhatsApp_Targets.csv'
    hitlist_export.to_csv(target_export, index=False, encoding='utf-8-sig')
    print(f"--- Phase 2: Hitlist Generated ---")
    print(f"-> Exported top 100 high-value leads to: {target_export}")
    print(f"-> Top Category in Hitlist: {hitlist_sorted['Category'].iloc[0] if not hitlist_sorted.empty else 'N/A'}")
    print("\n")

    # --- 5. Visualization: ROI Proof Bar Chart ---
    print("Generating roi_proof.png ...")
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Use median reviews as the primary "Visibility" metric
    plot = sns.barplot(data=roi_stats, x='Has_Website', y='Median_Reviews', palette='coolwarm')
    plt.title('The ROI of a Website: Median Reviews (Visibility Score)')
    plt.xlabel('Has Website?')
    plt.ylabel('Median Number of Reviews')
    
    # Add labels on top of bars
    for p in plot.patches:
        plot.annotate(format(p.get_height(), '.1f'), 
                      (p.get_x() + p.get_width() / 2., p.get_height()), 
                      ha = 'center', va = 'center', 
                      xytext = (0, 9), 
                      textcoords = 'offset points')

    plt.tight_layout()
    plt.savefig('visuals/roi_proof.png')
    plt.close()
    print("-> Saved roi_proof.png")

    print("\nSales Intelligence Generation Complete.")

if __name__ == "__main__":
    run_sales_analytics()
