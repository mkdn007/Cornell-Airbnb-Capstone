"""
KNN comparable-listing layer — NYC Airbnb Capstone (Manas Modeling).

This is the "here's WHY" layer that sits on top of the Ridge residual product.
The Ridge model says "you are priced $X vs fair value"; this layer explains the
gap by comparing each listing to its high-performing peers and surfacing the
concrete operational/amenity differences it can act on.

Method (per listing):
  1. Cohort = exact match on segment_ms = borough | room_type | capacity_tier
     | market_segment (short_stay / monthly). Adding market_segment keeps the
     KNN benchmarking consistent with the Ridge model's monthly/short-stay
     split — a short-stay listing is never compared against monthly rentals.
     If the cohort has too few members, fall back to standardized KNN across
     listings IN THE SAME market_segment only.
  2. High performers = cohort members in the top third of occupancy
     (occupancy_rate = occupied days out of 365).
  3. Peer gap = compare this listing's amenities/attributes against what the
     high performers typically have. Surface the amenities the peers have that
     this listing is missing -> the actionable roadmap.

Inputs:
  active_listings_clean_v6.csv        (features)
  ridge_listing_residuals.csv         (the fair-value residual per listing)

Output:
  knn_listing_comparables.csv — per listing: peer occupancy benchmark,
  missing high-impact amenities, and the paired pricing residual.

Run:
Run (from the project root):
  python "model-iterations/knn-layer/knn_comparables.py"
  # defaults read the clean data + the Ridge residuals and write the
  # segmented comparables next to this script.
"""

from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

MIN_COHORT = 15          # below this, fall back to standardized KNN
N_NEIGHBORS = 30         # neighbors to pull in the KNN fallback
TOP_PERF_QUANTILE = 0.67 # "high performer" = top third of cohort occupancy
MONTHLY_COL = "is_monthly_rental(min_nights>28)"


def main(input_path, residuals_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    resid = pd.read_csv(residuals_path)[
        ["listing_id", "predicted_fair_price_usd", "residual_usd", "pricing_signal"]
    ]

    # market segment (matches the Ridge model split) and the combined cohort key
    df["market_segment"] = np.where(df[MONTHLY_COL] == 1, "monthly", "short_stay")
    df["segment_ms"] = df["segment"].astype(str) + " | " + df["market_segment"]

    amenity_cols = [c for c in df.columns if c.startswith("has_")]
    # numeric feature space for the KNN fallback (distance metric)
    knn_feats = ["max_guests", "bedrooms", "beds", "bathrooms", "latitude",
                 "longitude"] + amenity_cols
    Xz = StandardScaler().fit_transform(df[knn_feats].fillna(df[knn_feats].median()))

    # separate nearest-neighbor index per market_segment so the fallback never
    # crosses the short-stay / monthly boundary
    seg_nn = {}
    for ms, ms_idx in df.groupby("market_segment").groups.items():
        ms_pos = df.index.get_indexer(ms_idx)
        k = min(N_NEIGHBORS + 1, len(ms_pos))
        seg_nn[ms] = (ms_pos, NearestNeighbors(n_neighbors=k).fit(Xz[ms_pos]))

    occ = df["occupancy_rate"].to_numpy()
    rows = []

    for seg, seg_idx in df.groupby("segment_ms").groups.items():
        seg_pos = df.index.get_indexer(seg_idx)
        use_cohort = len(seg_pos) >= MIN_COHORT

        for i in seg_pos:
            if use_cohort:
                peers = seg_pos
                method = "exact_cohort"
            else:
                # fallback: nearest neighbors within the SAME market_segment
                ms = df.iloc[i]["market_segment"]
                ms_pos, nn = seg_nn[ms]
                _, nbr = nn.kneighbors(Xz[i:i + 1])
                peers = np.array([ms_pos[p] for p in nbr[0] if ms_pos[p] != i])
                method = "knn_fallback"

            peer_occ = occ[peers]
            cutoff = np.quantile(peer_occ, TOP_PERF_QUANTILE)
            high = peers[peer_occ >= cutoff]
            if len(high) == 0:
                high = peers

            # amenity gap: amenities >=60% of high performers have that this lacks
            my_amen = df.iloc[i][amenity_cols].to_numpy()
            peer_share = df.iloc[high][amenity_cols].mean().to_numpy()
            missing = [
                amenity_cols[k].replace("has_", "")
                for k in range(len(amenity_cols))
                if peer_share[k] >= 0.60 and my_amen[k] == 0
            ]

            rows.append({
                "listing_id": df.iloc[i]["id"],
                "segment": df.iloc[i]["segment"],
                "market_segment": df.iloc[i]["market_segment"],
                "cohort_key": seg,
                "match_method": method,
                "n_peers": len(peers),
                "n_high_performers": len(high),
                "my_occupancy_days": int(occ[i]),
                "peer_high_occupancy_days": round(float(np.mean(occ[high])), 1),
                "occupancy_gap_days": round(float(np.mean(occ[high]) - occ[i]), 1),
                "missing_amenities_vs_peers": "; ".join(missing) if missing else "(none)",
                "n_missing_amenities": len(missing),
            })

    out = pd.DataFrame(rows).merge(resid, on="listing_id", how="left")
    out.to_csv(output_dir / "knn_listing_comparables_segmented.csv", index=False)

    print(f"Wrote {output_dir/'knn_listing_comparables_segmented.csv'} ({len(out)} listings)")
    print(f"  exact_cohort matches: {(out.match_method=='exact_cohort').sum()}")
    print(f"  knn_fallback matches: {(out.match_method=='knn_fallback').sum()}")
    print(f"  mean occupancy gap vs high performers: "
          f"{out.occupancy_gap_days.mean():.1f} days")
    print(f"  mean missing amenities vs peers: "
          f"{out.n_missing_amenities.mean():.1f}")


if __name__ == "__main__":
    # Defaults resolve relative to this script so it runs from any directory.
    # Project root is two levels up: <root>/model-iterations/knn-layer/
    _HERE = Path(__file__).resolve().parent
    _ROOT = _HERE.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path,
                        default=_ROOT / "active_listings_clean_v6.csv")
    parser.add_argument("--residuals", type=Path,
                        default=_ROOT / "model-iterations" / "ridge-model"
                        / "ridge_listing_residuals.csv")
    parser.add_argument("--output-dir", type=Path, default=_HERE)
    args = parser.parse_args()
    main(args.input, args.residuals, args.output_dir)
