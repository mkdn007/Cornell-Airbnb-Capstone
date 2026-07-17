"""
Manas modeling section for the Cornell NYC Airbnb Capstone.

Primary model:
    Log-linear OLS with Duan smearing retransformation.

Alternate model:
    Random Forest using the same inputs and a log-price target.

Outputs:
    1. 80/20 holdout model metrics
    2. Five-fold out-of-fold listing residuals
    3. OLS coefficient table with HC3 robust standard errors

Run:
    python manas_airbnb_modeling.py \
        --input active_listings_clean_v6.csv \
        --output-dir modeling/outputs
"""

from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import statsmodels.api as sm

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import KFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


RANDOM_STATE = 42
TEST_SIZE = 0.20
N_FOLDS = 5


def build_ols_pipeline(categorical_features, numeric_features):
    preprocessor = ColumnTransformer(
        [
            (
                "cat",
                OneHotEncoder(
                    drop="first",
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                categorical_features,
            ),
            ("num", "passthrough", numeric_features),
        ],
        verbose_feature_names_out=False,
    )
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("model", LinearRegression()),
        ]
    )


def build_rf_pipeline(categorical_features, numeric_features):
    preprocessor = ColumnTransformer(
        [
            (
                "cat",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                categorical_features,
            ),
            ("num", "passthrough", numeric_features),
        ],
        verbose_feature_names_out=False,
    )
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=500,
                    min_samples_leaf=3,
                    max_features=0.7,
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def evaluate(y_true, pred_price, pred_log):
    pred_price = np.maximum(np.asarray(pred_price), 0.01)
    y_true = np.asarray(y_true)

    return {
        "MAE_USD": mean_absolute_error(y_true, pred_price),
        "RMSE_USD": mean_squared_error(y_true, pred_price) ** 0.5,
        "R2_price": r2_score(y_true, pred_price),
        "MAPE": mean_absolute_percentage_error(y_true, pred_price),
        "Median_APE": np.median(np.abs(y_true - pred_price) / y_true),
        "RMSE_log": mean_squared_error(np.log(y_true), pred_log) ** 0.5,
        "R2_log": r2_score(np.log(y_true), pred_log),
    }


def main(input_path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(input_path)

    target = "nightly_price"
    amenities = [column for column in df.columns if column.startswith("has_")]

    categorical = ["borough", "room_type", "host_tier"]
    numeric = [
        "max_guests",
        "bedrooms",
        "beds",
        "bathrooms",
        "rating_overall",
        "rating_cleanliness",
        "rating_checkin",
        "rating_communication",
        "rating_location",
        "rating_value",
        "rating_listing_accuracy",
    ] + amenities

    model_features = categorical + numeric

    missing_columns = [
        column for column in [target] + model_features
        if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    X = df[model_features].copy()
    y = df[target].astype(float)
    y_log = np.log(y)

    all_indices = np.arange(len(df))
    train_indices, test_indices = train_test_split(
        all_indices,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    X_train = X.iloc[train_indices]
    X_test = X.iloc[test_indices]
    y_train = y.iloc[train_indices]
    y_test = y.iloc[test_indices]
    y_log_train = y_log.iloc[train_indices]

    metric_rows = []

    ols = build_ols_pipeline(categorical, numeric)
    ols.fit(X_train, y_log_train)
    ols_train_log = ols.predict(X_train)
    ols_smear = float(np.mean(np.exp(y_log_train.to_numpy() - ols_train_log)))
    ols_test_log = ols.predict(X_test)
    ols_test_price = np.exp(ols_test_log) * ols_smear

    ols_row = {
        "model": "Log-linear OLS",
        "evaluation": "80/20 holdout",
        "train_rows": len(train_indices),
        "test_rows": len(test_indices),
        "smearing_factor": ols_smear,
    }
    ols_row.update(evaluate(y_test, ols_test_price, ols_test_log))
    metric_rows.append(ols_row)

    rf = build_rf_pipeline(categorical, numeric)
    rf.fit(X_train, y_log_train)
    rf_train_log = rf.predict(X_train)
    rf_smear = float(np.mean(np.exp(y_log_train.to_numpy() - rf_train_log)))
    rf_test_log = rf.predict(X_test)
    rf_test_price = np.exp(rf_test_log) * rf_smear

    rf_row = {
        "model": "Random Forest (log target)",
        "evaluation": "80/20 holdout",
        "train_rows": len(train_indices),
        "test_rows": len(test_indices),
        "smearing_factor": rf_smear,
    }
    rf_row.update(evaluate(y_test, rf_test_price, rf_test_log))
    metric_rows.append(rf_row)

    pd.DataFrame(metric_rows).to_csv(
        output_dir / "manas_model_metrics.csv",
        index=False,
    )

    # Five-fold out-of-fold OLS predictions make the residual product
    # available for every listing without using that row to train its own
    # prediction.
    oof_price = np.empty(len(df), dtype=float)
    oof_fold = np.empty(len(df), dtype=int)

    kfold = KFold(
        n_splits=N_FOLDS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    for fold, (fit_idx, valid_idx) in enumerate(kfold.split(X), start=1):
        fold_model = build_ols_pipeline(categorical, numeric)
        fold_model.fit(X.iloc[fit_idx], y_log.iloc[fit_idx])

        fit_pred_log = fold_model.predict(X.iloc[fit_idx])
        fold_smear = float(
            np.mean(np.exp(y_log.iloc[fit_idx].to_numpy() - fit_pred_log))
        )

        valid_pred_log = fold_model.predict(X.iloc[valid_idx])
        oof_price[valid_idx] = np.exp(valid_pred_log) * fold_smear
        oof_fold[valid_idx] = fold

    residual = y.to_numpy() - oof_price
    split_label = np.full(len(df), "train_80", dtype=object)
    split_label[test_indices] = "test_20"

    residual_output = pd.DataFrame(
        {
            "listing_id": df["id"],
            "listing_name": df["listing_name"],
            "listing_url": df["listing_url"],
            "borough": df["borough"],
            "neighborhood": df["neighborhood"],
            "room_type": df["room_type"],
            "max_guests": df["max_guests"],
            "host_tier": df["host_tier"],
            "segment": df["segment"],
            "split_80_20": split_label,
            "cv_fold": oof_fold,
            "actual_price_usd": y.round(2),
            "predicted_fair_price_log_ols_oof_usd": np.round(oof_price, 2),
            "residual_actual_minus_predicted_usd": np.round(residual, 2),
            "residual_pct_of_predicted": np.round(residual / oof_price, 4),
            "pricing_signal": np.where(
                residual > 0,
                "Above model benchmark",
                np.where(residual < 0, "Below model benchmark", "At benchmark"),
            ),
        }
    )

    residual_output.to_csv(
        output_dir / "manas_listing_residuals.csv",
        index=False,
    )

    # Full-sample coefficient table with heteroskedasticity-robust errors.
    X_stats = pd.get_dummies(
        df[model_features],
        columns=categorical,
        drop_first=True,
        dtype=float,
    )
    X_stats = sm.add_constant(X_stats, has_constant="add")
    ols_stats = sm.OLS(y_log, X_stats).fit(cov_type="HC3")

    coefficient_output = pd.DataFrame(
        {
            "feature": ols_stats.params.index,
            "coefficient_log_price": ols_stats.params.values,
            "robust_std_error_HC3": ols_stats.bse.values,
            "p_value": ols_stats.pvalues.values,
            "approx_percent_effect": (
                np.exp(ols_stats.params.values) - 1
            ) * 100,
        }
    )
    coefficient_output.to_csv(
        output_dir / "manas_ols_coefficients.csv",
        index=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("active_listings_clean_v6.csv"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("modeling/outputs"),
    )
    arguments = parser.parse_args()
    main(arguments.input, arguments.output_dir)
