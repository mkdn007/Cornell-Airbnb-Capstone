# Model V3 Change Log

## Baseline preserved
Model V2 remains unchanged in the team's repository. This package is an independent V3 branch/folder.

## Pricing engine changes
- Kept the segment-specific log-price Ridge framework.
- Tuned Ridge alpha separately for short-stay and monthly segments.
- Retained five-fold out-of-fold scoring and Duan smearing.
- Added prediction uncertainty proxies based on segment error and category support.
- Added confidence scores and labels for every listing.
- Added segment diagnostics by host tier and borough.

## Comparable layer changes
- Added host tier to the first-choice exact cohort.
- Added hierarchical fallback: host-tier exact cohort -> base exact cohort -> KNN fallback.
- Added peer-support and overall recommendation-confidence scores.
- Preserved market-segment boundaries so monthly and short-stay listings are never mixed.

## Why these changes matter
- Hosts should see how confident the system is, not only a single predicted price.
- Enterprise and individual hosts may operate differently; host-tier-aware peers create more defensible comparisons.
- Segment diagnostics reveal where the model needs more data or should avoid strong recommendations.

## Limitations
- The uncertainty score is a practical confidence proxy, not a formal prediction interval.
- Static listing data cannot establish causal amenity ROI.
- Occupancy may include host-blocked calendar dates.
- Seasonality should be added using real monthly market data rather than simulated factors before production claims are made.
