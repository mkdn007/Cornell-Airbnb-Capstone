"""
Diagnostic reports on the full-sample fit (Q3, Q4, Q5).
Q3: does plain OLS blow up on rare neighborhoods vs Ridge?
Q4: do weird coefficients (hot water etc.) clean up under Ridge?
Q5: do short-stay vs monthly segments price differently?
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import importlib.util
_HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mc", _HERE / "model_comparison.py")
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)

OUTDIR = _HERE / "comparison_outputs"
raw = mc.prep(pd.read_csv(mc.INPUT))
raw["monthly_flag"] = raw[mc.MONTHLY_COL].astype(int)


def fit_coefs(df, kind, include_flag):
    cat, num = mc.feature_lists(df, include_flag)
    X = df[cat + num]
    y = np.log(df["nightly_price"].astype(float))
    drop = "first" if kind == "ols" else None
    scale = kind == "ridge"
    pre = ColumnTransformer(
        [("cat", OneHotEncoder(drop=drop, handle_unknown="ignore",
                               sparse_output=False), cat),
         ("num", StandardScaler() if scale else "passthrough", num)],
        verbose_feature_names_out=False)
    model = RidgeCV(alphas=np.logspace(-2, 3, 20)) if kind == "ridge" else LinearRegression()
    pipe = Pipeline([("pre", pre), ("model", model)])
    pipe.fit(X, y)
    names = pipe.named_steps["pre"].get_feature_names_out()
    coefs = pipe.named_steps["model"].coef_
    return dict(zip(names, coefs))

# ---- Q3: neighborhood coefficient magnitude, OLS vs Ridge ----
ols_c = fit_coefs(raw, "ols", True)
ridge_c = fit_coefs(raw, "ridge", True)
nb_ols = {k: v for k, v in ols_c.items() if k.startswith("neighborhood_")}
nb_ridge = {k: v for k, v in ridge_c.items() if k.startswith("neighborhood_")}
vc = raw["neighborhood"].value_counts()

q3 = pd.DataFrame({
    "neighborhood": [k.replace("neighborhood_", "") for k in nb_ols],
    "ols_coef": list(nb_ols.values()),
})
q3["ridge_coef"] = [nb_ridge.get("neighborhood_" + n, np.nan) for n in q3["neighborhood"]]
q3["n_listings"] = q3["neighborhood"].map(vc)
q3["abs_ols"] = q3["ols_coef"].abs()
q3 = q3.sort_values("abs_ols", ascending=False)
q3.to_csv(OUTDIR / "q3_neighborhood_stability.csv", index=False)

print("=== Q3: neighborhood coefficient magnitude (log-price) ===")
print(f"OLS   max |coef|: {q3['abs_ols'].max():.2f}   mean |coef|: {q3['abs_ols'].mean():.3f}")
print(f"Ridge max |coef|: {q3['ridge_coef'].abs().max():.2f}   mean |coef|: {q3['ridge_coef'].abs().mean():.3f}")
rare = q3[q3["n_listings"] < 30]
print(f"\nRare neighborhoods (<30 listings), n={len(rare)}:")
print(f"  OLS   mean |coef|: {rare['ols_coef'].abs().mean():.3f}  (max {rare['ols_coef'].abs().max():.2f})")
print(f"  Ridge mean |coef|: {rare['ridge_coef'].abs().mean():.3f}  (max {rare['ridge_coef'].abs().max():.2f})")
print("\nWorst 5 OLS neighborhood coefficients (should be tiny/rare):")
print(q3.head(5)[["neighborhood", "n_listings", "ols_coef", "ridge_coef"]].to_string(index=False))

# ---- Q4: amenity + rating coefficient cleanup ----
watch = ["has_hot_water", "has_kitchen", "has_hangers", "has_microwave",
         "rating_value", "rating_communication", "rating_checkin",
         "has_hair_dryer", "has_self_check_in", "rating_cleanliness"]
q4 = pd.DataFrame({
    "feature": watch,
    "ols_pct_effect": [(np.exp(ols_c.get(f, 0)) - 1) * 100 for f in watch],
    "ridge_pct_effect": [(np.exp(ridge_c.get(f, 0)) - 1) * 100 for f in watch],
})
q4.to_csv(OUTDIR / "q4_coefficient_cleanup.csv", index=False)
print("\n=== Q4: coefficient cleanup, OLS vs Ridge (approx % price effect) ===")
print(q4.to_string(index=False))

# ---- Q5: short-stay vs monthly coefficient differences ----
ss = raw[raw[mc.MONTHLY_COL] == 0].copy()
mo = raw[raw[mc.MONTHLY_COL] == 1].copy()
ss_c = fit_coefs(ss, "ridge", False)
mo_c = fit_coefs(mo, "ridge", False)
compare = ["neighborhood_Midtown", "borough" , "max_guests", "bedrooms",
           "room_type_Private room", "has_self_check_in", "has_air_conditioning",
           "rating_cleanliness", "host_tier_Individual", "has_dedicated_workspace"]
feats = [f for f in ss_c if f in mo_c]
q5 = pd.DataFrame({
    "feature": feats,
    "short_stay_coef": [ss_c[f] for f in feats],
    "monthly_coef": [mo_c[f] for f in feats],
})
q5["abs_diff"] = (q5["short_stay_coef"] - q5["monthly_coef"]).abs()
q5 = q5.sort_values("abs_diff", ascending=False)
q5.to_csv(OUTDIR / "q5_segment_coefficient_diff.csv", index=False)
print("\n=== Q5: biggest short-stay vs monthly coefficient differences (Ridge, log-price) ===")
print(q5.head(12).to_string(index=False))
print(f"\nMean |coef difference| across all shared features: {q5['abs_diff'].mean():.3f}")
