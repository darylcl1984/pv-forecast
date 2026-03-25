#!/usr/bin/env python3
"""
Solar PR Calibration Tool
Run locally: python calibrate_pr.py

Reads Sungrow CSV exports from current directory and fetches matching
GTI data from Open-Meteo to back-calculate your actual Performance Ratio.
"""

import pandas as pd
import requests
import json
import glob
import sys

# ── System constants (edit to match your setup) ──
PV_KW      = 6.6    # Total panel capacity in kW
INVERTER_KW = 5.0   # Inverter output limit in kW
ASSUMED_PR = 0.80   # Starting performance ratio (typical range: 0.75–0.85)
TILT       = 25     # Panel tilt in degrees
AZIMUTH    = 180    # Panel azimuth (Open-Meteo convention: 0=south, 180=north)
LAT        = 0.0    # Your latitude  — replace before running
LON        = 0.0    # Your longitude — replace before running

def load_sungrow_csvs(paths):
    dfs = []
    for f in paths:
        df = pd.read_csv(f, encoding='utf-8-sig')
        df.columns = df.columns.str.strip()
        df['Time'] = pd.to_datetime(df['Time'])
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True).sort_values('Time').reset_index(drop=True)

def fetch_gti(start_date, end_date):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&hourly=global_tilted_irradiance"
        f"&timezone=auto"
        f"&start_date={start_date}&end_date={end_date}"
        f"&tilt={TILT}&azimuth={AZIMUTH}"
    )
    resp = requests.get(url, timeout=15)
    if resp.status_code != 200:
        print(f"API error {resp.status_code}, trying archive API...")
        url2 = url.replace("api.open-meteo.com/v1/forecast", "archive-api.open-meteo.com/v1/archive")
        resp = requests.get(url2, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return pd.DataFrame({
        'hour': pd.to_datetime(data['hourly']['time']),
        'gti_wm2': data['hourly']['global_tilted_irradiance']
    })

def kw_at_gti(gti):
    return min(INVERTER_KW, (PV_KW * ASSUMED_PR * gti) / 1000)

def main():
    # Find CSVs
    paths = sorted(glob.glob("*.csv"))
    if not paths:
        print("No CSV files found in current directory.")
        print("Place your Sungrow export CSVs here and re-run.")
        sys.exit(1)

    print(f"Found {len(paths)} CSV file(s): {', '.join(paths)}")
    actual = load_sungrow_csvs(paths)
    actual['PV_kW'] = actual['PV(W)'] / 1000.0
    actual['hour'] = actual['Time'].dt.floor('h')

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
    merged['clipped'] = merged['pv_kw_mean'] >= (INVERTER_KW * 0.95)
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
