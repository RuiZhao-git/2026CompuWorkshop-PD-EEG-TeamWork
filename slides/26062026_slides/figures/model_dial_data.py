#!/usr/bin/env python
"""Simulate the two model waveforms shown on the model slide.

Runs the 8-node Wilson-Cowan network at the Control and PD inhibitory time
constants, averages the excitatory activity across nodes, and saves a short
window of each to results/model_waveforms.csv. Feeds model_dial.gen.py.

Run:  python slides/26062026_slides/figures/model_dial_data.py
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, REPO)

from src.model import build_network, peak_frequency  # noqa: E402

TAU_CONTROL, TAU_PD = 18.25, 21.5   # the fitted Control / PD median tau_inh
SKIP_MS, WIN_MS, N = 3000, 820, 256


def sim(tau):
    m = build_network(8, float(tau))
    m.run()
    t = np.asarray(m.t)
    sig = np.asarray(m.exc).mean(axis=0)
    dt = t[1] - t[0]
    i0 = int(SKIP_MS / dt)
    i1 = i0 + int(WIN_MS / dt)
    win_t, win_s = t[i0:i1] - t[i0], sig[i0:i1]
    pk = peak_frequency(sig[int(2000 / dt):], dt_ms=dt)
    idx = np.linspace(0, len(win_t) - 1, N).astype(int)
    return win_t[idx], win_s[idx], pk


def main():
    tc, sc, pkc = sim(TAU_CONTROL)
    _, sp, pkp = sim(TAU_PD)
    out = pd.DataFrame({"t_ms": tc, "control": sc, "pd": sp})
    dst = os.path.join(REPO, "results", "model_waveforms.csv")
    out.to_csv(dst, index=False, float_format="%.5f")
    print(f"wrote {dst}  (Control tau={TAU_CONTROL} -> {pkc:.1f} Hz, "
          f"PD tau={TAU_PD} -> {pkp:.1f} Hz)")


if __name__ == "__main__":
    main()
