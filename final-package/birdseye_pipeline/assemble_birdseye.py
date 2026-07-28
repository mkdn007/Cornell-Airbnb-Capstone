import json

SRC = r"C:\Users\stava\OneDrive\Documents\Berkeley_DataViz_FinalProject\d3"
SCRATCH = r"C:\Users\stava\AppData\Local\Temp\claude\c--Users-stava-OneDrive-Documents-75TH\015c245a-15d9-4e73-b4f2-b3c0d03a7b62\scratchpad"
OUT = f"{SCRATCH}\\nyc_pricing_overview_gbm.html"

with open(f"{SRC}\\shareable_geo.json", encoding="utf-8") as f:
    geo_json_text = f.read()
with open(f"{SCRATCH}\\shareable_pricing_segmented.json", encoding="utf-8") as f:
    pricing_json_text = f.read()
with open(f"{SCRATCH}\\basemap_b64.txt", encoding="ascii") as f:
    basemap_b64 = f.read().strip()
with open(f"{SCRATCH}\\basemap_bounds.txt", encoding="ascii") as f:
    lon_left, lon_right, lat_top, lat_bottom = [float(x) for x in f.read().strip().split(",")]

CSS = """
:root {
  --bg: #f6f5f1;
  --surface: #ffffff;
  --text: #1c231e;
  --muted: #5b6560;
  --border: #dde0d9;
  --accent: #2a6f6a;
  --accent-soft: #e4f0ee;
  --shadow: 0 1px 3px rgba(20,23,20,0.08), 0 8px 24px rgba(20,23,20,0.06);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14171a;
    --surface: #1b1f22;
    --text: #e9e7e1;
    --muted: #9aa39d;
    --border: #2b3033;
    --accent: #6cc0b8;
    --accent-soft: #1f2d2b;
    --shadow: 0 1px 3px rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.35);
  }
}
:root[data-theme="dark"] {
  --bg: #14171a; --surface: #1b1f22; --text: #e9e7e1; --muted: #9aa39d;
  --border: #2b3033; --accent: #6cc0b8; --accent-soft: #1f2d2b;
  --shadow: 0 1px 3px rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.35);
}
:root[data-theme="light"] {
  --bg: #f6f5f1; --surface: #ffffff; --text: #1c231e; --muted: #5b6560;
  --border: #dde0d9; --accent: #2a6f6a; --accent-soft: #e4f0ee;
  --shadow: 0 1px 3px rgba(20,23,20,0.08), 0 8px 24px rgba(20,23,20,0.06);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, "Segoe UI", "Inter", ui-sans-serif, Arial, sans-serif;
}

.page {
  max-width: 1120px;
  margin: 0 auto;
  padding: 40px 28px 56px;
}

.eyebrow {
  font-size: 11.5px;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin: 0 0 10px;
}

h1 {
  font-size: 25px;
  line-height: 1.35;
  max-width: 760px;
  margin: 0 0 10px;
  text-wrap: balance;
  font-weight: 650;
}

.context {
  font-size: 14px;
  color: var(--muted);
  max-width: 700px;
  line-height: 1.55;
  margin: 0 0 28px;
}

.context strong { color: var(--text); }

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

#controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field label {
  font-size: 10.5px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
}

select, input[type="range"] {
  font: inherit;
  color: var(--text);
}

.segment-toggle {
  display: flex;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}
.segment-toggle button {
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  padding: 7px 14px;
  border: none;
  background: var(--bg);
  color: var(--muted);
  cursor: pointer;
}
.segment-toggle button.active {
  background: var(--accent);
  color: white;
}

#reset-view {
  font: inherit;
  font-size: 13px;
  color: var(--text);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 12px;
  cursor: pointer;
}
#reset-view:hover { border-color: var(--accent); color: var(--accent); }

select {
  padding: 7px 10px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  min-width: 220px;
  font-size: 13.5px;
}

#month-field.hidden { display: none; }

#opacity-field { min-width: 160px; }

#opacity-field input[type="range"] {
  width: 150px;
  accent-color: var(--accent);
}

#viz {
  position: relative;
  height: 620px;
  background: var(--bg);
}

#map-svg {
  width: 100%;
  height: 100%;
  display: block;
  cursor: grab;
  touch-action: none;
}
#map-svg.dragging { cursor: grabbing; }

path.neighborhood {
  stroke: var(--surface);
  stroke-width: 0.6;
  cursor: pointer;
  fill-opacity: 0.7;
  transition: stroke-width 0.1s;
}

path.neighborhood:hover {
  stroke: var(--text);
  stroke-width: 1.6;
}

path.neighborhood.no-data {
  fill: var(--border) !important;
}

.tooltip {
  position: absolute;
  z-index: 30;
  pointer-events: none;
  background: var(--text);
  color: var(--bg);
  font-size: 12.5px;
  padding: 7px 11px;
  border-radius: 7px;
  opacity: 0;
  transition: opacity 0.1s;
  max-width: 220px;
}

:root[data-theme="dark"] .tooltip,
@media (prefers-color-scheme: dark) {
  .tooltip { color: var(--bg); }
}

.tooltip strong {
  display: block;
  font-size: 13px;
  margin-bottom: 2px;
}

#legend-overlay {
  position: absolute;
  right: 18px;
  bottom: 18px;
  z-index: 20;
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 10px 14px 8px;
  border-radius: 10px;
  box-shadow: var(--shadow);
  pointer-events: none;
}

#legend-overlay .legend-label {
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 6px;
}

#legend-overlay svg text {
  font-size: 10px;
  fill: var(--muted);
  font-variant-numeric: tabular-nums;
}

#legend-overlay svg .tick line {
  stroke: var(--muted);
}

#legend-overlay svg .domain {
  stroke: var(--muted);
}

footer.note {
  margin-top: 16px;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.6;
  max-width: 760px;
}

.app-nav {
  display: flex; gap: 6px; margin-bottom: 18px;
  border-bottom: 1px solid var(--border); padding-bottom: 10px;
}
.app-nav a, .app-nav span {
  font-size: 13px; font-weight: 600; padding: 6px 14px; border-radius: 8px;
  text-decoration: none; color: var(--muted);
}
.app-nav .current { background: var(--accent-soft); color: var(--accent); }
.app-nav a:hover { color: var(--text); background: var(--accent-soft); }
"""

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NYC Airbnb Pricing &amp; Seasonality Overview</title>
<style>__CSS__</style>
</head>
<body>
<div class="page">
  <nav class="app-nav">
    <span class="current">Birds-eye view</span>
    <a href="https://claude.ai/code/artifact/cfb7b07c-82ed-4d24-bb9b-44bd64dbb473">Property pricing tool</a>
  </nav>
  <p class="eyebrow">Cornell Airbnb Capstone &middot; birds-eye view</p>
  <h1>Which NYC neighborhoods are priced furthest from fair value, and does that gap shift seasonally?</h1>
  <p class="context">
    <strong>High-level overview, not per-listing detail.</strong> Built from the current GBM fair-price model,
    calibrated confidence intervals, and real KNN peer-comparison layer, aggregated to the neighborhood level.
    Short-stay and monthly listings behave differently (price sensitivity, occupancy patterns), toggle between
    them below. The seasonal price index is illustrative and simulated, standing in for calendar-level pricing
    data that isn't publicly available.
  </p>

  <div class="card">
    <div id="controls">
      <div class="field">
        <label>Segment</label>
        <div class="segment-toggle">
          <button type="button" id="seg-shortstay" class="active">Short-stay</button>
          <button type="button" id="seg-monthly">Monthly</button>
        </div>
      </div>
      <div class="field">
        <label for="category-select">Metric</label>
        <select id="category-select">
          <option value="gap">Annual pricing gap</option>
          <option value="opportunity_occ">Occupancy gap vs. peers</option>
          <option value="season">Simulated seasonal price index</option>
          <option value="occ">Real occupancy rate</option>
        </select>
      </div>
      <div class="field hidden" id="month-field">
        <label for="month-select">Month</label>
        <select id="month-select"></select>
      </div>
      <div class="field" id="opacity-field">
        <label for="opacity-slider">Fill opacity</label>
        <input type="range" id="opacity-slider" min="0" max="1" step="0.05" value="0.7">
      </div>
      <button id="reset-view" type="button">Reset view</button>
    </div>
    <div id="viz">
      <svg id="map-svg"></svg>
      <div id="legend-overlay">
        <div class="legend-label" id="legend-label"></div>
        <svg id="legend-svg" width="230" height="40"></svg>
      </div>
    </div>
  </div>

  <footer class="note">
    Neighborhood boundaries: Inside Airbnb (New York City). Basemap: CARTO Positron (&copy; OpenStreetMap
    contributors, &copy; CARTO). Pricing model, KNN comparables, and seasonality proof-of-concept: Cornell
    BANA 5160 capstone team, rebuilt tonight on the GBM pipeline (previously Ridge-based). Short-stay and
    monthly are aggregated separately since their real occupancy patterns and price sensitivity differ
    meaningfully, not the same underlying distribution split two ways.
  </footer>
</div>

<script id="geo-data" type="application/json">__GEO__</script>
<script id="pricing-data" type="application/json">__PRICING__</script>
<script id="basemap-data" type="application/json">__BASEMAP__</script>
<script>__JS__</script>
</body>
</html>
"""

JS = """
(function () {
  const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const geo = JSON.parse(document.getElementById("geo-data").textContent);
  const allPricing = JSON.parse(document.getElementById("pricing-data").textContent);
  const basemap = JSON.parse(document.getElementById("basemap-data").textContent);

  // ---- percentile-clipped color domains (same approach as the live D3 version) ----
  function percentileBounds(values, lower, upper) {
    const sorted = values.filter(v => v !== null && v !== undefined).slice().sort((a, b) => a - b);
    function quantile(p) {
      const idx = (sorted.length - 1) * p;
      const lo = Math.floor(idx), hi = Math.ceil(idx);
      if (lo === hi) return sorted[lo];
      return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
    }
    return [quantile(lower), quantile(upper)];
  }

  const RDBU = ["#67001f","#b2182b","#d6604d","#f4a582","#fddbc7","#f7f7f7","#d1e5f0","#92c5de","#4393c3","#2166ac","#053061"];
  const BLUES = ["#f7fbff","#deebf7","#c6dbef","#9ecae1","#6baed6","#4292c6","#2171b5","#08519c","#08306b"];

  function hexToRgb(hex) {
    return { r: parseInt(hex.slice(1, 3), 16), g: parseInt(hex.slice(3, 5), 16), b: parseInt(hex.slice(5, 7), 16) };
  }
  function lerpColor(a, b, f) {
    const ca = hexToRgb(a), cb = hexToRgb(b);
    const r = Math.round(ca.r + (cb.r - ca.r) * f);
    const g = Math.round(ca.g + (cb.g - ca.g) * f);
    const bl = Math.round(ca.b + (cb.b - ca.b) * f);
    return `rgb(${r},${g},${bl})`;
  }
  function ramp(stops, t) {
    t = Math.max(0, Math.min(1, t));
    const n = stops.length - 1;
    const scaled = t * n;
    const i = Math.min(n - 1, Math.floor(scaled));
    return lerpColor(stops[i], stops[i + 1], scaled - i);
  }

  function makeDiverging(values, midpoint) {
    let [lo, hi] = percentileBounds(values, 0.05, 0.95);
    lo = Math.min(lo, midpoint);
    hi = Math.max(hi, midpoint);
    return {
      lo, mid: midpoint, hi,
      color(v) {
        if (v === null || v === undefined) return null;
        const vc = Math.max(lo, Math.min(hi, v));
        let t;
        if (vc <= midpoint) t = (midpoint === lo) ? 0 : 0.5 * (vc - lo) / (midpoint - lo);
        else t = (hi === midpoint) ? 1 : 0.5 + 0.5 * (vc - midpoint) / (hi - midpoint);
        return ramp(RDBU, 1 - t);
      },
      swatch(t) { return ramp(RDBU, 1 - t); },
    };
  }
  function makeSequential(values) {
    const [, hi] = percentileBounds(values, 0.05, 0.95);
    return {
      lo: 0, hi,
      color(v) {
        if (v === null || v === undefined) return null;
        const t = Math.max(0, Math.min(1, v / hi));
        return ramp(BLUES, t);
      },
      swatch(t) { return ramp(BLUES, t); },
    };
  }

  // Everything data-dependent (pricing, scales, modes) is rebuilt per
  // segment, since short-stay and monthly have genuinely different
  // distributions, not just a filtered view of the same one.
  let pricing, modes, currentSegment = "shortstay";
  const monthlyCategories = ["season", "occ"];
  const keyFor = (category, month) => monthlyCategories.includes(category) ? `${category}_${month}` : category;

  function buildModesForSegment(segKey) {
    pricing = allPricing[segKey];
    const gapScale = makeDiverging(pricing.gap, 0);
    const occGapScale = makeDiverging(pricing.occGap, 0);
    const allSeason = MONTHS.flatMap(m => pricing.monthly[m].season);
    const seasonScale = makeDiverging(allSeason, 1);
    const allOcc = MONTHS.flatMap(m => pricing.monthly[m].occ);
    const occScale = makeSequential(allOcc);

    const m = {
      gap: {
        value: i => pricing.gap[i], scale: gapScale,
        legendLabel: "Pricing gap (% from fair value)",
        format: v => `${(v * 100).toFixed(1)}% from fair value`,
        tickFormat: v => `${(v * 100).toFixed(0)}%`,
      },
      opportunity_occ: {
        value: i => pricing.occGap[i], scale: occGapScale,
        legendLabel: "Occupancy gap vs. high-performing peers (days/yr)",
        format: v => `${v.toFixed(0)} days ${v >= 0 ? "behind" : "ahead of"} peers`,
        tickFormat: v => v.toFixed(0),
      },
    };
    MONTHS.forEach(mo => {
      m[`season_${mo}`] = {
        value: i => pricing.monthly[mo].season[i], scale: seasonScale,
        legendLabel: `Seasonal price index, ${mo} (illustrative)`,
        format: v => `${(v * 100).toFixed(0)}% of average, ${mo}`,
        tickFormat: v => `${(v * 100).toFixed(0)}%`,
      };
      m[`occ_${mo}`] = {
        value: i => pricing.monthly[mo].occ[i], scale: occScale,
        legendLabel: `Real occupancy rate, ${mo}`,
        format: v => `${(v * 100).toFixed(0)}% occupied, ${mo}`,
        tickFormat: v => `${(v * 100).toFixed(0)}%`,
      };
    });
    return m;
  }
  modes = buildModesForSegment(currentSegment);

  // ---- projection: plain Web Mercator, no library, fit to the data's own bounds ----
  const toRad = d => d * Math.PI / 180;
  const mercY = lat => Math.log(Math.tan(Math.PI / 4 + toRad(lat) / 2));

  let minLon = Infinity, maxLon = -Infinity, minLat = Infinity, maxLat = -Infinity;
  function scanCoords(coords, depth) {
    if (depth === 1) {
      const [lon, lat] = coords;
      if (lon < minLon) minLon = lon;
      if (lon > maxLon) maxLon = lon;
      if (lat < minLat) minLat = lat;
      if (lat > maxLat) maxLat = lat;
    } else {
      coords.forEach(c => scanCoords(c, depth - 1));
    }
  }
  geo.features.forEach(f => {
    const depth = f.geometry.type === "Polygon" ? 3 : 4;
    scanCoords(f.geometry.coordinates, depth);
  });

  const pad = 0.03;
  const lonPad = (maxLon - minLon) * pad, latPad = (maxLat - minLat) * pad;
  const rawMinX = toRad(minLon - lonPad), rawMaxX = toRad(maxLon + lonPad);
  const rawMinY = mercY(minLat - latPad), rawMaxY = mercY(maxLat + latPad);

  const VIEW_H = 1000;
  const VIEW_W = VIEW_H * (rawMaxX - rawMinX) / (rawMaxY - rawMinY);

  function project(lon, lat) {
    const x = (toRad(lon) - rawMinX) / (rawMaxX - rawMinX) * VIEW_W;
    const y = VIEW_H - (mercY(lat) - rawMinY) / (rawMaxY - rawMinY) * VIEW_H;
    return [x, y];
  }
  function ringPath(ring) {
    return "M" + ring.map(([lon, lat]) => project(lon, lat).map(n => n.toFixed(1)).join(",")).join("L") + "Z";
  }
  function geometryPath(geometry) {
    if (geometry.type === "Polygon") return geometry.coordinates.map(ringPath).join(" ");
    return geometry.coordinates.map(poly => poly.map(ringPath).join(" ")).join(" ");
  }

  const svg = document.getElementById("map-svg");
  svg.setAttribute("viewBox", `0 0 ${VIEW_W} ${VIEW_H}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

  const nsUri = "http://www.w3.org/1999/xlink";
  const bmTopLeft = project(basemap.lonLeft, basemap.latTop);
  const bmBottomRight = project(basemap.lonRight, basemap.latBottom);
  const bmImage = document.createElementNS("http://www.w3.org/2000/svg", "image");
  bmImage.setAttributeNS(nsUri, "href", basemap.dataUri);
  bmImage.setAttribute("href", basemap.dataUri);
  bmImage.setAttribute("x", bmTopLeft[0]);
  bmImage.setAttribute("y", bmTopLeft[1]);
  bmImage.setAttribute("width", bmBottomRight[0] - bmTopLeft[0]);
  bmImage.setAttribute("height", bmBottomRight[1] - bmTopLeft[1]);
  bmImage.setAttribute("preserveAspectRatio", "none");
  svg.appendChild(bmImage);

  let nameIndex = new Map(pricing.neighborhoods.map((n, i) => [n, i]));
  const pathEls = [];
  geo.features.forEach(f => {
    const name = f.properties.neighbourhood;
    const el = document.createElementNS("http://www.w3.org/2000/svg", "path");
    el.setAttribute("d", geometryPath(f.geometry));
    el.setAttribute("fill-rule", "evenodd");
    el.classList.add("neighborhood");
    el.dataset.name = name;
    el.dataset.index = nameIndex.has(name) ? nameIndex.get(name) : "";
    svg.appendChild(el);
    pathEls.push(el);
  });

  // ---- tooltip ----
  const viz = document.getElementById("viz");
  const tooltip = document.createElement("div");
  tooltip.className = "tooltip";
  viz.appendChild(tooltip);

  let currentMode = "gap";
  function applyMode(modeKey) {
    currentMode = modeKey;
    const mode = modes[modeKey];
    pathEls.forEach(el => {
      const idx = el.dataset.index;
      const v = idx === "" ? undefined : mode.value(+idx);
      if (v === undefined || v === null) {
        el.classList.add("no-data");
        el.style.fill = "";
      } else {
        el.classList.remove("no-data");
        el.style.fill = mode.scale.color(v);
      }
    });
    drawLegend(mode);
  }

  pathEls.forEach(el => {
    el.addEventListener("mouseenter", () => { if (!dragging) tooltip.style.opacity = 1; });
    el.addEventListener("mousemove", (event) => {
      if (dragging) return;
      const name = el.dataset.name;
      const idx = el.dataset.index;
      const mode = modes[currentMode];
      const v = idx === "" ? undefined : mode.value(+idx);
      const vizBox = viz.getBoundingClientRect();
      tooltip.innerHTML = (v === undefined || v === null)
        ? `<strong>${name}</strong>No data`
        : `<strong>${name}</strong>${mode.format(v)}`;
      tooltip.style.left = `${event.clientX - vizBox.left + 14}px`;
      tooltip.style.top = `${event.clientY - vizBox.top + 14}px`;
    });
    el.addEventListener("mouseleave", () => { tooltip.style.opacity = 0; });
  });

  // ---- legend ----
  const legendSvg = document.getElementById("legend-svg");
  const legendLabel = document.getElementById("legend-label");
  const LW = 210, LH = 12;
  function drawLegend(mode) {
    legendLabel.textContent = mode.legendLabel;
    while (legendSvg.firstChild) legendSvg.removeChild(legendSvg.firstChild);
    const ns = "http://www.w3.org/2000/svg";
    const defs = document.createElementNS(ns, "defs");
    const grad = document.createElementNS(ns, "linearGradient");
    const gid = "legend-grad";
    grad.setAttribute("id", gid);
    grad.setAttribute("x1", "0%"); grad.setAttribute("x2", "100%");
    grad.setAttribute("y1", "0%"); grad.setAttribute("y2", "0%");
    for (let t = 0; t <= 1.0001; t += 0.1) {
      const stop = document.createElementNS(ns, "stop");
      stop.setAttribute("offset", `${Math.round(t * 100)}%`);
      stop.setAttribute("stop-color", mode.scale.swatch(t));
      grad.appendChild(stop);
    }
    defs.appendChild(grad);
    legendSvg.appendChild(defs);

    const rect = document.createElementNS(ns, "rect");
    rect.setAttribute("x", 2); rect.setAttribute("y", 6);
    rect.setAttribute("width", LW); rect.setAttribute("height", LH);
    rect.setAttribute("fill", `url(#${gid})`);
    legendSvg.appendChild(rect);

    const loVal = mode.scale.lo, hiVal = mode.scale.hi;
    const ticks = 4;
    for (let i = 0; i <= ticks; i++) {
      const frac = i / ticks;
      const val = loVal + (hiVal - loVal) * frac;
      const x = 2 + frac * LW;
      const line = document.createElementNS(ns, "line");
      line.setAttribute("x1", x); line.setAttribute("x2", x);
      line.setAttribute("y1", 18); line.setAttribute("y2", 22);
      line.setAttribute("stroke", "currentColor");
      line.classList.add("tick");
      legendSvg.appendChild(line);
      const text = document.createElementNS(ns, "text");
      text.setAttribute("x", x); text.setAttribute("y", 33);
      text.setAttribute("text-anchor", i === 0 ? "start" : i === ticks ? "end" : "middle");
      text.textContent = mode.tickFormat(val);
      legendSvg.appendChild(text);
    }
  }

  // ---- controls ----
  const categorySelect = document.getElementById("category-select");
  const monthField = document.getElementById("month-field");
  const monthSelect = document.getElementById("month-select");
  MONTHS.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m; opt.textContent = m;
    monthSelect.appendChild(opt);
  });

  function handleChange() {
    const category = categorySelect.value;
    const needsMonth = monthlyCategories.includes(category);
    monthField.classList.toggle("hidden", !needsMonth);
    applyMode(keyFor(category, monthSelect.value));
  }
  categorySelect.addEventListener("change", handleChange);
  monthSelect.addEventListener("change", handleChange);

  document.getElementById("opacity-slider").addEventListener("input", (e) => {
    pathEls.forEach(el => { el.style.fillOpacity = e.target.value; });
  });

  // ---- segment toggle ----
  const segShortstayBtn = document.getElementById("seg-shortstay");
  const segMonthlyBtn = document.getElementById("seg-monthly");
  function switchSegment(segKey) {
    currentSegment = segKey;
    segShortstayBtn.classList.toggle("active", segKey === "shortstay");
    segMonthlyBtn.classList.toggle("active", segKey === "monthly");
    modes = buildModesForSegment(segKey);
    nameIndex = new Map(pricing.neighborhoods.map((n, i) => [n, i]));
    pathEls.forEach(el => {
      const name = el.dataset.name;
      el.dataset.index = nameIndex.has(name) ? nameIndex.get(name) : "";
    });
    handleChange();
  }
  segShortstayBtn.addEventListener("click", () => switchSegment("shortstay"));
  segMonthlyBtn.addEventListener("click", () => switchSegment("monthly"));

  // ---- Zoom (wheel) and pan (drag), by rewriting the SVG's viewBox ----
  const MIN_SCALE = 1, MAX_SCALE = 6;
  const view = { scale: MIN_SCALE, cx: VIEW_W / 2, cy: VIEW_H / 2 };

  function clampedBox() {
    const w = VIEW_W / view.scale, h = VIEW_H / view.scale;
    let x = view.cx - w / 2, y = view.cy - h / 2;
    x = Math.max(0, Math.min(VIEW_W - w, x));
    y = Math.max(0, Math.min(VIEW_H - h, y));
    view.cx = x + w / 2; view.cy = y + h / 2;
    return { x, y, w, h };
  }
  function applyViewBox() {
    const { x, y, w, h } = clampedBox();
    svg.setAttribute("viewBox", `${x} ${y} ${w} ${h}`);
  }
  function clientToWorld(clientX, clientY) {
    const rect = svg.getBoundingClientRect();
    const { x, y, w, h } = clampedBox();
    return [x + (clientX - rect.left) / rect.width * w, y + (clientY - rect.top) / rect.height * h];
  }

  svg.addEventListener("wheel", (event) => {
    event.preventDefault();
    const rect = svg.getBoundingClientRect();
    const [worldX, worldY] = clientToWorld(event.clientX, event.clientY);
    view.scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, view.scale * Math.pow(1.0016, -event.deltaY)));
    const fracX = (event.clientX - rect.left) / rect.width;
    const fracY = (event.clientY - rect.top) / rect.height;
    const w = VIEW_W / view.scale, h = VIEW_H / view.scale;
    view.cx = worldX - fracX * w + w / 2;
    view.cy = worldY - fracY * h + h / 2;
    applyViewBox();
  }, { passive: false });

  let dragging = false, lastClient = null;
  svg.addEventListener("mousedown", (event) => {
    dragging = true; lastClient = [event.clientX, event.clientY];
    svg.classList.add("dragging");
    tooltip.style.opacity = 0;
  });
  window.addEventListener("mousemove", (event) => {
    if (!dragging) return;
    const rect = svg.getBoundingClientRect();
    const { w, h } = clampedBox();
    view.cx -= (event.clientX - lastClient[0]) / rect.width * w;
    view.cy -= (event.clientY - lastClient[1]) / rect.height * h;
    lastClient = [event.clientX, event.clientY];
    applyViewBox();
  });
  window.addEventListener("mouseup", () => {
    dragging = false;
    svg.classList.remove("dragging");
  });

  document.getElementById("reset-view").addEventListener("click", () => {
    view.scale = MIN_SCALE; view.cx = VIEW_W / 2; view.cy = VIEW_H / 2;
    applyViewBox();
  });

  applyMode("gap");
})();
"""

basemap_json_text = json.dumps({
    "dataUri": f"data:image/jpeg;base64,{basemap_b64}",
    "lonLeft": lon_left,
    "lonRight": lon_right,
    "latTop": lat_top,
    "latBottom": lat_bottom,
})

html = (HTML_TEMPLATE
        .replace("__CSS__", CSS)
        .replace("__GEO__", geo_json_text)
        .replace("__PRICING__", pricing_json_text)
        .replace("__BASEMAP__", basemap_json_text)
        .replace("__JS__", JS))

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

import os
print("wrote", OUT, os.path.getsize(OUT), "bytes")
