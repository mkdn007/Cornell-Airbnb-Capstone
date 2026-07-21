# Confidence Score Fix, Proposed for Review

**Not merged. This is a proposed fix for Manas to review and decide on, sitting alongside the original v3 files, not replacing them.**

## What's wrong in the original

In `model_v3.py`, `score_confidence()`:

```python
def score_confidence(rel_unc, seg_mape):
    stability=np.clip(1-rel_unc/0.25,0,1)
    model_quality=np.clip(1-seg_mape/0.60,0,1)
    score=100*(0.7*stability+0.3*model_quality)
    label=pd.cut(score,[-1,55,75,101],labels=['Low','Medium','High']).astype(str)
    return score,label
```

Checked directly against the actual output file (`v3_listing_pricing_signals.csv`): every one of the 9,752 listings comes back `confidence_level = "Low"`. Confidence score only ranges 17.5-27.4, nowhere near the 55/75 cutoffs that would ever produce "Medium" or "High".

## Root cause

`prediction_uncertainty_pct` (the `rel_unc` fed into this function) sits at:

| Segment | min | 25th | median | 75th | max |
|---|---|---|---|---|---|
| short_stay | 0.2662 | 0.2721 | 0.2765 | 0.2848 | 0.4438 |
| monthly | 0.2215 | 0.2239 | 0.2277 | 0.2338 | 0.3937 |

Two separate problems:

1. **The 0.25 threshold assumes uncertainty can approach 0.** It can't, the real floor sits at 0.22-0.28, right next to the cutoff. `stability = clip(1 - rel_unc/0.25, 0, 1)` clips to exactly 0 for almost every listing.
2. **Within-segment variation is too tight for a ratio-based fix.** Standard deviation is only 0.012-0.016 against a mean of ~0.23-0.28. Tried raising the denominator to the segment's own 95th percentile first, that still produced 0% Medium/High for both segments (tested directly, see below), because the bulk of listings (25th-75th percentile) are clustered within a few thousandths of each other. No fixed or percentile-ratio denominator can create real separation out of a distribution this tight.

## The fix

Use each listing's within-segment percentile rank instead of a ratio to any fixed or computed threshold:

```python
rel_unc_series = pd.Series(rel_unc)
stability = (1 - rel_unc_series.rank(pct=True)).to_numpy()
```

Percentile rank is uniform by construction, so this guarantees stability spreads across its full 0-1 range regardless of how tightly clustered the raw values are. Everything else, the 0.7/0.3 weighting, `model_quality`, the 55/75 label cutoffs, is unchanged.

## Verified before proposing this

- Ran the full pipeline end to end (`model_v3_confidence_fix.py`, same input file, same `--input`/`--output-dir` CLI), not just the isolated function.
- Pricing metrics are unchanged (confirms this only touches confidence scoring, nothing in the pricing model itself):

| Segment | R2_log | MAE_USD | Median_APE |
|---|---|---|---|
| short_stay | 0.6049 | $124.08 | 25.10% |
| monthly | 0.7058 | $47.43 | 21.07% |

Matches the original output exactly.

- New confidence distribution, real spread across all three labels:

| Level | Count |
|---|---|
| Low | 5,066 |
| Medium | 2,794 |
| High | 1,892 |

- Also tested a percentile-ratio approach first (denominator = segment's own 95th percentile of `rel_unc`) before landing on rank-based. It still produced 0 Medium and 0 High for both segments, confirmed directly, not assumed, which is why rank-based was used instead of just picking a different constant.

## Files here

- `model_v3_confidence_fix.py` — full copy of `model_v3.py` with only `score_confidence()` changed
- `outputs_with_fix/` — this script's real output, for direct comparison against `model v3/outputs/` (the original)
