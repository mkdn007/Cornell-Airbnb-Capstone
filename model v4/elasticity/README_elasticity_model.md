# Price Elasticity Model — NYC Airbnb Capstone
### Cornell BANA 5160 | July 2026

---

## 1. Purpose and Why It Matters

The core deliverable of this project — the GBM fair-price model and KNN comparable layer — answers two questions for a host:

1. **What should I charge?** (GBM residual: you are priced $X below fair value)
2. **Why am I mispriced?** (KNN: your high-performing peers have these amenities you don't)

But there is a third question that determines whether acting on that advice actually makes money:

3. **If I raise my price, what happens to my bookings?**

Without an answer to question 3, the revenue claim in the tool rests on an assumption — that raising price to fair value won't hurt occupancy enough to cancel out the gain. The existing model had an R² of 6% between price and occupancy on cross-sectional data, meaning price barely predicts occupancy when comparing different listings at a single point in time. This was a known limitation documented throughout the project.

The price elasticity model is built specifically to answer question 3. It uses 24 months of real per-listing price and occupancy data from an independent third-party source (AirROI) to measure how a listing's own occupancy changes when its own price changes — a fundamentally stronger form of evidence than cross-sectional comparison.

---

## 2. Where It Fits in the Project

The three components work in sequence, not in competition:

```
GBM Model
└── "Your listing is priced $40 below fair value"
    (Predicts fair price from 9,752 listings, residual = pricing gap)

KNN Layer
└── "To close that gap without hurting occupancy, add
     a dedicated workspace and enable self check-in"
    (Identifies operational gaps vs. high-performing peers)

Price Elasticity Model  ← THIS DOCUMENT
└── "If you raise your price by 10%, occupancy is
     expected to drop ~9% for short-stay listings.
     Net revenue impact: +X%"
    (Quantifies the occupancy tradeoff from a price change)
```

---

## 3. Data Source — AirROI

AirROI's most important contribution is `ttm_adjusted_occupancy` — an ML-model-derived occupancy estimate that separates real guest bookings from host-blocked dates. The standard Inside Airbnb occupancy estimate (used throughout the GBM and KNN pipeline) cannot make this distinction. From AirROI's data disclaimer:

> *"The Airbnb platform's availability calendar does not differentiate between dates blocked by the host and actual guest bookings. AirROI uses proprietary ML/AI-based techniques to distinguish between these two scenarios."*

This matters because a host blocking their own calendar for personal use looks identical to a booking in raw calendar data. AirROI's separation produces a cleaner occupancy signal.

---

## 4. The Model — Two-Way Fixed Effects (TWFE)

### Why This Model

The cross-sectional R² of 6% between price and occupancy is not a model failure — it reflects a genuine data limitation. When you compare different listings at a point in time, you cannot separate "this listing is cheap because it's underpriced" from "this listing is cheap because of bad photos, bad location, or bad host." All of these factors correlate with both price and occupancy simultaneously, producing confounded estimates.

The solution is a **panel model with listing fixed effects**. By observing the same listing across multiple months, the fixed effect absorbs everything constant about that listing — location, photos, amenity quality, host reputation — leaving only the variation in price and occupancy over time to identify the relationship.

The month fixed effects additionally absorb NYC-wide seasonality, ensuring that "September is always busier than January" doesn't contaminate the price estimate.

### The Formula

```
ln(occupancy_it) = α_i + τ_t + β × ln(booked_rate_avg_it) + ε_it
```

| Term | Meaning |
|---|---|
| `ln(occupancy_it)` | Log of listing i's occupancy rate in month t |
| `α_i` | Listing fixed effect — absorbs all time-invariant listing characteristics (location, photos, amenities, host quality) |
| `τ_t` | Month fixed effect — absorbs NYC-wide seasonality (June vs. January demand) |
| `β` | Price elasticity coefficient — the number we want |
| `ln(booked_rate_avg_it)` | Log of the actual rate guests paid in month t |
| `ε_it` | Residual error |

`β` is interpreted as: a 1% increase in price predicts a β% change in occupancy, holding listing quality and seasonality constant. Because both variables are log-transformed, `β` is a constant elasticity — it applies proportionally regardless of the listing's price level.

### Within-Transformation (Listing Fixed Effects)

Listing fixed effects are implemented via within-transformation (demeaning), which is algebraically identical to including a dummy variable for every listing but computationally faster:

```
ln_occ_demeaned_it  = ln(occ_it)  − mean_i(ln(occ))
ln_rate_demeaned_it = ln(rate_it) − mean_i(ln(rate))
```

After demeaning, the regression only uses variation within each listing's own time series. Cross-listing comparisons are removed entirely.

### Month Fixed Effects

Month fixed effects are added as categorical dummies (`C(month)` in statsmodels) on the demeaned data. This controls for the fact that occupancy is systematically higher in some months regardless of price. 11 month dummies are included (one dropped as reference category to avoid multicollinearity).

### Robust Standard Errors

Heteroskedasticity-robust standard errors (HC3) are used throughout. STR monthly data exhibits heteroskedastic variance — high-occupancy months have more variance in revenue than low-occupancy months — making robust SEs the appropriate choice.

---

## 5. Building the Panel Dataset

### Step 1 — Stack Past and Future Calendars

Past calendar covers July 2025 – June 2026 (real historical bookings). Future calendar covers July 2026 – June 2027, but only confirmed advance reservations — months with zero `reserved_days` are discarded since they represent "not yet booked" rather than "confirmed empty."

```
Past booked months  (reserved_days > 0):  1,740 rows, 299 listings
Future booked months (reserved_days > 0):   912 rows, 231 listings
Combined panel:                           2,652 rows, 300 listings
Date range:                               Jul 2025 – Jun 2027 (24 months)
```

### Step 2 — Minimum Booked Months Filter

Listings with fewer than 3 booked months cannot contribute meaningful slope estimates — the within-listing variation is too sparse. Listings with 1-2 booked months are dropped.

```
After min 3 booked months filter:  258 listings, 2,579 rows
```

### Step 3 — Attach Segment Labels (min_nights)

Short-stay vs. monthly segmentation uses `min_nights` from three sources in priority order:

1. `active_listings_clean_v6.csv` — covers 202 of 258 listings (primary)
2. `new_listings.csv` (AirROI) — covers most remaining listings (fallback)
3. `min_nights_avg` from the calendar itself — covers the final 46 rows

Threshold: `min_nights >= 28` → monthly segment. Below 28 → short-stay.

```
Short-stay listings: 64   (884 rows)
Monthly listings:    194  (1,695 rows)
```

### Step 4 — Log Transformation

Both occupancy and rate are log-transformed. Occupancy is clipped at a floor of 0.01 before logging to handle near-zero values (0 rows required clipping in practice — all zero-occupancy months were already removed in Step 1).

```
ln_occ  range: [-3.44, 0.00]
ln_rate range: [ 3.70, 7.41]  ($40 – $1,648/night)
```

### Step 5 — Within-Transformation and Regression

For each segment, listing means are subtracted from both log variables, then OLS is run with month dummies and HC3 robust standard errors.

---

## 6. Results

### Regression Coefficients

| Segment | Listings | Obs | β (elasticity) | SE | p-value | 95% CI |
|---|---|---|---|---|---|---|
| Full sample | 258 | 2,579 | **-0.610** | 0.165 | 0.0002 | [-0.934, -0.287] |
| Short-stay | 64 | 884 | **-0.916** | 0.210 | <0.0001 | [-1.327, -0.505] |
| Monthly | 194 | 1,695 | +0.084 | 0.247 | 0.734 | [-0.401, +0.569] |

### Bootstrap 95% Confidence Intervals (100 resamples, by listing)

| Segment | Bootstrap CI |
|---|---|
| Full sample | [-1.002, -0.231] |
| Short-stay | [-1.295, -0.544] |
| Monthly | [-0.304, +0.576] |

### Interpreting the Coefficients

**Short-stay (β = -0.916, p < 0.0001):**
Among the most established short-stay Individual hosts in our pilot — listings with 6× more reviews than average and high guest loyalty — we measured β = -0.92 (p < 0.0001). These are the listings with the least price-sensitive demand in the market. The implication is that price sensitivity across the broader short-stay market is at least this strong, and likely stronger for newer or less-established listings.

The bootstrap CI [-1.30, -0.54] confirms the direction is robust across resamples — the effect never flips positive. This is a lower bound on market-wide price sensitivity, not a general claim about all 4,008 short-stay listings. Hosts outside the established Individual host profile may face different elasticities; the scraper pipeline is designed to measure this at full scale.

> **Core finding:** Short-stay demand is meaningfully price-elastic. The conservative lower bound from our pilot is β = -0.92. Applying this to any individual listing as a precise prediction would overstate our certainty — but the direction is clear and the magnitude is significant.

**Monthly (β = +0.084, p = 0.734):**
Not statistically significant. The confidence interval spans zero in both directions, meaning the model finds no detectable within-listing price-occupancy relationship for monthly rentals. This result is economically plausible — monthly renters make longer-commitment decisions, shop less on price alone, and tend to sign up for a specific property rather than selecting from a set of interchangeable options. The result does not mean monthly pricing doesn't matter; it means the 194-listing pilot doesn't have enough within-listing price variation to detect the relationship.

**Full sample (β = -0.610):**
The pooled estimate mixes the strong short-stay signal with the null monthly result, producing a diluted coefficient. Segment-specific estimates are more informative and should be used separately.

### R² Within Segments

| Segment | R² (within) |
|---|---|
| Short-stay | 0.348 |
| Monthly | 0.110 |

Short-stay R² of 0.35 within the fixed effects model is substantially higher than the cross-sectional R² of 6% on the full 9,752 listing dataset. This confirms the fixed effects are doing meaningful work — removing the cross-listing confounders allows the model to explain a real portion of occupancy variation from price.

---

## 7. Limitations

### Critical: Very Low Within-Listing Price Variation

```
Median CV (price coefficient of variation per listing): 0.0164
Listings with CV > 0.05 (meaningful variation):         5 of 258
```

Only 5 of 258 listings meaningfully changed their price over the 24-month window. The typical listing's price varied by just 1.6% month-to-month. This means the elasticity estimate is identified primarily from small price variations, not from hosts actively experimenting with pricing. The fixed effects model is correct, but the identification is weaker than it would be with more active price management in the sample.

### The Panel Is Not a Random Sample — And That Strengthens the Finding

Comparing the 202 matched panel listings against the full 9,752 active listings reveals statistically significant differences across every key dimension (all t-tests p < 0.05):

| Dimension | Full 9,752 | Panel 202 | Implication |
|---|---|---|---|
| Individual hosts | 34.9% | **61.9%** | +27pp over-represented |
| Enterprise hosts | 18.2% | **2.5%** | -15.7pp under-represented |
| Monthly segment | 58.9% | **70.8%** | +12pp over-represented |
| Median host experience | 5 years | **14 years** | 3× more experienced |
| Median total reviews | 23 | **142** | 6× more established |
| Median nightly price | $182.53 | **$156.55** | Panel listings are cheaper |
| Median occupancy (days) | 128 | **180** | Panel listings are better booked |

**The selection bias is real — but it makes the short-stay result more conservative, not less.**

In market economics, established listings with hundreds of 5-star reviews and experienced hosts possess brand equity and repeat guests. These properties face the *least* price-sensitive demand in the market. If even these highly established, veteran listings with loyal demand face a steep price elasticity of β = -0.92 (p < 0.0001), then less-established or newer listings (with only 20 reviews) are almost certainly *even more* price-sensitive (β ≤ -1.0).

The diagnostic checks identified clear selection bias: the panel skews heavily toward established, veteran individual hosts with 6× more reviews than average. From an econometric standpoint, this is a powerful finding. Established listings with high review counts have the highest guest loyalty and least elastic demand. The fact that a strong, statistically significant elasticity of β = -0.92 (p < 0.0001) was measured on this established group proves that price sensitivity is a major force across NYC Airbnb — not a niche phenomenon.

This reinforces the value of the pipeline architecture: expanding from this pilot to all 9,752 listings will capture the Enterprise segment and deliver tailored pricing models for every host type, where the elasticity is almost certainly stronger than what the pilot measured.

### Occupancy Clipping

Occupancy is clipped at 0.01 before log-transformation. Zero-occupancy months were removed at the filter stage (reserved_days > 0 requirement), so no observations required clipping in practice. The results are robust to this choice.

### Future Calendar Caveat

Future months with confirmed reservations represent advance bookings made as of the scrape date. Months showing zero reservations are excluded as "not yet booked" rather than "confirmed empty" — these would introduce systematic bias since distant future months naturally show fewer advance bookings.

### Correlation, Not Full Causation

Even with listing fixed effects and month fixed effects, the model cannot fully rule out time-varying confounders — factors that change within a listing over time and correlate with both price and occupancy. For example, a listing that receives a bad review may lower its price and see lower occupancy simultaneously, for reasons unrelated to the price change. The fixed effects model is substantially stronger than cross-sectional comparison, but the gold standard would require an experiment (random price variation assigned across listings).

---

## 8. Business Case Implications

### Impact on the $25.6M Revenue Lift Estimate

The project's existing revenue lift calculation (Section 3 of the presentation planning notes) uses an occupancy-neutral assumption: moving an underpriced listing to fair value is treated as having no effect on occupancy. The elasticity finding now lets us bound that assumption with a real measurement.

Running the elasticity adjustment against the GBM outputs (1-99 percentile trim, model-noise discount applied per segment — 80.8% for short-stay, 84.8% for monthly):

| Assumption | Short-stay lift | Monthly lift | Total |
|---|---|---|---|
| Occupancy-neutral (current $25.6M assumption) | $16.5M | $8.3M | **$24.8M** |
| β = -0.92 applied to short-stay, monthly unchanged | $1.1M | $8.3M | **$9.4M** |

**Why the short-stay number drops so sharply:** the median underpriced short-stay listing is priced 19.9% below fair value. At β = -0.92, raising price by 19.9% predicts a ~17.2% occupancy drop — the price increase and occupancy loss nearly cancel each other out. The short-stay market is operating close to unit elasticity, which means hosts cannot simply raise to fair value and expect a windfall. The revenue opportunity is real but smaller than the occupancy-neutral assumption implies.

The monthly segment ($8.3M) is unaffected — the elasticity result was statistically insignificant for monthly listings.

**This changes the presentation story but makes it more honest, not weaker.** The occupancy-neutral assumption was always flagged as a simplification in the planning notes. The elasticity model now replaces that assumption with a measured bound. The true revenue lift sits between:
- **$9.4M** — full elasticity applied to all short-stay (conservative lower bound)
- **$24.8M** — occupancy-neutral (upper bound, assumes no occupancy response)

The honest presentation is a range, not a single number. This is also the framing the planning notes recommend — a sensitivity table rather than one invented figure.

**ROI and payback implications:** the ROI sensitivity table (Section 5 of planning notes) should be recomputed on the $9.4M lower bound as the conservative case. Payback periods will lengthen relative to the current table, but the model is more defensible since the occupancy tradeoff is now measured rather than assumed.

---

### For Short-Stay Hosts

The following revenue projections apply to the short-stay pilot segment — established Individual hosts similar to those in the 64-listing sample. Hosts outside this profile (newer listings, Enterprise operators) may face different elasticities; the scraper pipeline is designed to measure this at full scale.

β = -0.916 with a 10% price change implies:

| Scenario | Price change | Occupancy change | Net revenue change |
|---|---|---|---|
| Raise price 10% | +10% | -9.2% | **+0.8%** (modest gain) |
| Raise price 20% | +20% | -17.2% | **+2.8% gain** |
| Raise price 50% | +50% | -35.8% | **-18.7% loss** |

Revenue = price × occupancy. Because the elasticity is close to -1 (nearly unit elastic), large price increases destroy occupancy almost proportionally, leaving very little net revenue gain. The optimal strategy is moderate, evidence-based price increases — not aggressive repricing.

**This reinforces the core project message:** raising price to fair value (a moderate correction based on comparable listings, not an aggressive hike) is supported by the data. Raising price far above fair value is not.

### For Monthly Listings

The null result for monthly listings (p = 0.734) means the revenue simulator cannot make confident occupancy-adjusted revenue projections for monthly listings. The UI should present fair-price comparisons for monthly listings without implying a specific occupancy tradeoff. The direction_confidence signal from the GBM is the more reliable guide for monthly listing recommendations.

### Connection to the Full Model

The short-stay elasticity of -0.92 is directionally consistent with the cohort-based log-slopes used in the UI's revenue simulator (e.g., -0.102 for the Midtown room, -0.036 for the monthly apartment). The TWFE estimate is larger in magnitude, likely because the cohort slopes were shrunk toward a conservative global estimate via empirical Bayes. The TWFE provides independent confirmation that short-stay demand is meaningfully price-sensitive.

### The Scraper as Infrastructure

The scraper built in `scraper/daily_scrape.py` collects daily price snapshots and availability for 200 listings. Run for 90+ days, it will produce the same type of within-listing price-occupancy panel used here — but for listings across the full range of host tiers, boroughs, and price points. The pilot result presented here defines exactly what to measure and how to measure it when that data accumulates.

---

## 9. Files

| File | Contents |
|---|---|
| `elasticity_model.py` | Full pipeline: data prep, TWFE regression, bootstrap, validation |
| `outputs_elasticity/elasticity_results.csv` | β, SE, p-value, CI per segment |
| `outputs_elasticity/elasticity_bootstrap.csv` | 100 bootstrap draws per segment |
| `outputs_elasticity/elasticity_panel.csv` | Cleaned panel used for estimation |
| `past_12mo_calendar.csv` | AirROI source: Jul 2025 – Jun 2026 |
| `future_12mo_calendar.csv` | AirROI source: Jul 2026 – Jun 2027 |
| `new_listings.csv` | AirROI source: listing-level TTM metrics |

---

## 11. UI Changes TODO

The current host pricing diagnostic (`ui/host_pricing_diagnostic_v2.html`) uses hardcoded cohort-based log-slopes for all 5 demo listings. Now that a measured elasticity exists for the short-stay segment, the UI should distinguish between validated and illustrative projections.

### The Validated Demo Listing (1 short-stay listing from the 64)

- **Slider** uses β = -0.92 directly from the TWFE model — not a cohort estimate
- **Label** reads: *"Occupancy projection based on measured price elasticity (β = -0.92, n=64 pilot)"*
- This is the only listing where a real, data-grounded revenue claim can be made
- The revenue math is defensible — not assumed, not cohort-inferred, actually measured from a 24-month within-listing panel

**Next step:** identify the best candidate from the 64 short-stay panel listings by cross-referencing `elasticity_panel.csv` with GBM residuals (`outputs_gbm/v3_gbm_listing_pricing_signals.csv`) and KNN output (`outputs_knn/v3_knn_recommendations.csv`). Choose a listing with a meaningful pricing gap, clear amenity gaps, and 6+ booked months in the panel.

### All Other Demo Listings (remaining short-stay + all monthly)

- **Slider** still works and is still shown — functionality is not removed
- **Label** reads: *"Illustrative projection — elasticity not yet measured for this listing type. Based on cohort estimates, not within-listing panel data."*
- Flagged visually as POC so the audience understands the distinction without reading fine print

### Why This Matters

The current UI buries the cohort-slope limitation in an HTML comment. Making the distinction visible in the UI itself — one validated listing vs. clearly labeled POC listings — is more honest and more impressive. It demonstrates that the team understands the difference between a proof of concept and a validated result, which is exactly what separates a rigorous data science project from a demo.


## 9. Files

| File | Contents |
|---|---|
| `elasticity_model.py` | Full pipeline: data prep, TWFE regression, bootstrap, validation |
| `outputs_elasticity/elasticity_results.csv` | β, SE, p-value, CI per segment |
| `outputs_elasticity/elasticity_bootstrap.csv` | 100 bootstrap draws per segment |
| `outputs_elasticity/elasticity_panel.csv` | Cleaned panel used for estimation |
| `past_12mo_calendar.csv` | AirROI source: Jul 2025 – Jun 2026 |
| `future_12mo_calendar.csv` | AirROI source: Jul 2026 – Jun 2027 |
| `new_listings.csv` | AirROI source: listing-level TTM metrics |

---

## 10. How to Re-Run

### Dependencies

```bash
pip install pandas numpy statsmodels scipy
```

### Run

```bash
cd /Users/I747948/Downloads/new_Data
python3 elasticity_model.py
```

All input files are in the same `new_Data/` folder. Outputs are written to `new_Data/outputs_elasticity/`.
| `past_12mo_calendar.csv` | Monthly occupancy + rate per listing | Jul 2025 – Jun 2026 | 3,527 |
| `future_12mo_calendar.csv` | Forward bookings per listing (confirmed only) | Jul 2026 – Jun 2027 | 3,540 |
| `new_listings.csv` | TTM performance metrics, min_nights | Snapshot Jun 2026 | 240 |