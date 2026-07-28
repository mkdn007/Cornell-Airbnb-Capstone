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

**Revised revenue-lift range for short-stay, replacing the single $25.6M figure:**

| Assumption | Short-stay lift | Monthly lift (unaffected) | Total |
|---|---|---|---|
| Occupancy-neutral (upper bound — no occupancy response assumed) | $17.3M | $8.3M | **$25.6M** |
| β=−0.916 applied (lower bound — measured response) | $1.3M | $8.3M | **$9.6M** |

**Why the short-stay number drops so sharply:** the median underpriced short-stay listing sits ~17-20% below fair value. At β≈−0.92, raising price by that much predicts an occupancy drop of similar magnitude — the price gain and the occupancy loss nearly cancel out. Short-stay demand is close to unit-elastic, so hosts can't simply raise to fair value and expect a windfall. **The honest range is $9.6M–$25.6M, not a single number** — this is exactly the sensitivity-table framing this section already argued for, now with a real measured floor instead of an assumed ceiling.

**Overpriced listings — a related finding, resolved 7/27:** since revenue's elasticity w.r.t. price is `1+β` (≈0.084, barely positive under this model), lowering price for overpriced listings is revenue-*negative* for the host, not revenue-positive — meaning no rational host would act on a "lower your price" recommendation for revenue reasons, and it shouldn't be counted as monetizable opportunity or netted against the short-stay gain above. **Decision: frame the overpriced half of the dataset as a fairness/benchmarking signal in the deck ("here's how you compare to peers"), not a second revenue lever.** Worth a one-line acknowledgment on Slide 10 so it doesn't look like an oversight if asked.

**Still in progress (Jai):** NPV-discounting Sections 5-6's tables and the marginal-cost-to-Airbnb scenario (both flagged below, not yet actioned) — plus reconciling Sections 5-6's tables against this new $9.6M–$25.6M range instead of the flat $25.6M ceiling they're currently built on. **Open item, not yet decided: does Section 5/6 lead with the conservative $9.6M floor, the $25.6M ceiling, or present both as a range?** This is now the single biggest open call in the financial story.

**Not yet done:** the elasticity model itself (`elasticity_model.py`, `README_elasticity_model.md`, outputs, raw AirROI data) exists only locally as of 7/27 — needs pushing to the repo so the faculty-facing link actually shows this work.

**Sensitivity table below still reflects the $25.6M occupancy-neutral ceiling (pre-elasticity) — superseded, kept for reference until Jai's recompute lands:**

| Adoption | Host revenue lift | Airbnb's cut (15.5%) | Year-1 net (after build) | Payback |
|---|---|---|---|---|
| 15% | $3.8M | $603K | $308K | 5.9 months |
| 25% | $6.4M | $992K | $697K | 3.6 months |
| 35% | $9.0M | $1.39M | $1.09M | 2.5 months |
| 50% | $12.8M | $1.98M | $1.69M | 1.8 months |
| 75% | $19.2M | $2.98M | $2.68M | 1.2 months |
| 100% | $25.6M | $3.97M | $3.67M | 0.9 months |

**Flag for the team:** this table is now superseded by the elasticity-adjusted range above — even the most conservative case (15% adoption) paying back in under 6 months was true on the $25.6M ceiling, but the honest floor is $9.6M, which roughly doubles every payback figure in this table. Don't present these payback numbers as-is until Jai's recompute lands.

**Open items:** recompute this table on the $9.6M–$25.6M range (Jai); reconcile with whatever final adoption assumption the team wants to lead with on the Financial Case slides (Section 7, Slides 10-11).

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

**Flagged by Jai (7/24), not yet actioned — Jai to own:** the $190K/$105K figures above are "cost if built standalone." Airbnb almost certainly already has model-serving infra, A/B testing pipelines, and pricing-feature engineering in place, so the real *incremental* cost of adding this feature is likely closer to **$50-80K in engineering time** (Jai's estimate, not externally sourced). Using the standalone figure overstates cost and therefore understates ROI. If this gets incorporated, it should run as a second scenario alongside the $190K greenfield build, not a replacement, since the greenfield number has real sourced benchmarks behind it — and Sections 5 and 6's ROI/payback tables would need a second column to match.

---

## 5. ROI

**⚠️ Superseded by the elasticity finding in Section 3 (7/27) — the table below is built on the flat $25.6M occupancy-neutral ceiling, not the real $9.6M–$25.6M range.** Don't present as-is; needs Jai's recompute (also still owes the NPV-discounting fix flagged below).

Using NPV/IRR/Payback methodology, flat steady-state adoption (Section 6 has the more realistic ramped version).

**5-year net revenue and ROI, by adoption (build $190K + $105K/yr run = $715K total 5-yr cost), GBM base:**

| Adoption | 5-yr Airbnb revenue | 5-yr net revenue | 5-yr ROI | Payback |
|---|---|---|---|---|
| 15% | $2.98M | $2.26M | 316% | 5.9 months |
| 25% | $4.96M | $4.24M | 594% | 3.6 months |
| 35% | $6.94M | $6.23M | 871% | 2.5 months |
| 50% | $9.92M | $9.20M | 1,287% | 1.8 months |
| 75% | $14.88M | $14.16M | 1,981% | 1.2 months |
| 100% | $19.84M | $19.12M | 2,675% | 0.9 months |

**Recommendation:** lead with the 25% and 50% rows as "conservative" and "expected" cases; don't headline the 100% row, it invites the obvious adoption-skepticism pushback.

**Open items:** none blocking — this table is a flat-adoption simplification; Section 6 has the year-by-year ramped version, which is the one to actually present.

**Flagged by Jai (7/24), not yet actioned — Jai to own:** the "5-yr net revenue" figures above are nominal sums, a dollar in Year 5 is treated the same as a dollar today. That's inconsistent with naming NPV as the methodology at the top of this section without actually discounting anything. Jai's read: a proper NPV at a modest 10% discount rate would reduce these numbers somewhat, not enough to hurt the story, but worth doing for a technically rigorous audience (and for internal consistency with Section 4's cited methodology). Applies to Section 6's year-by-year cash flows too, same issue there.

---

## 6. Financial Timeline

**⚠️ Superseded by the elasticity finding in Section 3 (7/27) — the $3.97M/yr ceiling below is derived from the $25.6M occupancy-neutral figure. The adoption-ramp percentages themselves are unaffected (not model-dependent), but the dollar figures need Jai's recompute against the $9.6M–$25.6M range.**

Real, cited adoption-ramp framework — **Rogers' Diffusion of Innovation** (best fit: opt-in tool, individually-deciding hosts, word-of-mouth diffusion — not a mandated enterprise rollout). Bass diffusion model's classical parameters (Sultan/Farley/Lehmann 1990) are calibrated for 10-15+ year durable-goods adoption, too slow for a digital tool — recalibrated instead to real SaaS feature-adoption benchmarks (Product Metrics Benchmark Report 2024, 181 companies: avg 24.5%, median 16.5%, top quartile >45%).

**Adoption ramp used:**

| Year | Cumulative adoption | Basis |
|---|---|---|
| 1 | ~10% | Rogers' innovator + early-adopter pool, scaled for a slow first-year ramp |
| 2 | ~24% | Anchored to real SaaS average adoption benchmark |
| 3 | ~38% | Extrapolated, crossing into early-majority |
| 4+ (steady state) | ~42% | Anchored just under real SaaS top-quartile benchmark — deliberately not near 100% |

**Year-by-year timeline (on the $3.97M/yr Airbnb-revenue ceiling at 100% adoption, GBM base; build $190K Year 1 + $105K/yr run cost every year):**

| Year | Adoption | Airbnb revenue | Cost | Net cash flow | Cumulative |
|---|---|---|---|---|---|
| 1 | 10% | $397K | $295K | $102K | $0.10M |
| 2 | 24% | $952K | $105K | $847K | $0.95M |
| 3 | 38% | $1.51M | $105K | $1.40M | $2.35M |
| 4 | 42% | $1.67M | $105K | $1.56M | $3.91M |
| 5 | 42% | $1.67M | $105K | $1.56M | $5.47M |

**Payback: ~8.9 months into Year 1** (assumes roughly linear revenue accrual through the year) — this is the number to lead with over the flat-adoption sensitivity table, since it doesn't assume instant adoption.

**Caveat for the slide:** no verified case study of an Airbnb-specific or directly comparable host/seller-tool adoption curve exists — this is a recalibration of general SaaS/diffusion benchmarks, not a directly analogous real-world number.

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
| 10 | Financial Case: Revenue Lift & Cost | Methodology (real data, trim, noise discount), cost (TCO framework) | Predictions/recommendations (partial) | 2 min |
| 11 | Financial Case: ROI & Timeline | Payback, 5-year ROI, adoption ramp | Predictions/recommendations (partial) | 1.5 min |
| 12 | Challenges & Caveats | Risks/assumptions, model-noise discount reasoning, known data gaps | Challenges/caveats/data mitigation | 1 min |
| 13 | Recommendations, Next Steps & Close | The "so what," what the team would explore further, brief career/company relevance, memorable close — merged | Predictions/recommendations; next steps; relevance to career/company | 1.5 min |

**Planned total: ~21.5 minutes** — leaves roughly 3.5-8.5 minutes of buffer under the 25± actual limit, closer to the real target once delivery inevitably runs long.

**Deliberately left out of this outline:** who presents which slide. That's for the team to work out on their own — no suggestions here.

**⚠️ Slide 6 occupancy stat corrected 7/28.** The 71.5% (Small-Multi) vs. 47.3% (Individual) figure doesn't reproduce from the current dataset under any occupancy metric checked — likely a transcription error from the original EDA writeup (full reasoning in `README.md`). Verified current numbers show the *opposite* trend: **Individual 44.1%, Small-Multi 37.8%, Mid-Multi 32.6%, Enterprise 30.0%** — occupancy declines as host scale increases. This also means Slide 6's planned narrative needs to change: the story isn't "bigger operators occupy better," it's the reverse, and it arguably strengthens the pitch (individual hosts already have strong demand, so the product's job is purely about pricing that demand correctly, not fixing an occupancy problem that isn't real). Also worth checking Slide 6's other claim ("more established hosts have higher occupancy") — this holds for review count (real, monotonic: 33.6%→41.8% by quartile) but does *not* hold for host tenure/years-of-experience (flat ~37-39% across all quartiles) — don't conflate the two when rewriting.

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
| **Wed 7/29** | **Script v2 Review** | Script v2 (folds in Jai's finalized numbers + Meeting 1/2 feedback) | **Gate: UI approved final** (tech + branding both done) unlocks demo recording. **Demo recording scheduled for Wed**, right after approval — on track. |
| **Thu 7/30** | **Deck v2 Review** | Deck v2 (demo embedded, finalized financials, near-final repo cleanup) | **Due EOD Thursday, firm: Brendan's appendices, fully complete** — not just close, so the team has them in hand to review before Friday, not discovering gaps at v3 FINAL. Thursday 11:30am meeting with Jamie happens same day — prep open questions beforehand. |
| **Fri 7/31** | **v3 FINAL** | Script v3 (FINAL), Deck v3 (FINAL), demo embedded, appendix (final since Thursday), repo cleaned and organized | Matches the team's existing ~Aug 1 target. This needs to be genuinely final — see residency note below. |

**Residency week (Aug 3-9, NYC) — 3 scheduled work sessions.** Goal: all three dedicated to rehearsal, not more building, if it can be avoided. That's only realistic if Friday's v3 is actually final, not "final unless something breaks" — worth stating explicitly when the team reviews Friday's deliverable, since it changes what "done" needs to mean by then.

---

## Reminders for whoever picks this up

- **Sign-off rule:** none of the parent to-do items get marked done just because a draft exists here — needs the whole team's sign-off first.
- **Scope:** NYC-only pilot, not platform-wide, per the README's positioning.
- **Framing:** presenting from a hypothetical "we are Airbnb's internal product team" position, which is why real occupancy-response/elasticity data is assumed even though the actual dataset doesn't contain it. **Update 7/27: this is no longer entirely hypothetical for short-stay** — Jai's elasticity pilot measured a real (if narrow-sample) price-response coefficient. Frame it as proof-of-mechanism using proxy data, not as validation of the full model at Airbnb scale.
- **Model version:** GBM quantile regression + KNN (v3) is current — supersedes the earlier Ridge model referenced in some older repo docs. The GBM code, updated pricing-signal outputs, and demo UI prototypes currently live on the `final-model-package` branch, **still not merged into `main` as of 7/28.**
- **⚠️ RISK — do not merge `origin/jai` carelessly:** that branch diffs ~120K lines of deletions against `main` (would wipe `scraper-poc/`, the seasonality PoC, and both planning docs). Looks like a stale personal fork that never rebased. Flag to Jai directly before repo cleanup starts.
- **⚠️ EDA correction (7/28):** the README's/Data Cleaning Process's host-tier occupancy-gap stat (71.5%/47.3%) doesn't reproduce and is likely a transcription error — see the correction notes in both files and in Section 7 (Slide 6) above. Verified numbers show occupancy *declining* with host scale, the opposite of the original claim. This hasn't propagated into the script or deck yet — keep it that way by using the corrected numbers if it comes up.
- **Ownership:** see Section 10 above for current status as of 7/28.

### What's genuinely still outstanding (7/28 snapshot)
- Jai: push elasticity work to repo; NPV-discounting + marginal-cost scenarios; recompute Sections 3/5/6's tables on the $9.6M–$25.6M range; repo cleanup (mind the `origin/jai` risk above); merge or otherwise resolve `final-model-package`.
- Team: decide whether Sections 5/6 lead with the conservative floor, the ceiling, or the full range.
- Manas/Francois/Rachael: Script v2 + Deck v2, folding in the elasticity numbers once Jai's recompute lands, plus the Script v1 fixes in Section 8.
- Francois: UI tech pass, ahead of Wednesday's approval gate.
- Brendan: appendix assembly (structure agreed, in progress) and the separate anticipated-questions quick-reference doc.
- Everyone: Manas and Rachael still need repo access from Jai.
