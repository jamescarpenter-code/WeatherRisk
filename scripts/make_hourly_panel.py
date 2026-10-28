"""Pre-shift workload panel: one panel per forecast hour of a single shift.

Usage: make_hourly_panel.py <grid_json> <shift_date YYYY-MM-DD> <F|N> <out.png> [fetch_label]
  F shift: panels at 09/12/15/18Z (same UTC date), accumulation from 06Z.
  N shift: panels at 15/18/21/00Z (00Z is the next UTC date), accumulation from 12Z.
Each panel: precip sum from window start through that hour (in, greens),
200 mb streamlines at that hour, Ellrod contours (orange, 2/4/8),
icing-potential hours accumulated from window start through that hour
(blue hatch: / = 3-5h, // = 6+h), VATSIM KZJX boundary.
Colors follow AWC conventions: precip greens, icing blue, turbulence orange.
Workload badge per panel uses the standing shift-string rule applied to
cumulative-to-hour in-boundary stats (so the last panel approximates the
full-shift badge):
  HIGH if Ellrod max >= 8, or icing>=6h over >=50% of boundary,
        or precip >1.0in over >=10% of boundary.
  MEDIUM if Ellrod max >= 4, or icing>=3h over >=25%,
        or precip >0.5in over >=10%.
  Else LOW.
Grid JSON: {"pts":[[lat,lon],...], "data":[Open-Meteo hourly,...]} on the
24-35.25N, 88.5-76.5W grid at 0.75 deg spacing.
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from datetime import date, timedelta

grid_json, start, shift, out = sys.argv[1:5]
fetch_label = sys.argv[5] if len(sys.argv) > 5 else "GFS via Open-Meteo"
shift = shift.upper()
if shift == "F":
    panel_hours = [9, 12, 15, 18]
    win_start = 6
    shift_label = "F 0515-1315"
else:
    panel_hours = [15, 18, 21, 0]
    win_start = 12
    shift_label = "N 1300-2100"

gj = json.load(open(grid_json))
pts = gj["pts"]; data = gj["data"]
lats = sorted(set(p[0] for p in pts)); lons = sorted(set(p[1] for p in pts))
nl, no = len(lats), len(lons)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
kz = json.load(open(os.path.join(DATA_DIR, "kzjx_boundary.geojson")))
g = kz["geometry"]
if g["type"] == "MultiPolygon":
    ring = np.array(g["coordinates"][0][0])
else:  # Polygon
    ring = np.array(g["coordinates"][0])
inside = np.array([Path(ring).contains_point((lo, la)) for (la, lo) in pts])
states = json.load(open(os.path.join(DATA_DIR, "ne_states.geojson")))

def uv(s, d):
    s = (s or 0) / 3.6; r = np.radians(d or 0); return -s * np.sin(r), -s * np.cos(r)

y0, m0, d0 = map(int, start.split("-"))
base = date(y0, m0, d0)
# UTC date for each panel hour: N 00Z panel is next UTC day; all others base day
panel_dates = []
for hh in panel_hours:
    if shift == "N" and hh == 0:
        panel_dates.append(base + timedelta(days=1))
    else:
        panel_dates.append(base)

# Ordered list of (date, hour) from window start through the last panel hour
seq = []
d = base
h = win_start
last_day, last_h = panel_dates[-1], panel_hours[-1]
while (d, h) <= (last_day, last_h):
    seq.append((d, h))
    h += 1
    if h == 24:
        h = 0; d += timedelta(days=1)

fig, axes = plt.subplots(2, 2, figsize=(18, 10.4))
fig.suptitle(f"ZJX pre-shift workload — {base.strftime('%a %b %d, %Y')} — {shift_label} ET (panels by forecast hour)",
             fontsize=17, weight="bold")
levels = [0, 0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0]
for ax, (pday, ph) in zip(axes.flat, zip(panel_dates, panel_hours)):
    # hours to accumulate: window start through this panel hour
    upto = seq.index((pday, ph)) + 1
    acc = seq[:upto]
    precip = np.zeros((nl, no)); ice = np.zeros((nl, no))
    U300 = np.full((nl, no), np.nan); V300 = np.full_like(U300, np.nan)
    U500 = np.full_like(U300, np.nan); V500 = np.full_like(U300, np.nan)
    Z300 = np.full_like(U300, np.nan); Z500 = np.full_like(U300, np.nan)
    U200 = np.full_like(U300, np.nan); V200 = np.full_like(U300, np.nan)
    for (la, lo), loc in zip(pts, data):
        hh_data = loc["hourly"]; t = hh_data["time"]; r = lats.index(la); c = lons.index(lo)
        for (ad, ah) in acc:
            i = t.index(f"{ad.strftime('%Y-%m-%d')}T{ah:02d}:00")
            precip[r, c] += hh_data["precipitation"][i] or 0.0
            for lev in ("850", "700", "500"):
                temp = hh_data[f"temperature_{lev}hPa"][i]; rh = hh_data[f"relative_humidity_{lev}hPa"][i]
                if temp is not None and rh is not None and -18 <= temp <= 0 and rh >= 75:
                    ice[r, c] += 1; break
        i = t.index(f"{pday.strftime('%Y-%m-%d')}T{ph:02d}:00")
        U300[r, c], V300[r, c] = uv(hh_data["wind_speed_300hPa"][i], hh_data["wind_direction_300hPa"][i])
        U500[r, c], V500[r, c] = uv(hh_data["wind_speed_500hPa"][i], hh_data["wind_direction_500hPa"][i])
        Z300[r, c] = hh_data["geopotential_height_300hPa"][i]; Z500[r, c] = hh_data["geopotential_height_500hPa"][i]
        U200[r, c], V200[r, c] = uv(hh_data["wind_speed_200hPa"][i], hh_data["wind_direction_200hPa"][i])
    precip = precip / 25.4
    dUdy, dUdx = np.gradient(U300, 0.75, 0.75); dVdy, dVdx = np.gradient(V300, 0.75, 0.75)
    coslat = np.cos(np.radians(lats))[:, None]
    dUdx = dUdx / (111320 * coslat); dUdy = dUdy / 111320
    dVdx = dVdx / (111320 * coslat); dVdy = dVdy / 111320
    DEF = np.sqrt((dUdx - dVdy) ** 2 + (dVdx + dVdy) ** 2)
    TI = DEF * np.hypot(U300 - U500, V300 - V500) / np.maximum(Z300 - Z500, 500.0) * 1e7
    Lon, Lat = np.meshgrid(lons, lats)
    ax.contourf(Lon, Lat, precip, levels=levels, cmap="Greens", extend="max", alpha=0.85)
    for feat in states["features"]:
        geom = feat["geometry"]
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        for poly in polys:
            for ring2 in poly:
                ax.plot([p[0] for p in ring2], [p[1] for p in ring2], color="#444444", lw=0.5)
    ax.plot(ring[:, 0], ring[:, 1], color="#b00000", lw=1.6, linestyle="--")
    cs = ax.contourf(Lon, Lat, ice, levels=[2.5, 5.5, 12.5], colors="none", hatches=["/", "//"])
    for col in getattr(cs, 'collections', [cs]):
        col.set_edgecolor("#0066cc"); col.set_linewidth(0.5)
    ax.contour(Lon, Lat, TI, levels=[2, 4, 8], colors="#e67300", linewidths=[0.8, 1.2, 1.8])
    ax.streamplot(Lon, Lat, U200, V200, density=0.7, color="#555555", linewidth=0.6, arrowsize=0.7)
    for name, (x, y) in {"JAX": (-81.66, 30.33), "SAV": (-81.20, 32.13), "TLH": (-84.35, 30.39),
                         "TPA": (-82.53, 27.98), "ORL": (-81.38, 28.55)}.items():
        ax.plot(x, y, "ko", ms=3)
        ax.text(x + 0.12, y + 0.1, name, fontsize=7, weight="bold",
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=0.5))
    pi = precip.ravel()[inside]; ti = TI.ravel()[inside]; ic = ice.ravel()[inside]
    ti_max = np.nanmax(ti); pmax = pi.max(); imax = ic.max()
    if ti_max >= 8 or np.mean(ic >= 6) >= 0.50 or np.mean(pi > 1.0) >= 0.10:
        wl, wcol = "HIGH", "#c00000"
    elif ti_max >= 4 or np.mean(ic >= 3) >= 0.25 or np.mean(pi > 0.5) >= 0.10:
        wl, wcol = "MEDIUM", "#d88000"
    else:
        wl, wcol = "LOW", "#2e7d32"
    ax.set_title(f"{ph:02d}Z (accumulated from {win_start:02d}Z)", fontsize=12, weight="bold", loc="left")
    ax.text(0.02, 0.96, f"Workload: {wl}", transform=ax.transAxes, fontsize=11, weight="bold",
            color="white", va="top",
            bbox=dict(facecolor=wcol, edgecolor="none", pad=4))
    ax.text(0.02, 0.02, f"Rain max {pmax:.2f}\u2033 \u00b7 Ellrod max {ti_max:.1f} \u00b7 Icing max {imax:.0f}h",
            transform=ax.transAxes, fontsize=8, va="bottom",
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=2))
    ax.set_xlim(-88.5, -76.0); ax.set_ylim(23.5, 35.0)
    ax.set_xticks([]); ax.set_yticks([])
fig.text(0.5, 0.01,
         f"{fetch_label} \u00b7 Precip sum from window start through panel hour (in, greens) \u00b7 200 mb streamlines at panel hour \u00b7 "
         "Ellrod contours 2/4/8 (orange, x1e-7 s^-2) \u00b7 Icing-potential hours accumulated: / = 3\u20135h, // = 6+h (blue) \u00b7 "
         "Workload per panel from cumulative in-boundary stats (standing rule) \u00b7 Boundary: VATSIM KZJX polygon (not FAA-official)",
         ha="center", fontsize=9, style="italic", wrap=True)
plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.savefig(out, dpi=150)
print("wrote", out)
