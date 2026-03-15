import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_nr_analytics():
    print("=========================================================================================")
    print("                           NASHIK ROAD MARKET ANALYTICS")
    print("=========================================================================================\n")
    
    raw_file = 'nashik_road_leads_raw.csv'
    tier1_file = 'Tier_1_NashikRoad_No_Website.csv'
    
    if not os.path.exists(raw_file) or not os.path.exists(tier1_file):
        print(f"Error: Required files not found. Ensure {raw_file} and {tier1_file} exist.")
        return

    try:
        raw_df = pd.read_csv(raw_file)
        tier1_df = pd.read_csv(tier1_file)
        
        # Strip column names to avoid hidden space KeyError
        raw_df.columns = raw_df.columns.str.strip()
        tier1_df.columns = tier1_df.columns.str.strip()
        
    except Exception as e:
        print(f"Error loading files: {e}")
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

    raw_df['Reviews'] = raw_df['Review Count'].apply(clean_reviews)
    raw_df['Rating'] = raw_df['Rating'].apply(clean_rating)
    
    # Track website presence for the reputation matrix
    raw_df['Has Website'] = raw_df['Website URL'].apply(lambda x: False if pd.isna(x) or str(x).lower() == 'n/a' else True)

    # --- 1. The Opportunity Matrix ---
    print("--- Phase 1: The Opportunity Matrix ---")
    total_stats = raw_df.groupby('Category').agg(
        Total_Businesses=('Business Name', 'count'),
        Avg_Reviews=('Reviews', 'mean'),
        Median_Reviews=('Reviews', 'median')
    ).reset_index()

    no_web_stats = tier1_df.groupby('Category').size().reset_index(name='No_Website_Count')
    
    opp_matrix = pd.merge(total_stats, no_web_stats, on='Category', how='left').fillna(0)
    opp_matrix['% Missing Website'] = (opp_matrix['No_Website_Count'] / opp_matrix['Total_Businesses']) * 100
    
    # Sort by highest % Missing Website
    opp_matrix = opp_matrix.sort_values(by='% Missing Website', ascending=False)
    
    print(f"{'Category':<25} | {'Total':<6} | {'Avg Rev':<8} | {'Med Rev':<8} | {'No Web %'}")
    print("-" * 65)
    for _, row in opp_matrix.iterrows():
        print(f"{row['Category'][:24]:<25} | {int(row['Total_Businesses']):<6} | {row['Avg_Reviews']:<8.1f} | {row['Median_Reviews']:<8.1f} | {row['% Missing Website']:.1f}%")
    print("\n")

    # --- 2. The Ghost Matrix ---
    print("--- Phase 2: The Ghost Matrix (Invisible Businesses) ---")
    # Missing Website AND Phone
    ghosts = raw_df[
        ((raw_df['Website URL'].isna()) | (raw_df['Website URL'].str.lower() == 'n/a')) & 
        ((raw_df['Phone Number'].isna()) | (raw_df['Phone Number'].str.lower() == 'n/a'))
    ]
    ghost_stats = ghosts.groupby('Category').size().reset_index(name='Ghost_Count')
    ghost_stats = ghost_stats.sort_values(by='Ghost_Count', ascending=False)
    
    if not ghost_stats.empty:
        print(f"{'Category':<25} | {'Ghost Count'}")
        print("-" * 38)
        for _, row in ghost_stats.iterrows():
            print(f"{row['Category'][:24]:<25} | {int(row['Ghost_Count'])}")
    else:
        print("No 'Ghost' businesses found in this dataset.")
    print("\n")

    # --- 3. Visualizations ---
    print("Generating Visualizations...")
    
    # A. Review Distribution Boxplot
    plt.figure(figsize=(12, 8))
    sns.boxplot(data=raw_df, x='Reviews', y='Category', palette='Set2')
    plt.title('Nashik Road: Review Distribution (Whale Check)')
    plt.xlabel('Number of Reviews')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.savefig('nr_review_distribution.png')
    plt.close()
    print("-> Saved nr_review_distribution.png")

    # B. Reputation Matrix (Scatter Plot)
    plt.figure(figsize=(10, 6))
    # Use log scale for Y (Reviews) because outliers skew the plot
    sns.scatterplot(data=raw_df, x='Rating', y='Reviews', hue='Has Website', alpha=0.6)
    plt.yscale('log')
    plt.title('Nashik Road: Reputation Matrix (Rating vs Reviews)')
    plt.xlabel('Rating (0-5)')
    plt.ylabel('Reviews (Log Scale)')
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.tight_layout()
    plt.savefig('nr_reputation_matrix.png')
    plt.close()
    print("-> Saved nr_reputation_matrix.png")
    
    print("\nAnalytics Complete.")

if __name__ == "__main__":
    run_nr_analytics()
