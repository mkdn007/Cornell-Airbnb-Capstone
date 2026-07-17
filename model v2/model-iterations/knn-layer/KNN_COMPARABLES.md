# KNN Comparable-Listing Layer — NYC Airbnb Capstone 

## What this is

The **"here's why" layer** that sits on top of the Ridge residual product. The Ridge model tells a host *that* they're mispriced ("you're $40 below fair value"). This layer explains **why** by comparing each listing to its high-performing peers and surfacing the concrete operational gaps it can close.

Together they complete the Option C pitch:
> *"You're underpriced by $X/night — and to capture that yield without hurting occupancy, close your feature gap: your high-performing neighbors offer a dedicated workspace and self-check-in; you don't."*

**Output:** `knn_listing_comparables_segmented.csv` — 9,752 listings.

---

## How it works (per listing)

1. **Find the cohort.** Start with an **exact match** on `segment | market_segment` = `borough | room_type | capacity_tier | (short_stay or monthly)` (e.g. "Brooklyn | Private room | small | short_stay"). Including `market_segment` keeps this **consistent with the Ridge model's split** — a short-stay listing is never benchmarked against monthly rentals, which price and book on different logic. **9,560 of 9,752 listings** matched this way.
2. **KNN fallback.** If a cohort is too small (< 15 listings), fall back to **standardized K-nearest-neighbors** — the 30 closest listings by feature distance (size, location, amenities), restricted to the **same market_segment**. **192 listings** needed this (up from 92 before segmenting — the price of stricter, cleaner cohorts).
3. **Identify high performers.** Within the cohort, the top third by occupancy (`occupancy_rate` = occupied days out of 365).
4. **Compute the gaps:**
   - **Occupancy gap** — how many more days the high performers are booked vs. this listing.
   - **Missing amenities** — amenities that ≥60% of high performers have but this listing lacks. This is the actionable roadmap.

---

## Why KNN here and not as the price model

KNN and Ridge do **different jobs** — they don't compete:

| Aspect   | Ridge                          | KNN                                                  |
|----------|--------------------------------|------------------------------------------------------|
| Question | What's the fair *price*?       | Who are my *peers* and what do they do differently?  |
| Output   | Fair price + residual ($ gap)  | Occupancy benchmark + missing amenities (the "why")  |
| Method   | Regression on features         | Comparable-listing retrieval                         |

KNN was **deliberately not** used as the price model (regression) — Ridge owns that. KNN's only role is peer benchmarking, which is what it's genuinely good at.

---

## What it found

- **Exact-cohort matches:** 9,560 / 9,752 (98%) — comparisons are highly like-for-like, now segment-clean.
- **Mean occupancy gap:** 64 days — the typical listing is booked ~2 months less per year than its high-performing peers. (Lower than the pre-segmentation figure of 90 days, because peers are now genuinely comparable — short-stay listings are no longer measured against high-occupancy monthly rentals.)
- **Mean missing amenities:** 3.3 per listing.
- **Most commonly missing high-impact amenities:** dedicated workspace (2,590), refrigerator (2,427), iron (2,156), fire extinguisher (2,105), cooking basics (2,089).

`dedicated_workspace` topping the list is notable — it's exactly the lever the EDA and Ridge coefficients flagged as valuable, and mirrors the Option C pitch example.

> **Note on segmenting:** an earlier version matched on `segment` alone (ignoring monthly vs short-stay), which let short-stay listings be benchmarked against monthly rentals. Adding `market_segment` to the cohort key fixed this — it shifted 100 listings from exact-match to KNN-fallback and lowered the mean occupancy gap from 90 → 64 days, because the peer sets are now truly comparable.

---

## Output columns

| Column                       | Meaning                                                     |
|------------------------------|-------------------------------------------------------------|
| `listing_id`                 | Airbnb listing ID                                           |
| `segment`                    | borough \| room_type \| capacity_tier                       |
| `market_segment`             | `short_stay` or `monthly` (matches the Ridge split)         |
| `cohort_key`                 | Full matched cohort = `segment \| market_segment`           |
| `match_method`               | `exact_cohort` or `knn_fallback`                            |
| `n_peers`                    | Cohort size                                                 |
| `n_high_performers`          | How many peers are top-third performers                     |
| `my_occupancy_days`          | This listing's occupied days (of 365)                       |
| `peer_high_occupancy_days`   | High performers' average occupied days                      |
| `occupancy_gap_days`         | The gap — how far behind the peers this listing is          |
| `missing_amenities_vs_peers` | Amenities ≥60% of high performers have that this lacks      |
| `n_missing_amenities`        | Count of the above                                          |
| `predicted_fair_price_usd`   | Fair-value benchmark (paired in from Ridge product)         |
| `residual_usd`               | The $ pricing gap (paired in from Ridge product)            |
| `pricing_signal`             | Over/under label (paired in from Ridge product)             |

---

## Caveats

1. **Occupancy is a proxy** — `occupancy_rate` counts unavailable days, which mixes real bookings with host-blocked dates (a known Inside Airbnb limitation).
2. **Correlation, not causation** — "high performers have a workspace" doesn't prove adding one *causes* more bookings; it's a benchmarking signal, not a controlled experiment.
3. **Missing amenities are a starting point** — the 60% threshold flags common peer amenities; a human should prioritize which are realistic to add.

---

## How to re-run

```bash
python "knn-layer/knn_comparables.py" \
    --input active_listings_clean_v6.csv \
    --residuals "ridge-model/ridge_listing_residuals.csv" \
    --output-dir "knn-layer"
```

**Dependency:** run *after* `ridge_residuals_product.py`, since this layer pairs in that model's residuals. If Ridge is re-run, re-run this too.

---

## Files

- `knn-layer/knn_comparables.py` — this script
- `knn-layer/knn_listing_comparables_segmented.csv` — the comparables output (segment-clean)
- [RIDGE_RESIDUAL_PRODUCT.md](../ridge-model/RIDGE_RESIDUAL_PRODUCT.md) — the pricing layer this builds on
- [TESTING_MODELS.md](../testing_models/TESTING_MODELS.md) — the model-selection story
