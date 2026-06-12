"""
draft_03_fit_per_subject.py   (TEMPORARY / BACKUP -- not part of the git repo)
==============================================================================

WHAT THIS FILE IS
-----------------
A reserve copy of pipeline step 03 ("per-subject model fitting") for the
PD EEG project. Step 03 was assigned to a teammate, so this file is kept
OUTSIDE the repository on purpose:

  * it lives in a throwaway folder on the Desktop, not in scripts/;
  * it writes its outputs NEXT TO ITSELF, not into the repo's results/;
  * it only READS the repo's input files, so the repo stays untouched.

It is over-commented so it can double as an explanation if a teammate
needs to be walked through what step 03 does and why. If it ever has to
"go live", see the section "PROMOTING THIS TO THE REAL PIPELINE" at the
very bottom.

======================================================================
1. THE IDEA, IN PLAIN WORDS
======================================================================
Our hypothesis is that Parkinson's disease slows the cortical alpha
rhythm. In our Wilson-Cowan network model, the single knob we turn to
change the alpha frequency is the inhibitory time constant `tau_inh`:

        larger tau_inh  ->  slower inhibition  ->  slower oscillation
                        ->  LOWER alpha peak frequency.

"Fitting the model to one subject" therefore means:

        find the tau_inh that would make the model oscillate at
        exactly THAT subject's measured alpha peak frequency.

There are two ways to do that:

  (a) The expensive way. For each of the 149 subjects, run the model
      many times with different tau_inh until the model's peak matches
      the subject's peak. That is an optimisation loop PER subject, i.e.
      hundreds of simulations. Slow.

  (b) The cheap way (what we do). The model's alpha peak depends on
      tau_inh in a simple, strictly one-directional way (more tau_inh
      always means a lower peak). So in step 02 we already simulated the
      model ONCE across a whole grid of tau_inh values and wrote down
      the alpha peak that each produced. That gave us a lookup curve:

            tau_inh  ->  alpha peak          (results/peak_curve.csv)

      Fitting is then nothing more than reading that curve BACKWARDS:

            subject's measured alpha peak  ->  tau_inh

This is "fitting by inverting a precomputed curve". It is the same
core idea as the grid search in the model-fitting prep notebook, but
because there is only ONE parameter and the curve is monotone, the
inverse is a single 1-D interpolation. That one interpolation is, quite
literally, the whole fitting step.

======================================================================
2. THE ONE TECHNICAL TRAP: np.interp NEEDS INCREASING X
======================================================================
We will use numpy.interp(x, xp, fp). It estimates, for each query `x`,
the value `fp` at that `x`, assuming the known sample points (xp, fp)
describe a function. CRUCIAL RULE: np.interp requires `xp` (the known
x-coordinates) to be sorted in INCREASING order. If they are not,
np.interp gives silently wrong answers (no error is raised).

Here we want to go FROM peak TO tau, so for np.interp:

        xp = the peak values   (these must be increasing)
        fp = the tau values    (the answers we read off)
        x  = each subject's measured alpha peak

But peak_curve.csv is stored in increasing tau, which means the peak
column is DECREASING (bigger tau, lower peak). So before interpolating
we must SORT the curve by peak ascending. We do that explicitly below
and even assert it, so this trap cannot bite us silently.

======================================================================
3. TWO HONEST CAVEATS WORTH KNOWING (not bugs)
======================================================================
  * Out-of-range subjects ("clamping"). If a subject's measured peak is
    outside the range the curve covers, np.interp does not extrapolate;
    it returns the nearest endpoint value (it "clamps"). For OUR data
    this never happens: the curve covers 6.0-13.5 Hz and every subject
    sits at 7-13 Hz. The code below still checks and reports the count,
    so a future dataset cannot clamp without us noticing.

  * Resolution. The curve's peak axis is coarse (about 0.5 Hz steps, and
    several tau values map to the same peak -- "plateaus"). So the fitted
    tau is fairly discrete and cannot be more precise than the curve
    underneath it. That is a property of the lookup table, not an error.
"""

from pathlib import Path

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# PATHS
# ----------------------------------------------------------------------
# This temp script lives OUTSIDE the repo, so we cannot use the usual
# "repo root is two levels up from scripts/" trick that the real scripts
# use. Instead we point at the repo by an absolute path. A teammate on a
# different machine only has to edit this ONE line.
REPO_ROOT = Path("/Users/r.z/Desktop/2026CompuWorkshop-PD-EEG-modeling")
if not REPO_ROOT.exists():
    raise SystemExit(
        "REPO_ROOT does not exist. Edit it to point at your local clone "
        "of the PD EEG repository."
    )

# Inputs we READ from the repo (read-only; the repo is never modified):
PEAK_CURVE_CSV = REPO_ROOT / "results" / "peak_curve.csv"   # tau -> peak, from step 02
FEATURES_CSV = REPO_ROOT / "results" / "features.csv"       # per-subject features, from step 01

# Output we WRITE -- deliberately BESIDE THIS SCRIPT, not into results/,
# so this backup leaves no trace in the repo. The real pipeline step
# would instead write to REPO_ROOT / "results" / "fitted_tau.csv".
OUT_DIR = Path(__file__).resolve().parent
FITTED_TAU_CSV = OUT_DIR / "fitted_tau.csv"


def invert_peak_curve(measured_peak_hz, curve_tau_ms, curve_peak_hz):
    """Map a measured alpha peak (Hz) to the tau_inh (ms) that produces it.

    This is the actual "fitting" operation, isolated into one function so
    it is easy to read and easy to test. In the real pipeline this would
    live in `src/fitting.py` and be imported by the script.

    Parameters
    ----------
    measured_peak_hz : float or array of float
        One subject's alpha peak frequency, or an array of them.
    curve_tau_ms : 1-D array
        The tau_inh grid from step 02 (the lookup curve's tau column).
    curve_peak_hz : 1-D array
        The alpha peak each tau produced (the lookup curve's peak column),
        aligned element-by-element with `curve_tau_ms`.

    Returns
    -------
    float or array of float
        The fitted tau_inh in ms for each input peak.

    How it works
    ------------
    np.interp needs its known x-coordinates (here the peaks) increasing.
    The curve arrives in increasing tau, i.e. DECREASING peak, so we sort
    both columns by peak ascending first, then interpolate peak -> tau.
    """
    curve_tau_ms = np.asarray(curve_tau_ms, dtype=float)
    curve_peak_hz = np.asarray(curve_peak_hz, dtype=float)

    # Sort both arrays by peak ascending, keeping each (tau, peak) pair
    # together. argsort gives the ordering of the peak column; we apply
    # the same ordering to tau so the pairing is preserved.
    order = np.argsort(curve_peak_hz)
    peak_sorted = curve_peak_hz[order]
    tau_sorted = curve_tau_ms[order]

    # Safety: np.interp is only correct if peak_sorted is non-decreasing.
    # After the sort it must be, but we assert it so a malformed curve
    # would fail loudly instead of returning quiet nonsense.
    assert np.all(np.diff(peak_sorted) >= 0), "peak axis is not sorted ascending"

    # The fit itself. For a peak that sits between two grid points,
    # np.interp returns the linearly interpolated tau. For a peak outside
    # the grid it returns the nearest endpoint (clamping) -- see caveats.
    return np.interp(measured_peak_hz, peak_sorted, tau_sorted)


def main():
    # --- load the lookup curve produced by step 02 -------------------
    if not PEAK_CURVE_CSV.exists():
        raise FileNotFoundError(
            f"{PEAK_CURVE_CSV} not found. Run scripts/02_simulate_network.py "
            "first to produce the tau -> peak lookup curve."
        )
    curve = pd.read_csv(PEAK_CURVE_CSV)
    # Columns are: tau_inh_ms, simulated_peak_hz (see results/peak_curve.csv).

    # --- load the per-subject features produced by step 01 -----------
    if not FEATURES_CSV.exists():
        raise FileNotFoundError(
            f"{FEATURES_CSV} not found. Run scripts/01_extract_features.py first."
        )
    feats = pd.read_csv(FEATURES_CSV)
    # We only need the subject id, the group label, and the measured
    # alpha peak; the other feature columns are irrelevant for fitting.

    # --- report the ranges so any future clamping is visible ---------
    curve_lo, curve_hi = curve.simulated_peak_hz.min(), curve.simulated_peak_hz.max()
    subj_lo, subj_hi = feats.alpha_peak_hz.min(), feats.alpha_peak_hz.max()
    n_below = int((feats.alpha_peak_hz < curve_lo).sum())
    n_above = int((feats.alpha_peak_hz > curve_hi).sum())
    print(f"Lookup curve covers alpha peak {curve_lo:.2f}-{curve_hi:.2f} Hz "
          f"(tau {curve.tau_inh_ms.min():.1f}-{curve.tau_inh_ms.max():.1f} ms)")
    print(f"Subjects span alpha peak {subj_lo:.2f}-{subj_hi:.2f} Hz "
          f"(n = {len(feats)})")
    if n_below or n_above:
        print(f"  WARNING: {n_below} below and {n_above} above the curve -> "
              f"those were clamped to the nearest endpoint.")
    else:
        print("  All subjects fall inside the curve range -> no clamping.")

    # --- the fit: one call does all 149 subjects at once -------------
    fitted_tau = invert_peak_curve(
        feats.alpha_peak_hz.values,
        curve.tau_inh_ms.values,
        curve.simulated_peak_hz.values,
    )

    # --- assemble and save the per-subject fitted table --------------
    out = pd.DataFrame({
        "subject_id": feats.subject_id,
        "group": feats.group,
        "alpha_peak_hz": feats.alpha_peak_hz,   # kept so step 05 / sanity checks can see both
        "tau_inh_ms": fitted_tau,
    })
    out.to_csv(FITTED_TAU_CSV, index=False, float_format="%.4f")

    # --- a short human-readable summary ------------------------------
    # Sanity check on the DIRECTION of the effect: PD has the slower
    # alpha, so PD should get the LARGER fitted tau_inh. If this prints
    # the other way round, something is inverted.
    med = out.groupby("group").tau_inh_ms.median()
    print(f"\nWrote {len(out)} fitted tau values to {FITTED_TAU_CSV}")
    print("Median fitted tau_inh by group:")
    for g, v in med.items():
        print(f"  {g:>8s}: {v:6.2f} ms")
    if {"Control", "PD"}.issubset(med.index):
        direction = "PD > Control (expected: PD alpha is slower)" \
            if med["PD"] > med["Control"] else \
            "PD < Control (UNEXPECTED -- check the inversion direction!)"
        print(f"  -> {direction}")


if __name__ == "__main__":
    main()


# ======================================================================
# PROMOTING THIS TO THE REAL PIPELINE (only if a teammate cannot)
# ======================================================================
# 1. Move the `invert_peak_curve` function into  src/fitting.py.
# 2. Save this file as  scripts/03_fit_per_subject.py  and at the top
#    replace the absolute REPO_ROOT line with the same pattern the other
#    scripts use:
#
#        import sys
#        REPO_ROOT = Path(__file__).resolve().parent.parent
#        sys.path.insert(0, str(REPO_ROOT))
#        from src.fitting import invert_peak_curve
#
# 3. Point the output at the repo's results folder:
#
#        FITTED_TAU_CSV = REPO_ROOT / "results" / "fitted_tau.csv"
#
# 4. Then  scripts/05_compare_tau.py  reads that fitted_tau.csv.
