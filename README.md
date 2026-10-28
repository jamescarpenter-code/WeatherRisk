# ZJX workload imagery

GFS-based workload graphics for FAA ARTCC ZJX (Jacksonville Center) airspace,
rendered twice daily by GitHub Actions and published to GitHub Pages.

## What it renders

- `string-panel.png` — one panel per day for the next 4 days (N shifts):
  precipitation sum in inches, 200 mb streamlines, Ellrod turbulence contours,
  icing-potential hatching, plus a per-day workload badge.
- `hourly-panel.png` — four panels for one N shift (15/18/21/00Z) with
  precip/icing accumulated from 12Z and a per-hour workload badge.

Colors follow AWC conventions: precipitation in greens, Ellrod turbulence
contours in orange, icing-potential hatching in blue.

Workload rule (from in-boundary GFS stats): HIGH if Ellrod max ≥ 8, icing 6+ h
over ≥ 50% of the area, or rain > 1″ over ≥ 10%; MEDIUM if Ellrod max ≥ 4,
icing 3+ h over ≥ 25%, or rain > 0.5″ over ≥ 10%; else LOW.

## Sources and caveats

- Model: GFS (`gfs_seamless`) via Open-Meteo, no API key required.
- Boundary: the real VATSIM vatspy-data-project KZJX polygon (53 vertices,
  `data/kzjx_boundary.geojson`) — a VATSIM mirror, NOT FAA-official.
- Decision-support only. AWC, SPC and NHC remain authoritative.

## Run it locally

```sh
pip install -r requirements.txt
python scripts/fetch_grid.py --start 2026-10-29 --end 2026-11-01 --out grid.json
python scripts/make_string_panel.py grid.json 2026-10-29 4 N string-panel.png
python scripts/make_hourly_panel.py grid.json 2026-10-29 N hourly-panel.png
```

`make_gfs_map.py` renders a single-day map (precip + 200 mb barbs and
streamlines, Ellrod contours, icing hatching) for a given date and shift:
`make_gfs_map.py <grid_json> <date> <F|N> <out.png>`.

## Automation

`.github/workflows/update-imagery.yml` runs at 10:30 and 22:30 UTC daily
(06:30/18:30 EDT, 05:30/17:30 EST) and deploys `site/` to GitHub Pages.
Repo Settings → Pages → Source: GitHub Actions. No secrets are needed.
