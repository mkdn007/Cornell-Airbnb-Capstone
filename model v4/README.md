# Model V4 — GBM Quantile Regression (CURRENT MODEL)

**This is the current model the deliverable runs on.** Supersedes `model v1/` (OLS baseline), `model v2/` (Ridge + KNN), and `model v3/` (confidence scoring, still Ridge-based) — see the root `README.md` for the full version progression and why each change happened. Full technical history, including the price-elasticity pilot built on top of this model, is in `NYC_Airbnb_Appendix_Technical.docx`.

See `dev_journey_narrative.md` for the full story of how we got here.

- `ui/` — the two interactive tools (self-contained HTML, no build step, open directly in a browser)
  - `host_pricing_diagnostic_v2.html` — property-level pricing tool, 5 demo listings. Live: https://claude.ai/code/artifact/cfb7b07c-82ed-4d24-bb9b-44bd64dbb473
  - `nyc_pricing_overview_gbm.html` — birds-eye neighborhood map. Live: https://claude.ai/code/artifact/39564fab-a183-4762-9bfd-f0865ee9b034
- Team status board (what's locked, what's building now): https://claude.ai/code/artifact/b3c6574e-a7fc-44fb-a11b-e05adbea1433
- `model/` — the current GBM pricing model, KNN comparable-listings layer, and their outputs
  - `model_v3_gbm.py`, `knn_v3.py`, `active_listings_clean_v6.csv`, `requirements.txt`
  - `outputs_gbm/`, `outputs_knn/` — the CSVs the UIs are built from
  - `seasonality/` — simulated seasonal price index and demo script
- `birdseye_pipeline/` — scripts that turn the model outputs above into the birds-eye map's data (`prepare_birdseye_data.py` → `build_birdseye_pricing_json.py` → `assemble_birdseye.py`)
- `docs/` — Model V3 insights/technical report
- `scraper/` — the reconfigured scraper (`daily_scrape.py`, real run data, README)

Excludes exploratory scripts, superseded Ridge-based V3 outputs, and one-off investigation code, this is what the current deliverable actually runs on.
