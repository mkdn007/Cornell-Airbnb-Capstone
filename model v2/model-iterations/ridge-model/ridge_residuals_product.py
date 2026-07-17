"""
Ridge pricing model + listing-level residual product — NYC Airbnb Capstone.

This is the PRODUCTION model chosen after the model bake-off (see TESTING_MODELS.md).
It replaces the original borough-only OLS residuals with a Ridge model that uses
neighborhood-level features and is fit SEPARATELY per market segment.

Why Ridge + segment split:
  - Ridge: same accuracy as OLS (R2_log ~0.75) but 2-3x more stable coefficients
    and no implausible signs -> trustworthy host-facing "fair price" benchmark.
  - Segment split: short-stay and monthly rentals price on different logic, so a
    short-stay listing is benchmarked only against other short-stay listings
    (and monthly against monthly). No cross-segment contamination.

Method (per segment):
  log(nightly_price) target -> one-hot encode categoricals + standardize numerics
  -> RidgeCV (alpha auto-selected) -> Duan smearing back to dollars
  -> 5-fold out-of-fold, so every listing is scored by a model that did NOT
     train on it.

Outputs:
  ridge_listing_residuals.csv  — one row per listing: fair price, residual, signal
  ridge_segment_metrics.csv    — per-segment holdout accuracy

Run:
Run (from the project root):
  python "model-iterations/ridge-model/ridge_residuals_product.py"
  # defaults read active_listings_clean_v6.csv from the project root and
  # write outputs next to this script.
"""

from pathlib import Path
import argparse
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
N_FOLDS = 5
ALPHAS = np.logspace(-2, 3, 20)
MONTHLY_COL = "is_monthly_rental(min_nights>28)"

CATEGORICAL = ["neighborhood", "room_type", "property_type", "host_tier",
               "is_superhost_cat"]
RATINGS = ["rating_overall", "rating_cleanliness", "rating_checkin",
           "rating_communication", "rating_location", "rating_value",
           "rating_listing_accuracy"]
SIZE = ["max_guests", "bedrooms", "beds", "bathrooms"]


def prep(df):
    """Null handling + helper columns."""
    df = df.copy()
    df["is_superhost_cat"] = (
        df["is_superhost"].astype("object")
        .where(df["is_superhost"].notna(), "unknown").astype(str)
    )
    df["sentiment_missing"] = df["sentiment_score"].isna().astype(int)
    df["sentiment_score"] = df["sentiment_score"].fillna(df["sentiment_score"].median())
    return df


def numeric_features(df):
    amenities = [c for c in df.columns if c.startswith("has_")]
    return SIZE + RATINGS + amenities + ["sentiment_score", "sentiment_missing"]


def build_ridge(categorical, numeric):
    pre = ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
          categorical),
         ("num", StandardScaler(), numeric)],
        verbose_feature_names_out=False,
    )
    return Pipeline([("pre", pre), ("model", RidgeCV(alphas=ALPHAS))])


def oof_fair_price(df, categorical, numeric):
    """5-fold out-of-fold Ridge fair-price with per-fold Duan smearing."""
    X = df[categorical + numeric]
    y = df["nightly_price"].astype(float).to_numpy()
    y_log = np.log(y)
    fair = np.empty(len(df))
    fold_id = np.empty(len(df), dtype=int)
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    for fold, (fit_idx, val_idx) in enumerate(kf.split(X), start=1):
        m = build_ridge(categorical, numeric)
        m.fit(X.iloc[fit_idx], y_log[fit_idx])
        smear = float(np.mean(np.exp(y_log[fit_idx] - m.predict(X.iloc[fit_idx]))))
        fair[val_idx] = np.exp(m.predict(X.iloc[val_idx])) * smear
        fold_id[val_idx] = fold
    fair = np.maximum(fair, 0.01)
    return fair, fold_id


def metrics_row(segment, df, fair):
    y = df["nightly_price"].astype(float).to_numpy()
    resid = y - fair
    return {
        "segment": segment,
        "n_listings": len(df),
        "R2_log": r2_score(np.log(y), np.log(fair)),
        "R2_price": r2_score(y, fair),
        "MAE_USD": mean_absolute_error(y, fair),
        "RMSE_USD": mean_squared_error(y, fair) ** 0.5,
        "Median_APE": float(np.median(np.abs(resid) / y)),
    }


def main(input_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    df = prep(pd.read_csv(input_path))
    numeric = numeric_features(df)

    segments = {
        "short_stay": df[df[MONTHLY_COL] == 0].copy(),
        "monthly": df[df[MONTHLY_COL] == 1].copy(),
    }

    parts = []
    metric_rows = []
    for seg_name, seg_df in segments.items():
        fair, fold_id = oof_fair_price(seg_df, CATEGORICAL, numeric)
        y = seg_df["nightly_price"].astype(float).to_numpy()
        resid = y - fair
        metric_rows.append(metrics_row(seg_name, seg_df, fair))
        parts.append(pd.DataFrame({
            "listing_id": seg_df["id"].to_numpy(),
            "listing_name": seg_df["listing_name"].to_numpy(),
            "listing_url": seg_df["listing_url"].to_numpy(),
            "borough": seg_df["borough"].to_numpy(),
            "neighborhood": seg_df["neighborhood"].to_numpy(),
            "room_type": seg_df["room_type"].to_numpy(),
            "property_type": seg_df["property_type"].to_numpy(),
            "max_guests": seg_df["max_guests"].to_numpy(),
            "host_tier": seg_df["host_tier"].to_numpy(),
            "segment": seg_df["segment"].to_numpy(),
            "market_segment": seg_name,
            "cv_fold": fold_id,
            "actual_price_usd": np.round(y, 2),
            "predicted_fair_price_usd": np.round(fair, 2),
            "residual_usd": np.round(resid, 2),
            "residual_pct_of_fair": np.round(resid / fair, 4),
            "pricing_signal": np.where(
                resid > 0, "Above fair value (overpriced)",
                np.where(resid < 0, "Below fair value (underpriced)", "At fair value")),
        }))

    residuals = pd.concat(parts, ignore_index=True)
    residuals.to_csv(output_dir / "ridge_listing_residuals.csv", index=False)
    pd.DataFrame(metric_rows).to_csv(output_dir / "ridge_segment_metrics.csv",
                                     index=False)

    print("Segment accuracy (5-fold out-of-fold):")
    for r in metric_rows:
        print(f"  {r['segment']:11s} n={r['n_listings']:5d}  "
              f"R2_log={r['R2_log']:.3f}  MAE=${r['MAE_USD']:.0f}  "
              f"MedAPE={r['Median_APE']*100:.1f}%")
    print(f"\nWrote {output_dir/'ridge_listing_residuals.csv'} "
          f"({len(residuals)} listings)")


if __name__ == "__main__":
    # Defaults resolve relative to this script so it runs from any directory.
    # Project root is two levels up: <root>/model-iterations/ridge-model/
    _HERE = Path(__file__).resolve().parent
    _ROOT = _HERE.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path,
                        default=_ROOT / "active_listings_clean_v6.csv")
    parser.add_argument("--output-dir", type=Path, default=_HERE)
    args = parser.parse_args()
    main(args.input, args.output_dir)
