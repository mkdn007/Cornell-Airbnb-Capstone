"""
Ridge robustness check for the log-linear pricing model.

Purpose:
    Manas's primary model (manas_airbnb_modeling.py) uses plain OLS. Several
    inputs are correlated (the 7 review sub-scores, and some amenity flags
    correlate with each other and with rental duration), so this script
    checks whether a Ridge penalty, with the penalty strength (alpha) chosen
    by 5-fold cross-validation, changes the fit materially. If it doesn't,
    that's evidence the OLS coefficients aren't unstable due to
    multicollinearity.

    This is NOT part of Manas's original modeling deliverable. It was run
    as an additional check while preparing the Unit "Model Definition and
    Initial Results" deck, to satisfy the rubric's request for
    hyperparameter tuning / cross-validation, and to confirm (or refute)
    that regularization changes the result before reporting a specific R^2.

Run:
    python ridge_robustness_check.py --input active_listings_clean_v6.csv
"""

from pathlib import Path
import argparse
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5


def main(input_path):
    df = pd.read_csv(input_path)

    target = "nightly_price"
    amenities = [column for column in df.columns if column.startswith("has_")]
    categorical = ["borough", "room_type", "host_tier"]
    numeric = [
        "max_guests", "bedrooms", "beds", "bathrooms",
        "rating_overall", "rating_cleanliness", "rating_checkin",
        "rating_communication", "rating_location", "rating_value",
        "rating_listing_accuracy",
    ] + amenities

    X = df[categorical + numeric].copy()
    y = df[target].astype(float)
    y_log = np.log(y)

    X_train, X_test, y_train, y_test, ylog_train, ylog_test = train_test_split(
        X, y, y_log, test_size=TEST_SIZE, random_state=RANDOM_STATE,
    )

    preprocessor = ColumnTransformer(
        [
            ("cat", OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False), categorical),
            ("num", StandardScaler(), numeric),
        ],
        verbose_feature_names_out=False,
    )
    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("model", RidgeCV(alphas=np.logspace(-3, 3, 50), cv=CV_FOLDS)),
        ]
    )
    pipeline.fit(X_train, ylog_train)

    chosen_alpha = pipeline.named_steps["model"].alpha_

    train_pred_log = pipeline.predict(X_train)
    smearing = float(np.mean(np.exp(ylog_train.to_numpy() - train_pred_log)))
    test_pred_log = pipeline.predict(X_test)
    test_pred_price = np.maximum(np.exp(test_pred_log) * smearing, 0.01)

    print(f"Chosen alpha (5-fold CV): {chosen_alpha}")
    print(f"R2 (price scale): {r2_score(y_test, test_pred_price):.3f}")
    print(f"R2 (log scale): {r2_score(ylog_test, test_pred_log):.3f}")
    print(f"MAE: {mean_absolute_error(y_test, test_pred_price):.2f}")
    print(f"RMSE: {mean_squared_error(y_test, test_pred_price) ** 0.5:.2f}")
    print()
    print("For comparison, Manas's plain OLS (manas_model_metrics.csv) reports:")
    print("R2 price = 0.243, R2 log = 0.486, MAE = $113.22, RMSE = $218.92")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("active_listings_clean_v6.csv"))
    arguments = parser.parse_args()
    main(arguments.input)
