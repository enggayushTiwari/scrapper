import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_advanced_analytics():
    print("--- Loading Data for Advanced Analytics ---")
    
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

    # Clean Rating
    raw_df['Rating'] = raw_df['Rating'].replace(['N/A', 'None', 'nan'], np.nan)
    raw_df['Rating'] = pd.to_numeric(raw_df['Rating'], errors='coerce')

    # =========================================================================
    # Distribution of Reviews vs. Business (The Outlier Check)
    # =========================================================================
    print("Generating review_distribution.png ...")
    plt.figure(figsize=(14, 8))
    sns.boxplot(data=raw_df, x='Review Count', y='Category', palette='viridis')
    plt.title('Distribution of Reviews by Category (Outlier & Whale Check)')
    plt.xlabel('Number of Reviews')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.savefig('visuals/review_distribution.png')
    plt.close()

    # =========================================================================
    # Geographical Clustering (Density by Category and Location)
    # =========================================================================
    print("Generating geo_clustering.png ...")
    plt.figure(figsize=(14, 8))
    sns.countplot(data=raw_df, y='Category', hue='Location', palette='plasma')
    plt.title('Business Density by Category and Location')
    plt.xlabel('Number of Businesses')
    plt.ylabel('Category')
    plt.legend(title='Location', loc='lower right')
    plt.tight_layout()
    plt.savefig('visuals/geo_clustering.png')
    plt.close()

    # =========================================================================
    # Cross-Sector Location Matrix (Pivot Table)
    # =========================================================================
    print("\nCalculating Cross-Sector Location Matrix...")
    
    # 1. Total businesses per Category-Location
    total_counts = raw_df.groupby(['Category', 'Location']).size().reset_index(name='Total')
    
    # 2. No website businesses per Category-Location
    if not tier1_df.empty and 'Category' in tier1_df.columns and 'Location' in tier1_df.columns:
        no_web_counts = tier1_df.groupby(['Category', 'Location']).size().reset_index(name='NoWeb')
    else:
        no_web_counts = pd.DataFrame(columns=['Category', 'Location', 'NoWeb'])
    
    # 3. Merge and compute percentage
    merged = pd.merge(total_counts, no_web_counts, on=['Category', 'Location'], how='left')
    merged['NoWeb'] = merged['NoWeb'].fillna(0)
    merged['% Missing Website'] = (merged['NoWeb'] / merged['Total']) * 100
    
    # 4. Generate Pivot Table format
    pivot_table = merged.pivot(index='Category', columns='Location', values='% Missing Website').fillna(0)
    
    print("\n=========================================================")
    print("      CROSS-SECTOR LOCATION MATRIX (% NO WEBSITE)")
    print("=========================================================\n")
    
    # Configure pandas to print the full width
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    # Round to 1 decimal place and add '%'
    formatted_pivot = pivot_table.round(1).astype(str) + '%'
    print(formatted_pivot)
    print("\n=========================================================\n")

if __name__ == "__main__":
    run_advanced_analytics()
