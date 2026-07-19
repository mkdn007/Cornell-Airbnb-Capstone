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

## The database

`calendar_snapshots.db` is committed here and updated automatically, the script copies it into this folder and pushes it after every daily run. Trade-off worth knowing: it's a binary file, so each day's commit stores a new full-ish blob rather than a clean diff, the repo will grow noticeably over the run. Chosen anyway so the accumulating data is visible to the team without anyone needing to run this locally. `scrape_log.txt` is not committed, that one really is just local run history.

## Files

- `daily_scrape.py` — the scraper, plus the end-of-run git push step
- `scraper_listing_sample.csv` — the 200-listing sample (stratified across borough and room type)
- `calendar_snapshots.db` — the accumulating data, updated daily
