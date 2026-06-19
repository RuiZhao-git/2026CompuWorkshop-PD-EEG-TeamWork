#!/usr/bin/env python
"""Generate figures/spectrum_hypotheses.svg.

The hero figure for the Hypotheses slide: the group-average posterior EEG power
spectrum, Control vs PD (relative power, +/- SEM), with the three predicted
changes annotated directly on the curves. Real data from results/group_psd.csv.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PSD = os.path.join(REPO, "results", "group_psd.csv")

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Helvetica, Arial, sans-serif"
BLUE = "#185FA5"
CORAL = "#a8431f"
INK = "#0f172a"
SLATE = "#334155"
GREY = "#64748b"
MUTE = "#94a3b8"
LINE = "#e2e8f0"

W, H = 920, 430
FMIN, FMAX = 3.0, 34.0
YMAX = 0.115
PX0, PX1 = 84, 846     # plot box x (left axis .. right)
PY0, PY1 = 60, 372     # plot box y (top .. bottom axis)

d = pd.read_csv(PSD)
d = d[(d.freq_hz >= FMIN) & (d.freq_hz <= FMAX)].reset_index(drop=True)


def X(f):
    return PX0 + (f - FMIN) / (FMAX - FMIN) * (PX1 - PX0)


def Y(p):
    return PY1 - (p / YMAX) * (PY1 - PY0)


def val(col, f):
    i = (d.freq_hz - f).abs().idxmin()
    return float(d.loc[i, col])


P = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, size, fill, weight=400, anchor="start", family=SANS, extra=""):
    P.append(f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" font-family="{family}"{extra}>{esc(s)}</text>')


def line(x1, y1, x2, y2, stroke, sw=1, dash=None, marker=None):
    s = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"'
    if dash:
        s += f' stroke-dasharray="{dash}"'
    if marker:
        s += f' marker-end="url(#{marker})"'
    P.append(s + "/>")


def curve_path(col):
    pts = [f"{X(f):.1f} {Y(p):.1f}" for f, p in zip(d.freq_hz, d[col])]
    return "M " + " L ".join(pts)


def band_path(mcol, scol):
    up = [(X(f), Y(m + s)) for f, m, s in zip(d.freq_hz, d[mcol], d[scol])]
    lo = [(X(f), Y(m - s)) for f, m, s in zip(d.freq_hz, d[mcol], d[scol])]
    pts = up + lo[::-1]
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


P.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{SANS}">')
P.append('<defs>')
for mid, col in [("up", CORAL), ("dn", BLUE), ("lf", SLATE)]:
    P.append(f'<marker id="{mid}" markerWidth="9" markerHeight="9" refX="6" refY="4.5" '
             f'orient="auto"><path d="M0,0 L0,9 L8,4.5 z" fill="{col}"/></marker>')
P.append('</defs>')
P.append(f'<rect width="{W}" height="{H}" rx="16" fill="#ffffff"/>')

# frequency-band shading + labels
for lo, hi, fill, lbl in [(4, 8, "#f0fdf4", "THETA"), (8, 13, "#fffbeb", "ALPHA"),
                          (13, 30, "#f1f5f9", "BETA")]:
    P.append(f'<rect x="{X(lo):.1f}" y="{PY0}" width="{X(hi)-X(lo):.1f}" height="{PY1-PY0}" '
             f'fill="{fill}"/>')
    T((X(lo) + X(hi)) / 2, PY1 - 10, lbl, 11.5, MUTE, 600, "middle")

# axes
line(PX0, PY1, PX1, PY1, "#cbd5e1", 1.4)          # x axis
line(PX0, PY0, PX0, PY1, "#cbd5e1", 1.4)          # y axis
for f in [5, 10, 15, 20, 25, 30]:
    line(X(f), PY1, X(f), PY1 + 5, "#cbd5e1", 1.2)
    T(X(f), PY1 + 22, str(f), 13, GREY, 400, "middle")
for p in [0.0, 0.05, 0.10]:
    line(PX0 - 5, Y(p), PX0, Y(p), "#cbd5e1", 1.2)
    T(PX0 - 10, Y(p) + 4, f"{p:.2f}", 12, MUTE, 400, "end")
T((PX0 + PX1) / 2, PY1 + 44, "Frequency (Hz)", 15, SLATE, 500, "middle")
T(26, (PY0 + PY1) / 2, "Relative power", 15, SLATE, 500, "middle",
  extra=f' transform="rotate(-90 26 {(PY0+PY1)/2:.0f})"')

# SEM bands then curves
P.append(f'<path d="{band_path("control_mean","control_sem")}" fill="{BLUE}" fill-opacity="0.16"/>')
P.append(f'<path d="{band_path("pd_mean","pd_sem")}" fill="{CORAL}" fill-opacity="0.16"/>')
P.append(f'<path d="{curve_path("control_mean")}" fill="none" stroke="{BLUE}" stroke-width="2.8" stroke-linejoin="round"/>')
P.append(f'<path d="{curve_path("pd_mean")}" fill="none" stroke="{CORAL}" stroke-width="2.8" stroke-linejoin="round"/>')

# ---- numbered markers: the three changes, keyed to the list above the figure ----
def marker(num, fx, fy, tip_f, tip_p):
    cx, cy = X(fx), Y(fy)
    line(cx, cy, X(tip_f), Y(tip_p), "#94a3b8", 1.4)
    P.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="14" fill="{SLATE}" stroke="#ffffff" stroke-width="2"/>')
    T(cx, cy + 6, str(num), 17, "#ffffff", 700, "middle")

marker(1, 5.6, 0.066, 6.4, 0.085)     # theta: PD curve above control
marker(2, 8.4, 0.110, 8.4, 0.101)     # alpha peak (slowing)
marker(3, 20.0, 0.050, 20.0, 0.020)   # beta: control curve above PD

# legend (top-right inside plot)
lx, ly = PX1 - 168, PY0 + 16
P.append(f'<rect x="{lx-12}" y="{ly-16}" width="178" height="50" rx="9" fill="#ffffff" fill-opacity="0.86" stroke="{LINE}"/>')
line(lx, ly, lx + 26, ly, BLUE, 3)
T(lx + 34, ly + 5, "Control  (n = 49)", 13.5, SLATE, 500)
line(lx, ly + 22, lx + 26, ly + 22, CORAL, 3)
T(lx + 34, ly + 27, "PD  (n = 100)", 13.5, SLATE, 500)

P.append("</svg>")

out = os.path.join(HERE, "spectrum_hypotheses.svg")
with open(out, "w") as fh:
    fh.write("".join(P))
print("wrote", out)
