import pandas as pd
import os

def generate_category_leaders():
    # File paths
    input_file = r'c:\Users\ayush\.gemini\antigravity\scratch\scrapper\exports\Tier_1_Bytco_No_Website.csv'
    output_file = r'c:\Users\ayush\.gemini\antigravity\scratch\scrapper\exports\Bytco_Top_10_NoWebsite_Per_Category.csv'
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return

    # Load data
    df = pd.read_csv(input_file)
    
    # Pre-processing
    # Ensure Review Count and Rating are numeric
    df['Review Count'] = pd.to_numeric(df['Review Count'], errors='coerce').fillna(0)
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(0)
    
    # Sort by Category, then Review Count (desc), then Rating (desc)
    df_sorted = df.sort_values(
        by=['Category', 'Review Count', 'Rating'], 
        ascending=[True, False, False]
    )
    
    # Group by Category and take top 10
    top_10_per_category = df_sorted.groupby('Category').head(10)
    
    # Ensure exports directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Export to CSV
    top_10_per_category.to_csv(output_file, index=False)
    
    print(f"Successfully generated category-wise leaders (No Website) at: {output_file}")
    print(f"Total leads exported: {len(top_10_per_category)}")
    
    # Print summary of categories processed
    category_counts = top_10_per_category['Category'].value_counts()
    print("\nLeads per Category (Top 10):")
    print(category_counts)

if __name__ == "__main__":
    generate_category_leaders()
