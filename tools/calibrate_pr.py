#!/usr/bin/env python3
"""
Solar PR Calibration Tool
Run from repo root: python tools/calibrate_pr.py

Reads Sungrow CSV exports from this directory (tools/) and fetches matching
GTI from Open-Meteo's Historical Forecast API — the same radiation product
the PWA uses — to back-calculate your Performance Ratio.

Open-Meteo global_tilted_irradiance is a preceding-hour mean (stamp 14:00 =
13:00–14:00). Inverter 5-minute samples are aggregated onto that same
hour-ending window before they are joined.
"""

from pathlib import Path
import pandas as pd
import requests
import sys

# ── System constants (edit to match your setup) ──
PV_KW      = 10.0   # Total panel capacity in kW
INVERTER_KW = 8.0   # Inverter output limit in kW
ASSUMED_PR = 0.80   # Starting performance ratio (typical range: 0.75–0.85)
TILT       = 22.5   # Panel tilt in degrees
AZIMUTH    = 180    # Panel azimuth (Open-Meteo convention: 0=south, 180=north)
LAT        = 0.0    # Your latitude  — replace before running
LON        = 0.0    # Your longitude — replace before running

HERE = Path(__file__).resolve().parent
HISTORICAL_FORECAST = "https://historical-forecast-api.open-meteo.com/v1/forecast"
LIVE_FORECAST = "https://api.open-meteo.com/v1/forecast"

def load_sungrow_csvs(paths):
    dfs = []
    for f in paths:
        df = pd.read_csv(f, encoding='utf-8-sig')
        df.columns = df.columns.str.strip()
        df['Time'] = pd.to_datetime(df['Time'])
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True).sort_values('Time').reset_index(drop=True)

def _gti_url(host, start_date, end_date):
    return (
        f"{host}"
        f"?latitude={LAT}&longitude={LON}"
        f"&hourly=global_tilted_irradiance"
        f"&timezone=auto"
        f"&start_date={start_date}&end_date={end_date}"
        f"&tilt={TILT}&azimuth={AZIMUTH}"
    )


def fetch_gti(start_date, end_date):
    """Fetch GTI from Historical Forecast (same family as the PWA), then live forecast."""
    last_err = None
    for host, label in (
        (HISTORICAL_FORECAST, "historical forecast"),
        (LIVE_FORECAST, "live forecast"),
    ):
        url = _gti_url(host, start_date, end_date)
        print(f"  Trying {label}…")
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"    HTTP {resp.status_code}")
                last_err = f"HTTP {resp.status_code} from {label}"
                continue
            data = resp.json()
            hourly = data.get("hourly") or {}
            gti = hourly.get("global_tilted_irradiance") or []
            times = hourly.get("time") or []
            if not times or not any(v is not None for v in gti):
                print("    No GTI values in response")
                last_err = f"empty GTI from {label}"
                continue
            print(f"    OK ({label})")
            return pd.DataFrame({
                "hour": pd.to_datetime(times),
                "gti_wm2": gti,
            })
        except requests.RequestException as e:
            print(f"    {e}")
            last_err = str(e)
    raise RuntimeError(
        f"Could not fetch forecast GTI ({last_err}). "
        "Not falling back to ERA5 archive — that PR would not match the PWA."
    )

def kw_at_gti(gti):
    return min(INVERTER_KW, (PV_KW * ASSUMED_PR * gti) / 1000)

def main():
    if LAT == 0.0 and LON == 0.0:
        print("Set LAT and LON in calibrate_pr.py to your site before running.")
        print("Leaving them at 0,0 would fetch GTI for the Gulf of Guinea.")
        sys.exit(1)

    print(f"Site: {LAT}, {LON}  tilt={TILT}°  az={AZIMUTH}°  "
          f"array={PV_KW}kW  inv={INVERTER_KW}kW  assumed PR={ASSUMED_PR}")

    paths = sorted(HERE.glob("*.csv"))
    if not paths:
        paths = sorted(Path.cwd().glob("*.csv"))
    if not paths:
        print(f"No CSV files found in {HERE} or the current directory.")
        print("Place your Sungrow export CSVs in tools/ and re-run.")
        sys.exit(1)

    print(f"Found {len(paths)} CSV file(s): {', '.join(p.name for p in paths)}")
    actual = load_sungrow_csvs(paths)
    actual['PV_kW'] = actual['PV(W)'] / 1000.0
    # Hour-ending label: 13:00–13:59 production joins GTI stamped 14:00 (13:00–14:00 mean)
    actual['hour'] = actual['Time'].dt.floor('h') + pd.Timedelta(hours=1)

    dates = actual['Time'].dt.date.unique()
    start_date = str(min(dates))
    end_date = str(max(dates))
    print(f"Date range: {start_date} to {end_date}")
    print(f"Total 5-min readings: {len(actual)}")

    # Hourly aggregation
    hourly = actual.groupby('hour').agg(
        pv_kw_mean=('PV_kW', 'mean'),
        pv_kw_max=('PV_kW', 'max'),
    ).reset_index()
    hourly = hourly[hourly['pv_kw_mean'] > 0.01]
    print(f"Daylight hours with production: {len(hourly)}")

    # Fetch GTI
    print(f"\nFetching GTI from Open-Meteo...")
    gti_df = fetch_gti(start_date, end_date)
    print(f"GTI data points: {len(gti_df)}")

    # Merge
    merged = hourly.merge(gti_df, on='hour', how='inner')
    merged = merged[merged['gti_wm2'] > 10].copy()
    print(f"Matched daylight hours with GTI > 10: {len(merged)}")

    # Predictions and back-calc PR
    merged['predicted_kw'] = merged['gti_wm2'].apply(kw_at_gti)
    merged['actual_pr'] = (merged['pv_kw_mean'] * 1000) / (PV_KW * merged['gti_wm2'])
    merged['clipped'] = merged['pv_kw_max'] >= (INVERTER_KW * 0.95)
    merged['date'] = merged['hour'].dt.date

    unclipped = merged[~merged['clipped']]

    # Per-day breakdown
    print("\n" + "=" * 60)
    print("PER-DAY ANALYSIS")
    print("=" * 60)
    for date, grp in merged.groupby('date'):
        actual_kwh = grp['pv_kw_mean'].sum()
        predicted_kwh = grp['predicted_kw'].sum()
        unc = grp[~grp['clipped']]
        avg_pr = unc['actual_pr'].mean() if len(unc) > 0 else float('nan')
        ratio = actual_kwh / predicted_kwh if predicted_kwh > 0 else float('nan')
        print(f"\n  {date}:")
        print(f"    Actual:       {actual_kwh:6.1f} kWh")
        print(f"    Predicted:    {predicted_kwh:6.1f} kWh  (PR={ASSUMED_PR})")
        print(f"    Ratio:        {ratio:.3f}")
        print(f"    Avg PR:       {avg_pr:.4f}  (unclipped hours only)")
        print(f"    Clipped hrs:  {len(grp[grp['clipped']])} / {len(grp)}")

    # Overall
    print("\n" + "=" * 60)
    print("OVERALL CALIBRATION")
    print("=" * 60)
    total_actual = merged['pv_kw_mean'].sum()
    total_predicted = merged['predicted_kw'].sum()
    overall_ratio = total_actual / total_predicted if total_predicted > 0 else float('nan')

    if len(unclipped) > 0:
        pr_mean = unclipped['actual_pr'].mean()
        pr_median = unclipped['actual_pr'].median()
        pr_std = unclipped['actual_pr'].std()
        pr_p25 = unclipped['actual_pr'].quantile(0.25)
        pr_p75 = unclipped['actual_pr'].quantile(0.75)
    else:
        pr_mean = pr_median = pr_std = pr_p25 = pr_p75 = float('nan')

    print(f"  Total actual:      {total_actual:6.1f} kWh")
    print(f"  Total predicted:   {total_predicted:6.1f} kWh  (at PR={ASSUMED_PR})")
    print(f"  Overall ratio:     {overall_ratio:.4f}")
    print(f"  Effective PR:      {ASSUMED_PR * overall_ratio:.4f}")
    print()
    print(f"  Back-calculated PR (unclipped hours, n={len(unclipped)}):")
    print(f"    Mean:    {pr_mean:.4f}")
    print(f"    Median:  {pr_median:.4f}")
    print(f"    Std:     {pr_std:.4f}")
    print(f"    IQR:     {pr_p25:.4f} – {pr_p75:.4f}")
    print()
    print(f"  Clipped hours: {len(merged[merged['clipped']])} / {len(merged)}"
          f"  ({100 * len(merged[merged['clipped']]) / len(merged):.0f}%)")

    # Recommendation
    recommended = round(pr_median, 2)
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    print(f"  Current PR:     {ASSUMED_PR}")
    print(f"  Calibrated PR:  {recommended}  (median of unclipped hours)")
    delta = abs(recommended - ASSUMED_PR)
    if delta < 0.03:
        print(f"  → Your PR of {ASSUMED_PR} is within ±0.03 — no change needed.")
    else:
        direction = "up" if recommended > ASSUMED_PR else "down"
        print(f"  → Consider adjusting PR {direction} from {ASSUMED_PR} to {recommended}")

    # Hourly detail
    print("\n" + "=" * 60)
    print("HOURLY DETAIL")
    print("=" * 60)
    print(f"  {'Hour':>16} {'Actual':>8} {'GTI':>8} {'Pred':>8} {'PR':>8} {'Clip':>5}")
    print(f"  {'':>16} {'(kW)':>8} {'(W/m²)':>8} {'(kW)':>8} {'':>8} {'':>5}")
    print("  " + "-" * 55)
    for _, r in merged.iterrows():
        print(f"  {str(r['hour']):>16} {r['pv_kw_mean']:>8.2f} {r['gti_wm2']:>8.0f}"
              f" {r['predicted_kw']:>8.2f} {r['actual_pr']:>8.4f}"
              f" {'YES' if r['clipped'] else '':>5}")

if __name__ == "__main__":
    main()
