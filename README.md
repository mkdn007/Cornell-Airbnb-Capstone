# Cornell–Airbnb Capstone

This project builds a **hybrid analytics engine for NYC Airbnb hosts** that combines a hedonic pricing regression with KNN competitive-cohort benchmarking — pinpointing exact nightly revenue losses and prescribing the specific operational and amenity upgrades needed to close them.

The dataset was obtained from **Inside Airbnb**, an independent, non-commercial open-source project that aggregates publicly available data from the Airbnb platform. The snapshot is New York City, captured **June 14, 2026** — 30,259 raw listings filtered to **9,752 active listings**.

---

## The business use case

**Problem.** The EDA surfaced a clear *occupancy gap*: Small-Multi operators (2–5 listings) run **71.5%** occupancy while Individual hosts sit at **47.3%** — yet individual hosts often price their listings sub-optimally, leaving revenue on the table. Hosts have no objective way to know whether they are over- or under-priced, or what to change.

**Our solution — a Revenue Optimizer (Option C).** A two-layer, host-facing diagnostic:

1. **Fair-value pricing engine** — a hedonic regression estimates what each listing *should* charge given its location, size, amenities, and ratings. The gap between actual and fair price is the **mispricing signal** ("you're priced $X above/below comparable value").
2. **Comparable-cohort benchmarking (the "why")** — KNN matches each listing to genuinely similar peers, isolates the high-occupancy performers among them, and surfaces the concrete amenity/operational gaps to close.

**The deliverable a host receives:**
> *"Your listing is underpriced by $X/night relative to its fair value. To capture that missing yield without hurting occupancy, close your feature gap: your high-performing peers offer a dedicated workspace and self-check-in — you don't."*

Positioned commercially as either a **direct-to-consumer SaaS** tool for independent hosts or a **B2B value-add dashboard** a platform could offer to improve inventory quality and marketplace volume.

---

## Where we are now

| Phase | Status |
|-------|--------|
| Data cleaning & feature engineering | ✅ Complete — 9,752 active listings, 80 columns |
| EDA & business-case alignment | ✅ Complete |
| **Model v1** — baseline log-linear OLS | ✅ Complete |
| **Model v2** — Ridge pricing engine + KNN benchmarking, segment-split | ✅ Complete (current) |
| Dashboard & final narrative | 🔄 In progress |

The current modeling work (**Model v2**) refined the baseline into a production diagnostic: a systematic 6-model bake-off selected **Ridge regression** as the pricing engine (stable, interpretable coefficients at top-tier accuracy), a **KNN layer** was added to explain each pricing gap, and both were **split by market segment** (short-stay vs monthly) so listings are only ever benchmarked against genuinely comparable peers.

---

## Documentation

| Document | What it covers |
|----------|----------------|
| [Data Cleaning Process](Data%20Cleaning%20Process.md) | Full cleaning + feature-engineering pipeline: active-listing filter, imputation, amenity parsing, host tiers, calendar occupancy, BERT sentiment, and the complete column dictionary |
| [Model v2 — Model Iterations](model%20v2/model-iterations/README.md) | How the model evolved from OLS → Ridge → KNN → segment split, with links to the testing, pricing, and benchmarking sub-docs |
| [Capstone Presentation](https://1drv.ms/p/c/f8ae865111d402f7/IQDEBYREy05pSo0NkkGYIBVBAcsa5nQCOXdlw9JKNpdyrlA?e=UWj3oa) | Slide deck covering the business case, EDA findings, and modeling approach |
| `Capstone Project Visualizations.twb` | Tableau workbook with the EDA and results visualizations |

---

## Team

BANA 5160 — Brendan Meara, Jairam Manikandan, Francois Miaule, Rachael Chin, Manas Manu
Roles: Jai (data), Manas (modeling), Rachael (viz), Francois (insights), Brendan (PM/narrative)
