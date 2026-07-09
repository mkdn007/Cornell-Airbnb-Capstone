# NYC Airbnb Capstone — Data Cleaning Pipeline
### BANA 5160 | Brendan Meara, Jairam Manikandan, Francois Miaule, Rachael Chin, Manas Manu

---

## Overview

This document describes the full data cleaning and feature engineering pipeline that transforms the raw Inside Airbnb NYC dataset into a clean, model-ready file.

**Input:** `listings (2).csv` — 30,259 listings, 90 columns, snapshot date June 14, 2026  
**Output:** `active_listings_clean_v6.csv` — 9,752 listings, 80 columns

---

## Step 1 — Active Listing Filter

**Script:** `clean_listings.py`

The raw dataset contains 30,259 listings, many of which are inactive, orphaned, or have no pricing data. We define an **Active Listing** as one that meets all three of the following criteria:

- `price > 0` — has a nightly price set
- `availability_365 > 0` — has at least one day available in the next 365 days
- `number_of_reviews_ltm >= 1` — received at least one review in the last 12 months

This filters the dataset from **30,259 → 9,752 rows (32.2% of raw)**. Inactive and orphaned listings are excluded because they would skew the baseline pricing coefficients in the hedonic regression model downward.

---

## Step 2 — Bathroom Imputation from bathrooms_text

**Script:** `clean_listings.py`

The raw `bathrooms` column had 11,069 nulls. However, Inside Airbnb stores bathroom descriptions as free text in `bathrooms_text` (e.g. "1.5 shared baths", "Half-bath", "2 baths"). We first parsed this column into a numeric value before falling back to imputation:

- `"1.5 shared baths"` → `1.5`
- `"Half-bath"` → `0.5`
- `"2 baths"` → `2.0`

This recovered **1,062 bathroom values** from text, leaving only **7 truly missing** rows.

### Remaining Null Imputation (bedrooms, beds, bathrooms)

For values still missing after text parsing, we impute using the **median value for each `accommodates` group** from non-null rows:

| accommodates | median bedrooms |
|---|---|
| 1–3 guests | 1 bedroom |
| 4–6 guests | 2 bedrooms |
| 7–9 guests | 3 bedrooms |

We use median (not mean) because bedrooms is a discrete whole number — a mean could produce non-integer values like 1.73. A `_imputed` binary flag column is added for each field (`bedrooms_imputed`, `beds_imputed`, `bathrooms_imputed`) to mark which values were filled vs. observed.

**Final null counts after imputation:**
- `bedrooms`: 3,887 nulls → 0
- `beds`: 720 nulls → 0
- `bathrooms`: 7 nulls → 0

---

## Step 3 — Amenity Parsing (Top 20 Binary Flags)

**Script:** `clean_listings.py`

The raw `amenities` column stores a JSON-style list per listing (e.g. `["Wifi", "Air conditioning", "Dedicated workspace"]`). Across all listings there are **6,014 unique amenity strings** — too many to use directly. The long tail is noise: brand-specific wifi speeds, local quirks, typos.

**Approach:** Parse all amenity strings to lowercase, count frequency across all active listings, extract the **top 20 by frequency**, and encode each as a binary `has_*` column (0 or 1).

**Top 20 amenities (active listings):**

| Rank | Amenity | Count |
|---|---|---|
| 1 | smoke_alarm | 9,443 |
| 2 | wifi | 8,914 |
| 3 | carbon_monoxide_alarm | 8,767 |
| 4 | hot_water | 8,663 |
| 5 | hangers | 8,187 |
| 6 | kitchen | 8,095 |
| 7 | bed_linens | 7,734 |
| 8 | hair_dryer | 7,671 |
| 9 | iron | 7,554 |
| 10 | essentials | 7,513 |
| 11 | dishes_and_silverware | 7,389 |
| 12 | microwave | 7,050 |
| 13 | refrigerator | 6,777 |
| 14 | cooking_basics | 6,731 |
| 15 | dedicated_workspace | 6,260 |
| 16 | air_conditioning | 6,150 |
| 17 | shampoo | 5,852 |
| 18 | heating | 5,824 |
| 19 | self_check_in | 5,811 |
| 20 | fire_extinguisher | 5,494 |

---

## Step 4 — Host Tier Classification

**Script:** `clean_listings.py`

Using `calculated_host_listings_count`, each listing is assigned a host tier based on how many total listings that host manages:

| Tier | Listings Count | Active Count |
|---|---|---|
| Individual | 1 listing | 3,402 |
| Small-Multi | 2–5 listings | 2,971 |
| Mid-Multi | 6–20 listings | 1,608 |
| Enterprise | 20+ listings | 1,771 |

This is the primary segmentation variable from the EDA. Small-Multi operators (71.5% occupancy) dramatically outperform Individual hosts (47.3%) and Enterprise operators (37.2%).

A binary flag `is_monthly_rental` is also added here:
- `is_monthly_rental = 1` if `min_nights >= 28`
- **58.9% of active listings** are flagged as monthly rentals — a critical finding. These listings are long-term rental products, not short-term stays, and behave fundamentally differently in pricing models. The modeling team should consider filtering these out or handling them separately.

---

## Step 5 — Matched Segment Key

**Script:** `clean_listings.py`

To enable apples-to-apples comparison between listings, each listing is assigned a `segment` key combining three dimensions:

```
segment = borough | room_type | capacity_tier
```

**`capacity_tier`** buckets `max_guests` into three groups:

| Old Value | New Label | Max Guests | Count |
|---|---|---|---|
| 1-2 | small | 1–2 guests | 6,079 |
| 3-4 | medium | 3–4 guests | 2,295 |
| 5+ | large | 5+ guests | 1,378 |

Note: Labels were changed from `1-2 / 3-4 / 5+` to `small / medium / large` to prevent Excel from auto-converting these to date formats.

**Result:** 48 unique segments across the active dataset.

Example segments: `Brooklyn | Private room | small`, `Manhattan | Entire home/apt | medium`

---

## Step 6 — Calendar Occupancy Features

**Script:** `clean_listings.py`

The `calendar (1).csv` file contains 11.15 million rows — one row per listing per day for 365 days. Each row has an `available` field: `t` (available) or `f` (unavailable/booked). We process this file in 500k-row chunks to avoid memory issues.

For each listing we compute:
- **`occupancy_rate_calendar`** — fraction of all 365 days marked as unavailable (`f / total days`)
- **`occupancy_Jan` through `occupancy_Dec`** — same rate broken down by month, giving seasonal patterns

**Important caveat:** `f` means "not available" — this includes both guest bookings AND host-blocked dates. These cannot be distinguished from calendar data alone. The same limitation applies to Inside Airbnb's own `occupancy_rate` column.

**Difference between occupancy columns:**

| Column | Source | Direction | Method |
|---|---|---|---|
| `occupancy_rate` | Inside Airbnb pre-computed | Backward-looking | Review frequency proxy |
| `occupancy_rate_calendar` | Raw calendar.csv (us) | Forward-looking | Direct availability flags |

Calendar coverage: **9,752 / 9,752 active listings (100%)**.

---

## Step 7 — Review Velocity Features

**Script:** `clean_listings.py`

From `reviews (1).csv` (990,172 rows), we compute two velocity features per listing:

- **`days_since_last_review`** — days between the snapshot date (June 14, 2026) and the most recent review. A high value signals a stale or declining listing.
- **`reviews_last_12mo_verified`** — our independent recount of reviews in the last 12 months, computed directly from raw review dates. This validates the pre-computed `reviews_last_12mo` from listings.csv. Discrepancies between the two are a data quality flag.

Both fields are populated for all 9,752 active listings.

---

## Step 8 — BERT Sentiment Score

**Script:** `clean_listings.py`

**Model:** `nlptown/bert-base-multilingual-uncased-sentiment` — a BERT model fine-tuned on hotel and product reviews. Chosen over VADER because:

| | VADER | nlptown BERT |
|---|---|---|
| Trained on | Social media | Hotel/product reviews |
| Output | -1 to +1 | 1–5 stars |
| Context awareness | No ("not great" reads as positive) | Yes |
| Domain match | Low | High |

**Speed optimization:** Rather than scoring all 990k reviews (hours on CPU), we take the **5 most recent reviews per listing** and score those — ~42,436 texts total, covering 9,731 of 9,752 active listings. Each listing's `sentiment_score` is the average BERT score across its top 5 reviews (1–5 scale).

**Result:** Mean sentiment score = **4.57 / 5.0** across active listings.

The 21 listings with no `sentiment_score` had reviews that were too short or blank for BERT to score.

---

## Post-Pipeline Additions (v2 → v6)

After the main pipeline, additional columns were added and fixes applied in separate scripts to avoid re-running the full pipeline:

| Version | Script | Change |
|---|---|---|
| v2 | `fix_column_order.py` | Reordered monthly occupancy columns chronologically (Jan → Dec) |
| v3 | `add_last_scraped.py` | Added `last_scraped` from listings.csv, placed after `id` |
| v4 | `add_columns_v4.py` | Added `host_experience_years`, `rating_accuracy`, `property_type`, `listing_first_review_date`, `listing_last_review_date`. Dropped `host_start_date` (100% null in source) |
| v5 | `build_v5.py` | Renamed `capacity_tier` values from `1-2/3-4/5+` to `small/medium/large` to prevent Excel date conversion. Rebuilt `segment` column accordingly |
| v6 | `build_v6.py` | Added `latitude`, `longitude`, `reviews_last_30d` for spatial analysis and short-term review velocity |

---

## Column Retention Logic

**Kept columns fell into one of three categories:**
1. **Directly needed for the model** — price, occupancy, revenue, review scores, room type, capacity
2. **Needed for segmentation/grouping** — borough, neighborhood, host listings count
3. **Engineered features we built** — host_tier, capacity_tier, segment, amenity flags, calendar occupancy, sentiment, velocity

**Dropped columns and reasons:**

| Category | Examples | Reason |
|---|---|---|
| 100% null | `instant_bookable`, `host_response_rate`, `host_neighbourhood` | No data |
| Operational metadata | `scrape_id`, `source`, `calendar_updated` | No analytical value |
| Redundant | `availability_30/60/90`, `price_quote_*` | Covered by other columns |
| Free text (signal extracted) | `description`, `host_about`, `amenities` | Signal extracted via BERT sentiment and amenity flags |
| Granular host counts | `calculated_host_listings_count_entire_homes` | Collapsed into `host_tier` |
| High null, no backup | `license` (82.5% null) | Not recoverable |

---

## Final Output Summary

**File:** `active_listings_clean_v6.csv`  
**Rows:** 9,752 active listings  
**Columns:** 80  

| Category | Columns |
|---|---|
| Identity & UI | `id`, `host_id`, `listing_name`, `listing_url`, `last_scraped` |
| Location | `borough`, `neighborhood`, `latitude`, `longitude` |
| Property | `room_type`, `property_type`, `max_guests`, `bedrooms`, `beds`, `bathrooms`, `*_imputed` flags |
| Pricing | `nightly_price`, `min_nights`, `max_nights`, `is_monthly_rental` |
| Availability | `days_available_next_365` |
| Reviews | `total_reviews`, `reviews_last_12mo`, `reviews_last_30d`, `reviews_per_month`, `reviews_last_12mo_verified`, `days_since_last_review` |
| Ratings | `rating_overall`, `rating_cleanliness`, `rating_checkin`, `rating_communication`, `rating_location`, `rating_value`, `rating_accuracy` |
| Host | `is_superhost`, `host_total_listings`, `host_experience_years`, `listing_first_review_date`, `listing_last_review_date` |
| Performance | `occupancy_rate`, `estimated_annual_revenue` |
| Engineered | `host_tier`, `capacity_tier`, `segment` |
| Sentiment | `sentiment_score` |
| Amenities (binary) | `has_wifi`, `has_kitchen`, `has_air_conditioning`, `has_dedicated_workspace` + 16 more |
| Calendar Occupancy | `occupancy_Jan` – `occupancy_Dec`, `occupancy_rate_calendar` |

**Remaining nulls (expected):**

| Column | Nulls | Reason |
|---|---|---|
| `host_experience_years` | 196 (2.0%) | Incomplete host profiles in source |
| `is_superhost` | 196 (2.0%) | Same 196 rows as above |
| `sentiment_score` | 21 (0.2%) | No usable review text for BERT |

---

## Column Dictionary

### Identity & UI

| Column | Type | Description | Calculation |
|---|---|---|---|
| `id` | int | Unique Airbnb listing ID | Direct from source |
| `host_id` | int | Unique Airbnb host ID — links all listings owned by the same host | Direct from source |
| `listing_name` | string | Title of the listing as shown on Airbnb (e.g. "Charming 1BR in Williamsburg") | Direct from source (`name`) |
| `listing_url` | string | Direct URL to the live Airbnb listing page | Direct from source |
| `last_scraped` | date | Date this listing was last scraped by Inside Airbnb | Direct from source |

### Location

| Column | Type | Description | Calculation |
|---|---|---|---|
| `borough` | string | NYC borough: Manhattan, Brooklyn, Queens, Bronx, Staten Island | Direct from source (`neighbourhood_group_cleansed`) |
| `neighborhood` | string | Specific neighborhood within the borough (e.g. Williamsburg, Harlem) | Direct from source (`neighbourhood_cleansed`) |
| `latitude` | float | Listing latitude coordinate | Direct from source |
| `longitude` | float | Listing longitude coordinate | Direct from source |

### Property

| Column | Type | Description | Calculation |
|---|---|---|---|
| `room_type` | string | Listing type: Entire home/apt, Private room, Shared room, Hotel room | Direct from source |
| `property_type` | string | More granular property type (e.g. Entire condo, Private room in house) | Direct from source |
| `max_guests` | int | Maximum number of guests the listing accommodates | Direct from source (`accommodates`) |
| `bedrooms` | float | Number of bedrooms. Nulls filled first from `bathrooms_text` parsing, then from median per `max_guests` group | See Step 2 |
| `beds` | float | Number of beds. Nulls filled from median per `max_guests` group | Median imputation by `max_guests` |
| `bathrooms` | float | Number of bathrooms. Nulls filled first from `bathrooms_text` parsing, then median imputation | See Step 2 |
| `bedrooms_imputed` | int (0/1) | Flag: 1 if `bedrooms` was imputed, 0 if observed | `1 if bedrooms was null before imputation` |
| `beds_imputed` | int (0/1) | Flag: 1 if `beds` was imputed, 0 if observed | `1 if beds was null before imputation` |
| `bathrooms_imputed` | int (0/1) | Flag: 1 if `bathrooms` was imputed, 0 if observed | `1 if bathrooms was null before imputation` |

### Pricing & Availability

| Column | Type | Description | Calculation |
|---|---|---|---|
| `nightly_price` | float | Nightly price in USD | Stripped `$` and `,` from raw `price` string, cast to float |
| `min_nights` | int | Minimum consecutive nights required to book | Direct from source (`minimum_nights`) |
| `max_nights` | int | Maximum consecutive nights allowed | Direct from source (`maximum_nights`) |
| `is_monthly_rental` | int (0/1) | Flag: 1 if listing requires 28+ night minimum stay (long-term rental product, not STR) | `1 if min_nights >= 28` |
| `days_available_next_365` | int | Number of days the listing is open for booking in the next 365 days | Direct from source (`availability_365`) |

### Reviews & Ratings

| Column | Type | Description | Calculation |
|---|---|---|---|
| `total_reviews` | int | Total number of reviews all time | Direct from source (`number_of_reviews`) |
| `reviews_last_12mo` | int | Reviews received in the last 12 months (Inside Airbnb pre-computed) | Direct from source (`number_of_reviews_ltm`) |
| `reviews_last_30d` | int | Reviews received in the last 30 days | Direct from source (`number_of_reviews_l30d`) |
| `reviews_per_month` | float | Average reviews per month over the listing's lifetime | Direct from source |
| `reviews_last_12mo_verified` | int | Our independent recount of reviews in the last 12 months from raw `reviews.csv` | `COUNT(review_date >= snapshot_date - 12 months)` per listing |
| `days_since_last_review` | int | Days between snapshot date (June 14, 2026) and most recent review — proxy for listing freshness | `snapshot_date - MAX(review_date)` per listing |
| `rating_overall` | float | Overall guest star rating (out of 5) | Direct from source (`review_scores_rating`) |
| `rating_cleanliness` | float | Cleanliness sub-score (out of 5) | Direct from source (`review_scores_cleanliness`) |
| `rating_checkin` | float | Check-in experience sub-score (out of 5) | Direct from source (`review_scores_checkin`) |
| `rating_communication` | float | Host communication sub-score (out of 5) | Direct from source (`review_scores_communication`) |
| `rating_location` | float | Location sub-score (out of 5) | Direct from source (`review_scores_location`) |
| `rating_value` | float | Value-for-money sub-score (out of 5) | Direct from source (`review_scores_value`) |
| `rating_accuracy` | float | Listing accuracy sub-score (out of 5) — measures whether the listing matched its description | Direct from source (`review_scores_accuracy`) |

### Host

| Column | Type | Description | Calculation |
|---|---|---|---|
| `is_superhost` | bool (t/f) | Whether the host holds Airbnb Superhost status | Direct from source (`host_is_superhost`) |
| `host_total_listings` | int | Total number of listings this host manages on Airbnb | Direct from source (`calculated_host_listings_count`) |
| `host_experience_years` | float | Number of years the host has been hosting on Airbnb | Direct from source (`hosts_time_as_host_years`) |
| `listing_first_review_date` | date | Date of the listing's first ever review — proxy for listing age | Direct from source (`first_review`) |
| `listing_last_review_date` | date | Date of the listing's most recent review | Direct from source (`last_review`) |

### Performance

| Column | Type | Description | Calculation |
|---|---|---|---|
| `occupancy_rate` | float | Inside Airbnb's pre-computed occupancy rate for the past 365 days, estimated using review frequency as a booking proxy | Direct from source (`estimated_occupancy_l365d`) |
| `estimated_annual_revenue` | float | Inside Airbnb's estimated trailing 12-month revenue in USD (`nightly_price × occupied_nights`) | Direct from source (`estimated_revenue_l365d`) |

### Engineered Features

| Column | Type | Description | Calculation |
|---|---|---|---|
| `host_tier` | string | Host scale classification based on total listings managed | `Individual` if host_total_listings=1, `Small-Multi` if 2–5, `Mid-Multi` if 6–20, `Enterprise` if 20+  |
| `capacity_tier` | string | Size class of the listing based on max guests | `small` if max_guests ≤ 2, `medium` if 3–4, `large` if 5+ |
| `segment` | string | Matched comparison group key combining borough, room type, and capacity tier | `borough + " \| " + room_type + " \| " + capacity_tier` |

### Sentiment

| Column | Type | Description | Calculation |
|---|---|---|---|
| `sentiment_score` | float (1–5) | Average BERT sentiment score from the listing's 5 most recent reviews. Produced by `nlptown/bert-base-multilingual-uncased-sentiment`, a model fine-tuned on hotel and product reviews | Average of up to 5 BERT scores, each on a 1–5 scale |

### Amenity Flags (Binary)

All amenity columns follow the pattern `has_<amenity>`. Value is `1` if the listing includes that amenity, `0` if not. Derived by parsing the raw `amenities` JSON list column and selecting the top 20 most frequent amenities across all active listings.

| Column | Description |
|---|---|
| `has_smoke_alarm` | Has a smoke alarm |
| `has_wifi` | Has wifi |
| `has_carbon_monoxide_alarm` | Has a carbon monoxide alarm |
| `has_hot_water` | Has hot water |
| `has_hangers` | Has hangers |
| `has_kitchen` | Has a kitchen |
| `has_bed_linens` | Has bed linens provided |
| `has_hair_dryer` | Has a hair dryer |
| `has_iron` | Has an iron |
| `has_essentials` | Has essentials (towels, soap, toilet paper) |
| `has_dishes_and_silverware` | Has dishes and silverware |
| `has_microwave` | Has a microwave |
| `has_refrigerator` | Has a refrigerator |
| `has_cooking_basics` | Has cooking basics (pots, pans, oil, salt) |
| `has_dedicated_workspace` | Has a dedicated workspace (desk/table) |
| `has_air_conditioning` | Has air conditioning |
| `has_shampoo` | Has shampoo provided |
| `has_heating` | Has heating |
| `has_self_check_in` | Supports self check-in (lockbox, keypad, etc.) |
| `has_fire_extinguisher` | Has a fire extinguisher |

### Calendar Occupancy

Computed from raw `calendar (1).csv` by counting days marked `f` (unavailable) per listing per month. Note: `f` includes both guest bookings and host-blocked dates — these cannot be distinguished.

| Column | Type | Description | Calculation |
|---|---|---|---|
| `occupancy_Jan` – `occupancy_Dec` | float (0–1) | Fraction of days in that calendar month marked as unavailable | `COUNT(available='f') / total_days` for that month per listing |
| `occupancy_rate_calendar` | float (0–1) | Overall fraction of all 365 calendar days marked as unavailable | `COUNT(available='f') / 365` per listing |
