import json
import pandas as pd

SRC = r"C:\Users\stava\OneDrive\Documents\Berkeley_DataViz_FinalProject\d3"
SCRATCH = r"C:\Users\stava\AppData\Local\Temp\claude\c--Users-stava-OneDrive-Documents-75TH\015c245a-15d9-4e73-b4f2-b3c0d03a7b62\scratchpad"

# Reuse the exact same neighborhood index/order as the existing geo file,
# so both segments' data stays aligned to the same shapes without
# rebuilding or re-validating the geojson.
with open(f"{SRC}\\shareable_pricing.json", encoding="utf-8") as f:
    old_pricing = json.load(f)
neighborhoods = old_pricing["neighborhoods"]
idx = {n: i for i, n in enumerate(neighborhoods)}

df = pd.read_csv(r"C:\Users\stava\OneDrive\Documents\Berkeley_DataViz_FinalProject\data\neighborhood_pricing_seasonality_gbm.csv")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def build_segment(seg_name):
    sub_df = df[df["market_segment"] == seg_name]
    annual = sub_df.drop_duplicates("neighborhood").set_index("neighborhood")
    gap = [None] * len(neighborhoods)
    occ_gap = [None] * len(neighborhoods)
    for n in neighborhoods:
        if n in annual.index:
            row = annual.loc[n]
            gap[idx[n]] = round(float(row["avg_residual_pct_of_fair"]), 4)
            occ_gap[idx[n]] = round(float(row["avg_occupancy_gap_days"]), 2)
    monthly = {}
    for m in MONTHS:
        month_sub = sub_df[sub_df["month"] == m].set_index("neighborhood")
        season = [None] * len(neighborhoods)
        occ = [None] * len(neighborhoods)
        for n in neighborhoods:
            if n in month_sub.index:
                row = month_sub.loc[n]
                season[idx[n]] = round(float(row["SIMULATED_price_seasonal_index"]), 4)
                occ[idx[n]] = round(float(row["real_avg_occupancy_rate"]), 4)
        monthly[m] = {"season": season, "occ": occ}
    return {"neighborhoods": neighborhoods, "gap": gap, "occGap": occ_gap, "monthly": monthly}

combined = {
    "shortstay": build_segment("short_stay"),
    "monthly": build_segment("monthly"),
}

out_path = f"{SCRATCH}\\shareable_pricing_segmented.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(combined, f, separators=(",", ":"))

import os
print("wrote", out_path, os.path.getsize(out_path), "bytes")
print("short_stay non-null neighborhoods (gap):", sum(1 for v in combined["shortstay"]["gap"] if v is not None))
print("monthly non-null neighborhoods (gap):", sum(1 for v in combined["monthly"]["gap"] if v is not None))
