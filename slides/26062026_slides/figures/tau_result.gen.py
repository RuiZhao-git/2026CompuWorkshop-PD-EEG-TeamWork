#!/usr/bin/env python
"""Generate figures/tau_result.svg -- the "Does the model separate ..." slide.

Three parts:
  LEFT   the separation  : Control vs PD fitted-tau distributions (overlap is honest).
  RIGHT  is it real?      : the parameter-recovery scatter (unbiased), and a
                            signal-vs-noise bar (group effect +3.25 ms is ~6x the
                            +/-0.5 ms fitting error).
Data: results/fitted_tau.csv, results/tau_recovery.csv.
"""
import os

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Helvetica, Arial, sans-serif"
BLUE = "#185FA5"
CORAL = "#a8431f"
INK = "#0f172a"
SLATE = "#334155"
GREY = "#64748b"
MUTE = "#94a3b8"
LINE = "#e2e8f0"

W, H = 1180, 440
P = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, size, fill, weight=400, anchor="start", family=SANS, extra=""):
    P.append(f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" font-family="{family}"{extra}>{esc(s)}</text>')


def raw(s):
    P.append(s)


def rrect(x, y, w, h, r, fill, stroke=None, sw=1):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    P.append(s + "/>")


def line(x1, y1, x2, y2, stroke, sw=1, dash=None, marker=None, op=None):
    s = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"'
    if dash:
        s += f' stroke-dasharray="{dash}"'
    if op:
        s += f' opacity="{op}"'
    if marker:
        s += f' marker-end="url(#{marker})"'
    P.append(s + "/>")


P.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{SANS}">')
P.append('<defs>')
P.append(f'<marker id="sh" markerWidth="9" markerHeight="9" refX="6.5" refY="4.5" orient="auto">'
         f'<path d="M0,0 L0,9 L8,4.5 z" fill="{GREY}"/></marker>')
P.append('</defs>')
P.append(f'<rect width="{W}" height="{H}" rx="16" fill="#ffffff"/>')
line(560, 36, 560, 410, LINE, 1.4)

# ============================================================ LEFT: THE SEPARATION
T(24, 28, "THE SEPARATION", 14.5, GREY, 600)
T(170, 28, "fitted τ_inh per subject, Control vs PD", 12.5, MUTE, 400)

ft = pd.read_csv(os.path.join(REPO, "results", "fitted_tau.csv"))
ctrl = ft[ft.group == "Control"].fitted_tau_ms.values
pdt = ft[ft.group == "PD"].fitted_tau_ms.values

TMIN, TMAX = 11, 27
DX0, DX1 = 84, 536
DY0, DY1 = 104, 286


def DX(t):
    return DX0 + (t - TMIN) / (TMAX - TMIN) * (DX1 - DX0)


grid = np.linspace(TMIN, TMAX, 240)
kc = gaussian_kde(ctrl, bw_method=0.35)(grid)
kp = gaussian_kde(pdt, bw_method=0.35)(grid)
gmax = max(kc.max(), kp.max())


def DY(d):
    return DY1 - (d / gmax) * (DY1 - DY0) * 0.92


def density(k, color):
    pts = [f"{DX(t):.1f} {DY(d):.1f}" for t, d in zip(grid, k)]
    area = f"M {DX(TMIN):.1f} {DY1:.1f} L " + " L ".join(pts) + f" L {DX(TMAX):.1f} {DY1:.1f} Z"
    raw(f'<path d="{area}" fill="{color}" fill-opacity="0.16"/>')
    raw(f'<path d="M {" L ".join(pts)}" fill="none" stroke="{color}" stroke-width="2.6"/>')


# axis
line(DX0, DY1, DX1, DY1, "#cbd5e1", 1.4)
for t in [12, 16, 20, 24]:
    line(DX(t), DY1, DX(t), DY1 + 5, "#cbd5e1", 1.2)
    T(DX(t), DY1 + 21, str(t), 12.5, GREY, 400, "middle")
T((DX0 + DX1) / 2, DY1 + 36, "fitted τ_inh (ms)", 13.5, SLATE, 500, "middle")

density(kc, BLUE)
density(kp, CORAL)
mc, mp = float(np.median(ctrl)), float(np.median(pdt))
for m, color in [(mc, BLUE), (mp, CORAL)]:
    line(DX(m), DY1, DX(m), DY0 + 24, color, 1.6, dash="4 3")
# +3.25 ms between the medians, near the top
yt = DY0 + 20
line(DX(mc) + 3, yt, DX(mp) - 3, yt, GREY, 1.8, marker="sh")
T((DX(mc) + DX(mp)) / 2, yt - 7, "+3.25 ms", 13, GREY, 700, "middle")
# legend (top-left)
raw(f'<rect x="{DX0+10}" y="{DY0+10}" width="15" height="4.5" rx="2" fill="{BLUE}"/>')
T(DX0 + 32, DY0 + 18, "Control", 12.5, BLUE, 600)
raw(f'<rect x="{DX0+10}" y="{DY0+28}" width="15" height="4.5" rx="2" fill="{CORAL}"/>')
T(DX0 + 32, DY0 + 36, "PD", 12.5, CORAL, 600)
# honest note
T(24, 344, "Medians differ by +3.25 ms (Control 18.25, PD 21.5 ms).", 13, SLATE, 500)
T(24, 366, "But individuals overlap: a random PD is higher only ≈ 68% of the time.", 12.5, GREY, 400)

# ============================================================ RIGHT: IS IT REAL?
T(584, 28, "IS THE DIFFERENCE REAL?", 14.5, GREY, 600)
T(820, 28, "validate the fit, then compare to the effect", 12.5, MUTE, 400)

rec = pd.read_csv(os.path.join(REPO, "results", "tau_recovery.csv"))
RMIN, RMAX = 11, 29
RX0, RX1 = 624, 812
RY0, RY1 = 90, 248


def RX(t):
    return RX0 + (t - RMIN) / (RMAX - RMIN) * (RX1 - RX0)


def RY(t):
    return RY1 - (t - RMIN) / (RMAX - RMIN) * (RY1 - RY0)


# diagonal (perfect recovery)
line(RX(RMIN), RY(RMIN), RX(RMAX), RY(RMAX), "#cbd5e1", 1.6, dash="4 4")
T(RX(12.5), RY(20.5), "perfect", 11, MUTE, 400)
T(RX(12.5), RY(19.0), "recovery", 11, MUTE, 400)
# axes
line(RX0, RY1, RX1, RY1, "#cbd5e1", 1.3)
line(RX0, RY0, RX0, RY1, "#cbd5e1", 1.3)
for t in [12, 18, 24]:
    line(RX(t), RY1, RX(t), RY1 + 5, "#cbd5e1", 1.1)
    T(RX(t), RY1 + 19, str(t), 11.5, MUTE, 400, "middle")
    line(RX0 - 5, RY(t), RX0, RY(t), "#cbd5e1", 1.1)
    T(RX0 - 9, RY(t) + 4, str(t), 11.5, MUTE, 400, "end")
T((RX0 + RX1) / 2, RY1 + 40, "true τ (ms)", 12.5, SLATE, 500, "middle")
T(RX0 - 36, (RY0 + RY1) / 2, "fitted τ (ms)", 12.5, SLATE, 500, "middle",
  extra=f' transform="rotate(-90 {RX0-36} {(RY0+RY1)/2:.0f})"')
for _, r in rec.iterrows():
    raw(f'<circle cx="{RX(r.tau_true_ms):.1f}" cy="{RY(r.tau_fit_ms):.1f}" r="4.5" '
        f'fill="{BLUE}" fill-opacity="0.85"/>')
# recovery summary to the right of the scatter
sx = 862
T(sx, 116, "The fit is unbiased.", 15, INK, 600)
T(sx, 144, "mean error  −0.1 ms", 13, SLATE, 400)
T(sx, 166, "typical error  ±0.5 ms", 13, SLATE, 400)
T(sx, 188, "worst error  1.75 ms", 13, MUTE, 400)

# ---- signal vs noise: the effect dwarfs the fitting error ----
T(584, 304, "The +3.25 ms difference is 6× the fitting error:", 14.5, INK, 600)
bx = 760
ppm = (1146 - bx) / 3.7   # px per ms
by1, by2 = 340, 376
rrect(bx, by1 - 9, 0.5 * ppm, 18, 4, "#cbd5e1")
T(bx - 12, by1 + 5, "fitting error", 12.5, GREY, 500, "end")
T(bx + 0.5 * ppm + 9, by1 + 5, "±0.5 ms", 12, GREY, 500)
rrect(bx, by2 - 9, 3.25 * ppm, 18, 4, CORAL)
T(bx - 12, by2 + 5, "group difference", 12.5, CORAL, 600, "end")
T(bx + 3.25 * ppm + 9, by2 + 5, "+3.25 ms", 12, CORAL, 600)

P.append("</svg>")
out = os.path.join(HERE, "tau_result.svg")
with open(out, "w") as fh:
    fh.write("".join(P))
print("wrote", out, "| medians:", round(mc, 2), round(mp, 2))
