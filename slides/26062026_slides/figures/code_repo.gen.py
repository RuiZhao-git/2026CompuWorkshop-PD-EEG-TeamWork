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
T(20, 16, "THE PIPELINE", 14.5, GREY, 500)
T(140, 16, "EEG to result, through six scripts", 13.5, MUTE, 400)

cy = 104  # spine vertical centre

STEP = "#185FA5"       # process-step boxes
STEPSUB = "#cfe2ff"    # step sub-line (number + what)
INKBOX = "#0f172a"     # the result endpoint

# spine: (kind, key, label, sub, width)
spine = [
    ("data", "EEG", "EEG · 149", "", 88),
    ("box", "01", "extract", "01 · features", 108),
    ("data", "features.csv", "features.csv", "", 112),
    ("box", "03", "fit", "03 · per subject", 108),
    ("data", "fitted_tau.csv", "fitted_tau.csv", "", 120),
    ("box", "05", "compare", "05 · the groups", 108),
    ("result", "PD vs Control", "PD vs Control", "", 138),
]
sum_w = sum(e[4] for e in spine)
gap = (1140 - sum_w) / (len(spine) - 1)
x = 20.0
pos = {}
prev_right = None
for kind, key, label, sub, w in spine:
    if prev_right is not None:
        raw(f'<line x1="{prev_right+9:.1f}" y1="{cy}" x2="{x-9:.1f}" y2="{cy}" '
            f'stroke="#cbd5e1" stroke-width="1.8" marker-end="url(#fa)"/>')
    if kind == "box":
        rrect(x, cy - 23, w, 46, 10, STEP)
        T(x + w / 2, cy - 2, label, 16, "#ffffff", 700, "middle")
        T(x + w / 2, cy + 15, sub, 10.5, STEPSUB, 500, "middle")
    elif kind == "data":
        rrect(x, cy - 14, w, 28, 7, "#eef2f7", LINE, 1)
        T(x + w / 2, cy + 4, label, 12.5, "#475569", 500, "middle", MONO)
    else:
        rrect(x, cy - 19, w, 38, 9, INKBOX)
        T(x + w / 2, cy + 5, label, 15, "#ffffff", 700, "middle")
    pos[key] = (x + w / 2, w)
    prev_right = x + w
    x += w + gap

# --- key idea callout (blue, points at the fit step); tau_inh is the one hero token
hcx = pos["03"][0]
hw, hh = 322, 40
hx, hy = hcx - hw / 2, 24
rrect(hx, hy, hw, hh, 10, "#eef4fb", STEP, 1.2)
T(hcx, hy + 15, "one number is the whole difference:", 13, GREY, 400, "middle")
P.append(f'<text x="{hcx}" y="{hy+33}" text-anchor="middle" font-family="{SANS}" font-size="15.5">'
         f'<tspan fill="{SLATE}" font-weight="500">the inhibitory time constant  </tspan>'
         f'<tspan fill="#a8431f" font-weight="700">τ_inh</tspan></text>')
raw(f'<line x1="{hcx}" y1="{hy+hh}" x2="{hcx}" y2="{cy-23}" stroke="{STEP}" '
    f'stroke-width="1.3" stroke-dasharray="3 3" opacity="0.6"/>')

# --- support tier: the 3 helper scripts hanging off the spine
sup_y = 152
support = [
    ("features.csv", "04", "data-level test", "down"),
    ("03", "02", "builds the τ→peak curve", "up"),
    ("fitted_tau.csv", "06", "recovers a known τ", "down"),
]
for anchor, num, label, direction in support:
    ax = pos[anchor][0]
    tw = 38 + len(label) * 6.4
    tx = ax - tw / 2
    rrect(tx, sup_y, tw, 23, 11.5, "#f8fafc", LINE, 1)
    raw(f'<circle cx="{tx+14}" cy="{sup_y+11.5}" r="8" fill="#e2e8f0"/>')
    T(tx + 14, sup_y + 15, num, 10, SLATE, 700, "middle")
    T(tx + 28, sup_y + 16, label, 11.5, GREY, 400)
    if direction == "down":
        raw(f'<line x1="{ax}" y1="{cy+14}" x2="{ax}" y2="{sup_y}" stroke="{MUTE}" '
            f'stroke-width="1.1" stroke-dasharray="2.5 2.5"/>')
    else:
        raw(f'<line x1="{ax}" y1="{sup_y}" x2="{ax}" y2="{cy+27}" stroke="{MUTE}" '
            f'stroke-width="1.1" stroke-dasharray="2.5 2.5" marker-end="url(#dk)"/>')

raw(f'<line x1="20" y1="186" x2="1160" y2="186" stroke="{LINE}" stroke-width="1.2"/>')
raw(f'<line x1="586" y1="198" x2="586" y2="588" stroke="{LINE}" stroke-width="1.4"/>')

# =============================================================== ZONE B-left: REPO
T(24, 212, "THE REPOSITORY", 14.5, GREY, 500)

tcx, tcy, tcw = 20, 222, 548
rrect(tcx, tcy, tcw, 196, 10, "#ffffff", LINE, 1)
rrect(tcx, tcy, tcw, 28, 10, "#eef2f7")
rrect(tcx, tcy + 14, tcw, 14, 0, "#eef2f7")
raw(f'<rect x="{tcx+14}" y="{tcy+9}" width="5" height="2.6" rx="1" fill="{SLATE}"/>')
raw(f'<rect x="{tcx+14}" y="{tcy+10.8}" width="14" height="9.4" rx="1.6" fill="{SLATE}"/>')
T(tcx + 36, tcy + 19, "pd-eeg", 13.5, SLATE, 500, "start", MONO)
T(tcx + tcw - 14, tcy + 19, "main", 12, BLUE, 400, "end", MONO)

row_y = tcy + 28 + 16
pitch = 14.0
guide_x = tcx + 24


def trow(level, icon, name, note=None):
    global row_y
    y = row_y
    if level == 0:
        if icon == "folder":
            folder(tcx + 18, y - 9, "#f0a83a")
        T(tcx + 40, y, name, 13, SLATE, 500, "start", MONO)
    else:
        raw(f'<line x1="{guide_x}" y1="{y-11}" x2="{guide_x}" y2="{y-1}" stroke="{LINE}" stroke-width="1"/>')
        if icon == "file":
            filei(tcx + 38, y - 9)
        else:
            folder(tcx + 38, y - 9, "#f0a83a")
        T(tcx + 56, y, name, 12.5, SLATE, 400, "start", MONO)
    if note:
        T(tcx + tcw - 14, y, note, 11.5, MUTE, 400, "end")
    row_y += pitch


trow(0, "folder", "scripts/", "01 … 06, numbered")
for f in ["01_extract_features.py", "02_simulate_network.py", "03_fit_per_subject.py",
          "04_compare_features.py", "05_compare_tau.py", "06_recover_tau.py"]:
    trow(1, "file", f)
trow(0, "folder", "src/", "features · model · fitting · stats")
trow(0, "folder", "results/", "every run writes here")
trow(1, "folder", "figures/", "compare_tau.png · tau_recovery.png")
trow(0, "folder", "slides/", "decks + notes")

# ----- version control (flattened into the lower-left strip)
T(24, 440, "VERSION CONTROL", 13.5, GREY, 500)
T(170, 440, "64 commits, all merged into main, reproducible", 12, MUTE, 400)

main_y = 566
gx0, gx1 = 52, 556
branches = [
    ("rui", BLUE, 466, 104, 466, 4),
    ("melissa", ORANGE, 490, 132, 236, 1),
    ("jan", TEAL, 514, 262, 360, 1),
    ("friedrich", PURPLE, 490, 380, 448, 1),
]

T(20, main_y + 4, "main", 13, INK, 600, "start", MONO)
raw(f'<line x1="{gx0}" y1="{main_y}" x2="{gx1}" y2="{main_y}" stroke="{INK}" stroke-width="2.6"/>')
main_commits = {gx0 + 10}
for _, _, _, xs, xe, _ in branches:
    main_commits.add(xs)
    main_commits.add(xe)
main_commits.add(gx1 - 6)
for mx in sorted(main_commits):
    raw(f'<circle cx="{mx}" cy="{main_y}" r="4.2" fill="{INK}"/>')
rrect(gx1 - 52, main_y - 25, 52, 17, 8.5, "#0f172a")
T(gx1 - 26, main_y - 12.5, "latest", 11, "#ffffff", 600, "middle")


def branch(name, color, ly, xs, xe, n):
    dx = 18
    a, b = xs + dx, xe - dx
    raw(f'<path d="M {xs} {main_y} C {xs+dx*0.6} {main_y} {a} {ly+(main_y-ly)*0.4} {a} {ly}" fill="none" stroke="{color}" stroke-width="2.2"/>')
    raw(f'<line x1="{a}" y1="{ly}" x2="{b}" y2="{ly}" stroke="{color}" stroke-width="2.2"/>')
    raw(f'<path d="M {b} {ly} C {b} {ly+(main_y-ly)*0.4} {xe-dx*0.6} {main_y} {xe} {main_y}" fill="none" stroke="{color}" stroke-width="2.2"/>')
    for i in range(n):
        cx = a + (b - a) * (i / max(1, n - 1)) if n > 1 else (a + b) / 2
        raw(f'<circle cx="{cx:.0f}" cy="{ly}" r="4.2" fill="#ffffff" stroke="{color}" stroke-width="2.2"/>')
    T(a - 2, ly - 9, name, 11.5, color, 600)
    chipx = a - 2 + len(name) * 6.9 + 9
    rrect(chipx, ly - 20, 60, 17, 8.5, "#ffffff", color, 1.3)
    raw(f'<text x="{chipx+30}" y="{ly-8}" fill="{color}" font-size="10" font-weight="700" '
        f'text-anchor="middle" font-family="{SANS}">✓ merged</text>')


for br in branches:
    branch(*br)

# =============================================================== ZONE B-right: CODE
T(612, 212, "THE MODEL, IN CODE", 14.5, GREY, 500)
T(806, 212, "one function, one free parameter", 13, MUTE, 400)

ccx, ccy, ccw, cch = 612, 222, 548, 370
rrect(ccx, ccy, ccw, cch, 10, "#fbfcfe", LINE, 1)
rrect(ccx, ccy, ccw, 26, 10, "#eef2f7")
rrect(ccx, ccy + 13, ccw, 13, 0, "#eef2f7")
for i, dot in enumerate(["#ef4444", "#f59e0b", "#22c55e"]):
    raw(f'<circle cx="{ccx+16+i*15}" cy="{ccy+13}" r="4" fill="{dot}"/>')
T(ccx + ccw - 14, ccy + 17, "src/model.py", 11.5, GREY, 400, "end", MONO)

KW, FN, ST, NU, CM, TX, CL = "#cf222e", "#6639ba", "#0a3069", "#0550ae", "#6e7781", "#1f2328", "#953800"
cln = ccy + 48
clh = 15.6


def code(segs, indent=0):
    global cln
    s = f'<text x="{ccx+18+indent}" y="{cln:.0f}" font-family="{MONO}" font-size="12.5">'
    for txt, col in segs:
        s += f'<tspan fill="{col}">{esc(txt)}</tspan>'
    P.append(s + "</text>")
    cln += clh


code([("# the whole model is one function; one number is the difference", CM)])
code([("def ", KW), ("build_network", FN), ("(n_nodes, tau_inh, ", TX), ("*", KW), (",", TX)])
code([("exc_ext=", TX), ("0.65", NU), (",", TX), ("       # external drive", CM)], indent=130)
code([("sigma_ou=", TX), ("0", NU), (",", TX), ("         # deterministic, no noise", CM)], indent=130)
code([("K_gl=", TX), ("0.6", NU), (",", TX), ("           # global coupling", CM)], indent=130)
code([("duration_ms=", TX), ("8000", NU), ("):", TX), ("  # simulation length", CM)], indent=130)
code([('"""A Wilson-Cowan network. tau_inh is the one free', ST)], indent=28)
code([('parameter; everything else stays at these defaults."""', ST)], indent=28)
code([("Cmat, Dmat = ", TX), ("all_to_all_coupling", FN), ("(n_nodes)", TX)], indent=28)
code([("model = ", TX), ("WCModel", CL), ("(Cmat=Cmat, Dmat=Dmat)", TX)], indent=28)
code([("model.params[", TX), ('"tau_inh"', ST), ("]  = tau_inh", TX), ("    # the one knob we turn", CM)], indent=28)
code([("model.params[", TX), ('"exc_ext"', ST), ("]  = exc_ext", TX)], indent=28)
code([("model.params[", TX), ('"sigma_ou"', ST), ("] = sigma_ou", TX)], indent=28)
code([("model.params[", TX), ('"K_gl"', ST), ("]     = K_gl", TX)], indent=28)
code([("model.params[", TX), ('"duration"', ST), ("] = duration_ms", TX)], indent=28)
code([("return ", KW), ("model", TX)], indent=28)
cln += 9
code([("# healthy vs patient: same function, one number changed", CM)])
code([("control = ", TX), ("build_network", FN), ("(", TX), ("8", NU), (", tau_inh=", TX), ("18.25", NU), (")", TX), ("   # alpha 9.25 Hz", CM)])
code([("patient = ", TX), ("build_network", FN), ("(", TX), ("8", NU), (", tau_inh=", TX), ("21.50", NU), (")", TX), ("   # 8 Hz, +3.25 ms", CM)])

P.append("</svg>")

import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "code_repo.svg")
with open(out, "w") as fh:
    fh.write("".join(P))
print("wrote", out, "tree_end=", row_y, "code_end=", cln)
