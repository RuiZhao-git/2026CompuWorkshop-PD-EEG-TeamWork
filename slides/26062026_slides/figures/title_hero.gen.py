#!/usr/bin/env python
"""Generate figures/title_hero.svg -- the cover visual (for a dark title slide).

The finding, exaggerated for impact: two resting rhythms over the same window.
Control (blue) packs in many cycles; the Parkinson's rhythm (coral) is visibly
slower, far fewer cycles. Transparent background so the dark slide shows through.
"""
import os
import numpy as np

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Helvetica, Arial, sans-serif"
BLUE = "#4d9be6"     # bright blue, glows on dark
CORAL = "#f1744e"    # bright coral
BASE = "#3b4759"     # faint baseline on dark
MUTE = "#8b97a8"

W, H = 1040, 300
P = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{SANS}">']

x0, x1 = 214, 1004


def T(x, y, s, size, fill, weight=400, anchor="start", spacing=0):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    P.append(f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" font-family="{SANS}"{sp}>{s}</text>')


def wave(yc, cyc, amp, color, label):
    n = 760
    xs = np.linspace(x0, x1, n)
    ys = yc - amp * np.sin(np.linspace(0, cyc * 2 * np.pi, n))
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in zip(xs, ys))
    P.append(f'<line x1="{x0}" y1="{yc}" x2="{x1}" y2="{yc}" stroke="{BASE}" stroke-width="1"/>')
    P.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="13" stroke-opacity="0.16" '
             f'stroke-linecap="round"/>')
    P.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" '
             f'stroke-linejoin="round"/>')
    P.append(f'<circle cx="44" cy="{yc}" r="6" fill="{color}"/>')
    T(60, yc + 8, label, 25, color, 800)


# Control: many tight cycles (fast)
wave(92, 14, 44, BLUE, "Control")
# Parkinson's: far fewer cycles in the same window (slow)
wave(214, 7, 44, CORAL, "Parkinson's")

# one quiet line, big enough to read
T(W / 2, 286, "same window  ·  the resting rhythm slows", 16, MUTE, 500, "middle", 0.3)

P.append("</svg>")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "title_hero.svg")
with open(out, "w") as fh:
    fh.write("".join(P))
print("wrote", out)
