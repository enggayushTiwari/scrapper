import pandas as pd
import math

df = pd.read_csv('nashik_road_leads_raw.csv')
df.columns = df.columns.str.strip()

def clean_reviews(val):
    if pd.isna(val) or str(val).lower() == 'n/a' or str(val).strip() == '':
        return 0
    try:
        return int(float(str(val).replace(',', '')))
    except:
        return 0

df['Reviews'] = df['Review Count'].apply(clean_reviews)
name_counts = df['Business Name'].value_counts()
chains = name_counts[name_counts > 1].index.tolist()
df_independent = df[~df['Business Name'].isin(chains)].copy()

category_counts = df_independent['Category'].value_counts()
top_10_categories = category_counts.head(10).index.tolist()

with open('monopoly_index.txt', 'w') as f:
    f.write("--- Monopoly Index Results ---\n")
    for cat in top_10_categories:
        cat_df = df_independent[df_independent['Category'] == cat].sort_values(by='Reviews', ascending=False)
        total_cat_reviews = cat_df['Reviews'].sum()
        if total_cat_reviews == 0: continue
        num_businesses = len(cat_df)
        top_10_count = max(1, math.ceil(num_businesses * 0.10))
        top_10_reviews = cat_df.head(top_10_count)['Reviews'].sum()
        percentage = (top_10_reviews / total_cat_reviews) * 100
        f.write(f"{cat}: The top 10% ({top_10_count} business/es) own {percentage:.1f}% of all reviews.\n")
    f.write(f"\nTotal Independent: {len(df_independent)}\n")
    f.write(f"Chain locations excluded: {df[df['Business Name'].isin(chains)].shape[0]}\n")
