# Cornell–Airbnb Capstone

This project builds a **hybrid analytics engine for NYC Airbnb hosts** that combines a hedonic pricing regression with KNN competitive-cohort benchmarking — pinpointing exact nightly revenue losses and prescribing the specific operational and amenity upgrades needed to close them.

The dataset was obtained from **Inside Airbnb**, an independent, non-commercial open-source project that aggregates publicly available data from the Airbnb platform. The snapshot is New York City, captured **June 14, 2026** — 30,259 raw listings filtered to **9,752 active listings**.

---

## The business use case

**Problem.** The EDA surfaced a clear *occupancy gap*: Small-Multi operators (2–5 listings) run **71.5%** occupancy while Individual hosts sit at **47.3%** — yet individual hosts often price their listings sub-optimally, leaving revenue on the table. Hosts have no objective way to know whether they are over- or under-priced, or what to change.

> **Correction (2026-07-28):** the 71.5% Small-Multi figure does not reproduce from `active_listings_clean_v6.csv` under any occupancy metric checked (mean, median, calendar-based, or raw days-booked) — most likely a transcription error from the original EDA writeup, no source notebook survives to check it against. The Individual (47.3%) and Enterprise (37.2%, see `Data Cleaning Process.md`) figures do reproduce closely, so this looks isolated to the one number. Verified current numbers (mean `occupancy_rate_calendar`): **Individual 44.1%, Small-Multi 37.8%, Mid-Multi 32.6%, Enterprise 30.0%** — occupancy actually *declines* as host scale increases, the opposite of the original claim. Use the corrected numbers and direction in any slide/script content going forward; this hasn't propagated beyond these repo docs as of this correction.

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
| **Model v3** (`model v3/`) | Same Ridge engine as v2, adds confidence scoring + host-tier-aware KNN | Superseded |
| **Model v4** (`model v4/`) | **GBM quantile regression (q10/q50/q90) with conformal calibration**, same host-tier-aware KNN layer carried forward, plus seasonality, two live UI tools, a real-price scraper proof of concept, and a price-elasticity pilot | **✅ CURRENT — this is what the deliverable runs on** |

Each version's own README explains why the change was made, not just what changed. Full narrative in [`NYC_Airbnb_Appendix_Technical.docx`](NYC_Airbnb_Appendix_Technical.docx); anticipated Q&A challenges with prepared answers in [`NYC_Airbnb_Anticipated_Questions.docx`](NYC_Airbnb_Anticipated_Questions.docx).

---

## Documentation

| Document | What it covers |
|----------|----------------|
| [Data Cleaning Process](Data%20Cleaning%20Process.md) | Full cleaning + feature-engineering pipeline: active-listing filter, imputation, amenity parsing, host tiers, calendar occupancy, BERT sentiment, and the complete column dictionary |
| [Model v1 — Baseline OLS](model%20v1/README_MANAS_MODELING.md) | The original log-linear OLS pricing model: target, features, holdout results (OLS vs Random Forest), and the residual definition |
| [Model v2 — Model Iterations](model%20v2/model-iterations/README.md) | How the model evolved from OLS → Ridge → KNN → segment split, with links to the testing, pricing, and benchmarking sub-docs |
| [Model v4 — CURRENT](model%20v4/README.md) | The GBM pricing engine, KNN layer, seasonality, live UI tools, scraper, and elasticity pilot — what the deliverable actually runs on |
| [NYC_Airbnb_Appendix_Technical.docx](NYC_Airbnb_Appendix_Technical.docx) | Full technical narrative: V1→V2→V3→V4, EDA, price elasticity, business recommendations, and carried-forward limitations. Backup for Q&A, not part of the timed presentation. |
| [NYC_Airbnb_Anticipated_Questions.docx](NYC_Airbnb_Anticipated_Questions.docx) | Prepared answers to the sharpest likely challenges — companion to the appendix above |
| [Presentation Planning Notes](Presentation%20Planning%20Notes.md) | Ground-truth source for the final presentation: problem/solution framing, revenue-lift methodology, cost/ROI, slide sequence, team assignments, and schedule |
| [Capstone Presentation](Model%20Definition%20%26%20Initial%20Results%20%28FINAL%29.pdf) | Original slide deck (PDF) covering the business case, EDA findings, and modeling approach — also viewable [online](https://1drv.ms/p/c/f8ae865111d402f7/IQDEBYREy05pSo0NkkGYIBVBAcsa5nQCOXdlw9JKNpdyrlA?e=UWj3oa) |
| `Capstone Project Visualizations.twb` | Tableau workbook with the EDA and results visualizations |
| [Team Status Dashboard](https://claude.ai/code/artifact/b3c6574e-a7fc-44fb-a11b-e05adbea1433) | Live status board: what's locked, what's building now, and open risks ahead of Friday's v3 FINAL |
| [GitHub Projects Board](https://github.com/users/mkdn007/projects/1) | Day-to-day task tracker |

---

## Team

BANA 5160 — Brendan Meara, Jairam Manikandan, Francois Miaule, Rachael Chin, Manas Manu
Roles: Jai (data), Manas (modeling), Rachael (viz), Francois (insights), Brendan (PM/narrative)
