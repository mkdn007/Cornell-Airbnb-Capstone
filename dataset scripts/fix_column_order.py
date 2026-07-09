"""
Reorders monthly occupancy columns chronologically.
Saves to a new file so the original is untouched.
"""

import pandas as pd

PATH   = "active_listings_clean.csv"
OUTPUT = "active_listings_clean_v2.csv"

df = pd.read_csv(PATH, low_memory=False)

MONTH_ORDER = [
    "occupancy_Jan", "occupancy_Feb", "occupancy_Mar", "occupancy_Apr",
    "occupancy_May", "occupancy_Jun", "occupancy_Jul", "occupancy_Aug",
    "occupancy_Sep", "occupancy_Oct", "occupancy_Nov", "occupancy_Dec",
    "occupancy_rate_calendar",
]

other_cols = [c for c in df.columns if c not in MONTH_ORDER]
df = df[other_cols + MONTH_ORDER]

df.to_csv(OUTPUT, index=False)
print(f"Saved → {OUTPUT}")
print(f"Rows: {len(df):,}  |  Columns: {len(df.columns)}")
print("\nLast 13 columns:")
for c in df.columns[-13:]:
    print(f"  {c}")
