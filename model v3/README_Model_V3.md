# Airbnb Revenue Optimizer - Model V3

Model V3 is a separate experimental version. It does not overwrite Model V2.

## Implemented enhancements

1. **Repeated decision support through out-of-fold Ridge pricing**: the Ridge alpha is tuned by segment and every listing receives an out-of-fold fair-price estimate.
2. **Recommendation confidence**: each pricing signal includes an uncertainty proxy, a 0-100 confidence score, and High/Medium/Low label.
3. **Segment diagnostics**: metrics are exported by market segment, host tier, and borough to identify where recommendations are strongest or weakest.
4. **Host-tier-aware comparable logic**: the KNN V3 script first looks for peers matching market segment, listing segment, and host tier; it relaxes the host-tier condition only when the cohort is too small.
5. **Peer-support score**: comparable recommendations include a score based on cohort size and match method.

## Current measured results

The pricing model was executed on 9,752 active NYC listings.

| Segment | Listings | Log R2 | Price R2 | MAE | Median APE |
|---|---:|---:|---:|---:|---:|
| Short stay | 4,008 | 0.605 | 0.419 | $124.08 | 25.1% |
| Monthly | 5,744 | 0.706 | 0.489 | $47.43 | 21.1% |

These figures are broadly consistent with Model V2 and show that V3's main value is better decision support and confidence communication rather than a claim of dramatic accuracy improvement.

## Run

```bash
pip install -r requirements.txt
python src/model_v3.py --input active_listings_clean_v6.csv --output-dir outputs
python src/knn_v3.py --input active_listings_clean_v6.csv --pricing outputs/v3_listing_pricing_signals.csv --output-dir outputs
```

The clean CSV should be placed in the Model V3 root or supplied using an absolute path.

## Important interpretation

A residual is a pricing-review signal, not proof of overpricing or underpricing. Amenity gaps are associations found among comparable high-performing listings, not guaranteed causal improvements.
