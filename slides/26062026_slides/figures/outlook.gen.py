#!/usr/bin/env python
"""Generate slides/26062026_slides/figures/outlook.svg.

Layout (viewBox 1180 x 560): two columns, three paired rows.
  LEFT  (coral)  : where the model is limited  -- 3 limitation cards.
  RIGHT (blue)   : where it goes next          -- 3 future-direction cards.
Each limit on the left is joined by a coral->blue arrow to the next step that
addresses it. Honest reflection, not a claim that the next step is done.

No external data; a pure conceptual diagram (like code_repo.svg).
"""

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Helvetica, Arial, sans-serif"

BLUE = "#1d6fd6"
BDK = "#185FA5"      # deck blue, for direction titles
ORANGE = "#e2622f"
DCOR = "#a8431f"     # dark coral, for limit titles
INK = "#0f172a"
SLATE = "#334155"
GREY = "#64748b"
MUTE = "#94a3b8"
LINE = "#e2e8f0"
CT = "#fdeee8"       # coral tint
BT = "#e9f1fb"       # blue tint
TEAL = "#0d9488"     # forward/growth colour for the next-step column
TDK = "#0f766e"      # dark teal, for direction titles
TT = "#e3f4f1"       # teal tint

W, H = 1180, 560
P = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, size, fill, weight=400, anchor="start", family=SANS):
    P.append(f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
             f'font-weight="{weight}" text-anchor="{anchor}" font-family="{family}">{esc(s)}</text>')


def raw(s):
    P.append(s)


def rrect(x, y, w, h, r, fill, stroke=None, sw=1):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    P.append(s + "/>")


# ---------------------------------------------------------------- glyphs (60px tile)
def g_alpha(cx, cy, accent, tint):
    by = cy + 15
    raw(f'<line x1="{cx-22}" y1="{by}" x2="{cx+22}" y2="{by}" stroke="#cbd5e1" stroke-width="1.3"/>')
    pts = f"{cx-22},{by-1} {cx-13},{by-5} {cx-8},{cy-15} {cx-3},{by-4} {cx+10},{by-7} {cx+22},{by-3}"
    raw(f'<polyline points="{pts}" fill="none" stroke="{MUTE}" stroke-width="2" stroke-linejoin="round"/>')
    raw(f'<line x1="{cx-8}" y1="{cy-15}" x2="{cx-8}" y2="{by}" stroke="{accent}" stroke-width="1.2" stroke-dasharray="2 2"/>')
    raw(f'<circle cx="{cx-8}" cy="{cy-15}" r="3.6" fill="{accent}"/>')
    T(cx - 8, cy - 20, "α", 11, accent, 700, "middle")


def g_degeneracy(cx, cy, accent, tint):
    raw(f'<rect x="{cx-22}" y="{cy-15}" width="11" height="11" rx="2.2" fill="{SLATE}"/>')
    raw(f'<rect x="{cx-22}" y="{cy+4}" width="11" height="11" rx="2.2" fill="{MUTE}"/>')
    raw(f'<line x1="{cx-9}" y1="{cy-9}" x2="{cx+5}" y2="{cy-2}" stroke="{GREY}" stroke-width="1.6"/>')
    raw(f'<line x1="{cx-9}" y1="{cy+10}" x2="{cx+5}" y2="{cy+2}" stroke="{GREY}" stroke-width="1.6"/>')
    raw(f'<circle cx="{cx+15}" cy="{cy}" r="9" fill="{tint}" stroke="{accent}" stroke-width="2"/>')
    T(cx + 15, cy + 3.5, "=", 11, accent, 700, "middle")


def g_coarse(cx, cy, accent, tint):
    pts = (f"{cx-22},{cy+15} {cx-22},{cy+7} {cx-11},{cy+7} {cx-11},{cy-1} "
           f"{cx},{cy-1} {cx},{cy-9} {cx+11},{cy-9} {cx+11},{cy-16} {cx+22},{cy-16}")
    raw(f'<polyline points="{pts}" fill="none" stroke="{accent}" stroke-width="2.4" stroke-linejoin="round"/>')


def g_spectrum(cx, cy, accent, tint):
    by = cy + 15
    pts = (f"{cx-22},{by-2} {cx-16},{by-9} {cx-9},{cy-14} {cx-3},{by-6} "
           f"{cx+4},{cy-11} {cx+12},{by-9} {cx+22},{by-4}")
    raw(f'<polyline points="{pts}" fill="none" stroke="{accent}" stroke-width="2.2" stroke-linejoin="round"/>')
    for dx, dy in [(-16, by - 9), (-9, cy - 14), (4, cy - 11)]:
        raw(f'<circle cx="{cx+dx}" cy="{dy}" r="2.6" fill="{accent}"/>')


def g_clinic(cx, cy, accent, tint):
    rrect(cx - 20, cy - 7, 40, 14, 7, "#ffffff", accent, 1.8)
    raw(f'<path d="M {cx} {cy-7} L {cx-13} {cy-7} a7 7 0 0 0 -7 7 a7 7 0 0 0 7 7 '
        f'L {cx} {cy+7} Z" fill="{accent}"/>')
    raw(f'<line x1="{cx}" y1="{cy-7}" x2="{cx}" y2="{cy+7}" stroke="#ffffff" stroke-width="1.4"/>')


def g_network(cx, cy, accent, tint):
    nodes = [(cx - 18, cy - 10), (cx + 2, cy - 16), (cx + 18, cy - 3),
             (cx + 8, cy + 14), (cx - 15, cy + 11)]
    edges = [(0, 1, 2.6), (1, 2, 1.3), (0, 4, 2.1), (2, 3, 2.9),
             (3, 4, 1.2), (1, 3, 1.0), (0, 2, 1.6)]
    for a, b, sw in edges:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        raw(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{accent}" '
            f'stroke-width="{sw}" opacity="0.55"/>')
    for x, y in nodes:
        raw(f'<circle cx="{x}" cy="{y}" r="4" fill="{accent}"/>')


# ---------------------------------------------------------------- frame + defs
P.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{SANS}">')
P.append("<defs>")
P.append(f'<linearGradient id="flow" x1="520" y1="0" x2="650" y2="0" gradientUnits="userSpaceOnUse">'
         f'<stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>')
P.append(f'<marker id="ar" markerWidth="9" markerHeight="9" refX="6.5" refY="4.5" orient="auto">'
         f'<path d="M0,1 L0,8 L7,4.5 z" fill="{TEAL}"/></marker>')
P.append("</defs>")

# ---------------------------------------------------------------- column headers
rrect(20, 28, 290, 32, 16, CT)
raw(f'<path d="M 40 52 L 47 38 L 54 52 Z" fill="{ORANGE}"/>')
raw(f'<line x1="47" y1="43" x2="47" y2="48" stroke="#ffffff" stroke-width="1.6"/>')
raw(f'<circle cx="47" cy="50" r="0.9" fill="#ffffff"/>')
T(64, 49, "WHERE THE MODEL IS LIMITED", 13.5, DCOR, 700)

rrect(650, 28, 250, 32, 16, TT)
raw(f'<circle cx="671" cy="44" r="9" fill="none" stroke="{TDK}" stroke-width="1.8"/>')
raw(f'<path d="M 667 44 L 670.5 47.5 L 676 41" fill="none" stroke="{TDK}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
T(688, 49, "WHERE IT GOES NEXT", 13.5, TDK, 700)

# ---------------------------------------------------------------- rows
rows = [
    (g_alpha, "Alpha only",
     ["One parameter was tuned to the alpha peak,", "so theta and beta stay unexplained."],
     g_spectrum, "Fit more than the peak",
     ["Match the whole spectrum or connectivity,", "and vary more, to reach theta and beta too."]),
    (g_degeneracy, "Describes, not proves",
     ["A different change could give the same slowing,", "so it re-describes the data, not the cause."],
     g_clinic, "Anchor it in biology",
     ["Tie the fitted inhibition to medication state", "(on vs off L-Dopa) and symptom severity."]),
    (g_coarse, "Coarse and uniform",
     ["Frequency is read in coarse steps,", "on a simplified, all-to-all network."],
     g_network, "Sharper and more realistic",
     ["Fit continuously, not from a lookup table,", "on a real whole-brain connectome."]),
]

LX, LW = 20, 500
RX, RW = 650, 510
CH, GAP = 132, 22
y0 = 84


def card(x, y, w, accent, tint, glyph, title, lines, tcolor):
    rrect(x, y, w, CH, 13, "#ffffff", LINE, 1)
    ts = 60
    tilex, tiley = x + 20, y + (CH - ts) / 2
    rrect(tilex, tiley, ts, ts, 14, tint)
    glyph(tilex + ts / 2, tiley + ts / 2, accent, "#ffffff")
    tx = x + 100
    T(tx, y + 46, title, 17.5, tcolor, 700)
    ly = y + 74
    for ln in lines:
        T(tx, ly, ln, 13.5, SLATE, 400)
        ly += 21


for i, (lg, lt, ll, rg, rt, rl) in enumerate(rows):
    y = y0 + i * (CH + GAP)
    cy = y + CH / 2
    card(LX, y, LW, ORANGE, CT, lg, lt, ll, DCOR)
    card(RX, y, RW, TEAL, TT, rg, rt, rl, TDK)
    raw(f'<line x1="{LX+LW+8}" y1="{cy}" x2="{RX-12}" y2="{cy}" stroke="url(#flow)" '
        f'stroke-width="4.5" marker-end="url(#ar)"/>')

P.append("</svg>")

import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outlook.svg")
with open(out, "w") as fh:
    fh.write("".join(P))
print("wrote", out)
