"""
Reproduce the headline revenue figure from committed repo data.

    COMBINED HOST GBV   +$7.57M / year
    x 15.5% take rate   +$1.17M / year
    nights unlocked     +77,606 / year

Why this file exists: the revenue figure is presentation-layer business
arithmetic sitting on top of the elasticity model (elasticity_model.py),
not a second modeling step. It was originally written up in prose. This
makes it checkable rather than asserted, which is the same standard the
elasticity regression itself already meets.

Run:
    python reproduce_revenue_lift.py

Expected output: ~$7.56M combined, against the $7.57M reported in the deck
and appendix. The 0.1% gap is rounding in the intermediate figures.

------------------------------------------------------------------------
THE ONE DETAIL THAT MATTERS MOST

The 1-99 percentile trim is applied to **actual nightly price**, NOT to the
computed revenue lift. This is not a stylistic choice:

    trim on actual_price_usd  ->  $7.56M   <- correct
    trim on computed dRev     ->  $5.97M   <- wrong, $1.6M lower

Same data, same elasticity, same everything else. If you are restating the
methodology anywhere, say which variable is trimmed.
------------------------------------------------------------------------

METHOD
  1. Residual per listing from the GBM (actual - predicted fair value).
  2. Trim the 1st/99th percentile of actual nightly price. Removes ~50
     luxury listings where GBM reliability breaks down (mean actual
     ~$927/night vs model fair ~$1,153).
  3. Discount the gap by the segment's own median error (19.2% short-stay,
     15.2% monthly), so the target price closes ~81%/~85% of the gap
     rather than all of it. Source: v3_gbm_segment_metrics.csv.
  4. Occupied nights via Inside Airbnb's formula:
     estimated_annual_revenue / nightly_price.
  5. Apply elasticity by review tier. Revenue elasticity is (1 + beta):
       beta = 0     -> full price gain flows through
       beta = -1.0  -> exactly zero, by algebra rather than assumption
     Tiers: short-stay >=142 reviews -> -0.916 (measured on that profile)
            short-stay  <142 reviews -> -1.0   (breakeven, no extrapolation)
            monthly, either side     -> 0      (beta not significant, p=0.734)
  6. Sum by bucket.

The 142 threshold is the elasticity panel's own median review count. It is
the boundary of where the measurement applies, not a behavioural break.
"""

import numpy as np
import pandas as pd
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

SIGNALS = REPO / "model v4" / "model" / "outputs_gbm" / "v3_gbm_listing_pricing_signals.csv"
LISTINGS = REPO / "active_listings_clean_v6.csv"

MEDIAN_ERROR = {"short_stay": 0.192, "monthly": 0.152}   # v3_gbm_segment_metrics.csv
BETA_MEASURED = -0.916                                    # elasticity_results.csv, short-stay
BETA_BREAKEVEN = -1.0                                     # algebraic identity
REVIEW_THRESHOLD = 142                                    # elasticity panel median
TAKE_RATE = 0.155                                         # Airbnb host-only fee


def build():
    sig = pd.read_csv(SIGNALS)
    lst = pd.read_csv(
        LISTINGS,
        usecols=["id", "total_reviews", "estimated_annual_revenue", "nightly_price"],
    )
    df = sig.merge(lst, left_on="listing_id", right_on="id", how="left")

    # 1-99 trim on ACTUAL NIGHTLY PRICE (see header note)
    lo, hi = df["actual_price_usd"].quantile([0.01, 0.99])
    df = df[(df["actual_price_usd"] >= lo) & (df["actual_price_usd"] <= hi)].copy()

    # move only partway to fair value, discounted by the model's own error
    noise = df["market_segment"].map(MEDIAN_ERROR)
    p0 = df["actual_price_usd"]
    gap = df["predicted_fair_price_usd"] - p0
    df["price_ratio"] = (p0 + gap * (1 - noise)) / p0

    df["beta"] = np.where(
        df["market_segment"] == "monthly",
        0.0,
        np.where(df["total_reviews"] >= REVIEW_THRESHOLD, BETA_MEASURED, BETA_BREAKEVEN),
    )

    # revenue change = current_revenue * ((P1/P0)^(1+beta) - 1)
    df["d_revenue"] = df["estimated_annual_revenue"] * (
        df["price_ratio"] ** (1 + df["beta"]) - 1
    )

    df["occupied_nights"] = df["estimated_annual_revenue"] / df["nightly_price"]
    df["nights_delta"] = df["occupied_nights"] * (
        df["price_ratio"] ** df["beta"] - 1
    )

    return df.replace([np.inf, -np.inf], np.nan).dropna(subset=["d_revenue"])


def bucket(d, segment, tier=None):
    m = d["market_segment"] == segment
    if tier == "established":
        m &= d["total_reviews"] >= REVIEW_THRESHOLD
    elif tier == "newer":
        m &= d["total_reviews"] < REVIEW_THRESHOLD
    return d[m]["d_revenue"].sum() / 1e6


def main():
    df = build()
    under = df[df["residual_usd"] < 0]
    over = df[df["residual_usd"] > 0]

    u_est = bucket(under, "short_stay", "established")
    u_new = bucket(under, "short_stay", "newer")
    u_mon = bucket(under, "monthly")
    o_est = bucket(over, "short_stay", "established")

    underpriced = u_est + u_new + u_mon
    overpriced = o_est
    combined = underpriced + overpriced

    # Nights span BOTH review tiers, unlike revenue. The <142 tier is held at
    # beta = -1.0, which nets exactly zero revenue but still recovers real
    # nights: at unit elasticity a price cut raises occupancy proportionally,
    # so the revenue cancels while the bookings are genuinely gained. Counting
    # nights only where revenue is non-zero undercounts them by ~3x.
    nights = over[over["market_segment"] == "short_stay"]["nights_delta"].sum()

    print(f"listings after trim: {len(df):,}\n")
    print("UNDERPRICED                              reported")
    print(f"  short-stay, >=142 reviews  {u_est:+7.2f}M      +0.34M")
    print(f"  short-stay,  <142 reviews  {u_new:+7.2f}M      ~0     (breakeven by construction)")
    print(f"  monthly                    {u_mon:+7.2f}M      +7.94M")
    print(f"  subtotal                   {underpriced:+7.2f}M      +8.27M\n")
    print("OVERPRICED")
    print(f"  short-stay, >=142 reviews  {overpriced:+7.2f}M      -0.70M")
    print(f"  short-stay,  <142 reviews    +0.00M      ~0     (breakeven by construction)")
    print(f"  monthly                       excluded          (beta=0 -> pure price loss)\n")
    print(f"COMBINED HOST GBV            {combined:+7.2f}M      +7.57M")
    print(f"x {TAKE_RATE:.1%} Airbnb take        {combined * TAKE_RATE:+7.2f}M      +1.17M")
    print(f"nights recovered             {nights:+10,.0f}   +77,606")


if __name__ == "__main__":
    main()
