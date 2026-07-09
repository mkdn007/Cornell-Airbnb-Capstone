"""
Adds latitude, longitude, number_of_reviews_l30d from listings.csv to v5.
Saves to active_listings_clean_v6.csv.
"""

import pandas as pd

SOURCE = "listings (2).csv"
INPUT  = "active_listings_clean_v5.csv"
OUTPUT = "active_listings_clean_v6.csv"

df = pd.read_csv(INPUT, low_memory=False)

new_cols = pd.read_csv(
    SOURCE,
    usecols=["id", "latitude", "longitude", "number_of_reviews_l30d"],
    low_memory=False
)

new_cols = new_cols.rename(columns={
    "number_of_reviews_l30d": "reviews_last_30d"
})

df = df.merge(new_cols, on="id", how="left")

# Place lat/lon after neighborhood, reviews_last_30d after reviews_last_12mo
cols = list(df.columns)
for new_col, after_col in [("latitude", "neighborhood"), ("longitude", "latitude"), ("reviews_last_30d", "reviews_last_12mo")]:
    cols = [c for c in cols if c != new_col]
    idx = cols.index(after_col) + 1
    cols = cols[:idx] + [new_col] + cols[idx:]

df = df[cols]

df.to_csv(OUTPUT, index=False)
print(f"Saved → {OUTPUT}")
print(f"Rows: {len(df):,}  |  Columns: {len(df.columns)}")

print("\nNull check for new columns:")
for col in ["latitude", "longitude", "reviews_last_30d"]:
    nulls = df[col].isna().sum()
    print(f"  {col}: {nulls} nulls ({nulls/len(df)*100:.1f}%)")
