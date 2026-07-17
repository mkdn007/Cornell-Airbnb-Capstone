"""
Multicollinearity evidence for the pitch:
  1. VIF (variance inflation factor) on the numeric features -> proves collinearity exists
  2. Coefficient stability: refit OLS vs Ridge on 30 bootstrap resamples,
     measure how much each coefficient swings (std dev). Ridge should be far tighter.
  3. Sign-flip table: features where OLS gives an implausible sign that Ridge corrects.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

import importlib.util
_HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mc", _HERE / "model_comparison.py")
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)

OUTDIR = _HERE / "comparison_outputs"
raw = mc.prep(pd.read_csv(mc.INPUT))
raw["monthly_flag"] = raw[mc.MONTHLY_COL].astype(int)
cat, num = mc.feature_lists(raw, True)

# ---------- 1. VIF on numeric features ----------
amenities = [c for c in raw.columns if c.startswith("has_")]
vif_feats = mc.SIZE + mc.RATINGS + amenities + ["sentiment_score"]
Xv = raw[vif_feats].astype(float).dropna()
Xv = Xv.assign(_const=1.0)
vif = pd.DataFrame({
    "feature": vif_feats,
    "VIF": [variance_inflation_factor(Xv.values, i) for i in range(len(vif_feats))],
}).sort_values("VIF", ascending=False)
vif.to_csv(OUTDIR / "vif_multicollinearity.csv", index=False)
print("=== 1. VIF (variance inflation factor) — top 12 ===")
print("   VIF>5 = notable collinearity, VIF>10 = severe")
print(vif.head(12).to_string(index=False))

# ---------- helper to fit and return named coefs ----------
def fit_coefs(df, kind):
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
    pipe = Pipeline([("pre", pre), ("model", model)]).fit(X, y)
    names = pipe.named_steps["pre"].get_feature_names_out()
    return dict(zip(names, pipe.named_steps["model"].coef_))

# ---------- 2. bootstrap coefficient stability ----------
rng = np.random.default_rng(42)
n = len(raw)
watch = ["has_hot_water", "has_kitchen", "has_hangers", "has_microwave",
         "has_cooking_basics", "has_dishes_and_silverware", "rating_value",
         "rating_communication", "rating_checkin", "beds", "bedrooms"]
ols_samples = {f: [] for f in watch}
ridge_samples = {f: [] for f in watch}
for b in range(30):
    idx = rng.integers(0, n, n)
    boot = raw.iloc[idx]
    oc = fit_coefs(boot, "ols")
    rc = fit_coefs(boot, "ridge")
    for f in watch:
        ols_samples[f].append(oc.get(f, np.nan))
        ridge_samples[f].append(rc.get(f, np.nan))

stab = pd.DataFrame({
    "feature": watch,
    "ols_coef_std": [np.nanstd(ols_samples[f]) for f in watch],
    "ridge_coef_std": [np.nanstd(ridge_samples[f]) for f in watch],
})
stab["stability_gain_x"] = stab["ols_coef_std"] / stab["ridge_coef_std"]
stab = stab.sort_values("stability_gain_x", ascending=False)
stab.to_csv(OUTDIR / "coefficient_stability_bootstrap.csv", index=False)
print("\n=== 2. Coefficient stability across 30 bootstrap resamples ===")
print("   coef_std = how much the coefficient swings; lower = more stable")
print("   stability_gain_x = how many times MORE stable Ridge is than OLS")
print(stab.to_string(index=False))

# ---------- 3. sign-flip / implausible-sign table ----------
oc = fit_coefs(raw, "ols")
rc = fit_coefs(raw, "ridge")
# "good" amenities that should logically be >= 0 (they add value)
should_be_positive = ["has_hot_water", "has_kitchen", "has_hangers",
                      "has_microwave", "has_cooking_basics",
                      "has_dishes_and_silverware", "has_heating"]
flip = pd.DataFrame({
    "feature": should_be_positive,
    "ols_pct_effect": [(np.exp(oc.get(f, 0)) - 1) * 100 for f in should_be_positive],
    "ridge_pct_effect": [(np.exp(rc.get(f, 0)) - 1) * 100 for f in should_be_positive],
})
flip["ols_implausible_negative"] = flip["ols_pct_effect"] < 0
flip.to_csv(OUTDIR / "sign_flip_table.csv", index=False)
print("\n=== 3. Implausible negative coefficients (amenities that should ADD value) ===")
print(flip.to_string(index=False))
print(f"\nOLS gives an implausible NEGATIVE price effect for "
      f"{int(flip['ols_implausible_negative'].sum())}/{len(flip)} value-adding amenities.")
