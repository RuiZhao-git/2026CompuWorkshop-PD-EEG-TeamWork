#!/usr/bin/env python
"""Generate figures/model_dial.svg  -- the Wilson-Cowan model slide.

Three zones, left to right:
  1. MECHANISM  the model: 8 coupled E-I nodes, why it oscillates.
  2. THE DIAL   tau_inh -> alpha peak frequency tuning curve (results/peak_curve.csv),
                with Control and PD marked: one knob sets the rhythm.
  3. THE RHYTHM the two simulated waveforms (results/model_waveforms.csv).
"""
import math
import os

import pandas as pd

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

W, H = 1200, 460
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


def circle(cx, cy, r, fill, stroke=None, sw=1, dash=None):
    s = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    if dash:
        s += f' stroke-dasharray="{dash}"'
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
P.append(f'<marker id="ex" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">'
         f'<path d="M0,0 L0,9 L8,4.5 z" fill="{BLUE}"/></marker>')
P.append(f'<marker id="bar" markerWidth="10" markerHeight="16" refX="3" refY="8" orient="auto">'
         f'<rect x="1" y="1.5" width="2.8" height="13" rx="1.2" fill="{CORAL}"/></marker>')
P.append(f'<marker id="sh" markerWidth="9" markerHeight="9" refX="6.5" refY="4.5" orient="auto">'
         f'<path d="M0,0 L0,9 L8,4.5 z" fill="{GREY}"/></marker>')
P.append('</defs>')
P.append(f'<rect width="{W}" height="{H}" rx="16" fill="#ffffff"/>')

# zone dividers
line(396, 40, 396, 420, LINE, 1.4)
line(804, 40, 804, 420, LINE, 1.4)

# ================================================================ ZONE 1: MECHANISM
T(28, 30, "THE MODEL: AN E–I LOOP", 14.5, GREY, 600)

# small all-to-all network ring
ncx, ncy, nr = 200, 104, 46
nodes = [(ncx + nr * math.cos(math.radians(-90 + i * 45)),
          ncy + nr * math.sin(math.radians(-90 + i * 45))) for i in range(8)]
for i in range(8):
    for j in range(i + 1, 8):
        line(nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1], "#9ec3f2", 0.8, op=0.5)
for i, (x, y) in enumerate(nodes):
    if i == 1:  # highlight one node
        circle(f"{x:.1f}", f"{y:.1f}", 11, "none", CORAL, 2, dash="3 2.5")
        circle(f"{x:.1f}", f"{y:.1f}", 7, CORAL)
    else:
        circle(f"{x:.1f}", f"{y:.1f}", 7, BLUE)
T(ncx, ncy + nr + 24, "8 nodes, all-to-all coupling", 13, SLATE, 500, "middle")

# zoom from the highlighted node to the E-I loop
hx, hy = nodes[1]
line(hx + 6, hy + 6, 248, 232, CORAL, 1.3, dash="4 3", op=0.6)
line(hx + 6, hy + 6, 150, 232, CORAL, 1.3, dash="4 3", op=0.6)

# the E-I loop
ex_c, in_c, ny = 150, 252, 300
circle(ex_c, ny, 30, BLUE)
T(ex_c, ny + 9, "E", 26, "#ffffff", 600, "middle")
T(ex_c, ny + 52, "excitatory", 13, SLATE, 400, "middle")
circle(in_c, ny, 30, CORAL)
T(in_c, ny + 9, "I", 26, "#ffffff", 600, "middle")
T(in_c, ny + 52, "inhibitory", 13, SLATE, 400, "middle")
# excites (E -> I, over the top)
raw(f'<path d="M {ex_c+26} {ny-16} Q {(ex_c+in_c)/2} {ny-58} {in_c-26} {ny-16}" '
    f'fill="none" stroke="{BLUE}" stroke-width="2.6" marker-end="url(#ex)"/>')
T((ex_c + in_c) / 2, ny - 48, "excites", 14, BLUE, 600, "middle")
# inhibits (I -> E, under the bottom)
raw(f'<path d="M {in_c-26} {ny+16} Q {(ex_c+in_c)/2} {ny+58} {ex_c+26} {ny+16}" '
    f'fill="none" stroke="{CORAL}" stroke-width="2.6" marker-end="url(#bar)"/>')
T((ex_c + in_c) / 2, ny + 64, "inhibits", 14, CORAL, 600, "middle")
# tau_inh knob tag
rrect(118, 388, 164, 30, 15, "#fdf1ec", CORAL, 1.4)
T(140, 408, "τ_inh", 14.5, CORAL, 700, "start")
T(180, 408, "the one knob", 13.5, SLATE, 500, "start")

# ================================================================ ZONE 2: THE DIAL
T(420, 30, "TURN τ_inh UP, THE RHYTHM SLOWS", 14.5, GREY, 600)

curve = pd.read_csv(os.path.join(REPO, "results", "peak_curve.csv"))
curve = curve[(curve.tau_inh_ms >= 12) & (curve.tau_inh_ms <= 26)]
TMIN, TMAX = 12, 26
HMIN, HMAX = 7, 13
DX0, DX1 = 470, 780
DY0, DY1 = 78, 372   # top, bottom


def DX(t):
    return DX0 + (t - TMIN) / (TMAX - TMIN) * (DX1 - DX0)


def DY(h):
    return DY1 - (h - HMIN) / (HMAX - HMIN) * (DY1 - DY0)


# alpha band shading (8-13 Hz)
rrect(DX0, DY(13), DX1 - DX0, DY(8) - DY(13), 0, "#fffbeb")
T(DX1 - 6, DY(12.4), "alpha band", 11, "#d8b46a", 600, "end")
# axes
line(DX0, DY1, DX1, DY1, "#cbd5e1", 1.4)
line(DX0, DY0, DX0, DY1, "#cbd5e1", 1.4)
for t in [14, 18, 22, 26]:
    line(DX(t), DY1, DX(t), DY1 + 5, "#cbd5e1", 1.2)
    T(DX(t), DY1 + 22, str(t), 13, GREY, 400, "middle")
for h in [8, 10, 12]:
    line(DX0 - 5, DY(h), DX0, DY(h), "#cbd5e1", 1.2)
    T(DX0 - 9, DY(h) + 4, str(h), 12.5, MUTE, 400, "end")
T((DX0 + DX1) / 2, DY1 + 44, "τ_inh  (ms)", 14, SLATE, 500, "middle")
T(434, (DY0 + DY1) / 2, "alpha peak  (Hz)", 14, SLATE, 500, "middle",
  extra=f' transform="rotate(-90 434 {(DY0+DY1)/2:.0f})"')
# the tuning curve
pts = " L ".join(f"{DX(t):.1f} {DY(h):.1f}" for t, h in zip(curve.tau_inh_ms, curve.simulated_peak_hz))
raw(f'<path d="M {pts}" fill="none" stroke="{SLATE}" stroke-width="2.8" stroke-linejoin="round"/>')
# Control and PD points
ctrl = (18.25, 9.25)
pdp = (21.5, 8.0)
# shift arrow control -> pd
raw(f'<path d="M {DX(ctrl[0])+11:.1f} {DY(ctrl[1])+4:.1f} Q {DX(20.4):.1f} {DY(8.0):.1f} '
    f'{DX(pdp[0])-2:.1f} {DY(pdp[1])-9:.1f}" fill="none" stroke="{GREY}" stroke-width="1.8" '
    f'stroke-dasharray="4 3" marker-end="url(#sh)"/>')
# Control point + label to its left, PD point + label to its right
circle(f"{DX(ctrl[0]):.1f}", f"{DY(ctrl[1]):.1f}", 8, BLUE, "#ffffff", 2)
T(DX(ctrl[0]) - 15, DY(ctrl[1]) - 5, "Control", 14.5, BLUE, 700, "end")
T(DX(ctrl[0]) - 15, DY(ctrl[1]) + 12, "18.25 ms · 9.25 Hz", 11.5, BLUE, 400, "end")
circle(f"{DX(pdp[0]):.1f}", f"{DY(pdp[1]):.1f}", 8, CORAL, "#ffffff", 2)
T(DX(pdp[0]) + 14, DY(pdp[1]) - 24, "PD", 14.5, CORAL, 700, "start")
T(DX(pdp[0]) + 14, DY(pdp[1]) - 7, "21.5 ms · 8 Hz", 11.5, CORAL, 400, "start")
T((DX0 + DX1) / 2, DY(7.35), "+3.25 ms longer τ  →  1.25 Hz slower", 12.5, GREY, 600, "middle")

# ================================================================ ZONE 3: THE RHYTHM
T(828, 30, "THE SIMULATED RHYTHM", 14.5, GREY, 600)

wav = pd.read_csv(os.path.join(REPO, "results", "model_waveforms.csv"))
WX0, WX1 = 838, 1172
tmin, tmax = wav.t_ms.min(), wav.t_ms.max()


def WX(t):
    return WX0 + (t - tmin) / (tmax - tmin) * (WX1 - WX0)


def wave(col, cy, amp, color, name, hz):
    s = wav[col].values
    s = s - s.mean()
    sc = amp / max(abs(s.min()), abs(s.max()))
    pts = " L ".join(f"{WX(t):.1f} {cy - v*sc:.2f}" for t, v in zip(wav.t_ms, s))
    raw(f'<path d="M {pts}" fill="none" stroke="{color}" stroke-width="2.6" '
        f'stroke-linejoin="round" stroke-linecap="round"/>')
    T(WX0, cy - amp - 18, name, 15, color, 600)
    T(WX1, cy - amp - 18, f"{hz}", 14, color, 500, "end")


wave("control", 132, 34, BLUE, "Control", "τ 18 ms · 9.5 Hz")
wave("pd", 286, 34, CORAL, "Parkinson's", "τ 22 ms · 8.0 Hz")
T((WX0 + WX1) / 2, 372, "same 0.82 s window — the patient rhythm fits in fewer cycles",
  12.5, MUTE, 400, "middle")

P.append("</svg>")

out = os.path.join(HERE, "model_dial.svg")
with open(out, "w") as fh:
    fh.write("".join(P))
print("wrote", out)
