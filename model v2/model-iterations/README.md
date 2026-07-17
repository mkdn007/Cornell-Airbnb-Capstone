# Model Iterations — NYC Airbnb Capstone 

**Recommended reading order:** [1. Testing](testing_models/TESTING_MODELS.md) → [2. Ridge](ridge-model/RIDGE_RESIDUAL_PRODUCT.md) → [3. KNN](knn-layer/KNN_COMPARABLES.md)


How the pricing model evolved from the original OLS baseline into the final Ridge + KNN diagnostic. Read the linked docs in the order below for the full story.

---

## 1. Tested many models — *why?*

Before committing, we ran a systematic bake-off: **6 model types × 3 data segments = 18 runs** on an identical feature set (OLS, Ridge, Elastic Net, Huber, Gamma GLM, Random Forest). The goal was to prove our choice was defensible, not a guess — and to check whether the price skew and functional form were handled correctly. All rigid models landed within 1% of each other (R² 0.745–0.752), confirming the result is robust. → [testing_models/TESTING_MODELS.md](testing_models/TESTING_MODELS.md)

## 2. Changed OLS → Ridge — *why?*

We expanded the feature set from borough-only to include **`neighborhood` (206 values) + `property_type` + `is_superhost` + `sentiment_score`**, which lifted accuracy from R² 0.49 → 0.75. That rich, correlated feature set made plain OLS produce unstable, nonsensical coefficients (e.g. "hot water lowers price"), so we switched to **Ridge**, which gives 2–3× more stable, believable coefficients at the *same* accuracy. Since the product is a diagnostic where coefficients are the host-facing advice, coefficient quality mattered more than raw accuracy. → [ridge-model/RIDGE_RESIDUAL_PRODUCT.md](ridge-model/RIDGE_RESIDUAL_PRODUCT.md)

## 3. Added a KNN layer — *why?*

Ridge tells a host *that* they're mispriced ("$40 below fair value") but not *why*. The **KNN layer** finds each listing's comparable peers, identifies the high-occupancy performers among them, and surfaces the amenities those peers have that the listing is missing — the actionable roadmap. This completes the Option C pitch: "you're underpriced by $X, and here's how to capture it." → [knn-layer/KNN_COMPARABLES.md](knn-layer/KNN_COMPARABLES.md)

## 4. Split by market segment

The bake-off proved short-stay and monthly rentals price on genuinely different logic, so both the **Ridge model and the KNN peer-matching are split by `market_segment`** (short_stay / monthly). A short-stay listing is only ever benchmarked against other short-stay listings — never against monthly rentals. Segmenting the KNN cohorts lowered the mean occupancy gap from 90 → 64 days because the peer comparisons became genuinely fair. → see the split details in both the [Ridge](ridge-model/RIDGE_RESIDUAL_PRODUCT.md) and [KNN](knn-layer/KNN_COMPARABLES.md) docs.

---

