# DOCUMENT: ELASTICITY → REVENUE JOURNEY

## Elasticity review

Ok prepare yourself for a long haul because this is going to get complicated and intense, but by the end of this document you will understand **how we got the elasticity to map to revenue.**

I think the first step is to understand our elasticities on a number line.

```
 -2+          -1          -0.92          0
  |            |            |            |
◄──────── ELASTIC ─────────────── INELASTIC ──────►
```

Elasticity is just how sensitive people's demand is to a price difference. Our model predicts that for **every 1% increase in price, there is a 0.92% decrease in occupancy.**

We got this from running:

> Bootstrap 95% CI | [−1.30, −0.54] | 100 resamples by listing → **−0.92 was the average.**

This was only found on a small sample dataset of **short-term stay** listings that had a **median (established) status — review count of 142.**

That brings me to the next point.

```
 -2+          -1          -0.92          0
  |            |            |            |
◄──────── ELASTIC ─────────────── INELASTIC ──────►
  <<142      <142          142         >142
  reviews    reviews      reviews      reviews
```

The range falls in between these elasticities. **The more established a listing, the less resistant to demand people are** — thus affecting the change in revenue.

The difference between *change in revenue* and *revenue* is this: a 5-review listing that's underpriced might move its price to fair value, but because it's so elastic (probably more than −1) it would be a net **negative change in revenue** — even if total revenue is still positive. This is why our model captures reviews as a feature to try to give a lower fair price to these listings — but still not 100%.

This is why the true change in revenue that we care about lives here:

```
              -1          -0.92          0
               |            |            |
             <142         142          >142
             reviews      reviews       reviews
```

## How to tie it with the numbers?

We can do this by looking at examples from the dataset.

Let's start with an underpriced listing first, because that's the easiest to understand I think.

---

## Underpriced Scenario

When looking at examples we have to **always compare against the 142-review benchmark.** That way we can apply the −0.92 elasticity and see how much more/less revenue we could expect. This will make sense below.

```
              -1          -0.92          0
               |            |            |
             <142         142        EXAMPLE
             reviews      reviews    >142 reviews
```

This example pulls a confident underpriced candidate according to our quantile ranges in the GBM model.

### Real Example — Spacious Clinton Hill Apt, Brooklyn

**Model confidence:** Confident: raise price — score 98.9
**Calibrated GBM interval:** [$274, $399] — actual price $244 sits **below the bottom**

```
┌─────────────────────────────────────────────────────────────────────────┐
│   UNDERPRICED LISTING — GBM Quantile Regression, 98.9% Confidence      │
├──────────────────────────────────────┬──────────────────────────────────┤
│ Status Quo (Underpriced)             │ Re-priced to Fair Value          │
├──────────────────────────────────────┼──────────────────────────────────┤
│ Nightly Rate:       $244/night       │ Nightly Rate:    $336/night (+38%)│
│ Booked Nights:   21.3 nights/mo     │ Booked Nights: ~15.8 nights/mo*  │
│ GBV:              $5,189/mo         │ GBV:             $5,324/mo (+2.6%)│
│ Host Earnings (−3%): $5,034/mo      │ Host Earnings:   $5,164/mo       │
│ Airbnb Take (15.5%): $804/mo        │ Airbnb Take:     $825/mo         │
└──────────────────────────────────────┴──────────────────────────────────┘
* Occupancy-adjusted using β = −0.92 (short-stay TWFE pilot, n=64).
```

**So what happened here?**

This listing has **541 reviews** — significantly above the panel median. Established listings with high review counts have more guest loyalty and face *less* price-sensitive demand than a typical listing. A listing with 541 reviews is arguably more established than the already-established panel average. The true elasticity for this listing is likely **less negative** than −0.92 — probably around −0.4. Meaning booked nights wouldn't decrease as much and we could make even more revenue.

So now we have a conservative floor. BUT —

That makes sense, and if we were to look at a **<142-review listing**, there might be some optimization possible if the elasticity is anywhere from −1 to −0.92. However, if we just apply −0.92 to everything <142 we are **inflating the revenue lift and this is not honest.**

In order to not purposely inflate all <142-review listings with a better-than-reality scenario, I wanted to segment this better.

Anything less than <142 reviews we would just assume **$0 revenue lift** as a worst-case scenario — or **−1 breakeven elasticity** (even though this isn't plausible, as there's opportunity from −0.99 to −0.92). But this is also to offset the chance that anything less than −1 elasticity would be a *negative* change in revenue. So this splits the difference and makes us even.

Now that we have realism, a floor, and a ceiling (occupancy-neutral, or elasticity = 0 so max price), let's calculate the true band for underpriced short stays:

| Scenario                              | SS ≥142   | SS <142   | Monthly   | Total       |
|---------------------------------------|-----------|-----------|-----------|-------------|
| **Ceiling** (β=0, no occ. response)   | —         | —         | —         | **~$26.8M** |
| **Segmented estimate** (symmetric β)  | +$0.34M   | ~$0       | +$7.94M   | **$8.27M**  |
| **Floor** (all SS at breakeven)       | ~$0       | ~$0       | +$7.94M   | **~$7.9M**  |

> **Note on the segmented estimate:** notice the short-stay side contributes almost nothing (+$0.34M) — the whole underpriced revenue number is really the **monthly segment (+$7.94M).** That's because monthly elasticity came back statistically insignificant (β = +0.084, p = 0.734), so we keep it occupancy-neutral. If a professor asks "isn't your revenue basically just the monthly listings?" the honest answer is yes — and the reason is that short-stay demand is near unit-elastic, so raising an underpriced short-stay listing to fair value barely nets anything after the occupancy drop.

Ok beautiful. But what about overpriced listings, you ask? Bro stfu.

---

## Overpriced Scenario

Again, when looking at examples we have to **always compare against the 142-review benchmark.** That way we can apply the −0.92 elasticity and see how much more/less revenue we could expect. This will make sense below.

```
              -1          -0.92          0
               |            |            |
           EXAMPLE         142          >142
       48 reviews <142   reviews       reviews
```

### Real Example — The GuestHouse Brooklyn, Flatlands

**Model confidence:** Confident: lower price — score 93.9
**Calibrated GBM interval:** [$311, $557] — actual price $563 sits **above the top**

```
┌─────────────────────────────────────────────────────────────────────────┐
│   OVERPRICED LISTING — GBM Quantile Regression, 93.9% Confidence       │
├──────────────────────────────────────┬──────────────────────────────────┤
│ Status Quo (Overpriced)              │ Re-priced to Fair Value          │
├──────────────────────────────────────┼──────────────────────────────────┤
│ Nightly Rate:       $563/night       │ Nightly Rate:    $470/night (−16%)│
│ Booked Nights:    16.0 nights/mo    │ Booked Nights:  18.9 nights/mo   │
│ GBV:              $9,008/mo         │ GBV:             $8,879/mo (−1.4%)│
│ Host Earnings (−3%): $8,738/mo      │ Host Earnings:   $8,612/mo       │
│ Airbnb Take (15.5%): $1,396/mo      │ Airbnb Take:     $1,376/mo       │
└──────────────────────────────────────┴──────────────────────────────────┘
Based on β = −0.92: (470/563)^(−0.92) = 1.181 → +18.1% occupancy
```

**So what happened here?**

This listing has **48 reviews** — *below* the panel median of 142. A listing with fewer reviews has less accumulated guest loyalty and faces *more* price-sensitive demand than the already-established panel — probably like −1.5 or so elasticity. The true elasticity for this listing is likely **more negative** than −0.92.

This means the occupancy recovery from repricing is probably *larger* than the +18.1% shown in the table.

But here's where overpriced gets weird and you have to pay attention.

### The revenue flip

Look at the table again. The price dropped 16%, occupancy went up 18%, and yet GBV **fell** by −1.4%. The host made slightly less money. What?

This is the whole game. When you *cut* a price, you only make more revenue if demand is elastic enough to overcome the lower rate. The exact breakeven is **elasticity = −1.0:**

```
 -2+         -1.0          -0.92           0
  |            |             |             |
 cut price   BREAKEVEN     cut price     cut price
 = MORE $    = $0 change   = LESS $       = way LESS $
```

Our measured −0.92 sits just *above* the breakeven line. So at −0.92, cutting price is barely revenue-negative — the extra bookings *almost*, but not quite, make up for the lower rate. That's why the GuestHouse listing loses $129/mo even though it fills 3 more nights.

**So can overpriced ever make money? Yes — but only past −1.0.**

That 48-review listing is probably at −1.5, which is past breakeven. So in reality it likely *gains* revenue when it drops to fair value. But — and this is the same trap as underpriced — we measured −0.92 on established hosts only. We never measured the elastic newbies. If we just assume −1.5 to book a fat revenue number, a professor asks "where'd that come from?" and we're cooked.

### Same segmentation trick as underpriced

- **≥142 reviews:** apply the measured −0.92. This *loses* a little revenue (−$0.70M), because established hosts are inelastic and cutting their price just leaves money on the table. For them the win is nights recovered, not dollars.
- **<142 reviews:** set them to breakeven (−1.0 = $0 change). We *believe* they'd actually gain revenue (they're probably −1.3 to −1.5), but assuming that inflates the number dishonestly. So we set it to $0.

And here's the key difference from underpriced — the direction of the "make us even" logic is flipped. On the underpriced side, $0 splits an *even* bet (upside and downside genuinely cancel). On the overpriced side, the likely truth leans hard toward the **upside** (newbies past −1.0 would gain). So setting <142 to $0 isn't splitting an even bet — **it's forfeiting a probable gain.** We took the hit where it's real (the −$0.70M on established hosts) and threw away the gain where it's only probable. That means our overpriced floor isn't a middle estimate — it's a genuine floor. Any honest real-world outcome is *better*, never worse.

### The overpriced band

Now realism, floor, ceiling — same as before:

| Scenario                          | β assumption                     | Overpriced SS Host GBV | Nights recovered |
|-----------------------------------|----------------------------------|------------------------|------------------|
| **Floor** (measured / breakeven)  | −0.92 for ≥142, −1.0 for <142    | **−$0.70M**            | +77,606          |
| **Midpoint** (newbies elastic)    | −0.92 for ≥142, −1.3 for <142    | **+$7.06M**            | +98,741          |
| **Ceiling** (won't happen)        | −1.5 for all overpriced          | **+$18.4M**            | —                |

So the honest overpriced band is **−$0.70M to +$12.7M, midpoint ~+$7M** — but every dollar of upside depends on an elasticity we haven't measured yet. **That's literally the AirROI data ask.**

**Two things to weave in so a sharp professor can't catch you:**

1. **The nights vs. revenue split.** On the underpriced side the headline is *dollars*. On the overpriced side the headline is *nights* (+77,606/yr). Don't try to make overpriced a dollar story for established hosts — it isn't one. Say it plainly: **"underpriced = margin, overpriced = volume."** That's your two-pillar frame and it's the honest one.

2. **The overpriced ceiling is softer than the underpriced ceiling.** Underpriced ceiling is β=0 — a *real* limit (occupancy can't respond less than zero). Overpriced ceiling is β=−1.5 — a number you *picked*. Flag it as "illustrative of commodity-tier elasticity," not a hard bound. That one sentence keeps you honest.

And on the ≥142 side, we don't hide from the loss — we book the full −$0.70M that the measured −0.92 produces. **We'd rather pick the loss than fake a crazy elasticity (−2) to inflate the revenue.**

---

## Ok great, final numbers time.

Before that, a couple of reminders:

## 1. The Internal Airbnb Pitch Frame

Before stating any numbers, the framing matters. This tool is presented as an **internal Airbnb product pitch** — not a host-facing blog post, and not a standalone academic model. That means the success metrics are not "how much does the host make tonight" but the platform health metrics Airbnb VPs and Product Leads actually track:

### A. Gross Booking Value (GBV) & Revenue Capture

GBV is the total dollar value of all bookings made on the platform — Airbnb's fee is a percentage of this number, so every booking that happens (or doesn't) is directly visible in their financials. An overpriced listing with zero demand is a dead calendar date: the host gets nothing, the guest books elsewhere (hotel or competitor), and Airbnb captures zero. Repricing it correctly unlocks that date and converts it to platform GBV. Volume drives total marketplace revenue at scale.

### B. Host Retention & Churn

Overpriced listings are a leading cause of new-host churn. When an inexperienced host lists at $400 for a $220 apartment, gets zero bookings for 6–8 weeks, and quietly deactivates — Airbnb loses a supply-side asset it paid to acquire. Getting that host their first 5–10 booked nights proves the platform works and breaks the abandonment cycle. Host retention is cheaper than host acquisition; this tool targets the moment hosts are most at risk.

### C. Marketplace Liquidity & Search Conversion

When guests search on Airbnb, overpriced unbooked listings degrade the search-to-booking conversion rate — they show up in results, create apparent supply, and then don't convert. Repricing overpriced inventory improves actual conversion efficiency across the NYC market without any additional demand-generation spend.

### D. ADR (Average Daily Rate) Growth

Underpriced listings suppress the platform's ADR metric. A host charging $244 for a listing that comparable peers charge $336 for is leaving $92/night on the table — and Airbnb's per-night fee is proportional to that rate. Moderate, evidence-backed price increases on underpriced listings grow ADR and grow Airbnb's absolute fee revenue without adding a single new listing.

### The Two-Pillar Frame

| Pillar                                            | Listings               | Mechanism                                                              | Platform Win                                    |
|---------------------------------------------------|------------------------|-----------------------------------------------------------------------|-------------------------------------------------|
| **Underpriced → Margin / ADR Optimization**       | 4,931 listings (50.6%) | Raise price to fair value; host earns more per night; Airbnb fee grows | ADR growth + raw fee revenue per booking        |
| **Overpriced → Volume & Liquidity Optimization**  | 4,821 listings (49.4%) | Lower price to fair value; unlock previously unbooked nights          | GBV growth + search conversion + host retention |

Let's look at the examples again to understand how we can spin up the numbers:

### Underpriced example

- Host: **+$130/mo → +$1,560/yr**
- Airbnb: **+$21/mo → +$250/yr per listing**

**KNN layer:** 67 comparable peers, 48 high performers. Only 1 missing amenity vs. high performers: **self check-in**. This listing has almost no operational gap — its underpricing is purely a pricing decision, not an amenity problem.

**Value Add Summary**

| Stakeholder  | Gain          | Mechanism                                                                          |
|--------------|---------------|------------------------------------------------------------------------------------|
| **Host**     | +$1,560/yr    | Higher nightly rate on the same or slightly fewer occupied nights                  |
| **Airbnb**   | +$250/yr      | 15.5% of higher GBV; ADR metric improves                                          |
| **Platform** | ADR growth    | One underpriced listing corrected; multiplied across 4,931 = measurable ADR impact |

### Overpriced example

**The numbers at a glance:**
- GBV change: **−$129/mo (−1.4%)** — nearly revenue-neutral
- Recovered nights: **+2.9/mo → +34.7 nights/year** that were previously sitting empty
- Airbnb delta: **−$20/mo** — a small nominal decline in fee revenue

**KNN layer:** 68 comparable peers, 49 high performers. This listing books 16 nights/month; its high-performing peers book **21.2 nights/month** — a 5.2 night/month gap. After repricing alone, the gap closes by 2.9 nights. The remaining 2.3 nights require closing the amenity gap:

> **Missing vs. high-performers:** hangers · bed linens · microwave · refrigerator · cooking basics

The two-layer pitch: repricing gets 2.9 nights back; adding kitchen basics and linens closes the remaining 2.3. Together the listing reaches peer performance (**+5.2 nights/month = +62 nights/year**).

**Why This Is a Strong Internal Airbnb Argument (Even With −$20/mo)**

The Airbnb fee income from a single overpriced listing barely moves: −$20/month is noise. The platform argument is not per-listing fee math. It is:

| Platform Metric           | Effect of Repricing This Listing                                                  |
|---------------------------|-----------------------------------------------------------------------------------|
| **Booked nights / GBV**   | +2.9 nights/mo that were previously unbooked; each night is a guest transaction   |
| **Search conversion**     | An overpriced unbooked listing clogs search results; repricing it converts        |
| **Host retention**        | A host getting bookings stays on the platform; a host at zero leaves              |
| **Competitor leakage**    | A guest who can't book on Airbnb goes to Booking.com or a hotel                  |

Multiply these effects across 1,228 confidently-overpriced listings and the argument shifts from individual-listing fee math to **platform health at scale.**

**Value Add Summary**

| Stakeholder  | Gain                    | Mechanism                                                                    |
|--------------|-------------------------|------------------------------------------------------------------------------|
| **Host**     | +34.7 nights/yr booked  | Near-neutral revenue (−1.4%) but calendar fills; proof the platform works    |
| **Airbnb**   | Nights booked           | Marketplace liquidity; each recovered night is a guest conversion            |
| **Platform** | Retention + conversion  | Host stays active; search results convert better                             |

---

## Here are the complete numbers

**The band: ~$7.6M (floor) to ~$26.8M (ceiling).**

- **Floor ($7.6M):** every assumption rounds against us. Underpriced segmented + overpriced measured. Bulletproof.
- **Ceiling ($26.8M):** the occupancy-neutral case — if raising prices cost zero bookings. Won't literally happen, but it bounds the top.
- **Note:** the ceiling counts underpriced only. Adding the overpriced upside (+$7M to +$18M if newer listings are elastic) would push the top *higher*, toward ~$40M+. So even our ceiling is conservative — it ignores overpriced revenue entirely.

That last line turns the inconsistency into a strength — you're telling them the ceiling is understated, which makes the whole band read as cautious.

**How to say it out loud:**

> "The revenue opportunity sits between $7.6M and $26.8M a year. The floor is what we can prove today — every guess rounds against us. The ceiling assumes prices move with zero occupancy cost. The truth is somewhere in the middle, and it's bigger than the floor — the AirROI data tells us exactly where."

### The full picture, both sides

|                                 | Underpriced                        | Overpriced                       |
|---------------------------------|------------------------------------|----------------------------------|
| **Ceiling** (won't happen)      | β = 0, occupancy-neutral → $26.8M  | β = −1.5 all listings → +$18.4M  |
| **Best estimate** (segmented β) | $8.3M                              | +$7.1M (−1.3 for <142)           |
| **Floor** (conservative)        | all SS breakeven → $7.9M           | measured/breakeven → −$0.70M     |

Notice the parallel is exact. Both sides have a fake ceiling that won't happen, a realistic middle, and a bulletproof floor. The only difference is **which direction we round when we're forced to guess** — and both times, we round against ourselves.

**One asterisk:** the underpriced ceiling (β=0) is a *real* wall — occupancy physically can't respond less than zero. The overpriced ceiling (β=−1.5) is a number we *picked*. So treat the underpriced ceiling as a hard bound and the overpriced ceiling as "illustrative of what commodity-tier elasticity would look like" — not a promise.

### So which number do we actually put on the slide?

We don't pitch a range to Airbnb execs — we pitch **one conservative number we can defend to the last decimal.** That's the floor of each side added together:

```
Underpriced floor (segmented)     +$8.27M
Overpriced floor (measured)       −$0.70M
─────────────────────────────────────────
COMBINED HOST GBV                 +$7.57M / year
× 15.5% Airbnb take               +$1.17M / year  ← the headline
+ Nights unlocked                 +77,606 nights / year
```

This is the number where every input is either **measured (−0.92)** or a **mathematical certainty (−1.0 breakeven / β=0 for monthly).** Nothing is invented. If a professor attacks any single piece, the honest answer is "that's the conservative choice, the real number is higher."

> **One note on the 77,606 nights:** these are *already inside* the GBV delta calculation — they're the mechanism that produces the −$0.70M, not a separate bucket of money you add on top. So present them as their own platform metric (marketplace liquidity), not as extra dollars stacked onto the $1.17M. The reason we can't turn recovered nights into a clean dollar figure is that we can't tell which recovered nights are net-new guests (won back from hotels = real new money for Airbnb) versus guests who'd have booked anyway (just cheaper = slightly less money). Splitting those buckets needs Airbnb's own booking-flow data — another line in the AirROI ask.

### The one-liner that closes it

> "$7.57M in new host earnings, $1.17M in new Airbnb fees, and 77,606 previously-empty nights filled — and that's the *floor*. Every assumption we made rounds against us. The real number is bigger, but proving how much bigger is exactly what the AirROI data unlocks."

That's your mic-drop. It ties the conservative number, the two-pillar frame (dollars + nights), and the data ask into one sentence.

---

## Caveats (read this before you defend the number)

These are the soft spots. Know them cold, because a sharp professor goes straight for them — and every one of them has an honest answer that actually makes the model look *more* rigorous, not less.

**1. Monthly elasticity is statistically insignificant — we assumed revenue-neutral.**
The TWFE model came back with β = +0.084, p = 0.734 for monthly listings. That's not a real signal — it's noise. So we don't apply any elasticity to monthly; we treat them as occupancy-neutral (raising to fair value = pure price gain, no booking loss assumed). This is the standard move when a coefficient isn't significant: you don't use it. But it means the monthly revenue is an *assumption*, not a measurement.

**2. The whole $7.57M leans on the monthly segment — and that's the softest spot in the stack.**
Here's the honest weakness: the combined $7.57M is basically the monthly segment (+$7.94M). The short-stay side nets to almost nothing (+$0.34M underpriced, −$0.70M overpriced). If a professor asks *"isn't your whole revenue number just the monthly listings?"* — the answer is **yes**, and the reason is exactly caveat #1: monthly elasticity wasn't significant (p=0.73), so we kept it occupancy-neutral, which lets the full price gap flow through as revenue. Short-stay demand is near unit-elastic, so raising an underpriced short-stay listing barely nets anything after the occupancy drop. Have this answer ready — don't get caught flat-footed by it.

**3. Low-review listings get an amenity recommendation, not a price hike.**
For very low-review listings (the elastic newbies), our model doesn't scream "raise your price." It recognizes that a 5-review listing raising its price is likely to lose bookings (elasticity past −1). Instead, the KNN layer surfaces the *amenity* gap — "your high-performing peers have self check-in and a dedicated workspace, you don't." The play for a new listing is: **close the feature gap and build reviews first, then move price as elasticity softens.** This is why the model captures reviews as a feature — to give newer listings a lower, safer fair-price target rather than an aggressive hike.

**4. We can't compute the extra Airbnb revenue from recovered bookings (both directions).**
This applies to overpriced *and* underpriced. When a listing reprices and fills more nights, some of those nights are net-new guests (won back from hotels/competitors = real new money for Airbnb) and some are just guests who would've booked anyway at a different price (no new money). We can't split those two buckets without Airbnb's own **booking-flow / substitution data** — where does a guest actually go when a listing is too expensive? Our −$0.70M and +77,606 nights are computed conservatively assuming *no* competitor win-back. The real Airbnb upside is higher, but quantifying it is another line in the AirROI ask.

**5. The 142-review segmentation line is a chosen threshold, not a natural break.**
We split at 142 reviews because that's the panel median — the profile our β = −0.92 was actually measured on. Above it, we trust the measured elasticity; below it, we fall back to the −1.0 breakeven (no extrapolation). But 142 isn't a magic number where behavior suddenly changes — it's just the honest boundary of where our measurement applies. A listing at 140 reviews and one at 144 aren't meaningfully different; we're using the median as a clean, defensible cutoff, not claiming a discontinuity exists there. The full AirROI dataset would let us measure elasticity continuously across review counts instead of segmenting at one line.

**6. The ceiling counts underpriced only — so even the ceiling is understated.**
The $26.8M ceiling (β=0, occupancy-neutral) is the underpriced side alone. It won't literally happen — it assumes raising prices costs zero bookings — but it bounds the top. And note: it *ignores* the overpriced upside entirely. Adding the overpriced potential (+$7M to +$18M if newer listings are elastic) would push the real top higher, toward ~$40M+. So even our stated ceiling rounds against us — it leaves overpriced revenue on the table.

Question to Brendon:

i hate how we can never show overpriced gain:

u can never show revenue growth like how we did with underpriced.

because ≥ 142 Reviews: Evaluated at $\beta = -0.92$ inflates revenue drop meaning true drop is larger

and keeping other side neutral means no revenue istings < 142 Reviews: We set their net impact floor to $\beta = -1.00$ (Break-Even / $0 Net Change). 

Thats why i introduced the band with the estimations. 
