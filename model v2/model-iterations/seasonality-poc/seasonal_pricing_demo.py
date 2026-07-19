"""
SIMULATED / ILLUSTRATIVE DEMO. Not a fitted model, not a refit of Ridge.

Joins the simulated neighborhood seasonal index onto the real, verified
Ridge fair-price output, producing a monthly price curve per listing.
Ridge's predicted_fair_price_usd (the annual-average fair value) is used
unchanged; only a seasonal multiplier is applied on top of it. This keeps
the verified model output and the illustrative layer clearly separate,
nothing here touches ridge_listing_residuals.csv or refits any
coefficient.

real_avg_occupancy_rate is carried alongside the simulated price so the
demo can show a real, historical occupancy figure next to the simulated
price figure for the same month, without blurring which is which.

See SIMULATED_neighborhood_seasonality_README.md in this same folder for
the full methodology and sources behind the seasonal index itself.
"""

import pandas as pd

RIDGE_CSV = "../ridge-model/ridge_listing_residuals.csv"
SEASONALITY_CSV = "SIMULATED_neighborhood_seasonality.csv"
OUTPUT_CSV = "SIMULATED_seasonal_pricing_demo.csv"

# A small, representative sample for the demo, not all 9,752 listings:
# one clearly underpriced, one clearly overpriced, one with a strong
# seasonal swing in its neighborhood. Picked after computing residual
# size and seasonal amplitude below.
N_DEMO_LISTINGS = 6

ridge = pd.read_csv(RIDGE_CSV)
season = pd.read_csv(SEASONALITY_CSV)

merged = ridge.merge(season, on=["borough", "neighborhood"], how="inner")
merged["SIMULATED_seasonal_price_usd"] = (
    merged["predicted_fair_price_usd"] * merged["SIMULATED_price_seasonal_index"]
).round(2)

cols = [
    "listing_id", "listing_name", "borough", "neighborhood", "market_segment",
    "actual_price_usd", "predicted_fair_price_usd", "residual_usd", "pricing_signal",
    "month", "real_avg_occupancy_rate", "neighborhood_seasonality_amplitude_weight",
    "SIMULATED_price_seasonal_index", "SIMULATED_seasonal_price_usd",
]
merged = merged[cols]
merged.to_csv(OUTPUT_CSV, index=False)
print(f"Wrote {len(merged)} rows ({merged['listing_id'].nunique()} listings x 12 months) to {OUTPUT_CSV}")

# --- pick demo listings: most underpriced, most overpriced, strongest seasonal swing ---
per_listing = ridge.dropna(subset=["residual_usd"]).copy()
most_underpriced = per_listing.nsmallest(2, "residual_usd")["listing_id"].tolist()
most_overpriced = per_listing.nlargest(2, "residual_usd")["listing_id"].tolist()

swing = merged.groupby("listing_id")["SIMULATED_seasonal_price_usd"].agg(lambda s: s.max() - s.min())
strongest_swing = swing.nlargest(2).index.tolist()

demo_ids = list(dict.fromkeys(most_underpriced + most_overpriced + strongest_swing))[:N_DEMO_LISTINGS]
demo = merged[merged["listing_id"].isin(demo_ids)]
demo.to_csv("SIMULATED_seasonal_pricing_demo_sample.csv", index=False)
print(f"Demo sample: {len(demo_ids)} listings -> SIMULATED_seasonal_pricing_demo_sample.csv")
print("Listing IDs:", demo_ids)
