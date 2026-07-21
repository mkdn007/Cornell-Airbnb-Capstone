"""
SIMULATED / ILLUSTRATIVE DEMO, v3 target. Not a fitted model, not a refit
of Manas's V3 pricing engine.

Same architecture as seasonal_pricing_demo.py in model v2 (which targets
the v2 Ridge output), retargeted to Manas's V3 pricing signals
(model v3/outputs/v3_listing_pricing_signals.csv): join by borough +
neighborhood, multiply predicted_fair_price_usd by the simulated monthly
seasonal index. V3's model itself is untouched here, no coefficient or
confidence-score logic is recomputed.

confidence_score and confidence_level are carried through from V3
alongside the simulated seasonal price, same principle as carrying real
occupancy alongside it in the v2 version: show the real signal next to
the simulated one, never blur which is which.

CONFIDENCE CAVEAT: this reads from model v3/outputs/, Manas's original,
unfixed output, where every listing's confidence_level is "Low" (a real
calibration bug, root-caused and reproduced in
model v3/proposed-confidence-fix/CONFIDENCE_FIX_WRITEUP.md). If that fix
gets merged, this script should be re-pointed at whatever output path
the fix produces and re-run, the confidence_score/confidence_level
columns here will need a follow-up pass either way, they are not yet
meaningful as-is.
"""

import pandas as pd

V3_CSV = "../outputs/v3_listing_pricing_signals.csv"
SEASONALITY_CSV = "../../model v2/model-iterations/seasonality-poc/SIMULATED_neighborhood_seasonality.csv"
OUTPUT_CSV = "SIMULATED_seasonal_pricing_demo_v3.csv"

v3 = pd.read_csv(V3_CSV)
season = pd.read_csv(SEASONALITY_CSV)

merged = v3.merge(season, on=["borough", "neighborhood"], how="inner")
merged["SIMULATED_seasonal_price_usd"] = (
    merged["predicted_fair_price_usd"] * merged["SIMULATED_price_seasonal_index"]
).round(2)

cols = [
    "listing_id", "listing_name", "borough", "neighborhood", "host_tier", "market_segment",
    "actual_price_usd", "predicted_fair_price_usd", "residual_usd", "pricing_signal",
    "confidence_score", "confidence_level",
    "month", "real_avg_occupancy_rate", "SIMULATED_price_seasonal_index", "SIMULATED_seasonal_price_usd",
]
merged = merged[cols]
merged.to_csv(OUTPUT_CSV, index=False)
print(f"Wrote {len(merged)} rows ({merged['listing_id'].nunique()} listings x 12 months) to {OUTPUT_CSV}")
print("Note: confidence_level here still reflects the unfixed v3 output. See proposed-confidence-fix/ for the diagnosis and fix; re-run this against the fixed output if that gets merged.")
