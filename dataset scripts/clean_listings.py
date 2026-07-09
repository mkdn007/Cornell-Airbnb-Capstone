"""
NYC Airbnb Capstone — Data Cleaning Pipeline
Produces: active_listings_clean.csv

Steps:
 1.  Filter to active listings (price > 0, availability_365 > 0, number_of_reviews_ltm >= 1)
 1b. Parse bathrooms_text → numeric bathrooms, then impute remaining nulls in
     bedrooms / beds / bathrooms using median per accommodates value
 2.  Parse amenities → top-20 binary flags
 3.  Build host tier flags + minimum_nights / maximum_nights / is_monthly_rental
 4.  Build matched segment keys (borough × room_type × capacity_bucket)
 5.  Calendar → per-listing monthly occupancy rates
 6.  Reviews → velocity features (days_since_last_review, review_count_ltm_verified)
 7.  Reviews → BERT sentiment score (nlptown, up to 5 most recent reviews per listing)
"""

import ast
import re
from collections import Counter
from datetime import datetime

import pandas as pd
import torch
from transformers import pipeline

LISTINGS_PATH = "listings (2).csv"
CALENDAR_PATH = "calendar (1).csv"
REVIEWS_PATH  = "reviews (1).csv"
OUTPUT_PATH   = "active_listings_clean.csv"
SNAPSHOT_DATE = pd.Timestamp("2026-06-14")   # dataset snapshot date
LTM_CUTOFF    = SNAPSHOT_DATE - pd.DateOffset(months=12)

# ── 1. Load listings ───────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1 — Load & filter listings")
df = pd.read_csv(LISTINGS_PATH, low_memory=False)
print(f"  Raw rows: {len(df):,}")

# ── 2. Clean price ─────────────────────────────────────────────────────────────
df["price_clean"] = (
    df["price"]
    .astype(str)
    .str.replace(r"[\$,]", "", regex=True)
    .str.strip()
    .replace("nan", None)
)
df["price_clean"] = pd.to_numeric(df["price_clean"], errors="coerce")

# ── 3. Active listing filter ───────────────────────────────────────────────────
active = df[
    (df["price_clean"] > 0) &
    (df["availability_365"] > 0) &
    (df["number_of_reviews_ltm"] >= 1)
].copy()
print(f"  Active listings: {len(active):,}  ({len(active)/len(df)*100:.1f}% of raw)")
active_ids = set(active["id"].astype(str))

# ── 1b. Fix bathrooms from bathrooms_text, then impute all capacity nulls ─────
print("\nSTEP 1b — Parse bathrooms_text + impute missing capacity fields")

def parse_bathrooms_text(raw):
    """Convert text like '1.5 shared baths', 'Half-bath', '2 baths' → float."""
    if not isinstance(raw, str):
        return None
    raw = raw.strip().lower()
    if raw in ("", "nan"):
        return None
    if "half" in raw:
        return 0.5
    match = re.match(r"([\d\.]+)", raw)
    if match:
        return float(match.group(1))
    return None

# Fill bathrooms nulls from bathrooms_text first (more accurate than accommodates proxy)
text_parsed = active["bathrooms_text"].apply(parse_bathrooms_text)
bathroom_from_text = active["bathrooms"].isna() & text_parsed.notna()
active.loc[bathroom_from_text, "bathrooms"] = text_parsed[bathroom_from_text]
print(f"  bathrooms filled from bathrooms_text: {bathroom_from_text.sum():,}")

# Now impute remaining nulls in bedrooms / beds / bathrooms from accommodates median
for col in ["bedrooms", "beds", "bathrooms"]:
    before = active[col].isna().sum()
    lookup = (
        active[active[col].notna()]
        .groupby("accommodates")[col]
        .median()
    )
    active[f"{col}_was_imputed"] = active[col].isna().astype(int)
    active[col] = active[col].fillna(active["accommodates"].map(lookup))
    active[col] = active[col].fillna(active[col].median())
    after = active[col].isna().sum()
    print(f"  {col}: {before} nulls → {after} nulls  (imputed {before - after})")

# ── 4. Parse amenities → top-20 binary flags ──────────────────────────────────
print("\nSTEP 2 — Parse amenities")

def parse_amenities(raw):
    if not isinstance(raw, str) or raw.strip() in ("", "[]"):
        return []
    try:
        items = ast.literal_eval(raw)
    except Exception:
        items = re.findall(r'"([^"]+)"', raw)
    return [i.strip().lower() for i in items if isinstance(i, str)]

counter = Counter()
active["amenities"].apply(lambda x: counter.update(parse_amenities(x)))
top20 = [a for a, _ in counter.most_common(20)]
print("  Top 20 amenities:")
for rank, (a, c) in enumerate(counter.most_common(20), 1):
    print(f"    {rank:2d}. {a}  ({c:,})")

def safe_col(name):
    return "amenity_" + re.sub(r"[^a-z0-9]+", "_", name).strip("_")

amenity_col_map = {a: safe_col(a) for a in top20}
parsed_series = active["amenities"].apply(parse_amenities)
for amenity, col in amenity_col_map.items():
    active[col] = parsed_series.apply(lambda lst, a=amenity: int(a in lst))

# ── 5. Host tier flags + rental type fields ───────────────────────────────────
print("\nSTEP 3 — Host tiers + rental type")

def host_tier(n):
    if n == 1:       return "Individual"
    elif n <= 5:     return "Small-Multi"
    elif n <= 20:    return "Mid-Multi"
    else:            return "Enterprise"

active["host_tier"] = active["calculated_host_listings_count"].apply(host_tier)
print(active["host_tier"].value_counts().to_string())

# Monthly rental flag — min_nights >= 28 means this is a long-term rental product,
# not a nightly STR; these should be handled separately in the model
active["is_monthly_rental"] = (active["minimum_nights"] >= 28).astype(int)
print(f"\n  is_monthly_rental=1: {active['is_monthly_rental'].sum():,} listings "
      f"({active['is_monthly_rental'].mean()*100:.1f}% of active)")

# ── 6. Capacity bucket + segment ──────────────────────────────────────────────
print("\nSTEP 4 — Segments")

def cap_bucket(n):
    if n <= 2:   return "1-2"
    elif n <= 4: return "3-4"
    else:        return "5+"

active["capacity_bucket"] = active["accommodates"].apply(cap_bucket)
active["segment"] = (
    active["neighbourhood_group_cleansed"].str.strip() + " | " +
    active["room_type"].str.strip()                    + " | " +
    active["capacity_bucket"]
)
print(f"  Unique segments: {active['segment'].nunique():,}")

# ── 7. Calendar — per-listing monthly occupancy ───────────────────────────────
print("\nSTEP 5 — Calendar occupancy (chunked)")

month_agg = {}
CHUNKSIZE = 500_000
chunks_read = 0
for chunk in pd.read_csv(
        CALENDAR_PATH,
        usecols=["listing_id", "date", "available"],
        parse_dates=["date"],
        chunksize=CHUNKSIZE,
        low_memory=False):
    chunk = chunk[chunk["listing_id"].astype(str).isin(active_ids)]
    if chunk.empty:
        continue
    chunk["month"]  = chunk["date"].dt.month
    chunk["booked"] = (chunk["available"] == "f").astype(int)
    grp = chunk.groupby(["listing_id", "month"])["booked"].agg(["sum", "count"])
    for (lid, mon), row in grp.iterrows():
        key = (lid, mon)
        if key not in month_agg:
            month_agg[key] = [0, 0]
        month_agg[key][0] += row["sum"]
        month_agg[key][1] += row["count"]
    chunks_read += 1
    if chunks_read % 5 == 0:
        print(f"  ...{chunks_read * CHUNKSIZE:,} calendar rows processed")

print(f"  Done. Unique (listing, month) pairs: {len(month_agg):,}")

MONTH_NAMES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

rows = {}
for (lid, mon), (booked, total) in month_agg.items():
    if lid not in rows:
        rows[lid] = {}
    rows[lid][f"cal_occ_{MONTH_NAMES[mon]}"] = round(booked / total, 4) if total > 0 else None

cal_df = pd.DataFrame.from_dict(rows, orient="index")
cal_df.index.name = "id"
cal_df = cal_df.reset_index()
cal_df["id"] = cal_df["id"].astype(int)

overall = {}
for (lid, mon), (booked, total) in month_agg.items():
    if lid not in overall:
        overall[lid] = [0, 0]
    overall[lid][0] += booked
    overall[lid][1] += total
cal_df["cal_occ_overall"] = cal_df["id"].map(
    {lid: round(b/t, 4) for lid, (b, t) in overall.items() if t > 0}
)

active = active.merge(cal_df, on="id", how="left")
covered = active["cal_occ_overall"].notna().sum()
print(f"  Calendar coverage: {covered:,} / {len(active):,} active listings")

# ── 8. Reviews — velocity features ────────────────────────────────────────────
print("\nSTEP 6 — Review velocity")

reviews = pd.read_csv(REVIEWS_PATH, usecols=["listing_id", "id", "date"],
                      parse_dates=["date"], low_memory=False)
reviews = reviews[reviews["listing_id"].isin(active["id"].values)]

# days since last review
last_review = reviews.groupby("listing_id")["date"].max().reset_index()
last_review.columns = ["id", "last_review_date"]
last_review["days_since_last_review"] = (
    SNAPSHOT_DATE - last_review["last_review_date"]
).dt.days

# review count in last 12 months (independent verification of number_of_reviews_ltm)
ltm_reviews = reviews[reviews["date"] >= LTM_CUTOFF]
ltm_count = ltm_reviews.groupby("listing_id").size().reset_index()
ltm_count.columns = ["id", "review_count_ltm_verified"]

active = active.merge(last_review[["id", "days_since_last_review"]], on="id", how="left")
active = active.merge(ltm_count, on="id", how="left")
active["review_count_ltm_verified"] = active["review_count_ltm_verified"].fillna(0).astype(int)
print(f"  days_since_last_review populated: {active['days_since_last_review'].notna().sum():,}")
print(f"  review_count_ltm_verified populated: {(active['review_count_ltm_verified'] > 0).sum():,}")

# ── 9. Reviews — BERT sentiment (up to 5 most recent per listing) ─────────────
print("\nSTEP 7 — BERT sentiment (nlptown/bert-base-multilingual-uncased-sentiment)")
print("  Loading model...")

device = 0 if torch.cuda.is_available() else -1
sentiment_pipe = pipeline(
    "text-classification",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    device=device,
    truncation=True,
    max_length=512,
)

reviews_full = pd.read_csv(REVIEWS_PATH,
                            usecols=["listing_id", "date", "comments"],
                            parse_dates=["date"],
                            low_memory=False)
reviews_full = reviews_full[reviews_full["listing_id"].isin(active["id"].values)]
reviews_full = reviews_full.dropna(subset=["comments"])
reviews_full["comments"] = reviews_full["comments"].astype(str).str.strip()
reviews_full = reviews_full[reviews_full["comments"].str.len() > 10]

# Keep 5 most recent reviews per listing
reviews_full = reviews_full.sort_values("date", ascending=False)
reviews_top5 = reviews_full.groupby("listing_id").head(5).copy()
print(f"  Running BERT on {len(reviews_top5):,} review texts "
      f"({reviews_top5['listing_id'].nunique():,} unique listings)...")

# Map label "X stars" → numeric 1–5
def label_to_score(label):
    return int(label.split()[0])

BATCH = 64
texts  = reviews_top5["comments"].tolist()
labels = []
for i in range(0, len(texts), BATCH):
    batch = texts[i: i + BATCH]
    results = sentiment_pipe(batch)
    labels.extend([label_to_score(r["label"]) for r in results])
    if i % (BATCH * 50) == 0:
        print(f"  ...{i:,} / {len(texts):,} texts scored")

reviews_top5 = reviews_top5.copy()
reviews_top5["bert_score"] = labels

# Average score per listing (1–5 scale)
bert_agg = (
    reviews_top5.groupby("listing_id")["bert_score"]
    .mean()
    .round(3)
    .reset_index()
    .rename(columns={"listing_id": "id", "bert_score": "sentiment_score_bert"})
)
active = active.merge(bert_agg, on="id", how="left")
scored = active["sentiment_score_bert"].notna().sum()
print(f"  Sentiment scored: {scored:,} / {len(active):,} active listings")
print(f"  Mean sentiment: {active['sentiment_score_bert'].mean():.3f} / 5.0")

# ── 10. Select output columns ─────────────────────────────────────────────────
print("\nSTEP 8 — Writing output")

core_cols = [
    # identity & UI
    "id", "host_id", "name", "listing_url",
    # location
    "neighbourhood_group_cleansed", "neighbourhood_cleansed",
    # property
    "room_type", "accommodates", "bedrooms", "beds", "bathrooms",
    "bedrooms_was_imputed", "beds_was_imputed", "bathrooms_was_imputed",
    # pricing
    "price_clean",
    # availability & rental type
    "availability_365", "minimum_nights", "maximum_nights", "is_monthly_rental",
    # reviews
    "number_of_reviews", "number_of_reviews_ltm", "reviews_per_month",
    "review_scores_rating", "review_scores_cleanliness",
    "review_scores_checkin", "review_scores_communication",
    "review_scores_location", "review_scores_value",
    # host
    "host_is_superhost", "calculated_host_listings_count",
    # performance
    "estimated_occupancy_l365d", "estimated_revenue_l365d",
    # engineered
    "host_tier", "capacity_bucket", "segment",
    # velocity & sentiment
    "days_since_last_review", "review_count_ltm_verified",
    "sentiment_score_bert",
]
amenity_cols = list(amenity_col_map.values())
cal_cols     = sorted(c for c in active.columns if c.startswith("cal_occ_"))

out_cols    = [c for c in core_cols if c in active.columns] + amenity_cols + cal_cols
active_out  = active[out_cols]

# ── Rename columns to intuitive names ─────────────────────────────────────────
rename_map = {
    # identity
    "name":                             "listing_name",
    # location
    "neighbourhood_group_cleansed":     "borough",
    "neighbourhood_cleansed":           "neighborhood",
    # property
    "room_type":                        "room_type",
    "accommodates":                     "max_guests",
    "bedrooms_was_imputed":             "bedrooms_imputed",
    "beds_was_imputed":                 "beds_imputed",
    "bathrooms_was_imputed":            "bathrooms_imputed",
    # pricing
    "price_clean":                      "nightly_price",
    # availability
    "availability_365":                 "days_available_next_365",
    "minimum_nights":                   "min_nights",
    "maximum_nights":                   "max_nights",
    "is_monthly_rental":                "is_monthly_rental",
    # reviews
    "number_of_reviews":                "total_reviews",
    "number_of_reviews_ltm":            "reviews_last_12mo",
    "reviews_per_month":                "reviews_per_month",
    "review_scores_rating":             "rating_overall",
    "review_scores_cleanliness":        "rating_cleanliness",
    "review_scores_checkin":            "rating_checkin",
    "review_scores_communication":      "rating_communication",
    "review_scores_location":           "rating_location",
    "review_scores_value":              "rating_value",
    # host
    "host_is_superhost":                "is_superhost",
    "calculated_host_listings_count":   "host_total_listings",
    # performance
    "estimated_occupancy_l365d":        "occupancy_rate",
    "estimated_revenue_l365d":          "estimated_annual_revenue",
    # engineered
    "capacity_bucket":                  "capacity_tier",
    # velocity & sentiment
    "days_since_last_review":           "days_since_last_review",
    "review_count_ltm_verified":        "reviews_last_12mo_verified",
    "sentiment_score_bert":             "sentiment_score",
    # calendar occupancy
    "cal_occ_overall":                  "occupancy_rate_calendar",
    "cal_occ_Jan":                      "occupancy_Jan",
    "cal_occ_Feb":                      "occupancy_Feb",
    "cal_occ_Mar":                      "occupancy_Mar",
    "cal_occ_Apr":                      "occupancy_Apr",
    "cal_occ_May":                      "occupancy_May",
    "cal_occ_Jun":                      "occupancy_Jun",
    "cal_occ_Jul":                      "occupancy_Jul",
    "cal_occ_Aug":                      "occupancy_Aug",
    "cal_occ_Sep":                      "occupancy_Sep",
    "cal_occ_Oct":                      "occupancy_Oct",
    "cal_occ_Nov":                      "occupancy_Nov",
    "cal_occ_Dec":                      "occupancy_Dec",
}

# Rename amenity columns: amenity_dedicated_workspace → has_dedicated_workspace
amenity_rename = {col: col.replace("amenity_", "has_") for col in amenity_cols}
rename_map.update(amenity_rename)

active_out = active_out.rename(columns=rename_map)

active_out.to_csv(OUTPUT_PATH, index=False)
print(f"\n  Saved → {OUTPUT_PATH}")
print(f"  Rows: {len(active_out):,}  |  Columns: {len(active_out.columns)}")
print(f"\nAll columns:")
for c in active_out.columns:
    print(f"  {c}")
