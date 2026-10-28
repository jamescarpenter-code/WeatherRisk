#!/usr/bin/env python3
"""Write the GitHub Pages index.html for a rendered site directory.

Usage: build_site.py --site-dir site --updated "2026-10-28 23:08 UTC"
Expects string-panel-F.png, string-panel-N.png, hourly-panel-F.png and
hourly-panel-N.png already in the site dir.
"""
import argparse
import os

PANELS = [
    ("string-panel-F.png", "Shift string — next 5 days (F shifts)"),
    ("string-panel-N.png", "Shift string — next 5 days (N shifts)"),
    ("hourly-panel-F.png", "Today — hourly workload (F shift)"),
    ("hourly-panel-N.png", "Today — hourly workload (N shift)"),
]

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
{sections}
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-dir", required=True)
    ap.add_argument("--updated", required=True)
    args = ap.parse_args()
    sections = []
    for name, heading in PANELS:
        assert os.path.exists(os.path.join(args.site_dir, name)), f"missing {name}"
        sections.append(f"<h2>{heading}</h2>\n<img src=\"{name}\" alt=\"{heading}\">")
    with open(os.path.join(args.site_dir, "index.html"), "w") as f:
        f.write(HTML.format(updated=args.updated, sections="\n".join(sections)))
    print(f"wrote {os.path.join(args.site_dir, 'index.html')}")


if __name__ == "__main__":
    main()
