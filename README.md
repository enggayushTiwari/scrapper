# 🚀 AI-Powered Lead Generation & Market Diagnostics Engine

An end-to-end local business intelligence pipeline designed to scrape, enrich, and analyze Google Maps leads using psychological sales triggers and market-theory diagnostics.

---

## 📂 Project Structure

The project follows a modular architecture for scalability and clean data management:

- **`scripts/`**: The brain of the operation. Contains the scraper, enrichment engine, and multiple analytics modules.
- **`data/`**: Storage for raw and processed CSV lead lists.
- **`exports/`**: Production-ready sales hitlists and competitor envy matrices.
- **`visuals/`**: Data visualizations including review distributions and reputation scatter plots.
- **`logs/`**: Terminal output snapshots and diagnostic reports.

---

## 🛠️ Installation

Ensure you have Python 3.8+ installed.

1. **Clone the repository** (or copy the files).
2. **Install Dependencies**:
   ```bash
   pip install pandas playwright playwright-stealth requests python-whois matplotlib seaborn
   ```
3. **Setup Playwright**:
   ```bash
   playwright install chromium
   ```

---

## 📡 Usage: Any City, Any Business

This engine is built to be flexible. To pivot to a new market:

### 1. Configure the Target
Open `scripts/scraper.py` and modify the `locations` and `categories` lists in the `scrape_google_maps()` function:

```python
# Example: Targeting Real Estate in Mumbai
locations = ['Bandra West, Mumbai', 'Andheri East, Mumbai']
categories = ['real estate agency', 'property consultant', 'coworking space']
```

### 2. Run the Pipeline
Execute the central orchestrator from the root directory:
```bash
python main.py
```
This will:
1. **Scrape**: Pull fresh data from Google Maps.
2. **Enrich**: Validate websites, check SSL, and perform WHOIS lookups to find "outdated" sites.
3. **Segment**: Create Tier 1 (No Website) and Tier 2 (Broken/Struggling) lists.

### 3. Generate Advanced Diagnostics
Run the specialized analytics scripts to find psychological hooks:
```bash
python scripts/psychological_sales_analytics.py  # Finds "Hidden Gems" and "Envy" gaps
python scripts/final_market_diagnostics.py        # Calculates Monopoly Index
```

---

## 📊 The "Nashik Road" Case Study

We used this tool to analyze the **Nashik Road** market. Here are the psychological insights discovered:

### 1. The Monopoly Index
We identified categories where review "power" is concentrated in the top 10% of players, indicating a high barrier to entry but a massive opportunity for disruption.
- **Used Car Dealers**: **84.8%** of all reviews are held by just 10% of dealers.
- **Modular Furniture**: **76.0%** concentration.

### 2. Hidden Gem Hitlist
Identified **412 businesses** with elite ratings (>= 4.8) but extremely low review counts (<= 50) and no website.
> **Sales Hook**: *"You are the best-kept secret in Nashik Road. Let's make sure the world knows it."*

### 3. Competitor Envy Matrix
Found massive "Traffic Gaps" where category leaders have 20k+ reviews, but independent owners without websites are stuck under 1k.
> **Sales Hook**: *"Your neighbors are capturing 10x the traffic because they have a digital storefront. Here is the gap you're losing."*

---

## ⚖️ Disclaimer
This tool is for educational and research purposes. Always ensure compliance with Google Maps' Terms of Service and local data privacy regulations.
