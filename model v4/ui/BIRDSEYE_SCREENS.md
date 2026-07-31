# Birds-eye view — screen guide

Each "screen" is a metric option in the **Metric** dropdown on `nyc_pricing_overview_gbm.html`. The map colors every NYC neighborhood by the selected metric; the **Segment** toggle (short-stay / monthly) and, for two screens, the **Month** picker change what's shown. Neighborhoods with no data grey out.

**Data sources:** the GBM pricing model (`v3_gbm_listing_pricing_signals.csv`, 9,752 active listings — 4,008 short-stay, 5,744 monthly, across 206 neighborhoods), the KNN peer layer, the real 12-month calendar (`past_12mo_calendar.csv`, 300 listings), and the measured elasticity (β = −0.92 short-stay; β = 0 / not significant for monthly).

---

## Original screens (pre-elasticity build)

### 1. Annual pricing gap
How far each neighborhood's listings sit from the GBM fair-value price, on average — diverging red/blue around 0. Blue = priced above fair value, red = below. **Source:** GBM model, all 9,752 listings. **Coverage:** full (177 short-stay / 191 monthly neighborhoods). This is the anchor screen and is current/good.

### 2. Occupancy gap vs. peers
Days per year a neighborhood's listings are booked *behind* their high-performing peers. **⚠️ Caveat:** built on the saturated `occupancy_rate` field (caps at ~255 days), the same artifact removed from the per-listing tool. Values aren't fully trustworthy — flagged for retirement.

### 3. Simulated seasonal price index
Month-by-month price index (needs the **Month** picker), showing the illustrative seasonal curve. Honestly labeled "simulated" — stands in for calendar-level pricing data that isn't public.

### 4. Real occupancy rate (monthly)
Month-by-month occupancy (needs the **Month** picker). **⚠️ Caveat:** "real" is a misnomer — same saturated field as screen 2.

---

## New screens (current-model, marked ▸ in the dropdown)

### 5. ▸ Repricing direction (current model)
Net repricing signal per neighborhood: **share of listings the model flags "raise" minus share it flags "lower"** (from `direction_confidence`), diverging around 0. Red = net underpriced (more raises), blue = net overpriced (more cuts), pale = balanced. **Source:** all 9,752 listings. **Coverage:** every neighborhood with listings of that segment — 177 short-stay / 191 monthly. The strongest new screen. *(Note: colors 1–2-listing neighborhoods the same as dense ones; only 98 short-stay / 125 monthly have ≥5 listings.)*

### 6. ▸ Revenue lift at fair value (current model)
Modeled **% change in revenue** if a neighborhood's listings moved to fair value, β-adjusted to match the per-listing tool exactly (short-stay β = −0.92; monthly β = 0). **Source:** all 9,752 listings + the β rule. **Coverage:** full (177 / 191). The elasticity story is visible in the spread: short-stay lifts are tiny (±a few %, the near-unit-elastic cancellation — raising price sheds almost as much occupancy as it gains), while monthly swings wide (±20–80%, because β = 0 holds occupancy flat). The monthly legend is relabeled *"β = 0, unmeasured — illustrative"* to keep it honest, consistent with the tool and UI_Script.

### 7. ▸ Real 12-mo occupancy (AirROI calendar)
Genuine annual occupancy from the real 12-month calendar, averaged per neighborhood — the trustworthy replacement for screens 2/4. **⚠️ Sparse by design:** only the 300-listing AirROI panel has real calendars, gated at ≥3 listings/neighborhood, so it covers just **8 short-stay / 14 monthly** neighborhoods; the rest grey out. Built as a standalone, deletable screen precisely because it may look too empty to keep.

---

## Coverage at a glance

| Screen | Source | Listings | Neighborhoods |
|---|---|---|---|
| 1. Pricing gap | GBM | 9,752 | 177 / 191 |
| 2. Occupancy gap vs peers ⚠️ | saturated field | — | (retire) |
| 3. Simulated seasonal index | simulated | — | 206 |
| 4. Real occupancy (monthly) ⚠️ | saturated field | — | (retire) |
| 5. ▸ Repricing direction | GBM | 9,752 | 177 / 191 |
| 6. ▸ Revenue lift at fair value | GBM + β | 9,752 | 177 / 191 |
| 7. ▸ Real 12-mo occupancy | AirROI calendar | 300 | 8 / 14 (sparse) |

**"Full coverage" = every listing in the 9,752-listing GBM output, aggregated to neighborhoods** — 177 (short-stay) / 191 (monthly) of the 206 map neighborhoods have listings of that segment; the rest have none and grey out. It is *not* a sample.

## Open items
- Screen 7 (real occupancy) is very sparse — decide keep vs. delete after viewing.
- Screens 2 & 4 use the saturated occupancy field — candidates for retirement (untouched for now, per instruction to build additively).
- Screens 5 & 6 color thin (1–2 listing) neighborhoods as confidently as dense ones — optional: gate at ≥5 listings to grey out thin ones (one-line threshold change).
- Screen 6 shows % on the map only; could add $/yr to the tooltip.
