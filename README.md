# Solar Forecast PWA

A responsive progressive web app that estimates photovoltaic output using [Open-Meteo's](https://open-meteo.com/) Global Tilted Irradiance (GTI) forecast API. No backend, no build step — a single HTML file you can host anywhere.

![License: MIT](https://img.shields.io/badge/license-MIT-blue)

## Why This Exists

Most solar forecast tools are either locked behind inverter vendor apps, require paid subscriptions, or don't let you configure your actual system parameters. This app gives you a 7-day PV output forecast based on your real array size, inverter capacity, tilt, azimuth, and performance ratio — all running client-side with free API data.

## Features

- **Responsive layout** — two-column desktop view (≥900px) with sticky sidebar; full mobile experience with pull-to-refresh
- **7-day forecast cards** — colour-coded kWh badges (green/amber/red) indicating EV charge window quality, with weather icon and temperature range
- **Hourly PV output chart** — solar curve, cloud cover overlay, diagonal-hatched EV charge window, inverter clipping line, and sunrise/sunset markers
- **Live "Now" indicator** — interpolated dot on today's chart showing current estimated output
- **EV charge window detection** — longest consecutive block above your kW threshold, with quality rating (great / fair / low yield)
- **Configurable system parameters** — array size, inverter limit, performance ratio, tilt, azimuth; each field has an inline hint explaining the parameter
- **Default value indicators** — config fields still at factory defaults are visually flagged so you know what to personalise
- **Setup prompt** — animated ring on the Configure button (mobile) when no location is set
- **Location search** with typeahead autocomplete via Open-Meteo geocoding, plus browser geolocation on first launch
- **PWA installable** — Add to Home Screen on Android Chrome and iOS Safari; opens as a standalone app
- **Offline support** — 6hr localStorage cache; service worker serves the app shell when offline
- **Auto-refresh** every 30 minutes; pull-to-refresh on mobile

## How It Works

The core calculation:

```
kW = min(inverterKw, (systemKw × performanceRatio × GTI_W/m²) / 1000)
```

GTI (Global Tilted Irradiance) is fetched from Open-Meteo's forecast API, which accounts for your panel tilt and azimuth. Output is clamped at inverter capacity. The app processes hourly GTI data into daily summaries, renders the chart, and identifies optimal EV charging windows.

All computation runs in the browser. No server, no API keys, no accounts.

## Quick Start

1. Clone this repo
2. Open `index.html` in a browser — or deploy to any static host
3. Allow location access (or search for your address manually)
4. Configure your system parameters: array size (kW), inverter limit (kW), tilt, azimuth, performance ratio

### GitHub Pages Deployment

```bash
# The app is a single file — just enable GitHub Pages on main branch
# Settings → Pages → Source: Deploy from branch → main → / (root)
```

Your app will be live at `https://<username>.github.io/<repo-name>/`

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Array (kW) | 7 | Total panel capacity |
| Inverter (kW) | 5 | Inverter output limit |
| Performance Ratio | 0.80 | System efficiency factor (typically 0.75–0.85) |
| Tilt (°) | 25 | Panel tilt from horizontal |
| Azimuth (°) | 180 | Panel direction — Open-Meteo convention: 0°=south, 180°=north |
| Forecast Days | 7 | 1–16 days ahead |
| EV Threshold (kW) | 4 | Minimum output for EV charge window detection |

**Azimuth note:** Open-Meteo uses 0°=south convention (not 0°=north). For southern hemisphere north-facing panels, use ~180°. For east-facing use -90°, west-facing use 90°.

## Calibration

The repo includes `calibrate_pr.py`, a standalone Python script for calibrating your performance ratio against real inverter data. It reads Sungrow CSV exports and fetches matching GTI data from Open-Meteo to back-calculate your actual PR.

```bash
# Place your Sungrow 5-minute CSV exports in the same directory
python calibrate_pr.py
```

The script produces per-day and overall PR statistics, identifies clipped hours, and recommends whether your current PR setting needs adjustment.

## Tech Stack

- Single HTML file (`index.html`) — HTML, CSS, JS, no build tools, no framework
- `sw.js` — service worker for PWA caching (network-first for app shell, cache-first for CDN assets)
- `manifest.json` + SVG icons — PWA install support for Android and iOS
- [Chart.js 4.4.1](https://www.chartjs.org/) via CDN
- [Open-Meteo API](https://open-meteo.com/) (free tier, CC BY 4.0) — GTI forecast and geocoding
- Google Fonts: Outfit · IBM Plex Mono · Space Grotesk

## Limitations

- **Forecast accuracy:** GTI is a weather-model forecast, not measured irradiance. Partly cloudy days can show ±50% error vs actual production.
- **No actual production overlay:** The app shows forecast only. Comparing against real inverter output would require vendor API integration.
- **Free API tier:** 10K calls/day, non-commercial use. Fine for personal use; commercial deployment requires an Open-Meteo paid plan.

## License

MIT

## Attribution

Weather data provided by [Open-Meteo](https://open-meteo.com/) under CC BY 4.0.