"""
Model comparison for the NYC Airbnb Capstone (Manas modeling section).

Answers:
  Q1 Does adding features (neighborhood etc.) + a better model beat current OLS?
  Q2 Which rigid model is best: OLS, Ridge, or Elastic Net?
  Q3 Does plain OLS overfit the 141 tiny neighborhoods?
  Q4 Do weird coefficients (e.g. -12% hot water) clean up under regularization?
  Q5 Was splitting monthly vs short-stay justified?
  Q6 How much do monthly rentals contaminate the shipped residual?

Design:
  3 data cuts (full+flag, short-stay, monthly) x 4 models (OLS, Ridge, ElasticNet, RF)
  Target: log(nightly_price), Duan smearing retransformation.
  Metrics: 5-fold out-of-fold (every listing scored by a model that didn't train on it).
"""

from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import (LinearRegression, RidgeCV, ElasticNetCV,
                                  HuberRegressor, TweedieRegressor)
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
N_FOLDS = 5
# Paths resolve relative to this script so it runs from any working directory.
# Project root is two levels up: <root>/model-iterations/testing_models/
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
INPUT = _ROOT / "active_listings_clean_v6.csv"
OUTDIR = _HERE / "comparison_outputs"

MONTHLY_COL = "is_monthly_rental(min_nights>28)"

# ---- feature set (locked) ------------------------------------------------
CATEGORICAL = ["neighborhood", "room_type", "property_type", "host_tier",
               "is_superhost_cat"]
RATINGS = ["rating_overall", "rating_cleanliness", "rating_checkin",
           "rating_communication", "rating_location", "rating_value",
           "rating_listing_accuracy"]
SIZE = ["max_guests", "bedrooms", "beds", "bathrooms"]


def prep(df):
    """Null handling + engineered helper columns, done once up front."""
    df = df.copy()
    # is_superhost: 196 nulls -> own 'unknown' category (as string)
    df["is_superhost_cat"] = df["is_superhost"].astype("object").where(
        df["is_superhost"].notna(), "unknown"
    ).astype(str)
    # sentiment: 21 nulls -> median fill + missingness flag
    df["sentiment_missing"] = df["sentiment_score"].isna().astype(int)
    df["sentiment_score"] = df["sentiment_score"].fillna(
        df["sentiment_score"].median()
    )
    return df


def feature_lists(df, include_flag):
    amenities = [c for c in df.columns if c.startswith("has_")]
    numeric = SIZE + RATINGS + amenities + ["sentiment_score", "sentiment_missing"]
    categorical = list(CATEGORICAL)
    if include_flag:
        numeric = numeric + ["monthly_flag"]
    return categorical, numeric


def make_model(kind, categorical, numeric):
    # OLS uses drop='first'; penalized/tree models keep all dummies.
    drop = "first" if kind in ("ols", "huber") else None
    # standardize numerics for penalized + iterative models (helps convergence)
    scale = kind in ("ridge", "enet", "huber", "gamma")
    num_steps = StandardScaler() if scale else "passthrough"
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(drop=drop, handle_unknown="ignore",
                                  sparse_output=False), categorical),
            ("num", num_steps, numeric),
        ],
        verbose_feature_names_out=False,
    )
    if kind == "ols":
        model = LinearRegression()
    elif kind == "ridge":
        model = RidgeCV(alphas=np.logspace(-2, 3, 20))
    elif kind == "enet":
        model = ElasticNetCV(l1_ratio=[.1, .5, .7, .9, .95, 1.0],
                             alphas=np.logspace(-3, 1, 20),
                             cv=3, random_state=RANDOM_STATE, max_iter=5000)
    elif kind == "huber":
        model = HuberRegressor(max_iter=2000)
    elif kind == "gamma":
        # Gamma GLM with log link: models skewed positive $ directly,
        # no log-transform of the target and no Duan smearing needed.
        model = TweedieRegressor(power=2, link="log", alpha=0.0, max_iter=5000)
    elif kind == "rf":
        model = RandomForestRegressor(n_estimators=500, min_samples_leaf=3,
                                      max_features=0.7, random_state=RANDOM_STATE,
                                      n_jobs=-1)
    return Pipeline([("pre", pre), ("model", model)])


def oof_metrics(df, kind, categorical, numeric):
    """5-fold out-of-fold predictions -> metrics + residuals.

    Each fold: fit on 4/5, compute that fold's Duan smearing factor from the
    training rows, then predict + smear the held-out 1/5.
    """
    X = df[categorical + numeric]
    y = df["nightly_price"].astype(float).to_numpy()
    y_log = np.log(y)
    oof_price = np.empty(len(df))
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    for fit_idx, val_idx in kf.split(X):
        m = make_model(kind, categorical, numeric)
        if kind == "gamma":
            # Gamma GLM predicts dollars directly: no log target, no smearing.
            m.fit(X.iloc[fit_idx], y[fit_idx])
            oof_price[val_idx] = m.predict(X.iloc[val_idx])
        else:
            m.fit(X.iloc[fit_idx], y_log[fit_idx])
            smear = float(np.mean(np.exp(y_log[fit_idx] - m.predict(X.iloc[fit_idx]))))
            oof_price[val_idx] = np.exp(m.predict(X.iloc[val_idx])) * smear
    oof_price = np.maximum(oof_price, 0.01)
    resid = y - oof_price
    return {
        "MAE_USD": mean_absolute_error(y, oof_price),
        "RMSE_USD": mean_squared_error(y, oof_price) ** 0.5,
        "R2_price": r2_score(y, oof_price),
        "Median_APE": float(np.median(np.abs(resid) / y)),
        "R2_log": r2_score(y_log, np.log(oof_price)),
    }, oof_price, resid


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    raw = prep(pd.read_csv(INPUT))
    raw["monthly_flag"] = raw[MONTHLY_COL].astype(int)

    cuts = {
        "full": (raw, True),
        "short_stay": (raw[raw[MONTHLY_COL] == 0].copy(), False),
        "monthly": (raw[raw[MONTHLY_COL] == 1].copy(), False),
    }
    models = ["ols", "ridge", "enet", "huber", "gamma", "rf"]

    rows = []
    for cut_name, (dfc, include_flag) in cuts.items():
        categorical, numeric = feature_lists(dfc, include_flag)
        for kind in models:
            metrics, _, _ = oof_metrics(dfc, kind, categorical, numeric)
            rows.append({"cut": cut_name, "n_rows": len(dfc),
                         "model": kind, **metrics})
            print(f"[done] cut={cut_name:11s} model={kind:5s} "
                  f"R2_log={metrics['R2_log']:.3f} MAE=${metrics['MAE_USD']:.0f} "
                  f"MedAPE={metrics['Median_APE']*100:.1f}%")

    pd.DataFrame(rows).to_csv(OUTDIR / "master_metrics.csv", index=False)
    print(f"\nWrote {OUTDIR/'master_metrics.csv'}")


if __name__ == "__main__":
    main()
