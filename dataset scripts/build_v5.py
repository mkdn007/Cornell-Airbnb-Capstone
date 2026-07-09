"""
Renames capacity_tier values to small/medium/large to prevent Excel date conversion.
Updates segment column accordingly. Saves to active_listings_clean_v5.csv.
"""

import pandas as pd

INPUT  = "active_listings_clean_v4.csv"
OUTPUT = "active_listings_clean_v5.csv"

df = pd.read_csv(INPUT, low_memory=False)

CAPACITY_MAP = {
    "1-2": "small",
    "3-4": "medium",
    "5+":  "large",
}

df["capacity_tier"] = df["capacity_tier"].map(CAPACITY_MAP)

# Rebuild segment with new capacity_tier values
df["segment"] = (
    df["borough"] + " | " +
    df["room_type"] + " | " +
    df["capacity_tier"]
)

df.to_csv(OUTPUT, index=False)
print(f"Saved → {OUTPUT}")
print(f"Rows: {len(df):,}  |  Columns: {len(df.columns)}")

print("\nCapacity tier mapping:")
print(f"  {'Old':<10} {'New':<10} {'Count'}")
print(f"  {'-'*30}")
for old, new in CAPACITY_MAP.items():
    count = (df["capacity_tier"] == new).sum()
    print(f"  {old:<10} {new:<10} {count:,}")

print("\nSample segment values:")
print(df["segment"].value_counts().head(10).to_string())
