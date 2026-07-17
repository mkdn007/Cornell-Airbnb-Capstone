# Ridge Pricing Residual Product — NYC Airbnb Capstone 

## What this is

The **listing-level pricing diagnostic** — the core deliverable of the Revenue Optimizer. For every active NYC listing it answers:

> *"What should this listing charge given its location, size, amenities, and ratings — and how far is the actual price from that fair value?"*

This replaces the original borough-only OLS residuals with the **Ridge + segment-split** model selected in the bake-off (see [TESTING_MODELS.md](TESTING_MODELS.md)). Accuracy improved from R² 0.49 → 0.75 and median error from 39% → ~24%.

**Output file:** `model-iterations/ridge-model/ridge_listing_residuals.csv` — 9,752 listings.

---

## How it works

1. **Target:** `log(nightly_price)` — corrects the severe price skew (7.36 → 0.27).
2. **Features:** `neighborhood` (206), `room_type`, `property_type`, `host_tier`, `is_superhost`, `max_guests`, `bedrooms`, `beds`, `bathrooms`, 7 rating fields, 20 amenity flags, `sentiment_score`.
3. **Model:** Ridge regression (alpha auto-selected by cross-validation). Ridge gives stable, believable coefficients under multicollinearity — critical because the coefficients are the host-facing advice.
4. **Segment split:** the model is fit **separately** for short-stay vs monthly rentals, because they price on different logic. A short-stay listing is only ever benchmarked against other short-stay listings.
5. **Retransformation:** Duan smearing converts the log prediction back to unbiased dollars.
6. **Out-of-fold scoring:** 5-fold — every listing's fair price comes from a model that did **not** train on that listing, so no listing grades its own homework.

**Residual = actual price − predicted fair price.**
- Positive → priced **above** fair value (potentially overpriced)
- Negative → priced **below** fair value (potentially underpriced)


---

## Accuracy (5-fold out-of-fold)

| Segment    | Listings | R² (log) |  MAE | Median % error |
|------------|---------:|---------:|-----:|---------------:|
| Short-stay |    4,008 |     0.61 | $124 |          25.1% |
| Monthly    |    5,744 |     0.71 |  $47 |          20.9% |

Short-stay is the harder, more variable segment; monthly rentals are more uniform. Reporting them separately is the honest presentation of true nightly-pricing accuracy.

---

## What the product found

| Signal                         | Listings |
|--------------------------------|---------:|
| Below fair value (underpriced) |    5,909 |
| Above fair value (overpriced)  |    3,843 |

The residual distribution is roughly centered (mean +$3, median −$11) — expected, since the model is calibrated to the market average. The action is in the **tails**: listings hundreds of dollars off their fair value are the prime targets for a repricing recommendation.

---

## Output columns

| Column                       | Meaning                                                  |
|------------------------------|----------------------------------------------------------|
| `listing_id`                 | Airbnb listing ID                                        |
| `listing_name`, `listing_url`| Listing title and live URL                               |
| `borough`, `neighborhood`    | Location                                                 |
| `room_type`, `property_type` | Listing type                                             |
| `max_guests`, `host_tier`    | Capacity and host scale                                  |
| `segment`                    | borough \| room_type \| capacity_tier cohort key         |
| `market_segment`             | `short_stay` or `monthly` — which model scored it        |
| `cv_fold`                    | Which of the 5 holdout folds produced this prediction    |
| `actual_price_usd`           | The host's current nightly price                         |
| `predicted_fair_price_usd`   | Model's fair-value benchmark                             |
| `residual_usd`               | actual − fair (the $ gap)                                |
| `residual_pct_of_fair`       | Gap as a % of fair price                                 |
| `pricing_signal`             | Human-readable over/under label                          |

---

## Important caveats

1. **The residual is a signal, not proof of mispricing.** It captures the gap *net of measured features*, but can also reflect omitted quality (photos, view, renovation, exact block, special events).
2. **Do not convert the nightly residual straight into annual revenue** — that requires an occupancy-response assumption.
3. **Correlated rating fields** mean individual coefficients should be read cautiously; the residual (the product) is the reliable output, which is exactly why Ridge was chosen over plain OLS.
4. The residual tells you *that* a gap exists; the **KNN comparable-listing layer** (next phase) explains *why* by surfacing the operational/amenity differences vs. high-performing peers.

---

## How to re-run

```bash
# from the project root
python "model-iterations/ridge-model/ridge_residuals_product.py"
```

Defaults read `active_listings_clean_v6.csv` from the project root and write outputs next to the script. Produces `ridge_listing_residuals.csv` (the product) and `ridge_segment_metrics.csv` (accuracy). Fully reproducible — fixed `random_state=42`.

---

## Files

- `model-iterations/ridge-model/ridge_residuals_product.py` — the production model (this script)
- `model-iterations/ridge-model/ridge_listing_residuals.csv` — the residual product
- `model-iterations/ridge-model/ridge_segment_metrics.csv` — per-segment accuracy
- [TESTING_MODELS.md](../testing_models/TESTING_MODELS.md) — the full model-selection story behind this choice
