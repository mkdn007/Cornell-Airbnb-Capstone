"""
Price Elasticity Model — NYC Airbnb Capstone
=============================================

Two-Way Fixed Effects (TWFE) log-log regression estimating within-listing
price elasticity of occupancy demand.

Model:
    ln(occupancy_it) = α_i + τ_t + β × ln(booked_rate_avg_it) + ε_it

    α_i  = listing fixed effect (absorbs location, photos, amenities,
            host quality — everything constant about a listing)
    τ_t  = month fixed effect (absorbs NYC-wide seasonality)
    β    = price elasticity: a 1% price increase → β% occupancy change

Inputs:
    new_Data/past_12mo_calendar.csv   — Jul 2025 – Jun 2026, per listing/month
    new_Data/future_12mo_calendar.csv — Jul 2026 – Jun 2027, confirmed bookings
    model/active_listings_clean_v6.csv — primary source for min_nights
    new_Data/new_listings.csv          — fallback min_nights source

Outputs:
    model/outputs_elasticity/elasticity_results.csv   — β, SE, CI per segment
    model/outputs_elasticity/elasticity_bootstrap.csv — 100 bootstrap draws
    model/outputs_elasticity/elasticity_panel.csv     — cleaned panel used

Run:
    python model/elasticity_model.py
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT        = Path("/Users/I747948/Downloads")
DATA_DIR    = ROOT / "new_Data"
MODEL_DIR   = ROOT / "nyc_airbnb_final_package" / "model"
OUT_DIR     = DATA_DIR / "outputs_elasticity"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAST_CAL    = DATA_DIR / "past_12mo_calendar.csv"
FUT_CAL     = DATA_DIR / "future_12mo_calendar.csv"
ACTIVE      = MODEL_DIR / "active_listings_clean_v6.csv"
AIRROI_LIST = DATA_DIR / "new_listings.csv"

# ── Config ─────────────────────────────────────────────────────────────────────
MIN_BOOKED_MONTHS = 3       # drop listings with fewer booked months
OCC_FLOOR         = 0.01    # clip occupancy before log (avoids log(0))
N_BOOTSTRAP       = 100     # bootstrap resamples
MONTHLY_THRESHOLD = 28      # min_nights >= this → monthly segment
RANDOM_SEED       = 42


# ── Step 1: Load and stack calendar data ──────────────────────────────────────
print("=" * 60)
print("STEP 1 — Load calendar data")

past = pd.read_csv(PAST_CAL)
fut  = pd.read_csv(FUT_CAL)

past['listing_id'] = past['listing_id'].astype(str)
fut['listing_id']  = fut['listing_id'].astype(str)

# Keep only months with actual bookings
past_booked = past[past['reserved_days'] > 0].copy()
fut_booked  = fut[fut['reserved_days'] > 0].copy()

combined = pd.concat([past_booked, fut_booked], ignore_index=True)
print(f"  Raw booked rows (past + future): {len(combined):,}")
print(f"  Unique listings:                 {combined['listing_id'].nunique()}")

# Drop listings with too few booked months to estimate a slope
months_per = combined.groupby('listing_id').size()
keep_ids   = months_per[months_per >= MIN_BOOKED_MONTHS].index
panel      = combined[combined['listing_id'].isin(keep_ids)].copy()

print(f"  After min {MIN_BOOKED_MONTHS} booked months filter:")
print(f"    Listings: {panel['listing_id'].nunique()}")
print(f"    Rows:     {len(panel):,}")


# ── Step 2: Attach min_nights for segment split ────────────────────────────────
print("\nSTEP 2 — Attach min_nights for segment split")

# Source 1: active_listings_clean_v6
active = pd.read_csv(ACTIVE, usecols=['id', 'min_nights'])
active['id'] = active['id'].astype(str)
active = active.rename(columns={'id': 'listing_id'})

panel = panel.merge(active, on='listing_id', how='left')
covered_active = panel['min_nights'].notna().sum()
print(f"  Covered by active_listings_clean_v6: {panel['listing_id'][panel['min_nights'].notna()].nunique()} listings")

# Source 2: AirROI new_listings (fallback)
airroi = pd.read_csv(AIRROI_LIST, usecols=['listing_id', 'min_nights'],
                     on_bad_lines='skip')
airroi['listing_id'] = airroi['listing_id'].astype(str)
airroi['min_nights_airroi'] = pd.to_numeric(airroi['min_nights'], errors='coerce')
airroi = airroi.drop(columns='min_nights')

panel = panel.merge(airroi, on='listing_id', how='left')
mask_airroi = panel['min_nights'].isna() & panel['min_nights_airroi'].notna()
panel.loc[mask_airroi, 'min_nights'] = panel.loc[mask_airroi, 'min_nights_airroi']
print(f"  Filled from AirROI new_listings:     {mask_airroi.sum()} rows")

# Source 3: calendar min_nights_avg (final fallback)
mask_cal = panel['min_nights'].isna()
panel.loc[mask_cal, 'min_nights'] = panel.loc[mask_cal, 'min_nights_avg']
print(f"  Filled from calendar min_nights_avg: {mask_cal.sum()} rows")

# Force numeric — all three sources now merged, cast once cleanly
panel['min_nights'] = pd.to_numeric(panel['min_nights'], errors='coerce')
print(f"  Still null after all sources:        {panel['min_nights'].isna().sum()}")

panel['segment'] = np.where(
    panel['min_nights'] >= MONTHLY_THRESHOLD, 'monthly', 'short_stay'
)
print(f"\n  Segment distribution:")
print(panel.groupby('segment')['listing_id'].nunique().rename('unique_listings').to_string())
print(panel['segment'].value_counts().rename('rows').to_string())


# ── Step 3: Feature engineering ───────────────────────────────────────────────
print("\nSTEP 3 — Feature engineering")

panel['occ_clipped']  = panel['occupancy'].clip(lower=OCC_FLOOR)
panel['ln_occ']       = np.log(panel['occ_clipped'])
panel['ln_rate']      = np.log(panel['booked_rate_avg'])
panel['month']        = pd.to_datetime(panel['date']).dt.to_period('M').astype(str)

# Sanity check
print(f"  ln_occ  — min: {panel['ln_occ'].min():.3f}, max: {panel['ln_occ'].max():.3f}")
print(f"  ln_rate — min: {panel['ln_rate'].min():.3f}, max: {panel['ln_rate'].max():.3f}")
print(f"  Rows clipped at OCC_FLOOR ({OCC_FLOOR}): {(panel['occupancy'] < OCC_FLOOR).sum()}")

# Save cleaned panel
panel.to_csv(OUT_DIR / 'elasticity_panel.csv', index=False)
print(f"\n  Saved panel → outputs_elasticity/elasticity_panel.csv")


# ── Step 4: Fit TWFE model ─────────────────────────────────────────────────────
print("\nSTEP 4 — Fit Two-Way Fixed Effects model")

def fit_twfe(df, label):
    """
    Fit log-log TWFE regression.
    Listing fixed effects via within-transformation (demean by listing).
    Month fixed effects via C(month) dummies in formula.
    Returns result dict.
    """
    if len(df) < 50 or df['listing_id'].nunique() < 10:
        print(f"  [{label}] Too few observations — skipping")
        return None

    # Within-transform: subtract each listing's mean from ln_occ and ln_rate
    # This is algebraically identical to including listing dummies but faster
    df = df.copy()
    df['ln_occ_dm']  = df['ln_occ']  - df.groupby('listing_id')['ln_occ'].transform('mean')
    df['ln_rate_dm'] = df['ln_rate'] - df.groupby('listing_id')['ln_rate'].transform('mean')

    # Month fixed effects on the demeaned data
    formula = 'ln_occ_dm ~ ln_rate_dm + C(month)'
    model   = smf.ols(formula, data=df).fit(cov_type='HC3')

    beta   = model.params['ln_rate_dm']
    se     = model.bse['ln_rate_dm']
    pval   = model.pvalues['ln_rate_dm']
    ci_lo  = model.conf_int().loc['ln_rate_dm', 0]
    ci_hi  = model.conf_int().loc['ln_rate_dm', 1]
    r2     = model.rsquared
    n_obs  = int(model.nobs)
    n_list = df['listing_id'].nunique()

    print(f"\n  [{label}]")
    print(f"    n_listings = {n_list}, n_obs = {n_obs}")
    print(f"    β (elasticity) = {beta:.4f}  SE = {se:.4f}  p = {pval:.4f}")
    print(f"    95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
    print(f"    R² (within) = {r2:.4f}")
    print(f"    Interpretation: 10% price increase → {beta*10:.2f}% occupancy change")

    return {
        'segment':      label,
        'n_listings':   n_list,
        'n_obs':        n_obs,
        'beta':         round(beta, 6),
        'se_HC3':       round(se, 6),
        'p_value':      round(pval, 6),
        'ci_95_low':    round(ci_lo, 6),
        'ci_95_high':   round(ci_hi, 6),
        'r2_within':    round(r2, 6),
        'pct_occ_change_per_10pct_price': round(beta * 10, 3),
    }


segments = {
    'full_sample': panel,
    'short_stay':  panel[panel['segment'] == 'short_stay'],
    'monthly':     panel[panel['segment'] == 'monthly'],
}

results = []
for label, df in segments.items():
    r = fit_twfe(df, label)
    if r:
        results.append(r)

results_df = pd.DataFrame(results)
results_df.to_csv(OUT_DIR / 'elasticity_results.csv', index=False)
print(f"\n  Saved results → outputs_elasticity/elasticity_results.csv")


# ── Step 5: Bootstrap confidence intervals ────────────────────────────────────
print("\nSTEP 5 — Bootstrap (resample by listing, not by row)")

rng = np.random.default_rng(RANDOM_SEED)

def bootstrap_elasticity(df, n_bootstrap, label):
    """
    Resample listings (not rows) to preserve panel structure.
    Returns array of beta estimates.
    """
    listing_ids = df['listing_id'].unique()
    betas = []

    for i in range(n_bootstrap):
        sampled = rng.choice(listing_ids, size=len(listing_ids), replace=True)
        # Build resampled panel — add suffix to deduplicate repeated listings
        frames = []
        for j, lid in enumerate(sampled):
            chunk = df[df['listing_id'] == lid].copy()
            chunk['listing_id'] = f"{lid}_{j}"
            frames.append(chunk)
        boot_df = pd.concat(frames, ignore_index=True)

        # Recompute within-transform on resampled panel
        boot_df['ln_occ_dm']  = boot_df['ln_occ']  - boot_df.groupby('listing_id')['ln_occ'].transform('mean')
        boot_df['ln_rate_dm'] = boot_df['ln_rate'] - boot_df.groupby('listing_id')['ln_rate'].transform('mean')

        try:
            m    = smf.ols('ln_occ_dm ~ ln_rate_dm + C(month)', data=boot_df).fit(disp=0)
            betas.append(m.params['ln_rate_dm'])
        except Exception:
            continue

    return np.array(betas)


boot_rows = []
for label, df in segments.items():
    if df['listing_id'].nunique() < 10:
        continue
    print(f"  Bootstrapping [{label}] — {N_BOOTSTRAP} resamples...")
    betas = bootstrap_elasticity(df, N_BOOTSTRAP, label)
    ci_lo, ci_hi = np.percentile(betas, [2.5, 97.5])
    print(f"    Bootstrap 95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]  (mean β = {betas.mean():.4f})")

    for b in betas:
        boot_rows.append({'segment': label, 'beta_bootstrap': round(b, 6)})

boot_df_out = pd.DataFrame(boot_rows)
boot_df_out.to_csv(OUT_DIR / 'elasticity_bootstrap.csv', index=False)
print(f"\n  Saved bootstrap → outputs_elasticity/elasticity_bootstrap.csv")


# ── Step 6: Validation checks ─────────────────────────────────────────────────
print("\nSTEP 6 — Validation checks")

# Check 1: Does price variation actually exist per listing?
price_cv = (panel.groupby('listing_id')['ln_rate']
            .std() / panel.groupby('listing_id')['ln_rate'].mean())
print(f"\n  Price variation (CV of rate per listing):")
print(f"    Median CV: {price_cv.median():.4f}")
print(f"    Listings with CV > 0.05: {(price_cv > 0.05).sum()} of {len(price_cv)}")
print(f"    Listings with CV > 0.10: {(price_cv > 0.10).sum()} of {len(price_cv)}")
print(f"    Listings with CV = 0 (no variation): {(price_cv == 0).sum()}")

# Check 2: Are short-stay and monthly elasticities different direction/magnitude?
if len(results_df) >= 3:
    ss = results_df[results_df['segment'] == 'short_stay']
    mo = results_df[results_df['segment'] == 'monthly']
    if len(ss) and len(mo):
        print(f"\n  Segment comparison:")
        print(f"    Short-stay β: {ss['beta'].values[0]:.4f}")
        print(f"    Monthly β:    {mo['beta'].values[0]:.4f}")
        if abs(ss['beta'].values[0]) > abs(mo['beta'].values[0]):
            print(f"    Short-stay guests are MORE price-sensitive than monthly (expected)")
        else:
            print(f"    Monthly guests are more price-sensitive than short-stay (unexpected — check data)")

# Check 3: Occupancy clipping impact
clipped_pct = (panel['occupancy'] < OCC_FLOOR).mean() * 100
print(f"\n  Occupancy clipping: {clipped_pct:.1f}% of rows clipped at {OCC_FLOOR}")
print(f"  (These are months with near-zero occupancy — clipping avoids log(0))")

# Check 4: Month coverage
print(f"\n  Month coverage in panel:")
print(panel['month'].value_counts().sort_index().to_string())


# ── Final summary ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("FINAL RESULTS SUMMARY")
print("=" * 60)
print(results_df[['segment','n_listings','n_obs','beta',
                   'ci_95_low','ci_95_high','p_value',
                   'pct_occ_change_per_10pct_price']].to_string(index=False))
print()
print("Bootstrap 95% CIs:")
for seg in boot_df_out['segment'].unique():
    b = boot_df_out[boot_df_out['segment'] == seg]['beta_bootstrap']
    lo, hi = np.percentile(b, [2.5, 97.5])
    print(f"  {seg}: [{lo:.4f}, {hi:.4f}]")
print()
print("Outputs written to: model/outputs_elasticity/")
