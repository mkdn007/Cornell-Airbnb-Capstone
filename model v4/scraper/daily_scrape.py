"""
Daily calendar-availability + price scraper, proof of concept.

What this does: for a fixed sample of 200 real NYC listings, calls
Airbnb's own public PdpAvailabilityCalendar endpoint (confirmed by
capturing live network traffic) and stores each listing's 365-day
forward availability snapshot, dated today, in SQLite. It then picks,
per listing, a genuinely open date range that respects that listing's
own minimum-stay requirement (using the minNights field the calendar
call already returns), and loads that listing's real page in a headless
browser with those dates, capturing the real per-stay price Airbnb
displays. Both are stored dated today, so running this daily builds an
actual price-and-occupancy time series per listing, not just one static
snapshot, the thing the whole project was missing.

Why a real browser for the price half, not a lightweight HTTP call like
the calendar one: confirmed directly that a plain HTTP GET/POST never
returns price, Airbnb's frontend requires a real page load. Also
confirmed, at length, exactly why every early attempt at this returned
"unavailable": not a data or access problem, every early attempt picked
a date range shorter than the listing's own minimum stay (one listing
tested has a real 3-night minimum), which Airbnb correctly rejects. Once
the date range respects minNights, both a real browser session and,
separately, a plain URL navigation with check_in/check_out query params
return a genuine price ("$457 for 3 nights", confirmed against listing
343276). A fully lightweight HTTP POST replication (bypassing the
browser rendering step entirely) was also found to be technically
possible in principle, the request is a standard persisted-query
GraphQL POST, not something requiring a live session, but the full
request body has many more required fields than were captured in this
session's discovery pass, and reconstructing all of them wasn't
finished. Worth revisiting if the per-listing browser load proves too
slow for a daily run at this sample size.

After each run, copies calendar_snapshots.db into the git repo and pushes
it, so the accumulating data is visible to the team without anyone
needing to run this locally. Best-effort: a git/network failure is
logged, not raised, so it never breaks the scrape itself.

ToS note: this scrapes Airbnb's public site, which sits outside their
Terms of Service, discussed at length before building this. Kept to a
200-listing sample with jittered delays between requests, not a
production-scale operation. The price half is a heavier per-listing
operation than the calendar half (a real browser page load vs. one fast
HTTP call), expect this run to take meaningfully longer per day.

Requires: pip install playwright && playwright install chromium
"""

import json
import sqlite3
import time
import random
import subprocess
import urllib.request
import urllib.parse
import urllib.error
import csv
import datetime
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS price_snapshots (
            listing_id TEXT,
            snapshot_date TEXT,
            check_in TEXT,
            check_out TEXT,
            nights INTEGER,
            price_display TEXT,
            nightly_price_estimate REAL,
            PRIMARY KEY (listing_id, snapshot_date)
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


def pick_price_check_dates(days, min_lead_days=7):
    """Find a check-in/check-out pair that's actually bookable: at least
    min_lead_days out, every night in the stay marked available, and long
    enough to satisfy that listing's own minNights (the calendar response
    already tells us this per day). Picking a range shorter than minNights
    is exactly why every early manual attempt this session came back
    "unavailable", not a data or access problem."""
    today = datetime.date.today()
    for i, day in enumerate(days):
        d = datetime.date.fromisoformat(day["calendarDate"])
        if d < today + datetime.timedelta(days=min_lead_days):
            continue
        if not day["available"]:
            continue
        min_nights = day.get("minNights") or 1
        run_days = days[i:i + min_nights]
        if len(run_days) < min_nights or not all(r["available"] for r in run_days):
            continue
        check_in = d
        check_out = datetime.date.fromisoformat(run_days[-1]["calendarDate"]) + datetime.timedelta(days=1)
        return check_in.isoformat(), check_out.isoformat(), min_nights
    return None


def fetch_price(page, listing_id, check_in, check_out):
    """Load the real listing page with a bookable date range and capture
    the price Airbnb's own frontend displays. Confirmed this requires a
    real browser render, a plain HTTP GET/POST to the page never returns
    price. Navigating with check_in/check_out query params is enough,
    no simulated clicking on the calendar widget needed, confirmed
    directly, as long as the dates themselves are genuinely bookable."""
    url = f"https://www.airbnb.com/rooms/{listing_id}?check_in={check_in}&check_out={check_out}&adults=1"
    captured = {}

    def on_response(response):
        if "StaysPdpSections" in response.url and "body" not in captured:
            try:
                captured["body"] = response.text()
            except Exception:
                pass

    page.on("response", on_response)
    try:
        page.goto(url, wait_until="load", timeout=45000)
        page.wait_for_timeout(6000)
    finally:
        page.remove_listener("response", on_response)

    if "body" not in captured:
        return None
    text = captured["body"]
    idx = text.find('"structuredDisplayPrice"')
    if idx == -1:
        return None
    window = text[idx:idx + 800]
    # Confirmed by inspecting real failures: Airbnb returns at least three
    # different primaryLine shapes depending on whether a discount
    # applies. QualifiedDisplayPriceLine has a direct "price" key.
    # DiscountedDisplayPriceLine has "discountedPrice" directly.
    # OrderedDisplayPriceLine nests the same "discountedPrice" key one
    # level down inside orderedComponents. The first version of this
    # function only handled the first shape, silently returning None
    # (logged as "no price in response") for the other two, which turned
    # out to be the majority of one full day's run. Whichever key appears
    # first in the window is the real, current price.
    match = re.search(r'"(?:price|discountedPrice)":"([^"]+)"', window)
    return match.group(1) if match else None


def parse_nightly_estimate(price_display, nights):
    """price_display looks like "$457" (total for the stay) alongside a
    separate "for N nights" qualifier, or occasionally a bare per-night
    figure. Best-effort divide by nights; store the raw display string
    too so this guess is always checkable against the source text."""
    digits = re.sub(r"[^\d.]", "", price_display or "")
    if not digits:
        return None
    try:
        total = float(digits)
        return round(total / nights, 2) if nights else total
    except ValueError:
        return None


def run():
    today = datetime.date.today()
    listings = load_listings()
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    log_lines = [f"=== run started {datetime.datetime.now().isoformat()} ==="]
    ok, failed = 0, 0
    price_ok, price_failed = 0, 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=USER_AGENT)

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
                all_days = [d for m in months for d in m["days"]]
                rows_to_insert = [
                    (listing_id, today.isoformat(), d["calendarDate"],
                     int(bool(d["available"])), d["minNights"], d["maxNights"])
                    for d in all_days
                ]
                conn.executemany(
                    "INSERT OR REPLACE INTO calendar_snapshots "
                    "(listing_id, snapshot_date, calendar_date, available, min_nights, max_nights) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    rows_to_insert,
                )
                conn.commit()
                ok += 1
                log_lines.append(f"OK  {listing_id}  ({len(rows_to_insert)} days)")

                # Price half: reuses the calendar data just fetched, no
                # extra lightweight call needed, to pick a date range that
                # actually respects this listing's own minimum stay.
                picked = pick_price_check_dates(all_days)
                if picked is None:
                    log_lines.append(f"PRICE SKIP {listing_id}: no bookable range found in forward calendar")
                else:
                    check_in, check_out, min_nights = picked
                    try:
                        price_display = fetch_price(page, listing_id, check_in, check_out)
                        if price_display is None:
                            price_failed += 1
                            log_lines.append(f"PRICE FAIL {listing_id}: no price in response for {check_in}..{check_out}")
                        else:
                            nightly_estimate = parse_nightly_estimate(price_display, min_nights)
                            conn.execute(
                                "INSERT OR REPLACE INTO price_snapshots "
                                "(listing_id, snapshot_date, check_in, check_out, nights, price_display, nightly_price_estimate) "
                                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (listing_id, today.isoformat(), check_in, check_out, min_nights,
                                 price_display, nightly_estimate),
                            )
                            conn.commit()
                            price_ok += 1
                            log_lines.append(f"PRICE OK   {listing_id}  {price_display} ({min_nights} nights, {check_in}..{check_out})")
                    except Exception as e:
                        price_failed += 1
                        log_lines.append(f"PRICE FAIL {listing_id}: {type(e).__name__} {e}")
            except Exception as e:
                failed += 1
                log_lines.append(f"FAIL {listing_id}: {type(e).__name__} {e}")

            time.sleep(random.uniform(1.5, 4.0))  # jittered delay, don't hammer

        browser.close()

    log_lines.append(
        f"=== run finished: {ok} ok, {failed} failed (calendar); "
        f"{price_ok} ok, {price_failed} failed (price) ==="
    )
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    print(f"{ok} listings scraped OK, {failed} failed (calendar). "
          f"{price_ok} price OK, {price_failed} price failed. See {LOG_PATH}")
    conn.close()

    push_db_to_repo(today)


REPO_SCRAPER_DIR = Path(r"C:\Users\stava\OneDrive\Documents\Capstone\repo_clone\scraper-poc")


def push_db_to_repo(today):
    """Copy today's database into the git repo and push it. Best-effort:
    logs failures instead of raising, so a git/network issue never breaks
    the scrape itself, only the push step."""
    import shutil
    log_lines = []
    try:
        repo_root = REPO_SCRAPER_DIR.parent
        dest = REPO_SCRAPER_DIR / DB_PATH.name
        shutil.copy2(DB_PATH, dest)

        def git(*args):
            return subprocess.run(
                ["git", *args], cwd=repo_root, capture_output=True, text=True, check=False
            )

        git("add", str(dest.relative_to(repo_root)))
        status = git("status", "--porcelain")
        if not status.stdout.strip():
            log_lines.append(f"git push {today.isoformat()}: no changes to commit")
        else:
            commit = git("commit", "-m", f"Scraper: daily database update {today.isoformat()}")
            push = git("push", "origin", "main")
            if push.returncode == 0:
                log_lines.append(f"git push {today.isoformat()}: OK")
            else:
                log_lines.append(f"git push {today.isoformat()}: FAILED\n{push.stdout}\n{push.stderr}")
    except Exception as e:
        log_lines.append(f"git push {today.isoformat()}: EXCEPTION {type(e).__name__} {e}")

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))


if __name__ == "__main__":
    run()
