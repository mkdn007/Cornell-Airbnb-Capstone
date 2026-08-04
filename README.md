# Cornell–Airbnb Capstone

This project builds a **hybrid analytics engine for NYC Airbnb hosts** that combines a hedonic pricing regression with KNN competitive-cohort benchmarking — pinpointing exact nightly revenue losses and prescribing the specific operational and amenity upgrades needed to close them.

The dataset was obtained from **Inside Airbnb**, an independent, non-commercial open-source project that aggregates publicly available data from the Airbnb platform. The snapshot is New York City, captured **June 14, 2026** — 30,259 raw listings filtered to **9,752 active listings**.

---

## The business use case

**Problem.** Hosts have no objective way to know whether they are over- or under-priced, or what to change about the listing itself. Verified occupancy by host tier (mean `occupancy_rate_calendar`) runs **Individual 44.1%, Small-Multi 37.8%, Mid-Multi 32.6%, Enterprise 30.0%** — occupancy *declines* as host scale increases. Individual hosts already hold the strongest demand in the market, which makes pricing that demand correctly the actual problem to solve, rather than an occupancy deficit that isn't there.

> **Erratum (2026-07-28).** An earlier version of this README claimed a reversed occupancy gap (Small-Multi 71.5% vs Individual 47.3%). The 71.5% figure does not reproduce from `active_listings_clean_v6.csv` under any occupancy metric checked (mean, median, calendar-based, or raw days-booked), and no source notebook survives to check it against — most likely a transcription error from the original EDA writeup. The Individual (47.3%) and Enterprise (37.2%, see `Data Cleaning Process.md`) figures do reproduce closely, so the error looks isolated to the one number. The corrected figures and direction are what appear above and in all current slide/script content.

**Our solution — a Revenue Optimizer (Option C).** A two-layer, host-facing diagnostic:

1. **Fair-value pricing engine** — a hedonic regression estimates what each listing *should* charge given its location, size, amenities, and ratings. The gap between actual and fair price is the **mispricing signal** ("you're priced $X above/below comparable value").
2. **Comparable-cohort benchmarking (the "why")** — KNN matches each listing to genuinely similar peers, isolates the high-occupancy performers among them, and surfaces the concrete amenity/operational gaps to close.

**The deliverable a host receives:**
> *"Your listing is underpriced by $X/night relative to its fair value. To capture that missing yield without hurting occupancy, close your feature gap: your high-performing peers offer a dedicated workspace and self-check-in — you don't."*

Positioned commercially as either a **direct-to-consumer SaaS** tool for independent hosts or a **B2B value-add dashboard** a platform could offer to improve inventory quality and marketplace volume.

---

## Model version progression

| Version | Approach | Status |
|---|---|---|
| **Model v1** (`model v1/`) | Log-linear OLS baseline | Superseded |
| **Model v2** (`model v2/`) | Ridge regression + KNN benchmarking, segment-split (6-model bake-off selected Ridge for coefficient stability) | Superseded |
| **Model v3** (`model v3/`) | Same Ridge engine as v2, adds confidence scoring + host-tier-aware KNN | Superseded — its KNN layer and segment diagnostics carried forward into v4 |
| **Model v4** (`model v4/`) | **GBM quantile regression (q10/q50/q90) with conformal calibration**, same host-tier-aware KNN layer carried forward, plus seasonality, two live UI tools, a real-price scraper proof of concept, and a price-elasticity pilot | **✅ CURRENT — this is what the deliverable runs on** |

Each version's own README explains why the change was made, not just what changed. Full narrative in [`NYC_Airbnb_Appendix_Technical.docx`](NYC_Airbnb_Appendix_Technical.docx); anticipated Q&A challenges with prepared answers in [`NYC_Airbnb_Anticipated_Questions.docx`](NYC_Airbnb_Anticipated_Questions.docx).

---

## Repository status — what's production, what isn't

**`main` is the production branch.** It holds everything the final presentation runs on. Nothing else needs to be checked out to review, run, or grade this project.

### Branches

| Branch | Status |
|---|---|
| **`main`** | ✅ **PRODUCTION.** The current, complete state of the project. |
| `final-model-package` | **Merged, retained for history.** Fully contained in `main` (merged 2026-07-28 as `model v4/`). Nothing unique remains on it. |
| `pending-planning-doc-qa-resolved` | **Merged, retained for history.** Fully contained in `main`. |
| `jai` | **Stale, superseded.** Last commit 2026-07-17; fully contained in `main`, which is 25 commits ahead. Nothing unique remains on it. Diffing it against `main` shows large apparent deletions — that is simply how far the project has moved since July 17, not work that would be lost. |
| `v3-confidence-fix-and-seasonality` | **Merged 2026-07-31, retained for history.** Carried the `model v3/` directory; now fully contained in `main`. |

**Every branch is now fully contained in `main`.** Nothing unique remains on any of them, so `main` alone is the complete project.

### Production artifacts inside `model v4/`

| Path | Status |
|---|---|
| `model v4/model/` | ✅ Production — GBM quantile-regression engine + KNN layer |
| `model v4/elasticity/` | ✅ Production — price-elasticity pilot (TWFE) and the business-case documents built on it |
| `model v4/ui/` | ✅ Production — the two interactive prototypes shown in the recorded demo |
| `model v4/ui/_archive/` | ⛔ Deprecated — superseded UI versions, kept for history only |
| `model v4/scraper/` | Proof of concept — real-price scraper, not part of the production pipeline |

### Superseded, kept as development history

| Path | Status |
|---|---|
| `model v1/`, `model v2/`, `model v3/` | ⛔ Superseded by `model v4/`. Retained so the version progression is reviewable; each carries its own README explaining what it contributed and where that work went. |
| `model v3/proposed-confidence-fix/` | ⛔ A *proposal* that was never adopted — v4's conformal calibration made the approach obsolete. Kept as a record of the reasoning, not as shipped code. |
| `model v4/ui/_archive/` | ⛔ Superseded UI versions |
| `_project-history/` | ⛔ Early-stage planning documents, kept for provenance. **Contains figures later retracted** — notably the 71.5%/47.3% host-tier occupancy claim corrected in the erratum above. Read as a record of how the project started, not as current findings. |
| `Presentation Planning Notes (DEPRECATED ...).docx` | ⛔ Superseded 2026-07-26 |

---

## Documentation

| Document | What it covers |
|----------|----------------|
| **[Airbnb Pricing Deck.pptx](Airbnb%20Pricing%20Deck.pptx)** | **The final presentation.** 14 core slides plus a BACKUP divider and six backup slides (B1–B6) held for Q&A. This is the deliverable submitted to Canvas. |
| **[Airbnb Pricing Script.docx](Airbnb%20Pricing%20Script.docx)** | Spoken script for the deck, slide by slide, with speaker assignments, handoff lines and a Q&A crib sheet |
| [Rehearsal Card](Rehearsal%20Card%20-%20Who%20Presents%20What.docx) | One-page rehearsal reference: who presents which slides, timing, and which backup slide answers which question |
| [Data Cleaning Process](Data%20Cleaning%20Process.md) | Full cleaning + feature-engineering pipeline: active-listing filter, imputation, amenity parsing, host tiers, calendar occupancy, BERT sentiment, and the complete column dictionary |
| [Model v1 — Baseline OLS](model%20v1/README_MANAS_MODELING.md) | The original log-linear OLS pricing model: target, features, holdout results (OLS vs Random Forest), and the residual definition |
| [Model v2 — Model Iterations](model%20v2/model-iterations/README.md) | How the model evolved from OLS → Ridge → KNN → segment split, with links to the testing, pricing, and benchmarking sub-docs |
| [Model v4 — CURRENT](model%20v4/README.md) | The GBM pricing engine, KNN layer, seasonality, live UI tools, scraper, and elasticity pilot — what the deliverable actually runs on |
| [Model v4 — Interactive Demo](model%20v4/ui/README.md) | The two production prototypes (per-listing diagnostic + NYC birds-eye), the narrated demo script, and the birds-eye screen guide |
| [Price Elasticity Model](model%20v4/elasticity/README_elasticity_model.md) | The TWFE elasticity pilot: data source, method, results, and what it does and doesn't establish |
| [Elasticity → Revenue](model%20v4/elasticity/ELASTICITY_TO_REVENUE.md) | How the measured elasticity becomes a defensible revenue number: review-tier segmentation, the underpriced and overpriced bands, and the combined floor |
| [Revenue → ROI](model%20v4/elasticity/REVENUE_TO_ROI.md) | **Current cost and ROI figures** — incremental cost basis, adoption sensitivity, NPV, and the five-year timeline |
| [`reproduce_revenue_lift.py`](model%20v4/elasticity/reproduce_revenue_lift.py) | Regenerates the headline figures from committed data — run it to check the arithmetic rather than take it on faith. Reproduces $7.56M host GBV, $1.17M Airbnb fee, and 77,499 nights against the $7.57M / $1.17M / 77,606 reported |
| [Revenue Lift & ROI — master working doc](model%20v4/elasticity/REVENUE_LIFT_ROI_MASTER.md) | Jai's full financial reasoning, including the Option A vs. Option B decision. Sections 1–5b and 7–8 are current; **Section 6's cost/ROI table is superseded** by Revenue → ROI above (see the header note in the file) |
| [NYC_Airbnb_Appendix_Technical.docx](NYC_Airbnb_Appendix_Technical.docx) | Full technical narrative: V1→V2→V3→V4, EDA, price elasticity, business recommendations, and carried-forward limitations. Backup for Q&A, not part of the timed presentation. |
| [NYC_Airbnb_Anticipated_Questions.docx](NYC_Airbnb_Anticipated_Questions.docx) | Prepared answers to the sharpest likely challenges — companion to the appendix above |
| [Presentation Planning Notes](Presentation%20Planning%20Notes.md) | Ground-truth source for the final presentation: problem/solution framing, revenue-lift methodology, cost/ROI, slide sequence, team assignments, and schedule |
| [Model Definition & Initial Results (PDF)](Model%20Definition%20%26%20Initial%20Results%20%28FINAL%29.pdf) | ⛔ **Superseded — this is the mid-project interim deck, not the final presentation.** Kept for history; the current deck is `Airbnb Pricing Deck.pptx` above. Covers the business case, EDA findings, and modeling approach as they stood mid-project — also viewable [online](https://1drv.ms/p/c/f8ae865111d402f7/IQDEBYREy05pSo0NkkGYIBVBAcsa5nQCOXdlw9JKNpdyrlA?e=UWj3oa) |
| `Capstone Project Visualizations.twb` | Tableau workbook with the EDA and results visualizations |
| [Team Status Dashboard](https://claude.ai/code/artifact/b3c6574e-a7fc-44fb-a11b-e05adbea1433) | Live status board: what's locked, what's building now, and open risks ahead of Friday's v3 FINAL |
| [GitHub Projects Board](https://github.com/users/mkdn007/projects/1) | Day-to-day task tracker |

https://drive.google.com/file/d/1OlrAfI1-gpK6cfne5SQt2Q0EjrdruFje/view?usp=drive_link - DEMO video link

---

## Team

BANA 5160 — Brendan Meara, Jairam Manikandan, Francois Miaule, Rachael Chin, Manas Manu
Roles: Jai (data), Manas (modeling), Rachael (viz), Francois (insights), Brendan (PM/narrative)
