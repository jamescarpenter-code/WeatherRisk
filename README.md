# ZJX workload imagery

GFS-based workload graphics for FAA ARTCC ZJX (Jacksonville Center) airspace,
rendered twice daily by GitHub Actions and published to GitHub Pages.

## What it renders

- `string-panel-F.png` / `string-panel-N.png` — one panel per day for the
  next 5 days, F shifts and N shifts respectively: precipitation sum in
  inches, 200 mb streamlines, Ellrod turbulence contours, icing-potential
  hatching, plus a per-day workload badge.
- `hourly-panel-F.png` / `hourly-panel-N.png` — four panels for one shift
  (F: 09/12/15/18Z with precip/icing accumulated from 06Z; N: 15/18/21/00Z
  with precip/icing accumulated from 12Z) and a per-hour workload badge.

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

`.github/workflows/update-imagery.yml` runs at 09:00 and 17:00 UTC daily
and deploys `site/` to GitHub Pages. 09:00 UTC lands just before the F shift
(0515–1315 ET); 17:00 UTC lands at the start of the N shift (1300–2100 ET).
Repo Settings → Pages → Source: GitHub Actions. No secrets are needed.
