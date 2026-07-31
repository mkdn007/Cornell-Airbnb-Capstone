# NYC Airbnb Pricing Diagnostic — Interactive Demo

**Status: PRODUCTION.** These are the two prototypes shown in the recorded demo and referenced in the final presentation.

No internet needed — all data is embedded. Open either HTML file in any browser (double-click).

## Current files

| File | What it is |
|---|---|
| **`host_pricing_diagnostic_v3.html`** | **Production.** The per-listing pricing tool. Pick a demo property from the dropdown (Midtown Room, Blue Room, Central Park Studio) to see its fair-value price, calibrated confidence range, real occupancy, amenity gaps vs. high-performing peers, and a revenue projection you can drag. |
| **`nyc_pricing_overview_gbm.html`** | **Production.** The birds-eye view: NYC neighborhoods colored by pricing gap, repricing direction, revenue lift, and occupancy. Toggle short-stay / monthly. |
| `assets/` | Airbnb logo and the real listing photos used by the diagnostic. **Required** — the pages break without it. |
| `UI_Script.md` | The ~5-minute narrated walkthrough script used to record the demo. Covers all three listings plus the birds-eye, with the caveat checklist. |
| `BIRDSEYE_SCREENS.md` | Screen-by-screen guide to the birds-eye view (7 screens, including the 3 current-model screens added 7/30). |

The two pages cross-link via chips at the top, so start with either.

## Deprecated

| File | Why |
|---|---|
| `_archive/host_pricing_diagnostic_v2.html` | **Superseded by v3 (2026-07-30).** v3 adds the real listing photography and Airbnb branding pass, and is the version the recorded demo actually shows. v2 is kept for version history only — nothing links to it and it links to nothing. Do not present from it. |

## To open

Double-click `host_pricing_diagnostic_v3.html`. Keep the `assets/` folder next to the HTML files; don't move an HTML file out on its own or the images and cross-links break.

---

Cornell BANA 5160 capstone · data reflects the Inside Airbnb NYC snapshot of June 14, 2026 · interactive prototype, not a shipped product. Independent academic analysis of public data; not affiliated with or endorsed by Airbnb.
