import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def run_analytics():
    print("=========================================================")
    print("        BYTCO PREMIUM ANALYTICS ENGINE")
    print("=========================================================\n")
    
    # Load Data
    file_path = 'data/bytco_modern_leads_raw.csv'
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
    
    # 1. Sector Breakdown
    print("--- 1. SECTOR BREAKDOWN (Bytco Niche Activity) ---")
    sector_breakdown = df.groupby('Category').agg({
        'Business Name': 'count',
        'Rating': 'mean',
        'Review Count': 'median'
    }).rename(columns={'Business Name': 'Total Leads', 'Rating': 'Avg Rating', 'Review Count': 'Median Reviews'}).sort_values(by='Total Leads', ascending=False)
    print(sector_breakdown)
    print("\n")
    
    # 2. The Premium ROI Proof (The Visibility Gap)
    print("--- 2. THE PREMIUM ROI PROOF ---")
    roi_proof = df.groupby('Has_Website')['Review Count'].median()
    web_median = roi_proof.get(True, 0)
    no_web_median = roi_proof.get(False, 0)
    
    visibility_gap = ((web_median - no_web_median) / no_web_median * 100) if no_web_median > 0 else 100
    
    print(f"Median Reviews (Has Website): {web_median}")
    print(f"Median Reviews (No Website):  {no_web_median}")
    print(f"THE VISIBILITY GAP: Businesses with websites have {visibility_gap:.1f}% more reviews than those without.")
    print("\n")
    
    # 3. The Envy Matrix (Bytco Edition)
    print("--- 3. THE ENVY MATRIX (Missed Traffic Gaps) ---")
    top_5_categories = df['Category'].value_counts().nlargest(5).index
    
    envy_results = []
    for cat in top_5_categories:
        cat_df = df[df['Category'] == cat]
        max_web = cat_df[cat_df['Has_Website'] == True]['Review Count'].max()
        max_no_web = cat_df[cat_df['Has_Website'] == False]['Review Count'].max()
        
        # Handle cases where one or the other might be NaN
        max_web = max_web if pd.notnull(max_web) else 0
        max_no_web = max_no_web if pd.notnull(max_no_web) else 0
        
        gap = max_web - max_no_web
        envy_results.append({
            'Category': cat,
            'Max Reviews (Web)': max_web,
            'Max Reviews (No Web)': max_no_web,
            'Missed Traffic Gap': gap
        })
    
    envy_df = pd.DataFrame(envy_results)
    print(envy_df)
    print("\n")
    
    # 4. The Bytco Hitlist (Top 50 Targets)
    print("--- 4. THE BYTCO HITLIST (High Potential, Low Visibility) ---")
    hitlist = df[(df['Has_Website'] == False) & (df['Has_Phone'] == True)].copy()
    hitlist['Lead_Score'] = hitlist['Rating'] * hitlist['Review Count']
    hitlist = hitlist.sort_values(by='Lead_Score', ascending=False)
    
    top_50 = hitlist.head(50)
    print(top_50[['Business Name', 'Category', 'Rating', 'Review Count', 'Lead_Score']].head(15))
    
    # Export Hitlist
    os.makedirs('exports', exist_ok=True)
    top_50.to_csv('exports/Bytco_Premium_Hitlist.csv', index=False)
    print(f"\n[EXPORT] Top 50 targets saved to: exports/Bytco_Premium_Hitlist.csv")
    
    # 5. Visualize ROI Proof
    os.makedirs('visuals', exist_ok=True)
    plt.figure(figsize=(10, 6))
    colors = ['#E63946', '#457B9D'] # Red-ish for No Web, Blue-ish for Web
    
    # Plot bars
    bars = plt.bar(['No Website', 'Has Website'], [no_web_median, web_median], color=colors)
    
    # Aesthetics
    plt.title('Visibility ROI: Median Reviews by Digital Presence (Bytco Area)', fontsize=14, fontweight='bold', pad=20)
    plt.ylabel('Median Number of Reviews', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # Branding
    plt.savefig('visuals/bytco_roi_proof.png', dpi=300, bbox_inches='tight')
    print(f"[VISUAL] Logic visualization saved to: visuals/bytco_roi_proof.png")
    print("\n=========================================================")
    print("        ANALYTICS COMPLETED SUCCESSFULLY")
    print("=========================================================")

if __name__ == "__main__":
    run_analytics()
