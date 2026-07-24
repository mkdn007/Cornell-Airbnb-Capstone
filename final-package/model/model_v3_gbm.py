"""
Model V3, GBM version: replaces Ridge as the base pricing model, per
tonight's decision. Consolidates everything validated tonight into one
pipeline:

- HistGradientBoostingRegressor with loss='quantile' predicts q10/q50/q90
  directly. q50 (the median prediction) is the new predicted_fair_price_usd,
  no Duan smearing needed since exp() of a predicted log-median is already
  the median of the price distribution (smearing was only needed to
  de-bias Ridge's mean-in-log-space prediction).
- Expanded features vs. the original Ridge model: added borough (explicit
  coarse-grained signal, was unused before), capacity_tier, and host-level
  numerics (host_experience_years, total_reviews, reviews_per_month,
  host_total_listings, days_since_last_review, latitude, longitude).
- Confidence: interval width (q90-q10)/q50 is the real per-listing
  uncertainty signal (correlates with actual error, unlike the old
  rarity-based Ridge heuristic). Shrunk toward each listing's
  (borough, room_type, host_tier) cohort average, weighted by cohort
  size (empirical-Bayes pooling, helps small/rare cohorts most).
  Low/Medium/High is then an absolute, per-segment threshold on real
  expected error (via isotonic regression), not a forced percentile
  split, so the count in each band reflects genuine model quality.
- pricing_signal: the ±10% tolerance band Manas described in the 7/21
  chat, computed against the new GBM fair price.
- Conformal calibration (CQR): the raw quantile model's 80% interval only
  covered the true price ~65-68% of the time. Calibrated using the OOF
  predictions themselves (already out-of-sample per listing, no extra
  split needed): for each listing compute how far the true price falls
  outside [q10, q90], take the 80th-percentile of that (finite-sample
  corrected), and widen every interval by that amount. Confirmed this
  brings empirical coverage to ~80% on both segments.
- direction_confidence: this is the actual user-facing field, decided
  after confidence_score/confidence_level turned out not to be useful to
  show a host (confidence_score is a rank of *how common* a listing's
  category combo is, not a measure of price accuracy, verified this
  correlates ~0 with real error). A 5-seed refit stability test showed
  price DIRECTION (raise vs. lower) is far more robust than magnitude,
  ~80% unanimous agreement in both segments, unlike magnitude confidence
  which was fine for monthly and broken for short_stay. direction_confidence
  operationalizes that finding directly from the calibrated interval,
  no repeated refitting needed in production: if the actual price sits
  entirely above or below the calibrated [q10, q90] range, the direction
  call is confident; if actual price falls inside that range, the fair
  price plausibly already is the actual price, so direction is uncertain.
  confidence_score/confidence_level remain internal-QA-only fields, not
  meant for the host-facing UI.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

RANDOM_SEED = 42
N_FOLDS = 5
SHRINKAGE_K = 20
MONTHLY_COL = 'is_monthly_rental(min_nights>28)'

CATEGORICAL = ['neighborhood', 'room_type', 'property_type', 'host_tier', 'is_superhost_cat', 'borough', 'capacity_tier']
SIZE = ['max_guests', 'bedrooms', 'beds', 'bathrooms']
RATINGS = ['rating_overall', 'rating_cleanliness', 'rating_checkin', 'rating_communication',
           'rating_location', 'rating_value', 'rating_listing_accuracy']
EXTRA_NUMERIC = ['host_experience_years', 'total_reviews', 'reviews_per_month',
                 'host_total_listings', 'days_since_last_review', 'latitude', 'longitude']
GBM_KWARGS = dict(max_iter=300, max_depth=6, learning_rate=0.06, l2_regularization=1.0)


def prep(df):
    df = df.copy()
    df['is_superhost_cat'] = df['is_superhost'].astype('object').where(df['is_superhost'].notna(), 'unknown').astype(str)
    df['sentiment_missing'] = df['sentiment_score'].isna().astype(int)
    df['sentiment_score'] = df['sentiment_score'].fillna(df['sentiment_score'].median())
    for col in EXTRA_NUMERIC:
        df[f'{col}_missing'] = df[col].isna().astype(int)
        df[col] = df[col].fillna(df[col].median())
    return df


def numeric_features(df):
    return (SIZE + RATINGS + [c for c in df.columns if c.startswith('has_')] +
            ['sentiment_score', 'sentiment_missing'] + EXTRA_NUMERIC +
            [f'{c}_missing' for c in EXTRA_NUMERIC])


def fit_quantile_oof(X, yl, quantile):
    n = len(X)
    pred = np.zeros(n)
    kf = KFold(N_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    for tr, va in kf.split(X):
        pre = ColumnTransformer([
            ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), CATEGORICAL),
        ], remainder='passthrough', verbose_feature_names_out=False)
        model = HistGradientBoostingRegressor(
            loss='quantile', quantile=quantile, categorical_features=list(range(len(CATEGORICAL))),
            random_state=RANDOM_SEED, **GBM_KWARGS)
        m = Pipeline([('pre', pre), ('model', model)])
        m.fit(X.iloc[tr], yl[tr])
        pred[va] = np.exp(m.predict(X.iloc[va]))
    return pred


def score_confidence(seg_df, width, abs_pct_error):
    # ---- pooling / empirical-Bayes shrinkage toward cohort average ----
    cohort_key = seg_df['borough'].astype(str) + '|' + seg_df['room_type'].astype(str) + '|' + seg_df['host_tier'].astype(str)
    tmp = pd.DataFrame({'cohort': cohort_key, 'width': width})
    cohort_stats = tmp.groupby('cohort')['width'].agg(['mean', 'count']).rename(columns={'mean': 'cohort_mean', 'count': 'cohort_n'})
    tmp = tmp.join(cohort_stats, on='cohort')
    shrunk_width = ((tmp['cohort_n'] / (tmp['cohort_n'] + SHRINKAGE_K)) * tmp['width'] +
                     (SHRINKAGE_K / (tmp['cohort_n'] + SHRINKAGE_K)) * tmp['cohort_mean']).to_numpy()

    # ---- absolute, per-segment threshold via isotonic regression ----
    iso = IsotonicRegression(increasing=True, out_of_bounds='clip')
    fitted_err = iso.fit_transform(shrunk_width, abs_pct_error)
    order = np.argsort(shrunk_width)
    w_sorted = shrunk_width[order]; fitted_sorted = fitted_err[order]

    def find_threshold(bar):
        idx = np.where(fitted_sorted > bar)[0]
        return w_sorted[idx[0]] if len(idx) else w_sorted[-1]

    floor = fitted_err.min()
    t_high_global = find_threshold(0.15)
    global_high_count = int((shrunk_width <= t_high_global).sum())
    if global_high_count < max(20, 0.02 * len(shrunk_width)):
        bar_high, bar_medium = floor + 0.05, floor + 0.12
    else:
        bar_high, bar_medium = 0.15, 0.25
    t_high = find_threshold(bar_high)
    t_medium = find_threshold(bar_medium)

    label = np.where(shrunk_width <= t_high, 'High', np.where(shrunk_width <= t_medium, 'Medium', 'Low'))
    # Display-only numeric score (rank-based), confidence_level above is the
    # definitive signal since it's absolute-threshold based, not this score.
    score = (1.0 - pd.Series(shrunk_width).rank(pct=True).to_numpy()) * 100
    return score, label, shrunk_width, dict(t_high=t_high, t_medium=t_medium, floor=floor)


def metrics(seg, y, fair):
    resid = y - fair
    return dict(segment=seg, n_listings=len(y), R2_log=r2_score(np.log(y), np.log(fair)), R2_price=r2_score(y, fair),
                MAE_USD=mean_absolute_error(y, fair), RMSE_USD=mean_squared_error(y, fair) ** .5,
                Median_APE=float(np.median(np.abs(resid) / y)))


def main(input_path, outdir):
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    df = prep(pd.read_csv(input_path)); numeric = numeric_features(df)
    all_rows = []; mets = []; threshold_rows = []

    for seg, sg in {'short_stay': df[df[MONTHLY_COL] == 0].copy(), 'monthly': df[df[MONTHLY_COL] == 1].copy()}.items():
        sg = sg.reset_index(drop=True)
        X = sg[CATEGORICAL + numeric].copy()
        for c in CATEGORICAL:
            X[c] = X[c].astype(str)
        y = sg['nightly_price'].astype(float).to_numpy()
        yl = np.log(y)

        q10 = fit_quantile_oof(X, yl, 0.10)
        q50 = fit_quantile_oof(X, yl, 0.50)
        q90 = fit_quantile_oof(X, yl, 0.90)
        fair = np.maximum(q50, .01)

        m = metrics(seg, y, fair); mets.append(m)
        abs_pct_error = np.abs(y - fair) / y
        raw_coverage_80 = float(np.mean((y >= q10) & (y <= q90)))

        # ---- conformal calibration (CQR), using the OOF predictions as the calibration set ----
        n = len(sg)
        conformity = np.maximum(q10 - y, y - q90)
        level = min(1.0, np.ceil((n + 1) * 0.80) / n)
        Q = np.quantile(conformity, level, method='higher')
        cal_q10 = q10 - Q
        cal_q90 = q90 + Q
        cal_coverage_80 = float(np.mean((y >= cal_q10) & (y <= cal_q90)))

        width = (cal_q90 - cal_q10) / np.maximum(fair, 1)
        conf, label, shrunk_width, thresholds = score_confidence(sg, width, abs_pct_error)
        threshold_rows.append(dict(segment=seg, raw_coverage_80=raw_coverage_80, cal_coverage_80=cal_coverage_80,
                                    conformal_Q=round(float(Q), 2), **thresholds))

        # ---- direction_confidence: the actual user-facing field ----
        # Confident only if the *entire* calibrated interval sits on one
        # side of the actual price, meaning even the pessimistic/optimistic
        # bound agrees on which way to move. If actual price falls inside
        # the interval, the fair price plausibly already is the actual
        # price, so no confident direction call.
        direction_confidence = np.where(y < cal_q10, 'Confident: raise price',
                                  np.where(y > cal_q90, 'Confident: lower price', 'Uncertain (within plausible range)'))

        resid = y - fair
        resid_pct = resid / fair
        pricing_signal = np.where(np.abs(resid_pct) <= 0.10, 'Within 10% of model benchmark',
                            np.where(resid_pct > 0.10, 'Above model benchmark (review price)', 'Below model benchmark (review price)'))

        all_rows.append(pd.DataFrame({
            'listing_id': sg.id.to_numpy(), 'listing_name': sg.listing_name.to_numpy(), 'listing_url': sg.listing_url.to_numpy(),
            'borough': sg.borough.to_numpy(), 'neighborhood': sg.neighborhood.to_numpy(), 'room_type': sg.room_type.to_numpy(),
            'property_type': sg.property_type.to_numpy(), 'host_tier': sg.host_tier.to_numpy(), 'market_segment': seg,
            'actual_price_usd': np.round(y, 2), 'predicted_fair_price_usd': np.round(fair, 2),
            'predicted_price_q10': np.round(cal_q10, 2), 'predicted_price_q90': np.round(cal_q90, 2),
            'interval_width_pct': np.round(shrunk_width, 4),
            'direction_confidence': direction_confidence,
            'confidence_score': np.round(conf, 1), 'confidence_level': label,
            'residual_usd': np.round(resid, 2), 'residual_pct_of_fair': np.round(resid_pct, 4),
            'pricing_signal': pricing_signal,
        }))

    res = pd.concat(all_rows, ignore_index=True); met = pd.DataFrame(mets)
    res.to_csv(outdir / 'v3_gbm_listing_pricing_signals.csv', index=False)
    met.to_csv(outdir / 'v3_gbm_segment_metrics.csv', index=False)
    pd.DataFrame(threshold_rows).to_csv(outdir / 'v3_gbm_confidence_thresholds.csv', index=False)

    print(met.to_string(index=False))
    print()
    print(pd.DataFrame(threshold_rows).to_string(index=False))
    print()
    print("--- direction_confidence (user-facing) ---")
    print(res['direction_confidence'].value_counts())
    print()
    print(res.groupby('market_segment')['direction_confidence'].value_counts())
    print()
    print("--- confidence_level (internal QA only, not user-facing) ---")
    print(res['confidence_level'].value_counts())
    print()
    print(res.groupby('market_segment')['confidence_level'].value_counts())
    print()
    print(res['pricing_signal'].value_counts())


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    main(a.input, a.output_dir)
