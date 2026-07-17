"""
SIMULATED / ILLUSTRATIVE DATA GENERATOR
Not a fitted model. Builds a proof-of-concept neighborhood-by-month seasonal
price index for the NYC Airbnb capstone, to be replaced with real data
(e.g. a proper Airbnb calendar-price source) when available.

Construction:
- Demand-timing shape per neighborhood: REAL. Uses occupancy_Jan..Dec,
  already computed in active_listings_clean_v6.csv from actual Inside
  Airbnb calendar availability data (not simulated).
- Price seasonal magnitude: SIMULATED. Airbnb does not publish calendar-level
  price data for NYC (confirmed by checking every archived snapshot back to
  2025-08-01; all have blank price/adjusted_price fields). As a proxy, this
  uses the real NYC hotel market's seasonal ADR (average daily rate) curve,
  averaged over 2016-2019 (pre-pandemic, 4 consistent years) from:
  NYC & Company / CBRE, "NYC Hotel Occupancy, ADR & Room Demand -
  5 Year Trend Report" (Feb 2021):
  https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/newyorkcity/FYI_HotelPerformance_5Year_22821_dk_82d984c7-b953-4b74-a906-0db91402564b.pdf

  The citywide hotel ADR seasonal index is then scaled per neighborhood by
  that neighborhood's own REAL occupancy seasonality (coefficient of
  variation across its 12 real monthly occupancy values) - neighborhoods
  that already show more seasonal swing in real booking/availability data
  get a proportionally larger simulated price swing; flatter neighborhoods
  get a dampened one. This is a deliberate modeling choice to avoid
  applying a uniform citywide swing to every neighborhood regardless of
  how touristy it actually is.

This file and its output are NOT validated against real Airbnb pricing.
Do not present the output as a fitted or verified result.
"""

import pandas as pd
import numpy as np

INPUT_CSV = "../../../active_listings_clean_v6.csv"
OUTPUT_CSV = "SIMULATED_neighborhood_seasonality.csv"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
OCC_COLS = [f"occupancy_{m}" for m in MONTHS]

# Real, cited NYC hotel ADR by month, 2016-2019 average (pre-pandemic, CBRE/NYC & Company).
# Source in module docstring above.
ADR_2016_2019_AVG = {
    "Jan": 209.25, "Feb": 203.75, "Mar": 254.00, "Apr": 283.50,
    "May": 309.75, "Jun": 299.75, "Jul": 259.75, "Aug": 251.00,
    "Sep": 356.75, "Oct": 338.50, "Nov": 316.00, "Dec": 341.25,
}
adr_annual_avg = np.mean(list(ADR_2016_2019_AVG.values()))
CITYWIDE_ADR_SEASONAL_INDEX = {m: v / adr_annual_avg for m, v in ADR_2016_2019_AVG.items()}

df = pd.read_csv(INPUT_CSV)

# Per-neighborhood real average occupancy by month
neigh_occ = df.groupby(["borough", "neighborhood"])[OCC_COLS].mean().reset_index()
neigh_occ["listing_count"] = df.groupby(["borough", "neighborhood"]).size().values

# Real seasonality strength per neighborhood: coefficient of variation across
# its 12 real monthly occupancy values (guard against zero mean).
occ_vals = neigh_occ[OCC_COLS].values
occ_mean = occ_vals.mean(axis=1)
occ_std = occ_vals.std(axis=1)
cov = np.where(occ_mean > 0, occ_std / occ_mean, 0.0)

# Normalize CoV to a 0.5x-1.5x amplitude-scaling weight so no neighborhood's
# simulated swing collapses to zero or blows up unrealistically.
cov_min, cov_max = cov.min(), cov.max()
if cov_max > cov_min:
    amplitude_weight = 0.5 + (cov - cov_min) / (cov_max - cov_min)  # 0.5 - 1.5
else:
    amplitude_weight = np.ones_like(cov)
neigh_occ["seasonality_amplitude_weight"] = amplitude_weight

rows = []
for _, r in neigh_occ.iterrows():
    for m in MONTHS:
        citywide_idx = CITYWIDE_ADR_SEASONAL_INDEX[m]
        # dampen/amplify the citywide swing around 1.0 by this neighborhood's weight
        sim_price_index = 1 + (citywide_idx - 1) * r["seasonality_amplitude_weight"]
        rows.append({
            "borough": r["borough"],
            "neighborhood": r["neighborhood"],
            "listing_count": int(r["listing_count"]),
            "month": m,
            "real_avg_occupancy_rate": round(r[f"occupancy_{m}"], 4),
            "neighborhood_seasonality_amplitude_weight": round(r["seasonality_amplitude_weight"], 4),
            "SIMULATED_price_seasonal_index": round(sim_price_index, 4),
            "data_type": "SIMULATED_PROOF_OF_CONCEPT",
        })

out = pd.DataFrame(rows)
out.to_csv(OUTPUT_CSV, index=False)

print(f"Wrote {len(out)} rows for {neigh_occ.shape[0]} neighborhoods x 12 months")
print(f"Citywide ADR seasonal index (real, cited): {CITYWIDE_ADR_SEASONAL_INDEX}")
print(f"Output: {OUTPUT_CSV}")
