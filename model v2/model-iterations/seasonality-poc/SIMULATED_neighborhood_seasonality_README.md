# SIMULATED data — proof of concept only

**This is not real Airbnb data and has not been fit or validated. Do not present it as a model result.**

## What it is

A neighborhood-by-month seasonal price index (`SIMULATED_neighborhood_seasonality.csv`), built as a stand-in for the calendar-level Airbnb price data that does not currently exist publicly for NYC (checked directly: every Inside Airbnb NYC snapshot from 2025-08-01 through 2026-06-14 has blank `price`/`adjusted_price` fields in calendar.csv). This exists so the team can demo what a seasonal-pricing layer would look like, to be replaced with real data (a proper calendar-price source, or the external proxies below, fully built out) if the project continues past this course.

## How each column was built

- `real_avg_occupancy_rate` — **real, not simulated.** Averaged from `occupancy_Jan`–`occupancy_Dec` in `active_listings_clean_v6.csv`, which Jai's pipeline already computed from actual Inside Airbnb calendar availability data.
- `neighborhood_seasonality_amplitude_weight` — **real, not simulated.** The coefficient of variation (std/mean) across each neighborhood's 12 real monthly occupancy values, rescaled to a 0.5x–1.5x range. Neighborhoods whose real booking pattern already swings more seasonally get a larger weight; flatter ones get a smaller one.
- `SIMULATED_price_seasonal_index` — **simulated.** Formula: `1 + (citywide_ADR_index[month] - 1) * neighborhood_amplitude_weight`.

## Where the simulated part's shape comes from

The citywide ADR (average daily rate) seasonal index is real, cited NYC hotel-market data, not invented: the average of 2016–2019 monthly hotel ADR (four consistent pre-pandemic years; 2020 excluded as pandemic-distorted), from:

> NYC & Company / CBRE, *"NYC Hotel Occupancy, ADR & Room Demand — 5 Year Trend Report"* (Feb 2021)
> https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/newyorkcity/FYI_HotelPerformance_5Year_22821_dk_82d984c7-b953-4b74-a906-0db91402564b.pdf

| Month | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Avg ADR ($) | 209 | 204 | 254 | 284 | 310 | 300 | 260 | 251 | 357 | 339 | 316 | 341 |
| Seasonal index | 0.73 | 0.71 | 0.89 | 0.99 | 1.09 | 1.05 | 0.91 | 0.88 | 1.25 | 1.19 | 1.11 | 1.20 |

Hotel ADR is used as a proxy for Airbnb seasonal price movement because no Airbnb-specific calendar price data is currently publicly available for NYC. It is a different market (hotels, not short-term rentals) and the two do not necessarily move together in magnitude, only used here for a directionally plausible shape.

## What this is not

- Not fit to any Airbnb price data.
- Not validated against actual bookings or realized prices.
- Not neighborhood-specific on the price side (only the amplitude weight varies by neighborhood; the underlying curve shape is one citywide hotel-market curve).
- Not a substitute for the real proxies discussed (NYC TLC trip data for neighborhood-level demand, or a properly sourced calendar-price file) if the project is extended.

## If used in the deck

Label every chart/table built from this file, visibly, as: *"Illustrative simulation, not fitted to Airbnb data — proof of concept pending a real neighborhood-level price source."*
