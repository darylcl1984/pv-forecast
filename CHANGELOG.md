# Changelog
All notable changes are documented here. New entries go at the top.
Versioning: `1.0.x` bug fix · `1.x.0` new feature · `x.0.0` breaking change

---

## [1.5.1] — 2026-09-07

### Fixed
- Desktop EV window hatch: Chart.js area-fill + tension glitches on Chromium (worse on a wide plot / after refresh). Hatch is now painted from the chart’s own point positions after the canvas is rebuilt, so it stays inside the charge window.

---

## [1.5.0] — 2026-09-05

### Added
- First-run azimuth follows hemisphere (0° south north of the equator, 180° north south of it)
- Chart Rise/Set markers placed between hourly ticks at the real sunrise/sunset minute
- Day cards are buttons with keyboard focus and `aria-pressed`; chart canvas has an accessible name

### Changed
- Settings stay open (gear ring on) until **Update Forecast** — GPS or a place pick no longer hides config
- Chart legend **To now** / **Forecast** (elapsed hours are still the GTI model, not inverter actuals)
- EV charge window uses sunrise–sunset instead of a fixed 06:00–18:00 band
- Offline badge shows cache age; expired cache is kept as a last resort
- Hourly tooltip notes GTI is a preceding-hour average
- Service worker cache bumped to v5; navigations (including GitHub Pages `/pv-forecast/`) are network-first; shell and icons are precached
- `calibrate_pr.py` reads CSVs from `tools/`, refuses LAT/LON 0,0, uses Historical Forecast GTI, joins hour-ending windows, and flags clip from hourly peak

### Fixed
- Installed GitHub Pages clients staying on a stale `index.html` until `CACHE_NAME` was bumped
- Forecast cache reused across location/tilt/azimuth changes; overlapping fetches could paint the previous site
- “Today” / Now marker used the phone clock instead of the site timezone from Open-Meteo
- Sunrise/sunset chart lines never drew (`indexOf` on minute times vs hourly labels)
- Pinch-zoom blocked by `user-scalable=no`

---

## [1.4.0] — 2026-07-28

### Added
- Photon (OpenStreetMap) place search for streets, suburbs, and cities; Open-Meteo geocoding kept as fallback
- Location bias from saved/GPS coordinates when searching
- Autocomplete keyboard navigation (↑/↓/Enter/Escape) and explicit multi-result picker (no silent first-hit commit)
- Soft solar atmospheric background wash and spacing/display CSS tokens
- Power meter with NOW fill and peak tick aligned under Forecast Peak / Peak so far

### Changed
- Estimated kWh promoted to hero metric; Peak/Now as secondary metrics on a shared one-line stats row (mobile + desktop)
- Day cards, chart, and EV strip de-carded; selected day uses warm sun-light wash with amber rail; header sun logo warmed to amber
- Chart: actual vs forecast join without hour gap; quieter cloud fill; sparse axes; mobile kW/Cloud labels moved into legend flanks for a wider plot
- Chart inverter clip labelled **inverter limit** (legend + dashed line)
- EV charge window strip integrated under the chart at full section width
- Location placeholder and Places attribution updated for Photon/OSM
- Chart tooltip surface warmed to match app surfaces; amber glow leftovers unified to `#E8950E`
- Service worker cache bumped to v4; Photon API requests bypass the SW cache

### Removed
- Redundant inverter kW limit caption from the stats meter card (shown on the chart only)

### Fixed
- Full street addresses failing to resolve (Open-Meteo place-name-only API)
- Ambiguous suburb Search auto-picking the wrong country via `count=1` / stale autocomplete cache

---

## [1.3.0] — 2026-03-30

### Added
- Desktop collapsible config panel: defaults to a compact summary card (location name + param summary + Edit button) when settings are already configured; clicking expands to full config; ↑ Collapse button returns to summary; auto-collapses after Update Forecast
- Gear/sliders icon in header replaces the full-width "Configure System" button on mobile — cleaner header with right-aligned control
- Animated ring moved to the header gear icon wrapper (same anti-clockwise ring when no location is set)
- Location name and date shown inline next to "7-Day Outlook" section title on mobile
- Combined info strip: weather description and sunrise/sunset on a single row (was two separate rows)
- MIT LICENSE file added to repository root

### Changed
- Default system parameters updated: array 10 kW, inverter 8 kW, tilt 22.5°
- Mobile layout reordered using CSS `order`: chart floats to top, followed by info strip, stats, EV card, then config panel
- Config panel repositioned above the chart on mobile, reducing scroll distance to reach settings
- Mobile spacing normalised and reduced throughout for a less cluttered feel
- Service worker updated to v3 with `updateViaCache: 'none'` to ensure the latest SW is always fetched on navigation

### Removed
- Mini bar chart (below 7-day outlook) removed — redundant with day card kWh values
- Full-width "Configure System" button removed — replaced by the header gear icon

---

## [1.2.0] — 2026-03-28

### Added
- Desktop two-column layout at ≥900px: sticky left panel with vertical 7-day card list and always-visible config panel; right column with stats, chart, and EV card
- Chart canvas height increased to 320px on desktop
- Attribution and auto-refresh notice pinned to the bottom of the desktop sidebar
- Animated amber ring on the Configure System button (mobile only) when no location is set — rotates anti-clockwise as a setup prompt, disappears once location is configured
- Default value indicators on config inputs: faint dashed amber underline on any field still at its factory default; `title` tooltip reads "Default value" on hover
- Inline field hints: tapping the `i` icon next to Array, Inverter, Perf. Ratio, Tilt, Azimuth, and EV Threshold reveals a one-line explanation; hover shows a native tooltip on desktop
- Space Grotesk added as the font for stat card values
- EV charge window now shown with diagonal green hatching fill on the chart for clearer visual separation
- Estimated stat card caption line now includes yield quality indicator: `kWh ▲ great day`, `kWh · fair day`, or `kWh ▼ low yield`
- Stat card unit labels (kW) for Peak and Now now coloured to match their value, consistent with the Estimated card

### Changed
- Amber accent colour deepened from `#F5A623` to `#E8950E` for improved contrast on white (applies to both mobile and desktop)
- Surface whites warmed from `#FFFFFF` to `#FEFCF8` for visual consistency with the app background
- Cloud grey shifted from `#B0BEC5` to `#90A4AE` to align CSS variable with the chart's existing cloud colour
- Config panel repositioned above the chart on mobile, reducing scroll distance to reach settings
- Mini bar chart hidden on desktop (redundant with the vertical card list)
- Location name shown in header subtitle on desktop; hidden from section title to avoid duplication
- Day card kWh badges softened: muted fill backgrounds, weight 500, desaturated text colours (Option C)
- Stat card values switched to Space Grotesk at 19px/500 weight for a cleaner, less technical feel
- Red EV badge and stat colours made slightly more saturated (`#BE3D28`) for legibility
- Chart legend label updated from "Output" to "PV Output"

### Fixed
- *(nothing)*

---

## [1.1.0] — 2026-03-25

### Added
- Chart "Now" marker: single orange dot interpolated to the exact current time on the output curve, with a fine dotted crosshair to both axes
- EV-quality colour coding on day cards: kWh badge is green (>2h window), amber (1–2h), or red (no window)
- EV charge window box now reflects window quality: green (>2h), amber (1–2h), red (none)
- Estimated kWh stat card colour matches EV window quality (green / amber / red)

### Changed
- Peak kW stat card colour changed from blue to orange, consistent with other solar output values

### Fixed
- Chart EV window fill was invisible for 1-hour windows (single isolated data point); endpoint now included so the area always renders
- EV window threshold comparison now uses the same 1dp rounding as the tooltip display, preventing values shown as e.g. `6.0kW` from being incorrectly excluded from the window

---

## [1.0.0] — 2025-03-24 · First Stable Release

### Added
- Initial PWA with 7-day solar forecast
- EV charge window detection
- Hourly chart with cloud cover overlay

### Changed
- *(nothing)*

### Fixed
- *(nothing)*