#!/usr/bin/env python
"""Generate slides/26062026_slides/figures/code_repo.svg  (v2 redesign).

Layout (viewBox 1180 x 600):
  ZONE A  top full-width : THE PIPELINE  -- all 6 scripts as a DAG,
          with the one-parameter idea build_network(tau_inh=tau) as the hero.
  ZONE B  bottom-left    : file tree (repo structure) + real-output terminal.
  ZONE B  bottom-right   : a real git graph (feature branches -> PR -> main).
"""

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace"

BLUE = "#1d6fd6"
ORANGE = "#e2622f"
TEAL = "#0d9488"
PURPLE = "#7c4dd6"
INK = "#0f172a"
SLATE = "#334155"
GREY = "#64748b"
MUTE = "#94a3b8"
LINE = "#e2e8f0"
CARD = "#f4f7fb"

W, H = 1180, 600
P = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def T(x, y, s, size, fill, weight=400, anchor="start", family=SANS):
    P.append(f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
             f'font-weight="{weight}" text-anchor="{anchor}" font-family="{family}">{esc(s)}</text>')


def raw(s):
    P.append(s)


def rrect(x, y, w, h, r, fill, stroke=None, sw=1, dash=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    if dash:
        s += f' stroke-dasharray="{dash}"'
    P.append(s + "/>")


def folder(x, y, color):
    raw(f'<rect x="{x}" y="{y}" width="5" height="2.6" rx="1" fill="{color}"/>')
    raw(f'<rect x="{x}" y="{y+1.8}" width="14" height="9.4" rx="1.6" fill="{color}"/>')


def filei(x, y):
    raw(f'<rect x="{x}" y="{y}" width="10" height="12" rx="1.4" fill="#bcdcff"/>')
    raw(f'<polygon points="{x+7},{y} {x+10},{y+3} {x+7},{y+3}" fill="#7fb0e8"/>')


P.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{SANS}">')
P.append("<defs>")
for mid, col in [("bl", BLUE), ("or", ORANGE), ("te", TEAL), ("pu", PURPLE),
                 ("mu", "#64748b"), ("fa", "#cbd5e1"), ("dk", "#475569")]:
    P.append(f'<marker id="{mid}" markerWidth="8" markerHeight="8" refX="6" refY="4" '
             f'orient="auto"><path d="M0,0 L0,8 L7,4 z" fill="{col}"/></marker>')
P.append("</defs>")

# =============================================================== ZONE A: PIPELINE
T(20, 16, "THE PIPELINE", 12.5, GREY, 500)
T(132, 16, "EEG to result, through six numbered scripts", 12, MUTE, 400)

cy = 104  # spine vertical centre

# --- spine elements
spine = [
    ("data", "EEG · 149", "", 88),
    ("box", "01", "extract", 92),
    ("data", "features.csv", "", 118),
    ("box", "03", "fit", 84),
    ("data", "fitted_tau.csv", "", 126),
    ("box", "05", "compare", 96),
    ("result", "PD vs Control", "", 150),
]
sum_w = sum(e[3] for e in spine)
gap = (1140 - sum_w) / (len(spine) - 1)
x = 20.0
pos = {}
prev_right = None
for kind, a, b, w in spine:
    if prev_right is not None:
        raw(f'<line x1="{prev_right+9:.1f}" y1="{cy}" x2="{x-9:.1f}" y2="{cy}" '
            f'stroke="#cbd5e1" stroke-width="1.8" marker-end="url(#fa)"/>')
    if kind == "box":
        rrect(x, cy - 22, w, 44, 9, BLUE)
        T(x + w / 2, cy - 3, a, 16, "#ffffff", 700, "middle")
        T(x + w / 2, cy + 14, b, 11, "#cfe2ff", 500, "middle")
    elif kind == "data":
        rrect(x, cy - 15, w, 30, 8, "#f1f5f9", LINE, 1)
        T(x + w / 2, cy + 4, a, 11.5, "#475569", 500, "middle", MONO)
    else:
        rrect(x, cy - 18, w, 36, 9, "#fdf1ec", ORANGE, 1.4)
        T(x + w / 2, cy + 5, a, 13, "#a8431f", 600, "middle")
    pos[a] = (x + w / 2, w)
    prev_right = x + w
    x += w + gap

# --- key idea: one plain-language callout (the heart of the method)
hcx = pos["03"][0]
hw, hh = 332, 40
hx, hy = hcx - hw / 2, 24
rrect(hx, hy, hw, hh, 10, "#fdf6f3", ORANGE, 1.2)
T(hcx, hy + 16, "one number separates the two models:", 11.5, GREY, 400, "middle")
P.append(f'<text x="{hcx}" y="{hy+32}" text-anchor="middle" font-family="{SANS}" font-size="13.5">'
         f'<tspan fill="{SLATE}" font-weight="500">the inhibitory time constant  </tspan>'
         f'<tspan fill="#a8431f" font-weight="700">τ_inh</tspan></text>')
raw(f'<line x1="{hcx}" y1="{hy+hh}" x2="{hcx}" y2="{cy-22}" stroke="{ORANGE}" '
    f'stroke-width="1.3" stroke-dasharray="3 3" opacity="0.7"/>')

# --- support tier: the 3 scripts that hang off the main line
sup_y = 152
support = [
    ("features.csv", "04", "data-level test", "down"),
    ("03", "02", "builds the τ→peak curve", "up"),
    ("fitted_tau.csv", "06", "recovers a known τ  ✓", "down"),
]
for anchor, num, label, direction in support:
    ax = pos[anchor][0]
    tw = 34 + len(label) * 5.6
    tx = ax - tw / 2
    rrect(tx, sup_y, tw, 22, 11, "#f8fafc", LINE, 1)
    raw(f'<circle cx="{tx+13}" cy="{sup_y+11}" r="7.5" fill="#e2e8f0"/>')
    T(tx + 13, sup_y + 14.5, num, 9, SLATE, 700, "middle")
    T(tx + 26, sup_y + 15, label, 10.5, GREY, 400)
    # dashed dropline to the spine
    if direction == "down":
        raw(f'<line x1="{ax}" y1="{cy+15}" x2="{ax}" y2="{sup_y}" stroke="{MUTE}" '
            f'stroke-width="1.1" stroke-dasharray="2.5 2.5"/>')
    else:
        raw(f'<line x1="{ax}" y1="{sup_y}" x2="{ax}" y2="{cy+27}" stroke="{MUTE}" '
            f'stroke-width="1.1" stroke-dasharray="2.5 2.5" marker-end="url(#dk)"/>')

raw(f'<line x1="20" y1="186" x2="1160" y2="186" stroke="{LINE}" stroke-width="1.2"/>')
raw(f'<line x1="586" y1="198" x2="586" y2="588" stroke="{LINE}" stroke-width="1.4"/>')

# =============================================================== ZONE B-left: REPO
T(24, 212, "THE REPOSITORY", 12.5, GREY, 500)

tcx, tcy, tcw = 20, 222, 548
rrect(tcx, tcy, tcw, 224, 10, "#ffffff", LINE, 1)
rrect(tcx, tcy, tcw, 28, 10, "#eef2f7")
rrect(tcx, tcy + 14, tcw, 14, 0, "#eef2f7")
raw(f'<rect x="{tcx+14}" y="{tcy+9}" width="5" height="2.6" rx="1" fill="{SLATE}"/>')
raw(f'<rect x="{tcx+14}" y="{tcy+10.8}" width="14" height="9.4" rx="1.6" fill="{SLATE}"/>')
T(tcx + 36, tcy + 19, "pd-eeg", 12.5, SLATE, 500, "start", MONO)
T(tcx + tcw - 14, tcy + 19, "main", 11, BLUE, 400, "end", MONO)

row_y = tcy + 28 + 16
pitch = 14.0
guide_x = tcx + 24


def trow(level, icon, name, note=None):
    global row_y
    y = row_y
    if level == 0:
        if icon == "folder":
            folder(tcx + 18, y - 9, "#f0a83a")
        T(tcx + 40, y, name, 12, SLATE, 500, "start", MONO)
    else:
        raw(f'<line x1="{guide_x}" y1="{y-11}" x2="{guide_x}" y2="{y-1}" stroke="{LINE}" stroke-width="1"/>')
        if icon == "file":
            filei(tcx + 38, y - 9)
        else:
            folder(tcx + 38, y - 9, "#f0a83a")
        T(tcx + 56, y, name, 11.5, SLATE, 400, "start", MONO)
    if note:
        T(tcx + tcw - 14, y, note, 10.5, MUTE, 400, "end")
    row_y += pitch


trow(0, "folder", "scripts/", "01 … 06, numbered")
for f in ["01_extract_features.py", "02_simulate_network.py", "03_fit_per_subject.py",
          "04_compare_features.py", "05_compare_tau.py", "06_recover_tau.py"]:
    trow(1, "file", f)
trow(0, "folder", "src/", "features · model · fitting · stats")
trow(0, "folder", "results/", "every run writes here")
for f in ["fitted_tau.csv", "tau_recovery.csv"]:
    trow(1, "file", f)
trow(1, "folder", "figures/", "compare_tau.png · tau_recovery.png")
trow(0, "folder", "slides/", "decks + notes")

# ----- terminal (real output + provenance)
T(24, 454, "every result is one script run", 12, GREY, 500)
tx, ty, tw, th = 20, 462, 548, 130
rrect(tx, ty, tw, th, 10, "#0f172a")
rrect(tx, ty, tw, 25, 10, "#1e293b")
rrect(tx, ty + 13, tw, 12, 0, "#1e293b")
for i, col in enumerate(["#ef4444", "#f59e0b", "#22c55e"]):
    raw(f'<circle cx="{tx+18+i*16}" cy="{ty+12.5}" r="4.4" fill="{col}"/>')
T(tx + tw - 14, ty + 16, "bash", 10.5, MUTE, 400, "end", MONO)

GRN, OUT, CYAN, CMD, HL = "#16a34a", "#86efac", "#7dd3fc", "#e2e8f0", "#fde68a"
ln = ty + 42
lh = 15.5


def term(segs):
    global ln
    s = f'<text x="{tx+18}" y="{ln:.0f}" font-family="{MONO}" font-size="11.5">'
    for txt, col, wt in segs:
        w = f' font-weight="{wt}"' if wt else ""
        s += f'<tspan fill="{col}"{w}>{esc(txt)}</tspan>'
    P.append(s + "</text>")
    ln += lh


term([("$ ", GRN, 700), ("python scripts/05_compare_tau.py", CMD, 0)])
term([("  Control 18.25 → PD 21.50 ms   diff ", OUT, 0), ("+3.25", HL, 700),
      ("   p = 0.00025 ***", OUT, 0)])
term([("  → wrote ", "#64748b", 0), ("results/figures/compare_tau.png", CYAN, 0)])
term([("$ ", GRN, 700), ("python scripts/06_recover_tau.py", CMD, 0)])
term([("  22 known tau recovered   bias ", OUT, 0), ("−0.10", HL, 700),
      ("   max err 1.75 ms", OUT, 0)])
term([("  → wrote ", "#64748b", 0), ("results/tau_recovery.csv", CYAN, 0)])

# =============================================================== ZONE B-right: GIT
T(612, 212, "VERSION CONTROL", 12.5, GREY, 500)
T(770, 212, "feature branches, reviewed, merged into main", 11.5, MUTE, 400)

main_y = 480
gx0, gx1 = 656, 1140
# branches: (name, color, lane_y, x_start, x_end, n_commits, pr)
# rui is the long-running main development line; teammates make lighter,
# occasional contributions (kept understated, not a one-person spotlight).
branches = [
    ("rui", BLUE, 306, 676, 1066, 4, ""),
    ("melissa", ORANGE, 352, 726, 838, 1, ""),
    ("friedrich", PURPLE, 352, 902, 1006, 1, ""),
    ("jan", TEAL, 398, 800, 904, 1, ""),
]

# main trunk (its name label sits to the left of where the line starts)
T(612, main_y + 4, "main", 13, INK, 600, "start", MONO)
raw(f'<line x1="{gx0}" y1="{main_y}" x2="{gx1}" y2="{main_y}" stroke="{INK}" stroke-width="3"/>')
# main commit dots at the start, each diverge/merge point, and head
main_commits = {gx0 + 12}
for _, _, _, xs, xe, _, _ in branches:
    main_commits.add(xs)
    main_commits.add(xe)
main_commits.add(gx1 - 6)
for mx in sorted(main_commits):
    raw(f'<circle cx="{mx}" cy="{main_y}" r="5" fill="{INK}"/>')
# "where we are now" tag at the tip of main (no jargon)
rrect(gx1 - 62, main_y - 30, 62, 19, 9.5, "#0f172a")
T(gx1 - 31, main_y - 16.5, "latest", 11, "#ffffff", 600, "middle")


def branch(name, color, ly, xs, xe, n, pr):
    dx = 22
    a = xs + dx
    b = xe - dx
    # diverge up
    raw(f'<path d="M {xs} {main_y} C {xs+dx*0.6} {main_y} {a} {ly+(main_y-ly)*0.4} {a} {ly}" '
        f'fill="none" stroke="{color}" stroke-width="2.4"/>')
    # branch line
    raw(f'<line x1="{a}" y1="{ly}" x2="{b}" y2="{ly}" stroke="{color}" stroke-width="2.4"/>')
    # merge down
    raw(f'<path d="M {b} {ly} C {b} {ly+(main_y-ly)*0.4} {xe-dx*0.6} {main_y} {xe} {main_y}" '
        f'fill="none" stroke="{color}" stroke-width="2.4"/>')
    # commit dots along the branch
    for i in range(n):
        cx = a + (b - a) * (i / max(1, n - 1)) if n > 1 else (a + b) / 2
        raw(f'<circle cx="{cx:.0f}" cy="{ly}" r="5" fill="#ffffff" stroke="{color}" stroke-width="2.4"/>')
    # branch label
    T(a - 2, ly - 11, name, 11.5, color, 600)
    # merge tag near the merge point
    rrect(xe - 34, ly - 1, 60, 17, 8.5, "#ffffff", color, 1.2)
    T(xe - 4, ly + 11.5, "✓ merged", 9.5, color, 600, "middle")


for br in branches:
    branch(*br)

# stats line under the graph
T(612, 540, "50 commits  ·  feature branches → reviewed → merged into main  ·  fully reproducible",
  12, GREY, 500)

P.append("</svg>")

import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "code_repo.svg")
with open(out, "w") as fh:
    fh.write("".join(P))
print("wrote", out, "tree_end=", row_y, "term_end=", ln)
