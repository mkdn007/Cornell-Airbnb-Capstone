"""
Rebuild the DataViz map's underlying data from the CURRENT pipeline
(GBM fair-price + calibrated confidence, tonight's model) instead of the
original Ridge-based files it was built on. Same four metrics, same
tidy neighborhood x month x segment shape, just fed by what we actually
landed on instead of an earlier iteration.

Real, not simulated: avg_residual_pct_of_fair and avg_occupancy_gap_days
(from the GBM + KNN outputs), and real_avg_occupancy_rate (recomputed
directly from each listing's real monthly occupancy, split by segment,
rather than reused from the old pooled-segment seasonality file, since
short-stay and monthly occupancy patterns are genuinely different).
Still simulated: SIMULATED_price_seasonal_index, unchanged, shared
across segments, it's an external simulated benchmark, not something
re-derived from this project's own data either version.
"""
import pandas as pd

GBM_CSV = r"C:\Users\stava\AppData\Local\Temp\claude\c--Users-stava-OneDrive-Documents-75TH\015c245a-15d9-4e73-b4f2-b3c0d03a7b62\scratchpad\option1_final\outputs_gbm\v3_gbm_listing_pricing_signals.csv"
KNN_CSV = r"C:\Users\stava\AppData\Local\Temp\claude\c--Users-stava-OneDrive-Documents-75TH\015c245a-15d9-4e73-b4f2-b3c0d03a7b62\scratchpad\option1_final\outputs_knn\v3_knn_recommendations.csv"
RAW_CSV = r"C:\Users\stava\AppData\Local\Temp\claude\c--Users-stava-OneDrive-Documents-75TH\015c245a-15d9-4e73-b4f2-b3c0d03a7b62\scratchpad\option1_final\active_listings_clean_v6.csv"
SEASONALITY_CSV = r"C:\Users\stava\OneDrive\Documents\Capstone\repo_clone\model v2\model-iterations\seasonality-poc\SIMULATED_neighborhood_seasonality.csv"
OUTPUT_CSV = r"C:\Users\stava\OneDrive\Documents\Berkeley_DataViz_FinalProject\data\neighborhood_pricing_seasonality_gbm.csv"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

gbm = pd.read_csv(GBM_CSV)
knn = pd.read_csv(KNN_CSV)
raw = pd.read_csv(RAW_CSV)
season = pd.read_csv(SEASONALITY_CSV)

# ---- pricing gap, real, per neighborhood x segment ----
neigh_pricing = (
    gbm.groupby(["borough", "neighborhood", "market_segment"])
    .agg(avg_residual_pct_of_fair=("residual_pct_of_fair", "mean"), n_listings=("listing_id", "count"))
    .reset_index()
)

# ---- occupancy gap vs. high-performing peers, real, per neighborhood x segment ----
# KNN file doesn't carry neighborhood cleanly post-merge (duplicate
# columns from earlier work), borrow a clean one from gbm via listing_id.
knn_seg = knn[["listing_id", "occupancy_gap_days"]].merge(
    gbm[["listing_id", "borough", "neighborhood", "market_segment"]], on="listing_id", how="left"
)
neigh_opportunity = (
    knn_seg.groupby(["borough", "neighborhood", "market_segment"])
    .agg(avg_occupancy_gap_days=("occupancy_gap_days", "mean"))
    .reset_index()
)

neigh_pricing = neigh_pricing.merge(neigh_opportunity, on=["borough", "neighborhood", "market_segment"], how="left")

# ---- real occupancy rate, per neighborhood x month x segment, recomputed
# directly from real per-listing monthly occupancy, not reused from the
# old pooled-segment file ----
raw["market_segment"] = raw["is_monthly_rental(min_nights>28)"].map({0: "short_stay", 1: "monthly"})
occ_cols = [f"occupancy_{m}" for m in MONTHS]
long_occ = raw.melt(
    id_vars=["borough", "neighborhood", "market_segment"], value_vars=occ_cols,
    var_name="month_col", value_name="real_avg_occupancy_rate",
)
long_occ["month"] = long_occ["month_col"].str.replace("occupancy_", "", regex=False)
real_occ_by_month = (
    long_occ.groupby(["borough", "neighborhood", "market_segment", "month"])
    .agg(real_avg_occupancy_rate=("real_avg_occupancy_rate", "mean"))
    .reset_index()
)

# ---- simulated seasonal index, unchanged, shared across segments ----
season_idx = season[["borough", "neighborhood", "month", "SIMULATED_price_seasonal_index"]]

merged = real_occ_by_month.merge(season_idx, on=["borough", "neighborhood", "month"], how="inner")
merged = merged.merge(neigh_pricing, on=["borough", "neighborhood", "market_segment"], how="inner")

merged = merged[[
    "borough", "neighborhood", "market_segment", "n_listings", "avg_residual_pct_of_fair",
    "avg_occupancy_gap_days", "month", "real_avg_occupancy_rate", "SIMULATED_price_seasonal_index",
]].round({
    "avg_residual_pct_of_fair": 4, "real_avg_occupancy_rate": 4,
    "SIMULATED_price_seasonal_index": 4, "avg_occupancy_gap_days": 2,
})

merged.to_csv(OUTPUT_CSV, index=False)
print(f"Wrote {len(merged)} rows to {OUTPUT_CSV}")
for seg in merged["market_segment"].unique():
    sub = merged[merged["market_segment"] == seg]
    print(f"  {seg}: {sub['neighborhood'].nunique()} neighborhoods x 12 months = {len(sub)} rows")
print(merged.head())
