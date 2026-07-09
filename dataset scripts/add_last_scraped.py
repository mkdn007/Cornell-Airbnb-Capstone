"""
Adds last_scraped column (from listings.csv) to active_listings_clean_v2.csv,
matched on id. Saves to active_listings_clean_v3.csv.
"""

import pandas as pd

SOURCE   = "listings (2).csv"
INPUT    = "active_listings_clean_v2.csv"
OUTPUT   = "active_listings_clean_v3.csv"

df       = pd.read_csv(INPUT, low_memory=False)
scraped  = pd.read_csv(SOURCE, usecols=["id", "last_scraped"], low_memory=False)

df = df.merge(scraped, on="id", how="left")

# Place last_scraped right after id
cols = ["id", "last_scraped"] + [c for c in df.columns if c not in ("id", "last_scraped")]
df = df[cols]

df.to_csv(OUTPUT, index=False)
print(f"Saved → {OUTPUT}")
print(f"Rows: {len(df):,}  |  Columns: {len(df.columns)}")
print(f"last_scraped nulls: {df['last_scraped'].isna().sum()}")
print(f"Sample values: {df['last_scraped'].value_counts().head(3).to_string()}")
