# Manas Modeling Section — NYC Airbnb Capstone

## Scope completed

- Primary model: **log-linear Ordinary Least Squares (OLS)**.
- Target: `nightly_price`.
- Inputs: borough, room type, capacity variables, top-20 amenity binaries, review-score variables, and host tier.
- Evaluation: fixed **80/20 train/test split** with `random_state=42`.
- Product output: a listing-level price residual for all 9,752 active listings.
- Alternate model: **Random Forest** using the same features and a log-price target.

The clean GitHub dataset contains 9,752 active listings. Its nightly-price skewness is **7.36**; after applying the natural log, skewness falls to **0.27**. This strongly supports the log-linear specification.

## First-pass holdout results

| Model | MAE | RMSE | R², dollar price | R², log price | Median absolute % error |
|---|---:|---:|---:|---:|---:|
| Log-linear OLS | $113.22 | $218.92 | 0.243 | 0.486 | 39.2% |
| Random Forest | $92.94 | $176.83 | 0.506 | 0.619 | 29.3% |

**Interpretation:** Random Forest is the stronger predictive benchmark. Log-linear OLS should remain the primary product model because it is transparent, stable under the severe price skew, produces positive price estimates, and gives an interpretable residual. Random Forest can be shown as the accuracy comparison.

## Residual definition

`Residual = Actual nightly price − OLS predicted fair price`

- Positive residual: the listing is priced **above** the model benchmark.
- Negative residual: the listing is priced **below** the model benchmark.
- The residual is a conditional pricing-gap signal, not proof of causal mispricing.

The residual file uses **five-fold out-of-fold predictions**, so every listing receives a prediction from a model that was not trained on that listing. The original 80/20 split is also retained in the `split_80_20` column.

## Does KNN plus log OLS make sense?

**Yes, but they should serve different purposes.**

- **Log OLS:** use as the fair-value pricing engine and residual generator.
- **KNN:** use for comparable-listing retrieval and matched benchmarking, not as the primary price model.
- Start with exact cohort matching by borough × room type × capacity tier.
- Use standardized KNN as a fallback when an exact cohort has too few comparable listings.
- Keep Random Forest, rather than KNN regression, as the requested alternate predictive model.

This separation makes Option C coherent: OLS quantifies the pricing gap, while exact matching/KNN explains the operational and amenity differences versus relevant peers.

## Important caveats for the advisor meeting

1. The residual may capture omitted quality factors such as photo quality, renovation level, view, exact block, or special events.
2. The clean-data documentation flags many monthly-rental listings. In this file, **58.9%** have `min_nights > 28`. The final model should either include that flag or report a separate short-stay sensitivity model.
3. Do not translate the nightly residual directly into annual revenue without an occupancy-response assumption.
4. Several review-score fields are highly correlated, so individual OLS coefficients should be interpreted cautiously; the prediction and residual are the main deliverables.

## Files

- `manas_airbnb_modeling.py` — reproducible GitHub-ready pipeline.
- `manas_listing_residuals.csv` — listing-level residual product.
- `manas_model_metrics.csv` — OLS versus Random Forest holdout results.
- `manas_ols_coefficients.csv` — full OLS coefficient table with HC3 robust standard errors.
- `requirements.txt` — Python dependencies.
