#!/usr/bin/env python
"""Generate figures/take_aways.svg -- four take-away cards, one per team member.

Each member's card carries a theme keyword, a small icon, and their quote, in
that member's git-branch colour (Rui blue, Melissa coral, Jan teal, Friedrich
purple). The shared thread, stated on the slide itself: the lessons were about
how a team does computational research, not about the model.
"""
import os

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Helvetica, Arial, sans-serif"
INK = "#0f172a"
SLATE = "#3f4b5b"
LINE = "#e2e8f0"

W, H = 1180, 392
P = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{SANS}">']


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, size, fill, weight=400, anchor="start", spacing=0):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    P.append(f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
             f'text-anchor="{anchor}" font-family="{SANS}"{sp}>{esc(s)}</text>')


def rrect(x, y, w, h, r, fill, stroke=None, sw=1):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    P.append(s + "/>")


def tint(color):
    return {"#185FA5": "#eaf1f9", "#a8431f": "#fbeee8",
            "#0d9488": "#e3f4f1", "#7c4dd6": "#f0eafb"}[color]


ICONS = {
    "repro": '<path d="M3.5 9 A 8 8 0 0 1 18 6.5"/><polyline points="18,2 18.5,7 13.3,7.4"/>'
             '<path d="M18.5 13 A 8 8 0 0 1 4 15.5"/><polyline points="4,20 3.5,15 8.7,14.6"/>',
    "doc": '<path d="M5 2.5 h8 l4 4 v12.5 a1.2 1.2 0 0 1 -1.2 1.2 H6.2 a1.2 1.2 0 0 1 -1.2 -1.2 V3.7 '
           'a1.2 1.2 0 0 1 1.2 -1.2 z"/><polyline points="13,2.5 13,6.5 17,6.5"/>'
           '<line x1="7.5" y1="11" x2="14" y2="11"/><line x1="7.5" y1="14.5" x2="14" y2="14.5"/>'
           '<line x1="7.5" y1="18" x2="11.5" y2="18"/>',
    "door": '<path d="M4 20 H18"/><path d="M7 20 V4 L15 2.3 V20"/>'
            '<circle cx="9" cy="11.4" r="0.95" fill="CUR" stroke="none"/>',
    "talk": '<path d="M3 5.6 a2 2 0 0 1 2 -2 h12 a2 2 0 0 1 2 2 v7.6 a2 2 0 0 1 -2 2 H9 l-4 3.4 '
            'V15.2 H5 a2 2 0 0 1 -2 -2 z"/><line x1="7" y1="8" x2="15" y2="8"/>'
            '<line x1="7" y1="11.4" x2="13" y2="11.4"/>',
}


def icon(ix, iy, key, color):
    paths = ICONS[key].replace("CUR", color)
    P.append(f'<g transform="translate({ix},{iy})" fill="none" stroke="{color}" stroke-width="2" '
             f'stroke-linecap="round" stroke-linejoin="round">{paths}</g>')


def wrap(text, maxchars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= maxchars:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(x, y, w, h, name, color, theme, ikey, quote):
    rrect(x, y, w, h, 13, "#ffffff", LINE, 1)
    rrect(x, y + 15, 4.5, h - 30, 2, color)                 # left accent tab
    rrect(x + 20, y + 18, 30, 30, 9, tint(color))           # icon tile
    icon(x + 24, y + 22, ikey, color)
    T(x + 60, y + 31, theme.upper(), 12, color, 700, "start", 0.7)
    T(x + 60, y + 47, name, 16.5, INK, 700)
    ly = y + 74
    for ln in wrap("“" + quote + "”", 74):
        T(x + 22, ly, ln, 13.5, SLATE, 400)
        ly += 20


CARDS = [
    (16, 8, "Rui", "#185FA5", "Reproducibility", "repro",
     "Carrying this end to end, from raw EEG to the fitted model, taught me that a result is "
     "only as trustworthy as the pipeline behind it; the reproducible scripts and the honest "
     "recovery check mattered as much as the model."),
    (16, 200, "Melissa", "#a8431f", "Documentation", "doc",
     "My biggest learning was how much easier good documentation makes everything, whether it's "
     "the repository structure, script naming, clear responsibilities, or the code itself. It "
     "keeps the whole team aligned, helps everyone track progress, and makes even complex or "
     "unfamiliar methods feel more approachable."),
    (603, 8, "Jan", "#0d9488", "Approachable", "door",
     "This course taught me that you do not have to be a master programmer to meaningfully "
     "contribute to, and clinically interpret, advanced computational research."),
    (603, 200, "Friedrich", "#7c4dd6", "Communication", "talk",
     "How big a difference good communication makes. Even missing one group meeting meant you "
     "basically missed all the progress. In-person communication is essential to work well "
     "together and establish a group-wide understanding."),
]
for x, y, name, color, theme, ikey, quote in CARDS:
    card(x, y, 561, 176, name, color, theme, ikey, quote)

P.append("</svg>")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "take_aways.svg")
with open(out, "w") as fh:
    fh.write("".join(P))
print("wrote", out)
