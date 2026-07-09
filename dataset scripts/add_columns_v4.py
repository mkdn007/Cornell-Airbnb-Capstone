"""
Adds host_since, hosts_time_as_host_years, review_scores_accuracy,
property_type, first_review, last_review from listings.csv into v3.
Saves to active_listings_clean_v4.csv.
"""

import pandas as pd

SOURCE = "listings (2).csv"
INPUT  = "active_listings_clean_v3.csv"
OUTPUT = "active_listings_clean_v4.csv"

df = pd.read_csv(INPUT, low_memory=False)

new_cols = pd.read_csv(
    SOURCE,
    usecols=["id", "host_since", "hosts_time_as_host_years",
             "review_scores_accuracy", "property_type",
             "first_review", "last_review"],
    low_memory=False
)

# Rename to interpretable names before merging
new_cols = new_cols.rename(columns={
    "host_since":               "host_start_date",
    "hosts_time_as_host_years": "host_experience_years",
    "review_scores_accuracy":   "rating_accuracy",
    "first_review":             "listing_first_review_date",
    "last_review":              "listing_last_review_date",
})

df = df.merge(new_cols, on="id", how="left")

# Place new columns in logical positions:
# property_type after room_type, host cols after host_id, review dates after last_scraped
insert_after = {
    "host_id":        ["host_start_date", "host_experience_years"],
    "room_type":      ["property_type"],
    "rating_value":   ["rating_accuracy"],
    "last_scraped":   ["listing_first_review_date", "listing_last_review_date"],
}

cols = list(df.columns)
for after_col, new in insert_after.items():
    # Remove from wherever they currently are
    cols = [c for c in cols if c not in new]
    # Insert after the anchor column
    idx = cols.index(after_col) + 1
    cols = cols[:idx] + new + cols[idx:]

df = df[cols]

# ── Null check ─────────────────────────────────────────────────────────────────
print(f"Saved → {OUTPUT}")
print(f"Rows: {len(df):,}  |  Columns: {len(df.columns)}")
print("\nNull check for new columns:")
new_col_names = ["host_start_date", "host_experience_years", "rating_accuracy",
                 "property_type", "listing_first_review_date", "listing_last_review_date"]
for col in new_col_names:
    nulls = df[col].isna().sum()
    pct   = nulls / len(df) * 100
    print(f"  {col}: {nulls} nulls ({pct:.1f}%)")

print("\nNull check — ALL columns:")
null_cols = {c: df[c].isna().sum() for c in df.columns if df[c].isna().sum() > 0}
if null_cols:
    for c, n in sorted(null_cols.items(), key=lambda x: -x[1]):
        print(f"  {c}: {n} nulls ({n/len(df)*100:.1f}%)")
else:
    print("  No nulls anywhere in the dataset.")

df.to_csv(OUTPUT, index=False)
