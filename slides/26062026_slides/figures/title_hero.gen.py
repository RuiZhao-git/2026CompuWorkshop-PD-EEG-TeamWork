#!/usr/bin/env python
"""Generate figures/title_hero.svg -- the cover visual.

The finding in one image: two resting alpha rhythms over the same time window,
Control (blue) and PD (coral). PD fits fewer cycles in the same window, so it is
slower. Frequencies are the real medians (9.25 vs 8.00 Hz); the window is shown a
little longer than a second so the difference is visible.
"""
import os
import numpy as np

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Helvetica, Arial, sans-serif"
BLUE = "#185FA5"
CORAL = "#a8431f"
SLATE = "#334155"
GREY = "#64748b"
MUTE = "#94a3b8"
LINE = "#e6ebf2"

W, H = 1020, 250
P = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{SANS}">']

x0, x1 = 196, 876


def T(x, y, s, size, fill, weight=400, anchor="start"):
    P.append(f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" font-family="{SANS}">{s}</text>')


def wave(yc, cyc, amp, color, label, freq):
    n = 600
    xs = np.linspace(x0, x1, n)
    ys = yc - amp * np.sin(np.linspace(0, cyc * 2 * np.pi, n))
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in zip(xs, ys))
    P.append(f'<line x1="{x0}" y1="{yc}" x2="{x1}" y2="{yc}" stroke="{LINE}" stroke-width="1.2"/>')
    P.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="8" stroke-opacity="0.12" '
             f'stroke-linecap="round"/>')
    P.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" '
             f'stroke-linejoin="round"/>')
    P.append(f'<circle cx="48" cy="{yc}" r="5.5" fill="{color}"/>')
    T(64, yc + 5, label, 18, color, 700)
    T(x1 + 16, yc + 5, freq, 15, color, 600)


# top: Control, faster (more cycles in the same window)
wave(74, 11.6, 33, BLUE, "Control", "9.25 Hz")
# bottom: PD, slower (fewer cycles)
wave(176, 10.0, 33, CORAL, "PD", "8.00 Hz")

# the quiet caption that ties it together
T(W / 2, 232, "same window, fewer cycles: the resting alpha rhythm slows", 13.5, GREY, 400, "middle")

P.append("</svg>")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "title_hero.svg")
with open(out, "w") as fh:
    fh.write("".join(P))
print("wrote", out)
