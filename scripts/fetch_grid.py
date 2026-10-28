#!/usr/bin/env python3
"""Fetch a GFS grid from Open-Meteo for the ZJX workload imagery scripts.

Usage: fetch_grid.py --start YYYY-MM-DD --end YYYY-MM-DD --out grid.json

Grid: 24-35.25N, 88.5-76.5W at 0.75 deg spacing (272 points), model
gfs_seamless, hourly, UTC. Output: {"pts": [[lat, lon], ...],
"data": [Open-Meteo hourly, ...]} — the format make_string_panel.py,
make_gfs_map.py and make_hourly_panel.py consume. No API key required.
"""
import argparse
import json
import urllib.parse
import urllib.request

VARIABLES = [
    "precipitation",
    "temperature_850hPa", "temperature_700hPa", "temperature_500hPa",
    "relative_humidity_850hPa", "relative_humidity_700hPa",
    "relative_humidity_500hPa",
    "wind_speed_300hPa", "wind_direction_300hPa",
    "wind_speed_500hPa", "wind_direction_500hPa",
    "geopotential_height_300hPa", "geopotential_height_500hPa",
    "wind_speed_200hPa", "wind_direction_200hPa",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="first date, YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="last date, YYYY-MM-DD")
    ap.add_argument("--out", required=True, help="output grid JSON path")
    args = ap.parse_args()

    lats = [24 + 0.75 * i for i in range(16)]
    lons = [-88.5 + 0.75 * i for i in range(17)]
    pts = [[la, lo] for la in lats for lo in lons]
    params = {
        "latitude": ",".join(str(la) for la, _ in pts),
        "longitude": ",".join(str(lo) for _, lo in pts),
        "hourly": ",".join(VARIABLES),
        "models": "gfs_seamless",
        "start_date": args.start,
        "end_date": args.end,
        "timezone": "UTC",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "zjx-workload-imagery/1.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        raw = json.load(resp)
    data = raw if isinstance(raw, list) else [raw]
    assert len(data) == len(pts), f"expected {len(pts)} points, got {len(data)}"
    times = data[0]["hourly"]["time"]
    for t in (f"{args.start}T00:00", f"{args.end}T23:00"):
        assert t in times, f"missing hour {t} in fetched grid"
    json.dump({"pts": pts, "data": data}, open(args.out, "w"))
    print(f"wrote {args.out} ({len(pts)} points, {args.start} to {args.end})")


if __name__ == "__main__":
    main()
