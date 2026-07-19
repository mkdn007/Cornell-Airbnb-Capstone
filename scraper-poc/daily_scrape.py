"""
Daily calendar-availability scraper, proof of concept.

What this does: for a fixed sample of 200 real NYC listings, calls Airbnb's
own public PdpAvailabilityCalendar endpoint (the same one the listing page's
JS calls, confirmed by capturing live network traffic) and stores each
listing's 365-day forward availability snapshot, dated today, in SQLite.

What this does NOT do: fetch price. Confirmed directly (multiple listings,
plus simulating real date-selection) that Airbnb does not expose per-day
price to anonymous requests without simulating an actual date-range
selection, which is a much heavier per-listing operation. This script is
availability-only, on purpose. Running it once a day for a week lets a
date that shows available today and blocked tomorrow be inferred as a
real booking event, the same mechanism AirDNA and academic Airbnb-pricing
research use.

ToS note: this scrapes Airbnb's public site, which sits outside their
Terms of Service, discussed at length before building this. Kept to a
200-listing sample with jittered delays between requests, not a
production-scale operation.
"""

import json
import sqlite3
import time
import random
import urllib.request
import urllib.parse
import urllib.error
import csv
import datetime
import re
from pathlib import Path

HERE = Path(__file__).parent
DB_PATH = HERE / "calendar_snapshots.db"
SAMPLE_CSV = HERE / "scraper_listing_sample.csv"
LOG_PATH = HERE / "scrape_log.txt"

CALENDAR_HASH = "be60714ead0a30db42ce6471ddad6a8f3855df0ed400b79282dd0bb8cecdf201"
API_KEY = "d306zoyjsyarp7ifhu67rjxn52tv0t20"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def load_listings():
    listings = []
    with open(SAMPLE_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            listings.append(row)
    return listings


def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            listing_id TEXT PRIMARY KEY,
            listing_url TEXT,
            borough TEXT,
            neighborhood TEXT,
            room_type TEXT,
            property_type TEXT,
            nightly_price_at_sample_time REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calendar_snapshots (
            listing_id TEXT,
            snapshot_date TEXT,
            calendar_date TEXT,
            available INTEGER,
            min_nights INTEGER,
            max_nights INTEGER,
            PRIMARY KEY (listing_id, snapshot_date, calendar_date)
        )
    """)
    conn.commit()


def fetch_calendar(listing_id, start_month, start_year):
    variables = json.dumps({
        "request": {
            "count": 12,
            "listingId": str(listing_id),
            "month": start_month,
            "year": start_year,
            "returnPropertyLevelCalendarIfApplicable": False,
        }
    })
    extensions = json.dumps({"persistedQuery": {"version": 1, "sha256Hash": CALENDAR_HASH}})
    url = (
        f"https://www.airbnb.com/api/v3/PdpAvailabilityCalendar/{CALENDAR_HASH}"
        f"?operationName=PdpAvailabilityCalendar&locale=en&currency=USD"
        f"&variables={urllib.parse.quote(variables)}&extensions={urllib.parse.quote(extensions)}"
    )
    req = urllib.request.Request(url, headers={
        "x-airbnb-api-key": API_KEY,
        "x-airbnb-graphql-platform-client": "minimalist-niobe",
        "x-airbnb-graphql-platform": "web",
        "content-type": "application/json",
        "user-agent": USER_AGENT,
        "accept": "*/*",
        "referer": f"https://www.airbnb.com/rooms/{listing_id}",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run():
    today = datetime.date.today()
    listings = load_listings()
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    log_lines = [f"=== run started {datetime.datetime.now().isoformat()} ==="]
    ok, failed = 0, 0

    for row in listings:
        listing_id = row["id"]
        conn.execute(
            "INSERT OR IGNORE INTO listings (listing_id, listing_url, borough, neighborhood, room_type, property_type, nightly_price_at_sample_time) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (listing_id, row["listing_url"], row["borough"], row["neighborhood"],
             row["room_type"], row["property_type"], row.get("nightly_price")),
        )
        try:
            body = fetch_calendar(listing_id, today.month, today.year)
            months = body["data"]["merlin"]["pdpAvailabilityCalendar"]["calendarMonths"]
            rows_to_insert = []
            for m in months:
                for d in m["days"]:
                    rows_to_insert.append((
                        listing_id, today.isoformat(), d["calendarDate"],
                        int(bool(d["available"])), d["minNights"], d["maxNights"],
                    ))
            conn.executemany(
                "INSERT OR REPLACE INTO calendar_snapshots "
                "(listing_id, snapshot_date, calendar_date, available, min_nights, max_nights) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                rows_to_insert,
            )
            conn.commit()
            ok += 1
            log_lines.append(f"OK  {listing_id}  ({len(rows_to_insert)} days)")
        except Exception as e:
            failed += 1
            log_lines.append(f"FAIL {listing_id}: {type(e).__name__} {e}")

        time.sleep(random.uniform(1.5, 4.0))  # jittered delay, don't hammer

    log_lines.append(f"=== run finished: {ok} ok, {failed} failed ===")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    print(f"{ok} listings scraped OK, {failed} failed. See {LOG_PATH}")
    conn.close()


if __name__ == "__main__":
    run()
