import pandas as pd
import os
import json

# --- CONFIGURATION & BENCHMARKS ---
# These benchmarks translate "Trust Volume" (Reviews) into "Financial Volume" (Revenue)
# customers_per_review: How many people visit for every 1 review written?
# aov: Average Order Value in INR
BENCHMARKS = {
    'cafe': {'customers_per_review': 150, 'aov': 350},
    'fine dining restaurant': {'customers_per_review': 80, 'aov': 1200},
    'restro bar': {'customers_per_review': 100, 'aov': 1500},
    'used car dealer': {'customers_per_review': 15, 'aov': 450000},
    'dentist': {'customers_per_review': 40, 'aov': 2500},
    'chartered accountant': {'customers_per_review': 25, 'aov': 15000},
    'physiotherapist': {'customers_per_review': 30, 'aov': 1200},
    'interior designer': {'customers_per_review': 20, 'aov': 200000},
    'modular furniture studio': {'customers_per_review': 15, 'aov': 150000},
    'chiropractor': {'customers_per_review': 35, 'aov': 3500},
    'specialty coffee shop': {'customers_per_review': 120, 'aov': 450},
    'premium bakery': {'customers_per_review': 180, 'aov': 500},
    'crossfit box': {'customers_per_review': 50, 'aov': 3000}, # Monthly membership proxy
    'unisex salon': {'customers_per_review': 100, 'aov': 800},
    'pet shop': {'customers_per_review': 120, 'aov': 1500},
    'veterinary clinic': {'customers_per_review': 60, 'aov': 1200},
    'tax consultant': {'customers_per_review': 30, 'aov': 5000},
    'premium bike modification': {'customers_per_review': 20, 'aov': 25000},
    'designer boutique': {'customers_per_review': 40, 'aov': 8000},
    'bridal makeup studio': {'customers_per_review': 25, 'aov': 15000},
    'car detailing studio': {'customers_per_review': 40, 'aov': 7000},
    'tattoo studio': {'customers_per_review': 50, 'aov': 5000},
    'boutique architect': {'customers_per_review': 10, 'aov': 500000},
    'default': {'customers_per_review': 50, 'aov': 1000}
}

DATA_PATH = r"c:\Users\ayush\.gemini\antigravity\scratch\scrapper\data\nashik_road_leads_raw.csv"
EXPORT_PATH = r"c:\Users\ayush\.gemini\antigravity\scratch\scrapper\exports\Revenue_Intelligence_Data.csv"

def estimate_revenue():
    print("="*80)
    print("REVENUE ESTIMATION ENGINE (PROXY MODEL)")
    print("="*80)

    if not os.path.exists(DATA_PATH):
        print(f"Error: Data not found at {DATA_PATH}")
        return

    # Load data
    df = pd.read_csv(DATA_PATH)
    
    # Pre-process Review Count
    # Handling cases like "1.2k" or "84 reviews"
    def clean_reviews(val):
        if pd.isna(val): return 0
        val = str(val).lower().replace('reviews', '').replace(',', '').strip()
        if 'k' in val:
            return int(float(val.replace('k', '')) * 1000)
        try:
            return int(float(val))
        except:
            return 0

    df['review_count_numeric'] = df['Review Count'].apply(clean_reviews)

    # Calculate Revenue
    def calculate_annual_rev(row):
        cat = str(row['Category']).lower()
        bench = BENCHMARKS.get(cat, BENCHMARKS['default'])
        
        # Formula: (Reviews * Customer_Ratio) * AOV
        # This assumes total reviews represent a snapshot of historical volume, 
        # but since we want "Annual", we use it as a proxy for the total wallet share captured.
        # Alternatively, we can assume Reviews/3 = Annual Review Velocity (Rough Estimate)
        annual_review_velocity = row['review_count_numeric'] / 5 # Assuming 5 years of operation on average
        if annual_review_velocity < 1: annual_review_velocity = 1 # Floor
        
        est_customers = annual_review_velocity * bench['customers_per_review']
        total_rev = est_customers * bench['aov']
        return round(total_rev)

    df['Estimated_Annual_Revenue_INR'] = df.apply(calculate_annual_rev, axis=1)

    # Sort by highest revenue
    df = df.sort_values(by='Estimated_Annual_Revenue_INR', ascending=False)

    # Create short version for export
    export_df = df[[
        'Business Name', 'Category', 'Rating', 'Review Count', 
        'Estimated_Annual_Revenue_INR', 'Website URL'
    ]]
    
    export_df.to_csv(EXPORT_PATH, index=False)
    print(f"📊 Exported revenue intelligence to {EXPORT_PATH}")

    # Key Statistics
    total_market = df['Estimated_Annual_Revenue_INR'].sum()
    print(f"\n💰 Total Estimated Annual Market Value (Analyzed): ₹{total_market:,.0f}")
    
    print("\n🚀 Top 10 High-Revenue Targets:")
    print(df[['Business Name', 'Category', 'Estimated_Annual_Revenue_INR']].head(10).to_string(index=False))

    # Hidden Gem Discovery with Revenue
    gems = df[(df['Rating'] >= 4.7) & (df['review_count_numeric'] < 100) & (df['Website URL'] == 'N/A')]
    print(f"\n💎 Found {len(gems)} 'Low Tech / High Quality' gems with significant upside.")


if __name__ == "__main__":
    estimate_revenue()
