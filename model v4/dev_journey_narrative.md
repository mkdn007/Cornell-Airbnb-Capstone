# NYC Airbnb Fair-Price Model: Development Journey

*Interim team writeup: confidence-score fix through the current pricing tool, birds-eye view, and scraper work.*

## 1. Manas's V3 and the confidence-score bug

Started from Manas's V3 model (`model_v3.py`) and its confidence score. Traced `score_confidence()` and found the calibration broken: nearly every listing landed "Low" regardless of actual interval width. Fixed it, verified the output distribution actually spread across Low/Medium/High, pushed as PR #3.

Manas had separately applied his own fix to the same function. Checked it directly rather than trusting the description:
- His math was correct, calibrated properly.
- The output file was never regenerated, still showed 100% "Low."
- A "±10% tolerance band pricing_signal" he described wasn't actually in the code.

Takeaway: verify against actual code and regenerated output, not the writeup.

## 2. Does price actually predict occupancy?

Tested directly before building further. Price + month fixed effect: R² = 0.063. Every feature we had (host tier, room type, amenities, reviews): R² = 0.099. Weak, and adding features barely moved it.

Low-hanging fruit first:
- **Log-price instead of linear-dollar.** Linear model extrapolated to 71% occupancy at $900/night. `occ ~ REAL_OCC[month] + LOG_SLOPE * ln(price/current_price)` flattens realistically at extremes.
- **Empirical-Bayes shrinkage per cohort.** `shrunk = w*own_slope + (1-w)*global_slope`, `w = n/(n+K)`. Pulls noisy small-cohort slopes toward the segment-level estimate.

Explicit about the limit: shrinkage makes the slope statistically defensible, it doesn't raise R². That ceiling is a data problem, not a model problem, see Section 5.

## 3. Seasonality layer

Added a simulated neighborhood-level seasonal price index (cited NYC hotel-market curve) so occupancy-at-a-different-price can be estimated per month, combining real occupancy shape + seasonal index + the pooled log-price slope.

Two honesty mechanisms:
- **Flagged months**: where real occupancy diverges >30pp from peer-implied occupancy at similar price, that month is pinned to real history in the tool instead of price-driven, the gap is too large to be about price.
- **No confident optimal price**: revenue-maximizing search is capped at the highest price any real peer charges. Past that, the tool says "no confident answer" instead of extrapolating.

## 4. Building the UI

**Model layer underneath it**: moved Ridge regression → GBM quantile regression (q10/q50/q90), added conformal calibration (widen q10/q90 by a constant so empirical coverage actually hits 80%). Confidence is now `direction_confidence` (confident raise / confident lower / uncertain, based on whether actual price falls outside vs. inside the calibrated interval), old Low/Medium/High score kept only as internal QA. Added a KNN comparable-listings layer (`knn_v3.py`): exact-cohort match on host tier/room type/segment, falling back to broader KNN match only when needed, powers the peer-occupancy and amenity-gap sections.

**Property-level tool**: one hardcoded listing → second (monthly) listing → consolidated into a single file with a `LISTINGS` data config and a dropdown, so units/copy/peer data/slope/flagged months/amenities all render per listing instead of per hardcoded page. Two corrections mid-build: monthly listings were quoting nightly price (fixed, monthly rent is now primary unit); central fair-price estimate is now always shown, even in lower-confidence cases, rather than hidden. Final set: 5 listings chosen to cover confident-raise, confident-lower, and uncertain across both short-stay and monthly, including one that's overpriced vs. fair value yet still ahead of peers on occupancy, and one that's fairly priced yet behind peers, both shown honestly rather than forced into a clean story.

**Birds-eye map**: was running on stale Ridge-based data. Rebuilt the neighborhood-aggregation pipeline from current GBM/KNN outputs, added a short-stay/monthly segment toggle, verified the swap was real (53 vs. 39 no-data neighborhoods between segments, not a relabel). Map is a from-scratch Web Mercator projection, no tile/CDN library, since the artifact host blocks external requests. Both tools now share a nav bar.

## 5. Scraper: closing the causal gap

Everything above is cohort comparison: how a listing compares to similar listings priced differently right now. That's correlational, it's never observed the same listing at a different price. That's the actual R² ceiling from Section 2, no amount of pooling or feature engineering fixes it because the needed data doesn't exist yet.

Extended the existing calendar-only scraper (`daily_scrape.py`) to also capture real per-stay price via Airbnb's `StaysPdpSections` GraphQL response, requires requesting a bookable date range that respects each listing's own minimum-stay (root cause of early failures, traced to a specific listing before finding it). Reconfigured the scraper to pick a valid date range from calendar data it already collects and log the quoted price to a new `price_snapshots` table, same run, no new infrastructure. Ran across the full 200-listing sample, found and fixed a parsing bug (price shows up in 3 different JSON shapes depending on listing, regex only caught one), verified the fix against real failing cases.

Why it matters: run this daily long enough and we get real within-listing price variation over time, same listing, different real prices, different days. That's what turns "how do similar listings compare" into "how does this listing's own occupancy respond when its own price changes," a materially stronger foundation for the revenue optimizer than a bigger cohort or better features, it's a different kind of evidence, not more of the same kind.
