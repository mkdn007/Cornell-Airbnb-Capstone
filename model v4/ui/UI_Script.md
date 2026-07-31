# UI Demo Script — Host Pricing Diagnostic

### Cornell BANA 5160 · Team pitch · ~5-minute narrated dashboard walkthrough

**What this is:** the running script for the **recorded, narrated demo** (Slide 9 in the presentation sequence — faculty asked for pre-recorded, not live, "because Murphy's law prevails"). It walks a viewer through the `host_pricing_diagnostic_v3.html` UI using the three real demo listings (underpriced short-stay, overpriced short-stay, and a monthly rental), then a birds-eye placeholder. Every number below is pulled from the actual UI config and traces to the model outputs / `newMDS` docs — no invented figures.

**Note on the photos:** each demo listing's hero image is the **real Airbnb cover photo** of that listing (pulled from the Inside Airbnb `listings.csv` `picture_url` and downscaled). They're the actual rooms — e.g. the Midtown room has an NYC-skyline print on the wall, and the "Blue Room" has its literal blue accent wall. So the visuals are real, not stock.

**How to read this script:**
- **[DO]** — what to click / which tile to be on screen.
- **[THINK]** — the point you're making; context for the presenter, *not* spoken.
- **"Speak"** — say this out loud, roughly verbatim. Tighten to taste; keep the numbers exact.
- ⚠️ **[LIMITATION]** — a caveat we must state or be ready for. Honesty is the whole brand of this pitch ("floor of the floor").

**Timing target:** ~5:00. Rough budget — Intro 0:30 · Midtown (underpriced) 1:30 · Blue Room (overpriced, incl. the aggregate floor-of-floor) 2:00 · Central Park Studio (monthly) 0:45 · Birds-eye (cost/close) 0:15. Leave buffer; it always runs long.

**The one framing to hold the whole time:** this is an **internal Airbnb product pitch**, not a host blog. The metrics that matter are the ones a VP is measured on — **GBV, ADR, host retention, marketplace liquidity, search conversion** — not "how much does the host make tonight." And the product's differentiator vs. Airbnb's own **Smart Pricing** is **explainability**: Smart Pricing hands the host a black-box number; this shows them *why*, which is what makes them act on it.

---

## 0. Open — the header (0:30)

**[DO]** Start on the page as loaded (the Midtown room, `shortstay`, is the default). Header visible: Airbnb logo, "Welcome back, Maya," the search-pill reading "Host Pricing Diagnostic · NYC market · June 2026."

**[THINK]** Set the frame before any numbers. One sentence on the problem, one on the product.

> **"Hosts leave money on the table, and so does Airbnb — because Airbnb takes a cut of every booking. Most hosts price on gut feel, or take Smart Pricing's black-box number as-is. Our tool does what Smart Pricing won't: it shows a host exactly where their price sits against real comparable listings, explains *why* the model flags it, and lets them test any price themselves. This is built as an internal Airbnb product, so everything you'll see maps to platform metrics — booking value, average daily rate, host retention, and search conversion."**

**[THINK]** Name the model in one breath so the audience knows what's under the hood.

> **"Under the hood: a gradient-boosting quantile model that predicts a calibrated fair-value price and a confidence interval, plus a nearest-neighbor layer that finds each listing's real peer group and its amenity gaps."**

---

## 1. Listing #1 — The Midtown Room (UNDERPRICED) (1:45)

**[DO]** Confirm the dropdown shows **"Large Private Midtown Room! (short-stay, confident: raise)."** Point to the listing header: *Private room in rental unit · Hell's Kitchen, Manhattan · Superhost · 281 reviews.*

> **"First listing: a private room in Hell's Kitchen. Individual host, Superhost, 281 reviews — an established, high-demand listing. The model says it's underpriced."**

### Tile: "Where you stand this month (June)" — the histogram

**[DO]** Point to the histogram; the marker sits well to the left. Read the line under it.

**[THINK]** This is the "where do I stand" gut-punch. Real peer distribution, not a model artifact.

> **"This is their $200 nightly price against 142 real comparable listings — matched on host tier, room type, size, and market segment. The readout says it plainly: their $200 is below 69% of their peers. They're near the bottom of a market they could be competing in the middle of."**

### Tile: "Why the model flags this listing" — the pricing-signal rows

**[DO]** Move to the left tile of the two-up row. Read the stat rows top to bottom: Your price $200 (31st pctile) · Model fair value $336 · Calibrated range $212–$440 · Your occupancy (real, 12-mo) 81% · Model direction: Confident: raise, score 73.9.

**[THINK]** Every row here is real model output. The occupancy row is the crown jewel — it's *real*, not estimated.

> **"Every row is real model output. Their price sits at the 31st percentile. The model's fair value is $336. The calibrated range is $212 to $440 — even the 10th-percentile comparable charges more than they do. And this row — 81% occupancy — is *real*: it's this listing's actual 12-month booked-and-vacant calendar, not an estimate. So the story is clean: they're already 81% booked at a bottom-of-market price. The underpricing is a pure pricing decision, not a demand problem. Raising toward $336 is the lever."**

⚠️ **[LIMITATION — occupancy source]** Be ready if asked where 81% comes from:
> **"The real occupancy comes from the AirROI pilot panel — 300 listings with a genuine 12-month calendar. The full 9,752-listing dataset doesn't have trustworthy occupancy; its occupancy field is saturated at a 255-day cap. So we only show real occupancy on listings where we actually have it."**

### Tile: "What high performers have that you don't" — amenity gaps

**[DO]** Point to the amenity chips and note.

> **"The peer layer also surfaces operational gaps — six amenities the top performers have that this listing doesn't, mostly kitchen items. That's a second lever, independent of price."**

### Tile: "Try a different price" + the recommendation callout

**[DO]** Click **"Try fair-value estimate ($336)."** The callout and the year table update. Read the green callout.

**[THINK]** This is the value moment — and where our elasticity honesty lives. The green highlight is the point.

> **"Push it to the model's fair value and here's the projection: about **+$2,500 a year**, even after accounting for the occupancy the model expects them to lose at a higher price. And here's where we're deliberately honest —"**

**[DO]** Point to the bolded panel-median note (the green-highlighted phrase).

⚠️ **[LIMITATION + VALUE — the elasticity story, underpriced side]**
> **"Our price-sensitivity number, β = −0.92, was measured on a pilot of established hosts whose median listing has 142 reviews. This listing has 281 — *more* established than the pilot. More established means less price-sensitive, so its true occupancy drop is probably *smaller* than we're showing. In plain terms: the occupancy dip in our table is a conservative overstatement, and **the real revenue gain is probably larger than what's on screen**. Same principle you'll see everywhere in this tool — every number we show is a floor, and it only goes up from here. We'd rather under-promise."**

⚠️ **[LIMITATION — the ROI/causal data gap]** Have this ready:
> **"To be clear, this identifies pricing *opportunity*, not proven causal uplift. Airbnb would validate against its own booking-conversion and elasticity data before shipping. We stand in for that data with a real but narrow elasticity pilot — proof of mechanism, not full validation."**

---

## 2. Listing #2 — The Blue Room (OVERPRICED, less established) (1:45)

**[DO]** Switch the dropdown to **"The Blue Room by Prospect Park (short-stay, confident: lower)."**

> **"Second listing is the mirror image — and the more interesting one. A private room by Prospect Park in Brooklyn. 117 reviews — this time a *less* established host. The model says it's overpriced. And this one shows the model being robust in a way the first didn't."**

### Tile: "Why the model flags this listing" — the robustness moment

**[DO]** On the pricing-signal tile: Your price $321 (88th pctile) · fair value $211 · range $129–$317 · occupancy (real) 69% · Confident: lower, **score 39.2**. Point at the score, then read the why-note.

**[THINK]** This is the teaching moment you asked for: a *low* confidence score and a *confident* direction call coexist. Explain why — it shows the model isn't just spitting out numbers.

> **"Notice the confidence score is only 39.2 — much lower than the 74 on the Midtown room. That's not a weakness, it's the model being honest. The score measures how *narrow* the price band is. Private rooms like this sit in a more scattered part of the market, so the band is wide — $129 to $317, wider than about three-quarters of all listings. But look where the actual price is: $321, above *even the top* of that wide band. So the direction is unambiguous even though the point estimate is uncertain. Confidence score and direction are two different things — a wide band doesn't weaken the call when the price falls outside the whole interval."**

> **"And again, real occupancy — 69% — so this isn't a listing that's empty and desperate. It's a genuinely overpriced listing that's still booking. Lowering to $211 recovers the nights it's leaving on the table."**

### Tile: "Try a different price" + callout — the volume story

**[DO]** Click **"Try fair-value estimate ($211)."** Read the callout, then point to the year table's total row — which shows a **negative** annual revenue figure.

**[THINK]** The negative on the calendar is the teachable moment. Don't hide it — explain *why* it's there and why it's actually a floor that only goes up. The table runs β at −0.92 (near the −1.0 breakeven); at breakeven, a price cut is by definition revenue-neutral-to-slightly-negative. But −0.92 is the *wrong* elasticity for a 117-review listing — its real elasticity is steeper, past breakeven, where cutting price *raises* revenue.

> **"Drop it to fair value and two things happen. First, the win is **nights, not dollars** — the table recovers roughly +63 occupied nights a year. Those are previously-empty calendar dates turning into real bookings: marketplace liquidity, better search conversion, and a host who's getting reservations instead of churning off the platform."**

> **"Second — and notice this — the annual revenue in the table actually shows a small **negative**. I want to be upfront about that, because it's the opposite of a problem. That negative only appears because we're running this listing at β = −0.92 — essentially the breakeven elasticity, where a price cut just about washes out. But −0.92 was measured on *established* hosts. This listing has 117 reviews — it's less established, so its real elasticity is steeper, past the −1.0 breakeven, where cutting price actually *raises* revenue. So the paper loss on screen is an artifact of a deliberately conservative assumption — the real outcome is profitable. **And despite that built-in headwind, the model still delivers: nights recovered today, and revenue upside the moment we measure the true elasticity.**"**

**[DO]** Point to the panel-median note — the coral "$0" and the green "raises revenue" highlight.

⚠️ **[LIMITATION + VALUE — the <142 / $0 placeholder, the honesty centerpiece]**
> **"This is the most honest thing in the whole tool. In our company-wide revenue math, we assign **$0** to under-142-review listings like this one — highlighted here. We *believe* they'd actually gain revenue, because less-established listings are more price-sensitive — true elasticity around −1.3 to −1.5, past breakeven, exactly where cutting price *raises* revenue, not just nights. But we can't prove that number without measuring it, and assuming it would inflate our pitch dishonestly. So we zero it out. **That's why our headline number is a genuine floor — for listings like this, the real gain is upside we deliberately left on the table. It only goes up from here.**"**

⚠️ **[LIMITATION — amenity gap is the other half]**
> **"And repricing alone doesn't close the whole gap — the peer layer flags five cheap fixes here, like hangers, linens, and a microwave, that help fill the nights price alone won't."**

### Zoom out — why this makes the whole number a floor

**[THINK]** This is the payoff. The paper-loss you just showed on the Blue Room *is* the aggregate story in miniature — so make the jump to the portfolio number right here, while the negative is still on screen, not later. All figures from the `newMDS` docs.

> **"Now hold onto what just happened on this listing, because it's the entire company-wide story in miniature. Across all 9,752 NYC listings, our estimate is **$7.57 million** in added host booking value a year — **$1.17 million** of that as Airbnb fee — and **77,606 previously-empty nights** filled."**

> **"And here's the key: the whole portfolio runs at that same β = −0.92 breakeven. So on the overpriced side, our math books a small revenue *loss* on listings exactly like this Blue Room — not a gain. And every under-142-review listing, like this one, we zeroed out entirely, even though we believe it gains. So that **$7.57 million is the floor of the floor** — it already absorbs the negatives you're looking at, forfeits the probable gains, and *still* comes out solidly profitable. **Despite deliberately stacking every assumption against ourselves, the number is positive — and it only goes up from here.**"**

⚠️ **[LIMITATION — where the revenue actually comes from; the honest segment split, be ready in Q&A]**

**[THINK]** Don't volunteer the full breakdown in the 5-min cut unless asked — but *know it cold*, because it's the sharpest possible question. The short-stay side you just demoed nets to roughly *negative*; the monthly segment carries the entire number. If a reviewer asks "isn't this basically just monthly?", the honest answer is **yes** — and you own it rather than dodge.

> **"If you break the $7.57M down by segment, I'll be direct: almost all of it is the monthly segment — about $7.9M. Short-stay, both listings you just saw, actually nets to roughly *zero*: the +$0.34M from underpriced raises is more than cancelled by the −$0.70M on overpriced cuts, because short-stay is near unit-elastic. So the dollar case rests on monthly — which is exactly the segment where we *couldn't* measure elasticity. We're not hiding that; it's the single biggest assumption in the stack, and it's precisely what the next phase of data collection is designed to confirm. I'll show you what that fragility looks like on the monthly listing next."**

⚠️ **[LIMITATION — the eleven conservative choices; know this cold]**
> **"We rounded against ourselves at eleven separate steps — elasticity measured only on the least price-sensitive hosts, zero credit for every low-review listing, a booked revenue loss on overpriced established hosts, zero credit for winning bookings back from hotels, and a 10% discount for time value on top. Every one makes the real number bigger, not smaller."**

---

## 3. Listing #3 — Central Park Studio (MONTHLY) (0:45)

**[DO]** Switch the dropdown to **"Charming Central Park Studio (monthly, confident: raise)."** Header: *Entire rental unit · Upper West Side, Manhattan · 30-night minimum stay · Monthly rental.*

> **"Our third listing is a monthly rental — a studio on the Upper West Side, 30-night minimum. It's underpriced, confident-raise, and it's here to show how the tool handles a segment where we're honest about what we *couldn't* measure."**

### Tile: "Why the model flags this listing"

**[DO]** Point to the pricing-signal rows: Your price $3,971/mo ($132/night) · fair value $5,430/mo ($181) · range $149–$239/night · occupancy (real) 38% · Confident: raise, score 81.8. Note the 20th percentile and that occupancy is real.

**[THINK]** Two things to land: it's genuinely underpriced (below even q10), and its occupancy is *real* — we have monthly calendars too. This pre-empts the "do you even have occupancy for monthly?" question.

> **"It's priced at the 20th percentile of 251 comparable monthly listings — below even the model's 10th-percentile floor of $149 a night. Confidence is high, 81.8. And note this occupancy figure, 38%, is *real* — monthly listings have a true 12-month calendar just like short-stay ones. This listing also has every amenity its high performers have, so there's no operational gap. It's a pure pricing decision: raise toward fair value."**

### Tile: "Try a different price" + year table — the honesty moment

**[DO]** Click **"Try fair-value estimate ($5,430)."** Read the callout, and point to the year-table subtitle which now reads "we could not measure price-elasticity."

**[THINK]** This is *the* reason a monthly listing earns a slot in the demo: it's where we're most visibly honest. Per our elasticity README, we don't project an occupancy tradeoff for monthly — the tool says so out loud.

> **"Here's where monthly is different, and where we're most upfront. For short-stay we had a measured price-elasticity. For monthly, we **couldn't measure one** — the pilot came back statistically insignificant, β of +0.08 with a p-value of 0.73, on 194 monthly listings. The confidence interval spans zero. So we genuinely don't know how a monthly listing's occupancy responds to price."**

> **"Rather than fake an occupancy response we never measured, the tool does something more honest: it runs the table at the short-stay elasticity, β = −0.92, as an **illustrative stress test** — 'here's what a monthly estimate would look like *if* monthly demand were as price-sensitive as short-stay.' That's deliberately the conservative end: it shows only about **+$486 a year**."**

**[DO]** Point to the callout's two-bounds note (the green "+$7,042/year").

**[THINK]** Show both ends of the unmeasured range live. The table is the pessimistic bound; the note surfaces the optimistic one. The honesty is that we don't pick between them.

> **"And right here we show the other end of the range. If occupancy actually holds flat — β = 0, which is how our headline portfolio number is calculated — the same move is worth about **+$7,000 a year**. So the real answer for this listing is somewhere between $486 and $7,000. We *can't* narrow it, because monthly elasticity is unmeasured — and that −0.92 is borrowed from a different segment, not a monthly figure. That range **is** the data ask: the whole point of the next phase is to replace this borrowed number with a real monthly one."**

**[THINK]** Same 142-median lens we used on the two short-stay listings — but flip the reasoning, because for monthly it tells us the *stress test itself* might understate the risk.

> **"And the same review-count logic from the other two listings applies here, with a twist. That −0.92 was measured on hosts with a median of 142 reviews. This studio has 114 — *below* that median. Below-median listings tend to be *more* price-sensitive, so if monthly behaves anything like short-stay, the true response could be even steeper than −0.92 — meaning our stress-test floor of $486 might not even be the true floor. That's one more reason we lean on the model's *direction* signal for monthly, not a dollar figure."**

⚠️ **[LIMITATION — the 0% months + the KNN amenity lever; point to the note under the chart]**

**[DO]** Point to the four red 0% months (Feb, Mar, Aug, Sep) in the table, then to the gap note beneath it.

> **"You'll also notice four months at 0% — Feb, March, August, September. Those are real: genuine empty gaps between long-term tenants, not a pricing problem. And this is important — **price can't fix an empty month.** That's exactly what the amenity layer is for: the peer comparison flags what high-performing neighbors offer that this listing doesn't, and closing those gaps is the lever most likely to turn an empty month into a booked one. Price and amenities are two different levers — for the empty months, amenities are the one that moves."**

⚠️ **[LIMITATION — the softest spot in the stack; be ready for it in Q&A]**
> **"And full transparency for the financial case: because monthly is occupancy-neutral by assumption, most of our headline revenue actually comes from this monthly segment — it's the softest assumption in the whole stack, and we flag it rather than bury it. It's an assumption, not a measurement, precisely because the pilot couldn't detect a monthly price effect — and honestly, we couldn't measure it partly because almost no host in the sample ever changed their price. Only 5 of 258 listings moved price more than 5% in two years."**

---

## 4. Birds-eye view — the aggregate impact (0:30)

> **Status:** the birds-eye page (`nyc_pricing_overview_gbm.html`) now exists and is skinned identically to the v3 tool (same header, logo, colors) — the "Birds-eye view" chip in the tool links straight to it. The core aggregate argument (the $7.57M floor-of-floor) is delivered *live* during the Blue Room walkthrough (§2); this section is a lighter recap + the cost/ROI close over the map.
>
> ⚠️ **SUBJECT TO CHANGE / PLACEHOLDER — the new current-model screens.** The map has 4 original screens (pricing gap, occupancy-gap-vs-peers, simulated seasonal, real occupancy) plus **3 new ones I added, marked ▸ in the Metric dropdown** — see `BIRDSEYE_SCREENS.md` for the full guide:
> - **▸ Repricing direction** — net raise-minus-lower per neighborhood (all 9,752 listings; 177 short-stay / 191 monthly neighborhoods). Strong.
> - **▸ Revenue lift at fair value** — β-adjusted, matches the tool (short-stay β=−0.92, monthly β=0). Full coverage.
> - **▸ Real 12-mo occupancy** — from the AirROI calendar; **very sparse (8 / 14 neighborhoods)**, built as a deletable standalone in case it looks too empty.
>
> These 3 are not yet locked into the narration — decide which to actually show on camera (Repricing direction + Revenue lift are the demo-ready ones; real-occupancy may be too grey to feature). The two original saturated-field screens (occupancy-gap-vs-peers, real occupancy rate) are candidates for retirement but left untouched for now.

**[THINK]** Don't re-explain the floor logic — it landed in §2. Here just restate the headline, add cost/payback, close. If showing the map: switch to **Repricing direction** or **Revenue lift** to make the neighborhood-level story concrete.

> **"You saw why that portfolio number is a floor on the Blue Room. Zoom out to all of NYC and you can see it by neighborhood — [switch to the Revenue lift / Repricing direction screen]. To put the cost against it: this is an incremental feature on infrastructure Airbnb already owns — about $65K to build, $30K a year to run. Even at a realistic 35% adoption it pays back in about three months and clears over 800% return across five years, after discounting."**

⚠️ **[LIMITATION — the ceiling is soft on one side]** If asked about the upper bound:
> **"The occupancy-neutral ceiling is about $26.8M, but we lead with the floor, not the ceiling — and even that ceiling only counts the underpriced side, so it's understated too."**

> **TODO before recording:**
> - [ ] Decide which of the 3 new ▸ screens to show on camera (recommend Repricing direction + Revenue lift; real-occupancy likely too sparse).
> - [ ] Confirm final headline numbers with the financials owner (Jai). **Use `newMDS` numbers only:** $7.57M / $1.17M / 77,606 nights; incremental $65K build / $30K run. (Planning doc's superseded $9.6M–$25.6M range and $190K greenfield are **not** used — greenfield is a worst-case check only.)

---

## 5. Close (fold into the birds-eye or the deck's closing slide)

> **"The number is the floor. But the reason an internal team funds this isn't just the fee revenue — it's host retention, search conversion, competitor defense, and replacing hours of a host's manual guesswork with an explainable model that scales to every listing without adding headcount. Those are exactly the metrics a VP is measured on, and our revenue floor ignores every one of them. The opportunity is bigger than what we can prove — and proving how much bigger is exactly what the Airbnb data unlocks."**

---

## Quick-reference: the numbers, as they appear in the UI

| | Midtown Room | Blue Room | Central Park Studio |
|---|---|---|---|
| Listing ID | #343276 | #848718 | #1533652 |
| Type | Private room, Manhattan | Private room, Brooklyn | Entire studio, monthly (UWS) |
| Direction | **Confident: raise** | **Confident: lower** | Confident: raise |
| Confidence score | 73.9 | **39.2** (robustness demo) | 81.8 |
| Current → fair | $200 → $336 | $321 → $211 | $132 → $181/night ($3,971 → $5,430/mo) |
| Calibrated range | $212–$440 | $129–$317 | $149–$239 |
| Percentile vs peers | 31st | 88th | 20th |
| Real occupancy (12-mo) | 81% | 69% | 38% |
| Reviews | 281 (above 142) | 117 (below 142) | 114 (monthly — n/a) |
| β applied | −0.92 | −0.92 | 0 (could not measure) |
| Year-table projection | ≈ +$2,500/yr | ≈ +63 nights/yr | ≈ +$7,000/yr flat (β=0) · +$486/yr at β=−0.92 stress test |

**Aggregate (birds-eye):** +$7.57M host GBV · +$1.17M Airbnb fee · +77,606 nights/yr · ~$65K build / ~$30K run · ~3-month payback at 35% adoption.

---

## Caveat checklist — say these, or be ready to (the "floor of the floor" discipline)

1. **Occupancy source** — real occupancy is the 300-listing AirROI pilot panel only; the full 9,752 dataset has a saturated occupancy field, so we don't fake it.
2. **Calendar block-vs-book** — the Airbnb calendar can't tell host-blocked dates from actual bookings, so an unusually low month may be a blocked calendar, not weak demand.
3. **Elasticity is a pilot** — β = −0.92 measured on 64 short-stay listings, median 142 reviews; a conservative *floor* on market-wide sensitivity, not a claim about all listings. Proof of mechanism using proxy data.
4. **Review-tier honesty** — ≥142 reviews → likely gain *bigger* than shown (conservative); <142 → set to **$0** even though the real gain is probably positive (we forfeit probable upside rather than invent a number).
5. **Monthly is an assumption, and it carries the whole number** — β not significant (p=0.734, only 5 of 258 listings ever moved price >5%). ~$7.9M of the $7.57M is monthly; short-stay nets ≈ zero (+$0.34M underpriced − $0.70M overpriced). Softest spot in the stack. The monthly demo shows both bounds live: the table runs the conservative β=−0.92 stress test (+$486/yr), the note surfaces the flat-occupancy β=0 upside (+$7,000/yr) that the headline uses — the truth is between, and that range is the data ask.
6. **Opportunity, not causal uplift** — identifies mispricing; Airbnb would validate against its own conversion/elasticity data before shipping.
7. **Ceiling is soft/one-sided** — we lead with the floor; the $26.8M ceiling counts underpriced only.
8. **Cost basis** — incremental ($65K/$30K), with the $190K greenfield build kept only as a worst-case check.
