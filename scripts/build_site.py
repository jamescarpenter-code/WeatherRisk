#!/usr/bin/env python3
"""Write the GitHub Pages index.html for a rendered site directory.

Usage: build_site.py --site-dir site --updated "2026-10-28 22:30 UTC"
Expects string-panel.png and hourly-panel.png already in the site dir.
"""
import argparse
import os

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ZJX workload imagery</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 1100px; margin: 0 auto; padding: 1rem; color: #222; }}
  img {{ width: 100%; height: auto; border: 1px solid #ccc; }}
  .note {{ color: #555; font-size: 0.9rem; }}
</style>
</head>
<body>
<h1>ZJX workload imagery</h1>
<p class="note">GFS via Open-Meteo. Last updated: {updated}. Colors follow AWC
conventions: precipitation in greens, Ellrod turbulence contours in orange,
icing-potential hatching in blue. Workload badges use the standing rule: HIGH
if Ellrod max &ge; 8, icing 6+&nbsp;h over &ge; 50% of the area, or rain
&gt; 1&Prime; over &ge; 10%; MEDIUM if Ellrod max &ge; 4, icing 3+&nbsp;h over
&ge; 25%, or rain &gt; 0.5&Prime; over &ge; 10%; else LOW. Boundary: VATSIM
KZJX polygon (a VATSIM mirror, NOT FAA-official). Decision-support only;
AWC, SPC and NHC remain authoritative.</p>
<h2>Shift string &mdash; next 4 days (N shifts)</h2>
<img src="string-panel.png" alt="ZJX shift-string workload panel">
<h2>Today &mdash; hourly workload (N shift)</h2>
<img src="hourly-panel.png" alt="ZJX hourly workload panel">
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-dir", required=True)
    ap.add_argument("--updated", required=True)
    args = ap.parse_args()
    for name in ("string-panel.png", "hourly-panel.png"):
        assert os.path.exists(os.path.join(args.site_dir, name)), f"missing {name}"
    with open(os.path.join(args.site_dir, "index.html"), "w") as f:
        f.write(HTML.format(updated=args.updated))
    print(f"wrote {os.path.join(args.site_dir, 'index.html')}")


if __name__ == "__main__":
    main()
