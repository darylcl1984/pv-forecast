# Changelog
All notable changes are documented here. New entries go at the top.
Versioning: `1.0.x` bug fix · `1.x.0` new feature · `x.0.0` breaking change

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