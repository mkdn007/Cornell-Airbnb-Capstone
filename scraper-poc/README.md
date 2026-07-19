# Calendar-availability scraper, proof of concept

**Not run as part of the model.** This is a separate exploration into a scalable, non-Airbnb-provided data source, kept out of `model v2/` on purpose since it's a data-collection experiment for a future capability, not an iteration of the current pricing model. See [seasonality-poc](../model%20v2/model-iterations/seasonality-poc/) for how the (currently simulated) seasonal pricing layer works today.

## What it does

For a fixed sample of 200 real NYC listings, calls Airbnb's own public `PdpAvailabilityCalendar` endpoint (the same GraphQL call the listing page's JavaScript makes) and stores each listing's 365-day forward availability snapshot, dated the day it ran, in SQLite. Run once a day for a stretch of time, a date that shows available today and blocked tomorrow can be inferred as a real booking, the same method academic Airbnb-pricing research and vendors like AirDNA use.

## What it does NOT do

Fetch price. Confirmed directly, by capturing live network traffic and by simulating an actual guest date-selection, that Airbnb does not expose per-day price to anonymous requests without simulating a real check-in/check-out selection, which is a much heavier operation per listing than a single calendar fetch. This script is availability-only, on purpose.

## Terms of Service

This scrapes Airbnb's public site, which sits outside their Terms of Service. Discussed at length before building this: kept to a 200-listing sample with jittered delays between requests (1.5-4s), not a production-scale operation, and does not use a logged-in account (confirmed unnecessary, the price gate is interaction-based, not authentication-based, and login would be a materially higher-risk step we chose not to take).

## Running it

```
python daily_scrape.py
```

Reads `scraper_listing_sample.csv` (in this folder) for the 200 listing IDs, writes to `calendar_snapshots.db` (created alongside the script, not committed to this repo, see below).

Running locally on a schedule via Windows Task Scheduler, once daily, no manual step required.

## What's not in this folder

`calendar_snapshots.db` and `scrape_log.txt` are not committed here. Both grow daily and are local run state, not code. If useful for the final deck or a teammate wants to inspect the accumulated data, ask and a CSV export can be shared directly instead of tracking the live database in git.

## Files

- `daily_scrape.py` — the scraper
- `scraper_listing_sample.csv` — the 200-listing sample (stratified across borough and room type)
