"""
SIMULATED / ILLUSTRATIVE DEMO, v3 target. Not a fitted model, not a refit
of the V3 pricing engine.

Retargeted to the GBM pipeline's output (../outputs_gbm/), which replaced
Ridge tonight: join by borough + neighborhood, multiply predicted_fair_price_usd
and its calibrated interval bounds by the simulated monthly seasonal
index. The pricing model itself is untouched here, no coefficient or
interval logic is recomputed, only scaled by month.

direction_confidence is recomputed per month, not just carried through
flat from the annual value. The annual direction_confidence compares
actual_price_usd to the annual calibrated interval [predicted_price_q10,
predicted_price_q90]; naively carrying that single call across all 12
months would be actively misleading, a listing could show "Confident:
raise price" in a month where the seasonally-adjusted fair price is
already close to (or below) the actual price, since the annual call was
never re-evaluated at the resolution it's shown at. Both are included
below (direction_confidence_annual, direction_confidence_monthly) so the
difference is visible rather than hidden, they can and do disagree.

confidence_score and confidence_level (internal-QA-only, not meant for
a host-facing UI, see model_v3_gbm.py) are carried through unchanged
alongside the simulated seasonal price, same principle as carrying real
occupancy alongside it in the v2 version: show the real signal next to
the simulated one, never blur which is which.
"""

import numpy as np
import pandas as pd

V3_CSV = "../outputs_gbm/v3_gbm_listing_pricing_signals.csv"
SEASONALITY_CSV = "SIMULATED_neighborhood_seasonality.csv"
OUTPUT_CSV = "SIMULATED_seasonal_pricing_demo_v3.csv"

v3 = pd.read_csv(V3_CSV)
season = pd.read_csv(SEASONALITY_CSV)

merged = v3.merge(season, on=["borough", "neighborhood"], how="inner")
merged["SIMULATED_seasonal_price_usd"] = (
    merged["predicted_fair_price_usd"] * merged["SIMULATED_price_seasonal_index"]
).round(2)

# Scale the calibrated interval bounds by the same seasonal index, then
# re-evaluate direction confidence against actual price at *this* month's
# resolution, exactly the same rule model_v3_gbm.py uses annually.
seasonal_q10 = merged["predicted_price_q10"] * merged["SIMULATED_price_seasonal_index"]
seasonal_q90 = merged["predicted_price_q90"] * merged["SIMULATED_price_seasonal_index"]
merged["SIMULATED_seasonal_q10_usd"] = seasonal_q10.round(2)
merged["SIMULATED_seasonal_q90_usd"] = seasonal_q90.round(2)

actual = merged["actual_price_usd"]
merged["direction_confidence_monthly"] = np.where(
    actual < seasonal_q10, "Confident: raise price",
    np.where(actual > seasonal_q90, "Confident: lower price", "Uncertain (within plausible range)")
)
merged = merged.rename(columns={"direction_confidence": "direction_confidence_annual"})

cols = [
    "listing_id", "listing_name", "borough", "neighborhood", "host_tier", "market_segment",
    "actual_price_usd", "predicted_fair_price_usd", "residual_usd", "pricing_signal",
    "direction_confidence_annual",
    "confidence_score", "confidence_level",
    "month", "real_avg_occupancy_rate", "SIMULATED_price_seasonal_index",
    "SIMULATED_seasonal_price_usd", "SIMULATED_seasonal_q10_usd", "SIMULATED_seasonal_q90_usd",
    "direction_confidence_monthly",
]
merged = merged[cols]
merged.to_csv(OUTPUT_CSV, index=False)

n_disagree = (merged["direction_confidence_annual"] != merged["direction_confidence_monthly"]).sum()
print(f"Wrote {len(merged)} rows ({merged['listing_id'].nunique()} listings x 12 months) to {OUTPUT_CSV}")
print(f"direction_confidence_monthly distribution:\n{merged['direction_confidence_monthly'].value_counts().to_string()}")
print(f"\nMonths where the monthly call disagrees with the flat annual call: {n_disagree} of {len(merged)} "
      f"({n_disagree/len(merged)*100:.1f}%), this is exactly the case a flat annual label would have hidden.")
