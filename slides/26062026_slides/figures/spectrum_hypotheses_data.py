#!/usr/bin/env python
"""Compute the group-average posterior power spectrum, Control vs PD.

Reads the preprocessed .fif recordings (PD_DATA_DIR), computes each subject's
posterior-channel Welch PSD via src.features, normalises each to relative power
over 2-35 Hz, and averages within group (with SEM). Writes results/group_psd.csv,
which feeds spectrum_hypotheses.gen.py (the Hypotheses-slide figure).

Run:  python slides/26062026_slides/figures/spectrum_hypotheses_data.py
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, REPO)

from src.features import compute_average_psd, load_raw  # noqa: E402

FMIN, FMAX = 2.0, 35.0


def _data_dir():
    env = os.path.join(REPO, ".env")
    if os.path.exists(env):
        for ln in open(env):
            if ln.startswith("PD_DATA_DIR"):
                return ln.split("=", 1)[1].strip()
    return os.environ["PD_DATA_DIR"]


DATA = _data_dir()


def group_psd(folder):
    """Return (freqs, mean, sem, n) of the relative PSD over a group folder."""
    rows, freqs = [], None
    for f in sorted(glob.glob(os.path.join(DATA, folder, "*.fif"))):
        fr, psd, _ = compute_average_psd(load_raw(f))
        m = (fr >= FMIN) & (fr <= FMAX)
        fr, psd = fr[m], psd[m]
        if freqs is None:
            freqs = fr
        rows.append(psd / (psd.sum() * (fr[1] - fr[0])))  # relative (unit area)
    arr = np.vstack(rows)
    return freqs, arr.mean(0), arr.std(0) / np.sqrt(len(arr)), len(arr)


def main():
    fr, cm, cs, nc = group_psd("Control")
    _, pm, ps, npd = group_psd("PD")
    out = pd.DataFrame({"freq_hz": fr, "control_mean": cm, "control_sem": cs,
                        "pd_mean": pm, "pd_sem": ps})
    dst = os.path.join(REPO, "results", "group_psd.csv")
    out.to_csv(dst, index=False, float_format="%.6e")
    print(f"wrote {dst}  (Control n={nc}, PD n={npd})")


if __name__ == "__main__":
    main()
