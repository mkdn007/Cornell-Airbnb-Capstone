> ## ⚠️ READ THIS FIRST — partially superseded (noted 2026-07-31)
>
> This is Jai's master financial working doc (timestamped 2026-07-29 14:03). Two later
> documents revised parts of it the same afternoon. Use this file for the **reasoning**,
> and `REVENUE_TO_ROI.md` for the **current cost and ROI figures**.
>
> | Section | Status |
> |---|---|
> | 1–5, 5b (pitch frame, two-pillar solution, worked examples, aggregate revenue range, Option A vs B) | **CURRENT.** This is the clearest statement of the revenue methodology in the project, including why the earlier $9.6M figure was never a true floor. |
> | **6 (Adoption, Cost, ROI & Timeline)** | **SUPERSEDED.** Uses the greenfield cost basis ($190K build + $105K/yr), giving a negative Year 1 and mid-Year-2 payback. The team adopted the **incremental** basis ($65K build + $30K/yr) — Airbnb already owns model-serving, pricing, and A/B infrastructure. Current figures, including the 10% NPV discounting flagged as an open item here, are in `REVENUE_TO_ROI.md`. |
> | 7–8 (elasticity facts, sources) | **CURRENT.** |
>
> Revenue figures agree across all three documents. Only the cost basis differs, and it
> is what moves payback from ~8 months (here) to ~3 months (current).

# Revenue Lift & ROI — AirROI Pricing Engine
### Cornell BANA 5160 | Jairam Manikandan | July 2026

---

## Elasticity & Review Spectrum — Quick Reference

```
REVIEW COUNT         0          30         142              300        500+
                     |          |           |                |           |
                     ▼          ▼           ▼                ▼           ▼
ELASTICITY        β ≤ -1.5   β ≈ -1.3   β = -0.92        β ≈ -0.7   β ≥ -0.5
                  (highly     (elastic)  (MEASURED         (mild)     (inelastic,
                  elastic)               PILOT MEDIAN)               loyal demand)

DEMAND TYPE       Commodity  Commodity   Near unit-elastic  Brand      Loyal brand
                  listing    listing     — our anchor       building   equity

PRICE CUT →       +GBV       ~$0 to      GBV barely        GBV        GBV falls
WHAT HAPPENS      (surplus   +GBV        falls (-0.8%)     falls      (guests stay
                  bookings)             per 10% cut       modestly   regardless)

PRICE HIKE →      GBV falls  GBV ~$0    GBV barely        GBV        GBV rises
WHAT HAPPENS      (guests    to falls   rises (+0.8%)     rises      (guests
                  leave)               per 10% hike      modestly   stay)

BREAKEVEN LINE    ◄─────────────────── β = -1.0 ───────────────────────────────►
                  (below this line: price cuts increase revenue)
                  (above this line: price hikes increase revenue)

PANEL DATA        ░░░░░░░░░░░░░░░░░░░░░█████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░
                  ← unmeasured         [64 listings]        unmeasured →
                                       med = 142 reviews
                                       med = 14 yrs exp

OUR LISTINGS      ████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░
                  ← 99.3% of underpriced SS listings    → only 0.7% match panel

β ASSIGNMENT      [  β = -1.0 breakeven (conservative)  ][  β = -0.92 measured  ]
(this model)      <── all listings < 142 reviews ───────><── ≥ 142 reviews ─────>

─────────────────────────────────────────────────────────────────────────────────
UNDERPRICED   ↑ price toward fair value
  ≥142 reviews:  small GBV gain  (+$0.34M across 488 listings)   β = -0.92
  <142 reviews:  ~$0 net revenue  (breakeven assumption)          β = -1.0
  Monthly:        full gap captured  (+$7.94M, 2,830 listings)    β = 0 (n.s.)

OVERPRICED    ↓ price toward fair value
  ≥142 reviews:  small GBV loss  (-$0.70M, 417 listings)         β = -0.92
  <142 reviews:  ~$0 net revenue  (+56,565 nights recovered)      β = -1.0
  Monthly:        excluded  (β=0 → pure price cut = pure loss)    β = 0 (n.s.)

COMBINED BEST ESTIMATE:   +$7.57M host GBV  |  +$1.17M Airbnb fee  |  +77,606 nights/yr
CEILING (β=0 all):        +$26.8M host GBV  |  +$4.15M Airbnb fee  |  (unrealistic)
FLOOR (all SS β=-1.0):    +$7.9M  host GBV  |  +$1.22M Airbnb fee  |  (monthly only)
─────────────────────────────────────────────────────────────────────────────────
```

> **Reading this chart:** The breakeven line at β = -1.0 is the single most important number.
> Above it (β between 0 and -1.0): raising price always helps, cutting price always hurts.
> Below it (β past -1.0): cutting price helps, raising price hurts.
> Our measured β = -0.92 sits just above the breakeven — which is why both underpriced gains
> and overpriced losses are tiny in dollar terms, while the nights-recovered story dominates
> the overpriced pitch.

---

## 1. The Internal Airbnb Pitch Frame

Before stating any numbers, the framing matters. This tool is presented as an **internal Airbnb product pitch** — not a host-facing blog post, and not a standalone academic model. That means the success metrics are not "how much does the host make tonight" but the platform health metrics Airbnb VPs and Product Leads actually track:

### A. Gross Booking Value (GBV) & Revenue Capture

GBV is the total dollar value of all bookings made on the platform — Airbnb's fee is a percentage of this number, so every booking that happens (or doesn't) is directly visible in their financials. An overpriced listing with zero demand is a dead calendar date: the host gets nothing, the guest books elsewhere (hotel or competitor), and Airbnb captures zero. Repricing it correctly unlocks that date and converts it to platform GBV. Volume drives total marketplace revenue at scale.

### B. Host Retention & Churn

Overpriced listings are a leading cause of new-host churn. When an inexperienced host lists at $400 for a $220 apartment, gets zero bookings for 6–8 weeks, and quietly deactivates — Airbnb loses a supply-side asset it paid to acquire. Getting that host their first 5–10 booked nights proves the platform works and breaks the abandonment cycle. Host retention is cheaper than host acquisition; this tool targets the moment hosts are most at risk.

### C. Marketplace Liquidity & Search Conversion

When guests search on Airbnb, overpriced unbooked listings degrade the search-to-booking conversion rate — they show up in results, create apparent supply, and then don't convert. Repricing overpriced inventory improves actual conversion efficiency across the NYC market without any additional demand-generation spend.

### D. ADR (Average Daily Rate) Growth

Underpriced listings suppress the platform's ADR metric. A host charging $244 for a listing that comparable peers charge $336 for is leaving $92/night on the table — and Airbnb's per-night fee is proportional to that rate. Moderate, evidence-backed price increases on underpriced listings grow ADR and grow Airbnb's absolute fee revenue without adding a single new listing.

---

## 2. The Two-Pillar Marketplace Solution

| Pillar                                        | Listings              | Mechanism                                                                 | Platform Win                              |
|-----------------------------------------------|-----------------------|---------------------------------------------------------------------------|-------------------------------------------|
| **Underpriced → Margin / ADR Optimization**   | 4,931 listings (50.6%) | Raise price to fair value; host earns more per night; Airbnb fee grows   | ADR growth + raw fee revenue per booking  |
| **Overpriced → Volume & Liquidity Optimization** | 4,821 listings (49.4%) | Lower price to fair value; unlock previously unbooked nights             | GBV growth + search conversion + host retention |

These two sides are not symmetric in terms of measurable dollar revenue — but they are symmetric in terms of what the platform needs. Section 3 handles underpriced. Section 4 handles overpriced. Section 5 shows the aggregate revenue range with appropriate caveats. Section 6 is cost, ROI, and adoption.

---

## 3. Pillar 1 — Underpriced Listings: Margin & ADR Optimization

### The Mechanism

An underpriced listing is one where the host's actual price sits **below** the GBM model's calibrated q10 lower bound — meaning even the 10th percentile of comparable listings charges more. The model has 98.9% confidence on the best-flagged listings. The revenue opportunity is the gap between what the host currently charges and what the market supports, multiplied by occupied nights.

### Working Assumption (Explicit, Presentation-Only)

> Per Manas (7/24): this dataset identifies pricing *opportunity*, not causal revenue uplift. In reality, Airbnb would validate these recommendations against its own proprietary booking-conversion and price-elasticity data before deployment — data this team's dataset doesn't contain. For presentation purposes, we stand in for that with a simplifying assumption: **moving an underpriced listing to fair value is treated as roughly occupancy-neutral**, since fair value is calibrated to what comparable listings already charge and get booked at.

The elasticity model (Section 3.3 below) measures what actually happens to occupancy. The occupancy-neutral assumption is the upper bound; the elasticity-adjusted number is the honest floor.

### Real Example — Spacious Clinton Hill Apt, Brooklyn

**Listing:** [airbnb.com/rooms/15785088](https://www.airbnb.com/rooms/15785088)
**Location:** Clinton Hill, Brooklyn · Entire home/apt · Individual host · Short-stay
**Model confidence:** Confident: raise price — score 98.9
**Calibrated GBM interval:** [$274, $399] — actual price $244 sits **below the bottom**

```
┌─────────────────────────────────────────────────────────────────────────┐
│   UNDERPRICED LISTING — GBM Quantile Regression, 98.9% Confidence      │
├──────────────────────────────────────┬──────────────────────────────────┤
│ Status Quo (Underpriced)             │ Re-priced to Fair Value          │
├──────────────────────────────────────┼──────────────────────────────────┤
│ Nightly Rate:       $244/night       │ Nightly Rate:    $336/night (+38%)│
│ Booked Nights:   21.3 nights/mo     │ Booked Nights: ~15.8 nights/mo*  │
│ GBV:              $5,189/mo         │ GBV:             $5,324/mo (+2.6%)│
│ Host Earnings (−3%): $5,034/mo      │ Host Earnings:   $5,164/mo       │
│ Airbnb Take (15.5%): $804/mo        │ Airbnb Take:     $825/mo         │
└──────────────────────────────────────┴──────────────────────────────────┘
* Occupancy-adjusted using β = −0.92 (short-stay TWFE pilot, n=64).
  Occupancy-neutral upper bound: 21.3 nights → no change.
```

**Monthly Δ (elasticity-adjusted):**
- Host: **+$130/mo → +$1,560/yr**
- Airbnb: **+$21/mo → +$250/yr per listing**

**KNN layer:** 67 comparable peers, 48 high performers. Only 1 missing amenity vs. high performers: **self check-in**. This listing has almost no operational gap — its underpricing is purely a pricing decision, not an amenity problem.

### Is β = −0.92 the Right Elasticity for This Listing?

The short-stay elasticity was measured on a 64-listing panel that skews heavily toward **established Individual hosts with a median of 142 reviews**. This listing has **541 reviews** — significantly above the panel median.

**Implication:** established listings with high review counts have more guest loyalty and face *less* price-sensitive demand than a typical listing. A listing with 541 reviews is arguably more established than the already-established panel average. The true elasticity for this listing is likely **less negative** than −0.92 — meaning the occupancy hit from raising the price is probably *smaller* than the table shows. The elasticity adjustment shown (+38% price → −25.5% occupancy) is a **conservative overestimate of the occupancy loss**. The actual net revenue gain is likely larger than +2.6%.

**Directional conclusion:** β = −0.92 applied here is a conservative floor. The true GBV gain for an established listing like this is higher.

### Value Add Summary

| Stakeholder  | Gain          | Mechanism                                                                 |
|--------------|---------------|---------------------------------------------------------------------------|
| **Host**     | +$1,560/yr    | Higher nightly rate on the same or slightly fewer occupied nights         |
| **Airbnb**   | +$250/yr      | 15.5% of higher GBV; ADR metric improves                                 |
| **Platform** | ADR growth    | One underpriced listing corrected; multiplied across 4,931 = measurable ADR impact |

---

## 4. Pillar 2 — Overpriced Listings: Volume & Liquidity Optimization

### The Mechanism

An overpriced listing is one where the host's actual price sits **above** the GBM model's calibrated q90 upper bound — meaning even the 90th percentile of comparable listings charges less. The signal is `direction_confidence = 'Confident: lower price'`, flagging **1,228 listings** with high model certainty. These listings are actively booking nights below their peer occupancy ceiling, meaning the overpricing is measurably suppressing demand.

The revenue math for the overpriced side is different from underpriced: because short-stay demand is close to unit-elastic (β ≈ −0.92), lowering price and gaining proportional occupancy is nearly revenue-neutral for the host. **The win is not dollars — it's nights booked.**

### Real Example — The GuestHouse Brooklyn, Flatlands

**Listing:** [airbnb.com/rooms/1083457132325313315](https://www.airbnb.com/rooms/1083457132325313815)
**Location:** Flatlands, Brooklyn · Entire home/apt · Individual host · Short-stay
**Model confidence:** Confident: lower price — score 93.9
**Calibrated GBM interval:** [$311, $557] — actual price $563 sits **above the top**

```
┌─────────────────────────────────────────────────────────────────────────┐
│   OVERPRICED LISTING — GBM Quantile Regression, 93.9% Confidence       │
├──────────────────────────────────────┬──────────────────────────────────┤
│ Status Quo (Overpriced)              │ Re-priced to Fair Value          │
├──────────────────────────────────────┼──────────────────────────────────┤
│ Nightly Rate:       $563/night       │ Nightly Rate:    $470/night (−16%)│
│ Booked Nights:    16.0 nights/mo    │ Booked Nights:  18.9 nights/mo   │
│ GBV:              $9,008/mo         │ GBV:             $8,879/mo (−1.4%)│
│ Host Earnings (−3%): $8,738/mo      │ Host Earnings:   $8,612/mo       │
│ Airbnb Take (15.5%): $1,396/mo      │ Airbnb Take:     $1,376/mo       │
└──────────────────────────────────────┴──────────────────────────────────┘
Based on β = −0.92: (470/563)^(−0.92) = 1.181 → +18.1% occupancy
```

**The numbers at a glance:**
- GBV change: **−$129/mo (−1.4%)** — nearly revenue-neutral
- Recovered nights: **+2.9/mo → +34.7 nights/year** that were previously sitting empty
- Airbnb delta: **−$20/mo** — a small nominal decline in fee revenue

**KNN layer:** 68 comparable peers, 49 high performers. This listing books 16 nights/month; its high-performing peers book **21.2 nights/month** — a 5.2 night/month gap. After repricing alone, the gap closes by 2.9 nights. The remaining 2.3 nights require closing the amenity gap:

> **Missing vs. high-performers:** hangers · bed linens · microwave · refrigerator · cooking basics

The two-layer pitch: repricing gets 2.9 nights back; adding kitchen basics and linens closes the remaining 2.3. Together the listing reaches peer performance (+5.2 nights/month = +62 nights/year).

### Is β = −0.92 the Right Elasticity for This Listing?

The short-stay elasticity panel median is **142 reviews**. The GuestHouse Brooklyn has **48 reviews** — below the panel median, and well below the population-established threshold.

**Implication:** a listing with fewer reviews has less accumulated guest loyalty and faces *more* price-sensitive demand than the already-established panel. The true elasticity for this listing is likely **more negative** than −0.92 — meaning the occupancy recovery from repricing is probably *larger* than the +18.1% shown in the table.

**Directional conclusion:** β = −0.92 understates the occupancy recovery for this listing. The actual recovered nights figure (+2.9/mo) is a **conservative floor**, not an overstatement. The real platform liquidity win is likely larger.

### Why This Is a Strong Internal Airbnb Argument (Even With −$20/mo)

The Airbnb fee income from a single overpriced listing barely moves: −$20/month is noise. The platform argument is not per-listing fee math. It is:

| Platform Metric           | Effect of Repricing This Listing                                                  |
|---------------------------|-----------------------------------------------------------------------------------|
| **Booked nights / GBV**   | +2.9 nights/mo that were previously unbooked; each night is a guest transaction   |
| **Search conversion**     | An overpriced unbooked listing clogs search results; repricing it converts        |
| **Host retention**        | A host getting bookings stays on the platform; a host at zero leaves              |
| **Competitor leakage**    | A guest who can't book on Airbnb goes to Booking.com or a hotel                  |

Multiply these effects across 1,228 confidently-overpriced listings and the argument shifts from individual-listing fee math to platform health at scale.

### Value Add Summary

| Stakeholder  | Gain                    | Mechanism                                                                    |
|--------------|-------------------------|------------------------------------------------------------------------------|
| **Host**     | +34.7 nights/yr booked  | Near-neutral revenue (−1.4%) but calendar fills; proof the platform works    |
| **Airbnb**   | Nights booked           | Marketplace liquidity; each recovered night is a guest conversion            |
| **Platform** | Retention + conversion  | Host stays active; search results convert better                             |

---

## 5. Aggregate Revenue Range

### Methodology

- **Source:** `outputs_gbm/v3_gbm_listing_pricing_signals.csv`, 9,752 active NYC listings (Inside Airbnb, June 14 2026 snapshot)
- **Outlier control:** 1–99 percentile trim. ~50 listings above the 99th percentile are excluded — this is exactly where GBM prediction reliability breaks down (luxury segment, mean actual ~$927/night vs. model fair ~$1,153/night).
- **Model-noise discount:** applied to the residual gap per segment — **19.2% for short-stay, 15.2% for monthly**. Sourced from the GBM model's own documented median error, not assumed.
- **Occupied nights:** backed out from Inside Airbnb's formula: `estimated_annual_revenue / nightly_price`.

### The Elasticity Problem — Why $9.6M Is Not a Lower Bound

The prior framing called $9.6M the "lower bound." That was wrong. β = -0.92 was measured on 64 listings with a median of 142 reviews and 14 years hosting experience. **99.3% of underpriced short-stay listings are below that profile.** Applying β = -0.92 to a 20-review listing uses an elasticity measured on the least price-sensitive hosts in the market — which is optimistic for newer listings whose true β is likely -1.3 to -2.0.

**The true floor is β = -1.0 — the mathematical breakeven.** At unit elasticity, every dollar gained from a higher price is exactly offset by occupancy loss, netting to $0. This requires no data — it is an algebraic identity. For listings where true β < -1.0, raising price actually loses money, meaning no rational host acts on the recommendation and those listings contribute $0 to the revenue calculation anyway.

### Symmetric β Framework

β is a property of demand, not price direction. The same β applies whether a listing is raising or cutting price. The conservative assignment:

| Review tier                   | β assigned | Rationale                                        |
|-------------------------------|------------|--------------------------------------------------|
| ≥142 reviews (panel-matched)  | **−0.92**  | Measured on this exact profile                   |
| <142 reviews (below panel)    | **−1.0**   | Mathematical breakeven — no extrapolation needed |
| Monthly (either side)         | **0**      | β not statistically significant (p = 0.734)      |

### Option A — Underpriced Listings Only

| Scenario                              | SS ≥142   | SS <142   | Monthly   | Total       |
|---------------------------------------|-----------|-----------|-----------|-------------|
| **Ceiling** (β=0, no occ. response)   | —         | —         | —         | **~$26.8M** |
| **Segmented estimate** (symmetric β)  | +$0.34M   | ~$0       | +$7.94M   | **$8.27M**  |
| **Floor** (all SS at breakeven)       | ~$0       | ~$0       | +$7.94M   | **~$7.9M**  |

The ceiling ($26.8M) is what you get if raising price has zero effect on occupancy — unrealistic for any real market. The segmented estimate ($8.27M) is the most defensible number: it uses the measured β where applicable and the mathematical breakeven everywhere else. The floor (~$7.9M) is the worst case where all short-stay gains cancel out and only the unaffected monthly segment remains.

**Why the short-stay segment contributes so little even at the best estimate:** the median underpriced short-stay listing is 17–20% below fair value. At β = -0.92, raising price by that much predicts an occupancy drop of similar magnitude — the two nearly cancel. Short-stay demand is close to unit-elastic. The monthly segment ($7.94M) dominates because its occupancy-neutral assumption is defensible (no significant elasticity measured).

### Option B — Combined Under + Overpriced (Complete Picture)

Including the overpriced side gives a complete view of what happens if the full addressable market reprices:

**Underpriced (host raises to fair value):**
- SS ≥142 reviews, β = -0.92: **+$0.34M**
- SS <142 reviews, β = -1.0: **~$0** — we assign breakeven as the best estimate, not worst case. The true β for these listings is unknown but plausibly sits between -0.92 and -1.3. Listings where β is between -0.92 and -1.0 would show a small positive revenue gain; listings where β is below -1.0 would show a small negative. We don't know which side each listing falls on, so $0 splits the difference — the upside and downside uncertainty offset each other. This is more honest than picking a direction we can't prove.
- Monthly, β = 0: **+$7.94M**
- **Underpriced total: +$8.27M**

**Overpriced (host cuts to fair value):**
- SS ≥142 reviews, β = -0.92: **−$0.70M** (established hosts barely gain nights; revenue loss)
- SS <142 reviews, β = -1.0: **~$0** — same logic as above, symmetric. The true β for these listings is unknown. If β is between -1.0 and -1.3, cutting price to fair value increases their revenue (upside). If β is between -0.92 and -1.0, it slightly decreases it (downside). Assigning $0 reflects that we genuinely don't know which side dominates — and the two possibilities plausibly cancel. What we can say with confidence: these listings recover nights regardless of which side of the breakeven their β sits on.
- Monthly excluded — β = 0 means a pure price cut with no occupancy response = pure revenue loss
- **Overpriced SS total: −$0.70M**

**Combined:**

| Metric                             | Value            |
|------------------------------------|------------------|
| **Host GBV delta**                 | **+$7.57M/yr**   |
| **Airbnb fee revenue (×15.5%)**    | **+$1.17M/yr**   |
| **Nights recovered (overpriced)**  | **+77,606/yr**   |

The 77,606 recovered nights are **not addable to the $7.57M** — they are already inside the GBV delta calculation. They are a separate platform metric: nights that were previously empty calendar dates converting to actual bookings, each representing a guest conversion, a search result that converts, and a host who stays on the platform.

**Why overpriced ≥142 loses revenue:** at β = -0.92, cutting price generates +9.2% more bookings per 10% price cut — but the host needed +10% more bookings just to break even (that's β = -1.0). The price cut is working, just not hard enough to overcome the lower rate. For <142 review listings, the true β is likely more negative than -1.0, meaning they probably gain revenue from repricing — but we can't prove the number without measuring it. That is the AirROI ask.

### The Honest Range

| Scenario                              | Host GBV               | Airbnb fee | What it means                                    |
|---------------------------------------|------------------------|------------|--------------------------------------------------|
| **Ceiling** (underpriced only, β=0)   | ~$26.8M                | ~$4.15M    | No one loses occupancy from repricing — unrealistic |
| **Best estimate** (Option B)          | **$7.57M**             | **$1.17M** | Most defensible; uses measured β where available |
| **Floor** (all SS at breakeven)       | ~$7.9M (underpriced)   | ~$1.22M    | Monthly dominates; SS nets zero                  |

**Recommended presentation frame:** lead with the $7.57M combined best estimate and $1.17M Airbnb fee at 100% adoption. Present the $26.8M ceiling as the occupancy-neutral upper bound. Use the sensitivity table below to show what realistic adoption rates produce.

### Overpriced Revenue Band — Mirroring the Underpriced Range

The underpriced side has a defensible range: a floor (all short-stay at breakeven, ~$7.9M) and a ceiling that won't literally happen (occupancy-neutral β = 0, $26.8M). The overpriced side has the exact same structure — a defensible floor and an illustrative ceiling — it just points in the opposite direction on revenue and requires a different bounding assumption.

**Why the overpriced side *can* show revenue growth (unlike at β = −0.92):** a price cut becomes revenue-positive once β passes −1.0. Established hosts (β = −0.92) sit just above breakeven, so they lose a little. But the 1,506 overpriced listings below 142 reviews are almost certainly *more* elastic than the panel — plausibly β = −1.3 to −1.5 — which is exactly the zone where cutting price to fair value *increases* host revenue.

| Scenario                                          | β assumption                          | Overpriced SS Host GBV | Nights recovered |
|---------------------------------------------------|---------------------------------------|------------------------|------------------|
| **Floor** (measured / breakeven)                  | −0.92 for ≥142, −1.0 for <142         | **−$0.70M**            | +77,606          |
| **Midpoint estimate** (newer listings elastic)    | −0.92 for ≥142, −1.3 for <142         | **+$7.06M**            | +98,741          |
| **Upper estimate** (commodity-tier elasticity)    | −0.92 for ≥142, −1.5 for <142         | **+$12.74M**           | +114,172         |
| **Illustrative ceiling** (won't happen)           | −1.5 applied to *all* overpriced SS   | **+$18.39M**           | —                |

**The defensible overpriced band: −$0.70M (measured floor) → +$12.74M (if sub-142-review listings are elastic at β = −1.5), midpoint ~+$7M.**

### The Symmetry With the Underpriced Ceiling — and One Honest Caveat

This is deliberately parallel to the underpriced logic:

| | **Underpriced** | **Overpriced** |
|-----------------|-----------------------------------------|------------------------------------------|
| Floor (conservative) | All SS at breakeven → ~$7.9M            | Measured/breakeven → −$0.70M             |
| Best estimate   | Segmented β → $8.3M                     | Segmented β (−1.3 for <142) → +$7.1M     |
| Ceiling (won't happen) | β = 0, occupancy-neutral → $26.8M       | β = −1.5 all → +$18.4M                    |

**The honest caveat you must state when presenting this:** the underpriced ceiling (β = 0) is a *cleaner* bounding assumption than the overpriced ceiling (β = −1.5). β = 0 is a natural boundary — occupancy literally cannot respond less than "not at all." β = −1.5 is a *chosen* extreme, not a natural limit. So the overpriced ceiling is softer and should be labeled explicitly as "illustrative of commodity-tier elasticity," not a hard upper bound.

For this reason we cap the illustrative overpriced ceiling at β = −1.5 (+$12.7M), not β = −2.0 (+$40.8M). The −2.0 figure is so large it invites skepticism and undercuts credibility; −1.5 is defensible as the low end of what commodity-listing elasticity looks like in demand literature.

### Note on Why the Overpriced Floor Is Negative (for Established Hosts)

At β = −0.92, overpriced listings that cut price lose a small amount of host revenue (−$0.70M across 417 listings ≥142 reviews). This is because `1 + β = 0.08` — revenue elasticity is barely positive, so cutting price nearly cancels out. No rational established host cuts their price for revenue reasons at this elasticity — for them, the pitch is nights recovered and platform health, not host revenue.

The revenue *upside* on the overpriced side lives entirely in the sub-142-review population, where elasticity is likely past −1.0. We present that as the +$7M midpoint band above, clearly flagged as dependent on an unmeasured elasticity — which is precisely the AirROI data ask.

---

## 5b. Combined Revenue: What Actually Matters for the Airbnb Pitch

Airbnb's internal executives track GBV, fee revenue, and nights booked — not host revenue in isolation. Here is the combined picture at 100% adoption:

| Metric                            | Value                          | How to present it                                     |
|-----------------------------------|--------------------------------|-------------------------------------------------------|
| Host GBV increase                 | +$7.57M/yr                     | "Hosts collectively earn $7.6M more"                  |
| Airbnb fee increase               | +$1.17M/yr                     | "Platform captures $1.2M in additional fees"          |
| Nights recovered                  | +77,606/yr                     | "77,600 previously empty calendar dates become bookings" |
| Airbnb fee on recovered nights    | +~$2.4M/yr at avg $200/night   | **Platform liquidity argument only — not added to $1.17M** |

The recovered nights fee (~$2.4M) is a ceiling estimate for what those 77,606 nights could generate if all booked at an average of $200 — but it double-counts with the −$0.70M already in the GBV delta for established hosts. Present it as a separate platform argument, clearly labeled as illustrative.

**The single headline number for the presentation:** at 25–35% adoption, the tool generates **$290K–$410K in incremental Airbnb fee revenue per year**, paying back the $295K Year-1 cost within the first year at 35% adoption.

---

## 6. Adoption, Cost, ROI & Timeline

### Adoption — Sensitivity Table

No external benchmark exists for "% of a measured pricing gap a host base actually captures." Presented as a sensitivity table rather than a single invented number — stronger for an evidence-backed rubric.

Revenue base: **$7.57M best estimate (Option B) → $26.8M ceiling (occupancy-neutral)**.

**At the best estimate ($7.57M, Option B):**

| Adoption | Host GBV lift | Airbnb fee (15.5%) | Year-1 net (after $295K) | Payback     |
|----------|---------------|--------------------|--------------------------|-------------|
| 15%      | $1.14M        | $176K              | −$119K                   | —           |
| 25%      | $1.89M        | $293K              | −$2K                     | ~12 months  |
| 35%      | $2.65M        | $410K              | $115K                    | ~8 months   |
| 50%      | $3.79M        | $587K              | $292K                    | ~6 months   |
| 75%      | $5.68M        | $880K              | $585K                    | ~4 months   |

**At the occupancy-neutral ceiling ($26.8M):**

| Adoption | Host GBV lift | Airbnb fee (15.5%) | Year-1 net (after $295K) | Payback      |
|----------|---------------|--------------------|--------------------------|--------------|
| 15%      | $4.02M        | $623K              | $328K                    | ~5 months    |
| 25%      | $6.70M        | $1.04M             | $743K                    | ~3.5 months  |
| 35%      | $9.38M        | $1.45M             | $1.16M                   | ~2.5 months  |
| 50%      | $13.4M        | $2.08M             | $1.78M                   | ~1.7 months  |
| 75%      | $20.1M        | $3.12M             | $2.82M                   | ~1.2 months  |

**Recommended presentation frame:** lead with the $7.57M best estimate at 35% adoption — $410K/yr Airbnb fee, payback in ~8 months. Show the ceiling as an upside scenario, not the headline.

### Cost

**One-time build:** ~$190K (0.6 FTE Sr. DS/MLE + 1.0 FTE Backend + 0.5 FTE Frontend + 0.25 FTE PM over 4 months; Glassdoor 2026 fully-loaded comp × 1.3 loading multiplier)

**Annual run (labor + infra + LLM):** ~$105K/yr

**Total 5-year cost:** ~$715K

**Note (Jai, 7/24):** the above is a "greenfield standalone build" cost. Airbnb almost certainly already has model-serving infra, A/B testing pipelines, and pricing-feature engineering in place. The true incremental cost of adding this as a feature is estimated at $50–80K in engineering time — but this uses Glassdoor-sourced benchmarks while the greenfield estimate doesn't, so both scenarios should be shown side by side rather than replacing one with the other.

### ROI — 5-Year, at Best Estimate $7.57M (Option B)

Using Rogers' Diffusion of Innovation adoption ramp (recalibrated to real SaaS feature-adoption benchmarks):

| Year | Adoption | Airbnb revenue | Cost  | Net cash flow | Cumulative |
|------|----------|----------------|-------|---------------|------------|
| 1    | 10%      | $117K          | $295K | −$178K        | −$178K     |
| 2    | 24%      | $281K          | $105K | $176K         | −$2K       |
| 3    | 38%      | $445K          | $105K | $340K         | $338K      |
| 4    | 42%      | $492K          | $105K | $387K         | $725K      |
| 5    | 42%      | $492K          | $105K | $387K         | $1.11M     |

**Payback: mid Year 2** on the best estimate. At the ceiling ($26.8M), payback is within Year 1.

**⚠️ Open item (Jai):** figures above are nominal sums — NPV at 10% discount rate would reduce Year 4–5 figures modestly. Flagged for correction before final deck.

---

## 7. Elasticity Model — Key Facts for the Pitch

The two-way fixed effects (TWFE) log-log regression is the methodological backbone for all occupancy-adjusted revenue claims. Key facts to have at hand:

| Fact                            | Value                 | Source                              |
|---------------------------------|-----------------------|-------------------------------------|
| Short-stay elasticity           | β = −0.916            | TWFE model, 64 listings, 884 obs    |
| p-value                         | p < 0.0001            | HC3 robust SE                       |
| Bootstrap 95% CI                | [−1.30, −0.54]        | 100 resamples by listing            |
| R² within (short-stay)          | 0.348                 | Post-demeaning OLS                  |
| Monthly elasticity              | β = +0.084, p = 0.734 | Not significant                     |
| Panel listings                  | 258 (64 SS, 194 mo.)  | AirROI free tier                    |
| Panel date range                | July 2025 – June 2027 | 24 months                           |
| Panel median reviews            | 142                   | vs. population median 24            |
| Panel median host experience    | 14 years              | vs. population median 5 years       |

**The selection bias argument (say this when asked):** the panel skews heavily toward the most established, loyal-demand Individual hosts in the market — listings with 6× more reviews and 3× more hosting experience than average. These hosts face the *least* price-sensitive demand of any segment. If even they face β = −0.92 (p < 0.0001), then the broader market — newer listings, less-established hosts, Enterprise operators — almost certainly faces stronger elasticity. β = −0.92 is a conservative lower bound on market-wide price sensitivity, not a claim about all 4,008 short-stay listings.

---

## 8. Data and Model Sources

| Component            | File                                              | Description                                      |
|----------------------|---------------------------------------------------|--------------------------------------------------|
| GBM pricing signals  | `outputs_gbm/v3_gbm_listing_pricing_signals.csv`  | 9,752 listings, direction_confidence, residuals  |
| KNN comparables      | `outputs_knn/v3_knn_recommendations.csv`          | Peer occupancy, amenity gaps per listing         |
| Active listings      | `active_listings_clean_v6.csv`                    | 80-column feature set, review counts, occupancy  |
| Elasticity model     | `new_Data/elasticity_model.py`                    | TWFE pipeline, bootstrap, segment split          |
| Elasticity results   | `new_Data/outputs_elasticity/elasticity_results.csv` | β, SE, p-value per segment                    |
| Elasticity README    | `new_Data/README_elasticity_model.md`             | Full methodology, limitations, business impl.    |
| AirROI panel listings| `new_Data/new_listings.csv`                       | 237 listings, TTM metrics, adjusted occupancy    |
