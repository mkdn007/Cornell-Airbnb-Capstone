# Presentation Planning Notes

Working notes for the final presentation, capturing where things stand so anyone on the team can pick up a section. Source material: the 7/23 team call with Stan (transcript in `transcript_labeled.txt` — external, not in this repo), this planning thread, and the faculty guidance email received 7/24 (Jamie, Vidur, Rob). Nothing here is final; each section needs team sign-off before it's locked. **This is a breadcrumb document, not a finished deck or script** — it exists to give whoever picks up a section enough context to finish it, not to hand over completed slides.

---

## 0. IMPORTANT — Read This First: Faculty Guidance Changes the Plan

An email from the faculty (7/24) makes clear the actual presentation context is different from what Sections 1-7 below were originally built for. **Sections 1-6 (problem/solution statements, revenue lift, cost, ROI, financial timeline) are still valid** — that's real analysis and doesn't change. **Section 7 (slide sequence) needed a rebuild** and has been redone below to reflect the real requirements. Key differences from the original plan:

- **Time is ~25 minutes, not 10.** The original 9-slide sequence was built for a 10-minute board-style pitch per Stan's coaching. Stan's advice is still good *advice* (business-first framing, one message per slide, don't over-index on technical depth), but the actual grading rubric requires more content than a 10-minute pitch allows.
- **✅ RESOLVED (7/26):** Jamie confirmed **25 minutes presentation + 10 minutes Q&A, separate.** This matches the assumption Section 7 was already built on — no rebuild needed. The team's ~20-minute planned target (buffer under the 25) still stands.
- **The demo should be pre-recorded and narrated, not live.** Faculty explicitly warn: "Murphy's law prevails... if something will go wrong it will."
- **There's a formal grading rubric** (below) with required content items that weren't all in the original plan — most notably 2-4 slides on key variables/relationships (EDA), which didn't exist before at all.
- **Submission has two parts:** the slide deck (PPT or PDF) goes to Canvas; a link to this GitHub repo (with model outputs/interim work) goes to the faculty member and CA separately, by email or Canvas comment. **The repo link has already been shared with our primary faculty advisor (Jamie).** Unconfirmed whether the CA has it too — worth double-checking before treating this as fully done.

### The grading rubric (50 points total = 25% of overall grade)

- **Coverage (10 pts):** all required components below are covered; -1 per missing item
- **Communication (25 pts):** clear "what/how/so what" narrative, persuasive with evidence, professional Q&A — this is half the grade, weight the prep time accordingly
- **Quality (10 pts):** clean, captioned, easy-to-read slides; straightforward text
- **Time (5 pts):** staying within the limit

### Required content checklist (from the grading criteria — cross-reference against Section 7's slide list)

- [ ] Introduction: team members + industry coach (Stan)
- [ ] Company/industry background
- [ ] Business situation and context ("why" this question)
- [ ] Key question + sub-questions + potential business benefit
- [ ] Dataset(s) used
- [ ] Key variables + key relationships (**2-4 slides**, faculty-specified — this is new, wasn't in the original plan)
- [ ] Model/approach overview + tools ("the how")
- [ ] Insights and learnings from the model
- [ ] Challenges, caveats, data mitigation
- [ ] Predictions/prescriptions/recommendations ("so what," what should the business do)
- [ ] Relevance to team members' current company/career, if applicable
- [ ] Next steps: what would the team explore further, what other data would help

### Other faculty tips worth remembering while building slides

- The Canvas item list is *not* a slide-order template — be creative with structure, just cover the bases
- Figure out the "punchline" / story first, then build slides to support it
- If presenting as a consulting team, pick one client lens (we're doing "internal Airbnb team," which already satisfies this)
- Give every team member a meaningful role, with smooth/natural transitions between speakers
- One message per slide — topic sentence/tagline carries the point, body supports it
- Prepare a separate **appendix** (not part of the timed presentation) for technical Q&A backup
- No phone notes during presentation — put notes on slides if needed
- This is an MS in *Business Analytics* — the business story matters as much as the analytics
- Think about how you want the class to remember this presentation

---

## 1. Problem Statement

**Current draft:**
> *Hosts are leaving money on the table, and so is Airbnb.*
> Most hosts price on gut feel, or take Smart Pricing's black-box number as-is, not on real data. Since Airbnb takes a cut of every booking, every underpriced night costs Airbnb revenue too.

**Notes:**
- Format is headline + one supporting sentence, matching Stan's guidance (short, numbers-first). Still fine to use in the expanded deck, just note it now shares billing with a fuller "Context & Problem" slide (Section 7, Slide 3) rather than standing alone.
- Airbnb's take rate is a real, sourced figure: 15.5% host-only fee (transitioning from the old 3%/14% split model), effective Sept 15 2026 (non-EU) / Oct 13 2026 (EU).
- Positions explicitly against Airbnb's existing **Smart Pricing** feature — auto-sets one nightly rate in a host-defined band, gives no explanation, widely reported (host-side sources, not an Airbnb statement) to lean toward optimizing occupancy over host revenue.

**Open items:** none blocking — ready for team review.

---

## 2. Solution Statement

**Current draft:**
> *We turn Airbnb's own data into a pricing engine for hosts.*
> Airbnb already recommends prices, but it doesn't give hosts enough evidence to trust and act on those recommendations. This product does: it shows the host where their price sits relative to real comps, explains why, and lets them test different price points themselves.

**Notes:**
- Key differentiator is agency + explainability, not a different price output. (Framing above tightened per Manas's note, 7/24 — sharper version of the same "goes further than Smart Pricing" point.)
- Current model output is a **GBM quantile-regression "fair value" price (with a calibrated confidence interval)** plus a **KNN peer-comparable layer** that also surfaces amenity/operational gaps — reconcile pitch language with this before finalizing.
- **Script-only line (not on the slide):** Brendan's Commander's Intent / Mission Command framing — soldiers perform better knowing the *why*, not just the order, because it builds buy-in. Same logic: a host who understands why a price is optimal is more likely to act on it. This is also the mechanism that makes the revenue-lift number realizable (see adoption rate, Section 3) — land this line during the Solution Statement slide delivery (Section 7, Slide 7).

**Open items:** reconcile solution language with the actual KNN/amenity-gap output; team sign-off.

---

## 3. Revenue Lift

**Data source (real, from this repo — GBM model, current as of 2026-07-26):**
`outputs_gbm/v3_gbm_listing_pricing_signals.csv` (GBM quantile regression, supersedes the earlier Ridge output), 9,752 listings, joined to `active_listings_clean_v6.csv`.
- 4,931 listings (50.6%) underpriced vs. fair value; 4,821 (49.4%) overpriced. (Under the earlier Ridge model this was a much less balanced 60.6%/39.4% — the GBM model is better calibrated, so less of the old gap survives as genuine mispricing vs. model noise.)
- Occupied nights/year backed out from Inside Airbnb's own formula: `estimated_annual_revenue / nightly_price`.

**Working assumption (explicit, presentation-only — per Manas, 7/24):** this dataset identifies pricing *opportunity*, not causal revenue uplift. In reality, Airbnb would validate these recommendations against its own proprietary booking-conversion and price-elasticity data before deployment — data this team's dataset doesn't contain. For presentation purposes, we stand in for that with a simplifying assumption: moving an underpriced listing to fair value is treated as roughly occupancy-neutral, since fair value is itself calibrated to what comparable listings already charge and get booked at.

**Outlier control — 1-99 percentile trim (recommended):** only ~50 listings sit above the 99th percentile, and that's exactly where prediction reliability breaks down (luxury listings, mean actual price ~$927/night vs. model "fair" price ~$1,153/night). Wider trims (2-98, 5-95) cut hundreds more listings for little additional cleanup — risks discarding real signal.

**Model-noise discount:** applied per segment using the GBM model's own documented median error — short-stay 19.2%, monthly 15.2% (down from 25.1%/20.9% under Ridge, since GBM is better calibrated). Sourced from the model's own accuracy metrics, not invented.

**Base after 1-99 trim + model-noise discount: $25.6M total addressable host revenue lift** (17.9% of the underpriced subset's current revenue), before any adoption-rate haircut. (Down from $41.4M under Ridge — smaller, more balanced underpriced pool, partly offset by the lighter noise discount.)

**Adoption rate:** no external benchmark exists for "% of a measured pricing gap a host base actually captures" — searched revenue-management/dynamic-pricing literature, found nothing that maps cleanly. **Presented as a sensitivity table, not one invented number** — stronger for a rubric that rewards "evidence-backed" claims, and it's the number the Commander's Intent narrative argues the team can move.

**✅ DONE (7/26-27): Jai's price-elasticity pilot changes the revenue-lift story from a single number to a real bounded range.** Independent third-party data (AirROI, free tier), 24-month per-listing price/occupancy panel, two-way fixed-effects regression (listing + month FE, isolates price's effect from everything else that's constant about a listing). Verified independently from raw data — every reported statistic reproduces exactly.

- **Short-stay: β = −0.916** (p<0.0001, bootstrap 95% CI [−1.30, −0.54]). A 10% price increase predicts a ~9.2% occupancy drop.
- **Monthly: not significant** (p=0.734) — no detectable within-listing price/occupancy relationship in this pilot; occupancy-neutral assumption stands for monthly, unchanged.
- **Sample caveat, stated plainly:** the 64 short-stay listings in the panel skew hard toward established, loyal-demand Individual hosts (6× the reviews, 3× the hosting tenure of the population) — this is a conservative floor on market-wide price sensitivity, not a claim about all 4,008 short-stay listings.

**✅ DONE (7/29): Jai's second pass — review-count segmentation, fixing the extrapolation problem in the first version.** The −0.916 coefficient was measured on established, high-review hosts. Applying it uniformly to every short-stay listing (including brand-new ones) extrapolates past where it was actually measured — the same flaw the team already avoided on the model side by capturing reviews as a feature. Jai's fix: split at 142 reviews (the panel's own median, where β was actually measured).

- **≥142 reviews:** apply the measured β = −0.916.
- **<142 reviews:** don't extrapolate — hold at β = −1.0 (mathematical breakeven → $0), even though the honest expectation is these newer, more price-sensitive listings sit somewhere between −1.0 and −0.92 with real (if unmeasured) upside.

**Underpriced band (short-stay + monthly):**

| Scenario | SS ≥142 reviews | SS <142 reviews | Monthly (unaffected) | Total |
|---|---|---|---|---|
| **Ceiling** (β=0, occupancy-neutral — won't happen, real upper wall) | — | — | — | **~$26.8M** |
| **Segmented estimate** (the honest middle) | +$0.34M | ~$0 | +$7.94M | **$8.27M** |
| **Floor** (all short-stay at breakeven) | ~$0 | ~$0 | +$7.94M | **~$7.9M** |

*(The ~$26.8M ceiling here is Jai's refreshed figure — slightly above the $25.6M cited earlier in this section; the gap is the segmentation refinement, not a data change. Use $26.8M going forward.)*

**Why underpriced short-stay contributes almost nothing (+$0.34M) despite being half the dataset:** the median underpriced short-stay listing sits ~17-20% below fair value. At β≈−0.92, raising price by that much predicts an occupancy drop of similar size — gain and loss nearly cancel. The number that actually carries the pitch is the **monthly segment (+$7.94M)**, because monthly elasticity came back statistically insignificant (p=0.734) and stays occupancy-neutral. If a professor asks "isn't your revenue basically just the monthly listings?" — yes, and that's the honest reason why.

**Overpriced listings — reopened 7/29, superseding the 7/27 "fairness signal only" decision.** The earlier call excluded overpriced entirely, reasoning that since revenue's elasticity w.r.t. price (`1+β` ≈ 0.084) is barely positive, cutting price is revenue-negative for hosts on average. That's true for the *established* segment — but it's the same extrapolation error being fixed above, just left uncorrected on this side. Applying the same 142-review segmentation instead of a population-average dismissal:

| Scenario | β assumption | Overpriced host GBV | Nights recovered |
|---|---|---|---|
| **Floor** (measured/breakeven) | −0.916 for ≥142, −1.0 for <142 | **−$0.70M** | +77,606/yr |
| **Midpoint** (newbies genuinely elastic) | −0.916 for ≥142, −1.3 for <142 | **+$7.06M** | +98,741/yr |
| **Ceiling** (illustrative, won't happen) | −1.5 for all overpriced | **+$18.4M** | — |

**Recommendation (Brendan's judgment, 7/29): adopt this instead of the 7/27 exclusion.** The segmented version applies the same rigor to both halves of the dataset rather than nuance on one side and a blanket dismissal on the other — that's more defensible under questioning, not less, and it doesn't cost the narrative anything: the existing two-pillar frame (**underpriced = margin, overpriced = volume**) already covers it. On the floor, established overpriced hosts book a real, honestly-stated −$0.70M loss on GBV, and +77,606 recovered nights is the actual story here, not dollars.

**✅ DECIDED — team agreed (confirmed 7/31): Option B, the combined figure.** Jai's master financial doc (`REVENUE_LIFT_ROI_MASTER.md`, Section 5) lays the choice out explicitly as "Option A (underpriced only, $8.27M)" vs "Option B (combined, $7.57M)" and recommends Option B. Every downstream deliverable already reflects it: the deck leads with $7.6M, the UI demo script uses $7.57M / $1.17M. **This supersedes the 7/27 "fairness signal only" decision.** The only thing left is leftover language — see the cleanup item below.

**⚠️ Language cleanup still needed (as of 7/31):** the deck's Slide 8 spoken line, Appendix A5's label ("Underpriced host GBV"), and the scripted Q&A answer all still describe overpriced as *fully excluded*, which contradicts the combined figure they sit next to. The number is right; the words around it are stale. Fix all three to say what the math actually does: overpriced is included, as a small honest −$0.70M loss on established hosts, and the real overpriced story is +77,606 recovered nights rather than dollars.

**The combined headline (the number to lead with):**

```
Underpriced floor (segmented)     +$8.27M
Overpriced floor (measured)       −$0.70M
─────────────────────────────────────────
COMBINED HOST GBV                 +$7.57M / year
× 15.5% Airbnb take               +$1.17M / year  ← the headline
+ Nights unlocked                 +77,606 nights / year
```

Every input here is either measured (−0.916) or a mathematical certainty (−1.0 breakeven / β=0 for insignificant monthly) — nothing invented. This **replaces** the earlier $9.6M–$25.6M range as the number the deck leads with.

**Clarified 7/29 (Jai):** the segmentation math (142-review split, underpriced/overpriced bands, combined headline) was never a second modeling step — it's presentation-layer business arithmetic applied to the already-verified, already-committed elasticity coefficient (`elasticity_model.py` and its outputs are real and in the repo). No script is owed here the way one was for the regression itself. **What's still needed:** the calculation steps (segment counts, per-band figures) should be laid out transparently in Brendan's appendix so a grader can check the arithmetic by hand — normal practice for a business case, distinct from the modeling work. **Owner: Brendan**, as part of appendix assembly.

**Sensitivity table below is now stale — replaced by the segmented ROI table in Section 5:**

| Adoption | Host revenue lift | Airbnb's cut (15.5%) | Year-1 net (after build) | Payback |
|---|---|---|---|---|
| 15% | $3.8M | $603K | $308K | 5.9 months |
| 25% | $6.4M | $992K | $697K | 3.6 months |
| 35% | $9.0M | $1.39M | $1.09M | 2.5 months |
| 50% | $12.8M | $1.98M | $1.69M | 1.8 months |
| 75% | $19.2M | $2.98M | $2.68M | 1.2 months |
| 100% | $25.6M | $3.97M | $3.67M | 0.9 months |

**Open items:** team sign-off on the overpriced-reframing above; commit Jai's segmentation math to the repo as a script; fold the combined $7.57M/$1.17M headline into Script v2 (Wed 7/29) and Deck v2 (Thu 7/30).

---

## 4. Cost to Implement

**Methodology (researched, citable):**
- **Gartner TCO framework** for the cost-structure skeleton: direct costs (hardware/software, implementation, admin/operation, support) vs. indirect costs (downtime, inefficiency, productivity loss).
- **"Hidden Technical Debt in Machine Learning Systems"** (Sculley et al., Google, NeurIPS 2015) to justify a distinct recurring line for retraining/pipeline upkeep/monitoring.
- **NPV / IRR / Payback Period** (Corporate Finance Institute) as the financial-ask template.

**Infrastructure cost (researched, NYC-pilot scale, ~9,752 listings, weekly retrain) — not model-dependent, unchanged by the GBM switch:**

| Category | Annual (Low–Mid–High) | Basis |
|---|---|---|
| Compute (retrain + ETL) | $120 – $480 – $1,320 | AWS Fargate/EC2/SageMaker pricing |
| Database | $360 – $720 – $1,800 | AWS RDS PostgreSQL pricing |
| Dashboard/API hosting | $180 – $540 – $1,500 | AWS Fargate pricing (note: App Runner deprecated for new customers Apr 2026) |
| Monitoring/observability | $60 – $1,320 – $3,000 | CloudWatch/Grafana/Datadog pricing |
| LLM (host explanations, weekly refresh) | ~$786/yr | Claude Haiku 4.5, ~800 in/150 out tokens per listing |
| **Total run cost (infra + LLM)** | **~$1,500 – $8,400/yr** | |

**The real cost story is labor, not infra** — infra/LLM is a rounding error against multi-million-dollar revenue figures. Per Gartner TCO and the ML-technical-debt paper, real product cost is engineering time.

**Labor cost (researched, fully-loaded 2026 tech comp):**

| Role | Fully-loaded annual | Basis |
|---|---|---|
| Senior Data Scientist/MLE | ~$286,000 | Glassdoor 2026 avg × 1.3 loading multiplier |
| Backend/Data Engineer | ~$214,500 | Glassdoor 2026 avg × 1.3 |
| Product Manager | ~$246,000 | Glassdoor 2026 avg × 1.3 |
| Frontend/Product Engineer | ~$190,300 | Glassdoor 2026 avg × 1.3 |

**Illustrative build + maintenance (extrapolated, flagged as estimate, no single source covers this exact scope):**
- One-time build: ~0.6 FTE Sr. DS/MLE + 1.0 FTE Backend + 0.5 FTE Frontend + 0.25 FTE PM over 4 months ≈ **$180K-$200K**
- Annual maintenance (labor): ~0.2 FTE DS/MLE + ~0.15 FTE Backend ≈ **$95K-$105K/yr**
- **Total annual run cost (labor + infra): ~$96,500-$113,400/yr**

**Open items:** decide "cost if built new" vs. "marginal cost to Airbnb" framing (some infra likely already exists on Airbnb's platform) — worth a one-line acknowledgment either way.

**✅ DONE (7/29): Jai formalized the incremental-cost scenario flagged 7/24.** The $180-200K/$95-105K figures above are "cost if built standalone" — the real number for an internal Airbnb pitch is the *marginal* cost to add this feature on top of infrastructure Airbnb already owns (model-serving, A/B testing, pricing-feature engineering — Smart Pricing already exists).

**Incremental cost basis (the number the ROI is now built on):**
- **One-time build:** ~$65K in engineering time (midpoint of $50-80K, Jai's estimate, not externally sourced) + under $1K in AI dev-tooling costs (Claude Code/Cursor/API usage during the ~4-month build — itemized for honesty, rounds to noise either way).
- **Annual run:** ~$30K/yr — ~0.1 FTE DS for retraining/monitoring plus ~$3K/yr incremental infra (compute, database, hosting, monitoring — all marginal load on Airbnb's existing stack).
- **5-year total:** $65K + ($30K × 5) = **~$215K** (vs. $715K on the standalone/greenfield basis).

**Keep the standalone $190K/$715K figures as the explicit "worst-case if built from scratch" check** — they have real sourced comp benchmarks behind them and are worth naming once so the incremental number doesn't look cherry-picked, but the $65K/$30K incremental basis is what Sections 5-6's ROI/payback tables now run on.

---

## 5. ROI

**✅ DONE (7/29): Jai's recompute, on the segmented $1.17M/yr headline (Section 3) and the incremental $65K/$30K cost basis (Section 4), with NPV discounting actioned.**

Using NPV/IRR/Payback methodology, flat steady-state adoption (Section 6 has the more realistic ramped version).

**5-year ROI by adoption ($1.17M @ 100% adoption, incremental cost $65K build + $30K/yr run):**

| Adoption | Airbnb Rev/yr | 5-yr Rev (nom) | 5-yr Net (nom) | 5-yr Net (NPV @10%) | 5-yr ROI (nom) | Payback |
|---|---|---|---|---|---|---|
| 15% | $176K | $0.88M | $0.66M | $0.49M | 308% | ~6 mo |
| 25% | $292K | $1.46M | $1.25M | $0.93M | 580% | ~4 mo |
| 35% | $410K | $2.05M | $1.83M | $1.37M | 852% | ~3 mo |
| 50% | $585K | $2.92M | $2.71M | $2.04M | 1,260% | ~2 mo |
| 75% | $878K | $4.39M | $4.17M | $3.15M | 1,941% | ~1 mo |
| 100% | $1.17M | $5.85M | $5.63M | $4.26M | 2,621% | ~1 mo |

**Recommendation: lead with the 25% and 35% rows** as the conservative and expected cases. On the incremental cost basis, even 15% adoption pays back in ~6 months and clears 300% ROI. Don't headline the 100% row — it invites the obvious adoption-skepticism pushback.

**For context — the occupancy-neutral ceiling ($4.15M @ 100%) produces multiples of these figures.** Show it as upside context if asked, not the headline.

**Why the ROI story holds even though the revenue number dropped:** the incremental cost basis ($65K/$30K) is small enough that the ROI/payback story is nearly insensitive to which revenue figure is used — even the most conservative adoption row clears "fund it" by a wide margin. That's a structural strength of the pitch, worth saying explicitly if a professor pushes on the exact size of the revenue number.

**Open items:** none blocking — this table is a flat-adoption simplification; Section 6 has the year-by-year ramped version, which is the one to actually present.

---

## 6. Financial Timeline

**✅ DONE (7/29): Jai's recompute on the segmented $1.17M/yr headline and incremental cost basis, with NPV discounting.** Adoption-ramp framework and percentages are unchanged from the original version — only the dollar figures and cost basis are new.

Real, cited adoption-ramp framework — **Rogers' Diffusion of Innovation** (best fit: opt-in tool, individually-deciding hosts, word-of-mouth diffusion — not a mandated enterprise rollout). Bass diffusion model's classical parameters (Sultan/Farley/Lehmann 1990) are calibrated for 10-15+ year durable-goods adoption, too slow for a digital tool — recalibrated instead to real SaaS feature-adoption benchmarks (Product Metrics Benchmark Report 2024, 181 companies: avg 24.5%, median 16.5%, top quartile >45%).

**Adoption ramp used (unchanged):**

| Year | Cumulative adoption | Basis |
|---|---|---|
| 1 | ~10% | Rogers' innovator + early-adopter pool, scaled for a slow first-year ramp |
| 2 | ~24% | Anchored to real SaaS average adoption benchmark |
| 3 | ~38% | Extrapolated, crossing into early-majority |
| 4+ (steady state) | ~42% | Anchored just under real SaaS top-quartile benchmark — deliberately not near 100% |

**Why 10%?** (NPV discount rate) Standard corporate rate for a moderate-risk internal project, per Corporate Finance Institute — same source as the payback methodology. Not aggressive (would understate the case), not zero (would be dishonest given NPV is the named methodology).

**Year-by-year timeline — $1.17M/yr Airbnb fee at 100% adoption; incremental $65K build Year 1 + $30K/yr run, with NPV @10%:**

| Year | Adoption | Airbnb Revenue | Cost | Net (nom) | Cum (nom) | Net (NPV @10%) | Cum (NPV) |
|---|---|---|---|---|---|---|---|
| 1 | 10% | $117K | $95K | +$22K | +$22K | +$20K | +$20K |
| 2 | 24% | $281K | $30K | +$251K | +$273K | +$207K | +$227K |
| 3 | 38% | $445K | $30K | +$415K | +$687K | +$311K | +$539K |
| 4 | 42% | $491K | $30K | +$461K | +$1.15M | +$315K | +$854K |
| 5 | 42% | $491K | $30K | +$461K | +$1.61M | +$286K | +$1.14M |

**Payback: net-positive in Year 1, both nominal and NPV.** On the incremental cost basis, even 10% first-year adoption ($117K revenue) covers the $95K Year-1 cost — no multi-year hole to climb out of, unlike the old $190K-standalone-cost version.

**The NPV haircut is real but doesn't threaten the story:** 5-yr net revenue $5.63M nominal → $4.26M at 10% NPV (~24% haircut). Still net-positive Year 1, still returns many multiples of cost over five years.

**Caveat for the slide:** no verified case study of an Airbnb-specific or directly comparable host/seller-tool adoption curve exists — this is a recalibration of general SaaS/diffusion benchmarks, not a directly analogous real-world number.

**On the ceiling for comparison:** the same ramp on the $4.15M occupancy-neutral ceiling produces multiples of the cumulative NPV net above. Present the floor as the headline, the ceiling as upside if asked.

**Open items:** none blocking.

---

## 7. Slide Sequence (~25-minute presentation) — REBUILT following the 7/24 faculty guidance for the real time limit and rubric

**This replaces the earlier 9-slide/10-minute version**, which was built for Stan's board-pitch coaching context, not the actual grading requirements. Stan's underlying advice (business-first, one message per slide, minimal unnecessary technical depth) is still incorporated — there's just more room now, and more required content to cover.

**Retargeted to ~20 minutes planned (2026-07-26), not 25.** Rationale (Brendan's, from experience): a plan built to the actual limit reliably overruns it — "plan for 25, it runs 30; plan for 8, it runs 10." Planning to ~20 leaves real buffer against the 25± actual limit even with a typical overrun. This means real consolidation, not just trimming a slide or two — some rubric items now share a slide that had separate slides before. That's a deliberate density trade-off: fewer slides means each one has to carry more, which cuts against "one message per slide" a bit. Flagged below wherever that tension is sharpest.

| # | Slide | Content | Rubric item(s) covered | ~Time |
|---|---|---|---|---|
| 1 | Title / Team Intro | Team members + roles, Stan as industry coach, product name, hook | Introduction | 1 min |
| 2 | Executive Summary | Problem + solution in one line each, headline payback/ROI numbers — required | — | 1.5 min |
| 3 | Context & Problem | Industry/company background + business situation + key question/sub-questions/benefit, merged — **densest slide in this version, watch it doesn't become a wall of text** | Company/industry background; business situation/context; key question | 2.5 min |
| 4 | Dataset | Inside Airbnb NYC snapshot (June 2026), 9,752 listings, NYC-pilot scope | Dataset(s) used | 1 min |
| 5 | Key Variables & Data Structure | EDA — what went into the model, cleaning/feature engineering | Key variables/relationships (1 of 2, minimum required) | 1.5 min |
| 6 | Key Relationship: The Pricing/Occupancy Gap | EDA — ⚠️ **corrected 7/28, see note below** — occupancy by host tier, mispricing distribution | Key variables/relationships (2 of 2, minimum required) | 1.5 min |
| 7 | Solution Statement | The product vs. Smart Pricing; Commander's Intent delivered verbally here | (supports business benefit / "how") | 1.5 min |
| 8 | Model, Approach & Insights | GBM quantile regression + KNN comparables, tools, segment split, accuracy, and what the model found — merged | Model/approach + tools; insights and learnings | 2.5 min |
| 9 | Recorded Demo | **Pre-recorded, narrated** video walkthrough of the dashboard (per faculty guidance — no live demo) | (supports "how" + insights) | 2 min |
| 10 | Financial Case: Revenue Lift & Cost | ⚠️ **Dense subject, kept deliberately shallow (7/29) — see note below.** Two-pillar table only (underpriced = margin, overpriced = volume) with headline $ totals, the combined $7.57M→$1.17M number, and the incremental cost line ($65K build/$30K yr) | Predictions/recommendations (partial) | 2 min |
| 11 | Financial Case: ROI & Timeline | 25%/35% adoption rows only, NPV-adjusted payback, adoption-ramp chart | Predictions/recommendations (partial) | 1.5 min |
| 12 | Challenges & Caveats | Risks/assumptions, model-noise discount reasoning, known data gaps | Challenges/caveats/data mitigation | 1 min |
| 13 | Recommendations, Next Steps & Close | The "so what," what the team would explore further, brief career/company relevance, memorable close — merged | Predictions/recommendations; next steps; relevance to career/company | 1.5 min |

**Planned total: ~21.5 minutes** — leaves roughly 3.5-8.5 minutes of buffer under the 25± actual limit, closer to the real target once delivery inevitably runs long.

**Deliberately left out of this outline:** who presents which slide. That's for the team to work out on their own — no suggestions here.

**⚠️ Slide 6 occupancy stat corrected 7/28.** The 71.5% (Small-Multi) vs. 47.3% (Individual) figure doesn't reproduce from the current dataset under any occupancy metric checked — likely a transcription error from the original EDA writeup (full reasoning in `README.md`). Verified current numbers show the *opposite* trend: **Individual 44.1%, Small-Multi 37.8%, Mid-Multi 32.6%, Enterprise 30.0%** — occupancy declines as host scale increases. This also means Slide 6's planned narrative needs to change: the story isn't "bigger operators occupy better," it's the reverse, and it arguably strengthens the pitch (individual hosts already have strong demand, so the product's job is purely about pricing that demand correctly, not fixing an occupancy problem that isn't real). Also worth checking Slide 6's other claim ("more established hosts have higher occupancy") — this holds for review count (real, monotonic: 33.6%→41.8% by quartile) but does *not* hold for host tenure/years-of-experience (flat ~37-39% across all quartiles) — don't conflate the two when rewriting.

**⚠️ Slides 10-11 density strategy, decided 7/29.** Jai's revenue/cost/ROI work (Sections 3, 5, 6) is real and thorough, but far too dense for 3.5 minutes of slide time — putting the 142-review segmentation, the underpriced/overpriced band tables, the "revenue flip" mechanics, or the eleven-point "floor of the floor" defensive list on the actual slides would bury the message. **Slide content stays to headline numbers only** (the two-pillar table, the combined $7.57M→$1.17M figure, the incremental cost line, 25%/35% adoption rows, NPV-adjusted payback). **All the underlying mechanics — segmentation reasoning, floor/ceiling tables, NPV mechanics, year-by-year cash flow — go in the Q&A appendix**, not the timed slides. Manas should deliver Jai's closing one-liner verbally on Slide 10/11 ("$7.57M in new host earnings... that's the floor") rather than putting it as slide text — same spoken-delivery pattern as the Commander's Intent line on Slide 7.

**Not yet done — real open items for Slide 7:**
- Team to assign owners for each slide
- Build the actual slide content for each row — this document only outlines what goes where, none of it is drafted yet. Slide 3 and Slide 8 especially need real editorial discipline given how much each is carrying. **Owner: Manas (lead), with Francois and Rachael on slide construction and visualizations.**
- Record and edit the demo video
- Prepare the separate **Q&A appendix** (not part of the 13 timed slides) — pull from Sections 3-6's full backup tables/methodology detail. **Owner: Brendan** (assembling appendices and the long-form work behind the model and presentation generally). See Section 10 for current structure/status.
- ✅ **UI/slide branding & design pass — Francois assumed ownership 7/27/28,** shared a draft (branding/style only, not populated content) for team review — team agreed it's good. Tech pass + branding both need to land before the UI-approval gate (Section 11, Wed 7/29).

---

## 8. Presentation Script

**Owner: Manas (lead), with Francois and Rachael supporting.** Team principle, decided 7/24-25: the message the team delivers matters more than the slides themselves — slides exist to support the message, not the other way around. Sections 1-6 of this document (problem/solution framing, the real numbers) are the substantive backbone the script should draw from; Section 7's slide outline exists to make sure the course's required content and the faculty's advice are actually covered, not to dictate the narrative. One confirmed script beat: the Commander's Intent framing (Section 2) is meant for spoken delivery only during Slide 7 (Solution Statement), not slide text.

**✅ Script v1 exists and was reviewed (Mon 7/27 meeting).** Structure maps cleanly onto the 13-slide sequence above and fits comfortably inside the real ~25min budget. Fixes identified for v2, notes sent to Manas:
- Slide 1 needs team members + Stan named explicitly — rubric requires this, current draft just says "We're Team 3."
- Exec Summary (Slide 2) needs to at least reference the headline payback/ROI numbers verbally — currently doesn't mention them at all, and that's a required rubric item.
- Commander's Intent is currently misattributed to "our industry coach" in the script — it's Brendan's framing (Section 2 above), needs correcting.
- The elasticity mechanism (Section 3) is currently hand-waved as "additional occupancy data" — given the real ~25min budget, there's room to actually name the method and finding instead of staying vague.
- No line yet addresses what the overpriced half of listings is worth (see Section 3's resolution above — fairness signal, not revenue lever).
- Minor: "nearly 9,800 active listings" → precise figure is 9,752.
- Slide 6 needs the occupancy-stat correction above folded in.

**Not yet pushed to the repo** — exists only as a local PDF as of 7/28.

---

## 9. Submission Logistics — don't lose track of this

Per the faculty email, two separate submission steps:
1. **Slide deck** (PPT or PDF of the final presentation slides) → Canvas
2. **A link to this GitHub repo**, with model outputs/interim work/appendices → sent directly to the faculty member and CA, by email or as a Canvas comment. **Already shared with our primary faculty advisor (Jamie).** Unconfirmed whether the CA has it too — someone should double-check/send separately if not. **Also now Jai's responsibility to clean up and organize the repo itself** (see Section 10) — right now it's a working directory, not something built for a grader to navigate cleanly.

**Live team tracker:** [GitHub Projects board](https://github.com/users/mkdn007/projects/1) — status of every task below is also tracked there as cards; this document is the narrative/ground-truth source, the board is the day-to-day checklist. Keep both in sync.

---

## 10. Team Assignments (decided 2026-07-24/25)

| Owner | Scope | Status (7/28) |
|---|---|---|
| **Manas** (lead) | Script writing — the message the team delivers, not just the slides. Supported by Francois and Rachael on the script itself and on slide construction/visualizations. | Script v1 done + reviewed, fixes identified for v2 (Section 8) |
| **Francois & Rachael** | Support Manas on script + slide construction, including visualizations. | Deck v1 reviewed 7/28; Deck v2 on track for Thu |
| **Jai** | Tightening the financials (includes the NPV/discounting and marginal-cost points flagged in Sections 4-5) plus additional model robustness checks — not expected to materially change headline numbers, but may shift them slightly. **Also: clean up and organize the GitHub repo** so graders don't get lost in it — right now it reads as a working directory, and it needs to present as professional and well-organized given it's already been shared with our faculty advisor. | **In progress.** Elasticity pilot (the big one) is done and verified (Section 3) but not yet pushed to the repo. NPV-discounting + marginal-cost items still open. Repo cleanup not started — **see risk flag in Reminders below re: the `origin/jai` branch before starting this.** |
| **Brendan** | Assembling the appendices and the long-form work behind the model and presentation. | **In progress.** Structure agreed: extends the existing dev-journey doc with new EDA, elasticity, business-recommendations, and anticipated-questions (red-team) sections — the last one as a separate quick-reference file. |
| **Francois** (Jai helping) | UI/slide branding & design pass — generically Airbnb-styled look, kept consistent between the slide deck and the dashboard UI. Assigned at Saturday's kickoff (7/25). | ✅ Ownership assumed 7/27/28; draft shared and approved by the team. Tech pass still needed before the Wed UI-approval gate. |

**Guiding principle:** the message matters more than the slides. Slides support the message; the framework in Sections 0-7 exists to make sure the course's required content and the faculty's advice are actually covered, not to dictate the narrative.

**Saturday team meeting agenda:**
1. Kick off the work assigned above and leave room for questions/clarifications — not a checkpoint where finished work is expected yet.
2. **Finalize the Thursday 11:30am meeting with Jamie** (our faculty advisor).
3. ✅ **UI/slide branding owner assigned** — Francois, with Jai helping (see Section 10).
4. ✅ **Q&A-timing question resolved** — see Section 0.
5. **Everyone joins the GitHub repo as a collaborator** — ⏳ **partial as of 7/28:** Jai (owner), Brendan, and Francois confirmed. **Manas and Rachael still not on it** — Jai needs to send invites; each person needs to accept before relying on repo access for their assigned work.

---

## 11. Meeting Schedule & Deliverables (decided 2026-07-25)

Daily team meetings Monday-Friday, work starting Saturday. Structure: script and deck reviewed in alternating v1/v2 stages, converging on a v3 FINAL Friday. Each meeting is for discussion and getting agreement where needed, not a first look at the work.

| Day | Meeting | Due | Notes |
|---|---|---|---|
| **Sat 7/25** | ✅ Kickoff | — | See Section 10's agenda above. UI branding owner assigned: Francois (Jai helping). |
| **Sun 7/26** | ✅ *(work day, no meeting)* | — | Jai's elasticity pilot landed (Section 3) — the major deliverable from this work day. |
| **Mon 7/27** | ✅ **Script v1 Review** | Script v1 | Done — see Section 8 for the reviewed status and fixes identified for v2. Q&A-timing question resolved 7/26 (see Section 0). |
| **Tue 7/28** | ✅ **Deck v1 Review** | Deck v1 (13 slides, populated) | Done. UI branding: Francois's draft shared and approved (style only, not full content yet); tech pass still needed before Wed's gate. **Financial tables in Sections 3/5/6 still need Jai's elasticity recompute before Script/Deck v2.** |
| **Wed 7/29** | ❌ **CANCELLED** | — | Meeting didn't happen. The overpriced-framing decision it was meant to settle got resolved by the artifacts instead (see Section 3) — all deliverables landed on the combined $7.57M. No meeting with Stan either; he's on vacation, team updates him by email. |
| **Thu 7/30** | ✅ **Demo recorded** | Demo raw footage | **Demo recorded 7/30. Jai editing as of 7/31 evening** — the biggest schedule risk is now closed, pending the edit. Francois's UI redo (v3 + real listing photos/logo) and the updated birds-eye also dated 7/30. |
| **Fri 7/31** | **v3 FINAL — today** | Script v3, Deck v3, demo embedded, appendix, repo clean | See "still outstanding" list below for what's actually left as of 7pm Friday. Residency is Monday, so anything unfinished tonight travels with the team. |

**Residency week (Aug 3-9, NYC) — 3 scheduled work sessions.** Goal: all three dedicated to rehearsal, not more building, if it can be avoided. That's only realistic if Friday's v3 is actually final, not "final unless something breaks" — worth stating explicitly when the team reviews Friday's deliverable, since it changes what "done" needs to mean by then.

---

## Reminders for whoever picks this up

- **Sign-off rule:** none of the parent to-do items get marked done just because a draft exists here — needs the whole team's sign-off first.
- **Scope:** NYC-only pilot, not platform-wide, per the README's positioning.
- **Framing:** presenting from a hypothetical "we are Airbnb's internal product team" position, which is why real occupancy-response/elasticity data is assumed even though the actual dataset doesn't contain it. **Update 7/27: this is no longer entirely hypothetical for short-stay** — Jai's elasticity pilot measured a real (if narrow-sample) price-response coefficient. Frame it as proof-of-mechanism using proxy data, not as validation of the full model at Airbnb scale.
- **Model version:** GBM quantile regression + KNN (v3) is current, now living in **`model v4/`** on `main` — Jai merged `final-model-package` and renamed it to match the v1/v2/v3 folder convention (7/28-29). No longer an unmerged-branch problem. Root `README.md` and `model v4/README.md` both mark V4 current with a version-progression table.
- **✅ CORRECTED 7/31 — the `origin/jai` "risk" was a misread, there is no danger.** Verified with `git merge-base --is-ancestor`: `origin/jai` is **fully contained in `main`** (last commit 7/17; `main` is 25 commits ahead). Merging it would be a no-op that brings in nothing. The alarming "283K lines of deletions" figure came from running `git diff main origin/jai`, which shows what you'd lose stepping *backward* to a July 17 snapshot — not what a merge does. Earlier notes in this document called it dangerous; that was wrong. It's simply stale, and safe to delete whenever.
- **✅ RESOLVED 7/31 — `model v3/` restored to `main`.** `origin/v3-confidence-fix-and-seasonality` had been the only branch with unmerged work, holding the entire `model v3/` directory. The root README's version table linked to `model v3/`, which didn't exist on `main`, so that link went nowhere and the v1→v2→v3→v4 narrative had a gap. Merged 7/31 after verifying the change was purely additive (17 files, all new, all under `model v3/`, zero path collisions). Confirmed post-merge that the `model v4` tree hash was byte-identical before and after, so nothing the presentation depends on moved. `model v3/README_Model_V3.md` now carries a status header explaining what V3 contributed, what carried forward into V4, and that `proposed-confidence-fix/` was never adopted. **All branches are now fully contained in `main`.**
- **⚠️ EDA correction (7/28):** the README's/Data Cleaning Process's host-tier occupancy-gap stat (71.5%/47.3%) doesn't reproduce and is likely a transcription error — see the correction notes in both files and in Section 7 (Slide 6) above. Verified numbers show occupancy *declining* with host scale, the opposite of the original claim. This hasn't propagated into the script or deck yet — keep it that way by using the corrected numbers if it comes up.
- **Repo access:** Jai, Brendan, Francois confirmed as collaborators (verified via API 7/29). **Manas and Rachael are genuinely not on the repo** — not a visibility issue, confirmed via the repo's public API. Jai needs to send real invites.
- **Ownership:** see Section 10 above for current status as of 7/28.

### What's genuinely still outstanding (7/31, 7pm — v3 FINAL day, NYC Monday)

- **⚠️ REPO IS TWO DAYS STALE — biggest gap.** `main` hasn't moved since 7/29 (`bcba89f`). The repo is a graded, faculty-facing deliverable and it currently ships: UI **v2** (7/28) instead of Francois's **v3** (7/30), a birds-eye missing its three new current-model screens, **no `assets/` folder at all** (so the pages break on images), and none of the demo package docs (`UI_Script.md`, `BIRDSEYE_SCREENS.md`, demo `README.md`). All of it exists in Jai's 7/31 zip, just unpushed. **Owner: Brendan, tonight.**
- **⚠️ Contradictory financial doc in circulation.** Jai's 7/31 zip includes `revenue_lift_roi.md` (his master doc, timestamped 7/29 14:03) alongside the two later "journey" docs (16:01, 16:41). The older doc uses the **greenfield** cost basis ($190K build + $105K/yr), which puts Year 1 at **−$178K** and payback at **mid-Year-2** — against the deck/UI-script's **incremental** basis ($65K/$30K), Year-1 positive, **~3-month** payback at 35% adoption. Revenue figures agree across all docs; only cost differs, and it swings payback from 3 months to 8. Don't commit that doc unmarked. Its Sections 5/5b reasoning is the best in the stack and belongs in the appendix; only its Section 6 is stale.
- **Deck language cleanup:** Slide 8, Appendix A5 label, and the scripted Q&A answer still say overpriced is excluded, contradicting the combined number they sit beside (Section 3). **Owner: Francois.**
- **Cost-basis defensibility, worth having an answer ready:** the deck leads with the incremental $65K/$30K, which is Jai's own estimate and *not* externally sourced, while the $190K greenfield figure *does* have Glassdoor benchmarks behind it. Leading with the unsourced number produces the better ROI. That's the likeliest place a sharp grader pushes. The honest answer: Airbnb demonstrably already owns model-serving, pricing, and A/B infrastructure (Smart Pricing ships today), so greenfield overstates the real marginal cost — and the greenfield number is shown alongside precisely so the comparison is visible rather than hidden.
- **Demo:** recorded 7/30, Jai editing as of 7/31 evening. Needs to land and get embedded.
- **Brendan: appendix** — was due EOD 7/30. Pull Jai's Option A/B framing, the four-scenario overpriced band, and the "99.3% of underpriced short-stay listings sit below the 142-review panel profile" argument (the strongest defensive point in the project, and the reason the old $9.6M was never a real floor).
- **Repo access:** Manas and Rachael still unverified as collaborators. **Owner: Jai.**
