# Changelog
All notable changes are documented here. New entries go at the top.
Versioning: `1.0.x` bug fix · `1.x.0` new feature · `x.0.0` breaking change

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