"""Per-subject model fitting: assign each subject a tau_inh from their alpha peak.

Reads:  results/peak_curve.csv  (tau_inh -> simulated peak, from script 02)
        results/features.csv     (per-subject features, from script 01)
Writes: results/fitted_tau.csv

Output columns:
    subject_id, group, fitted_tau_ms

For each subject we invert the peak-vs-tau_inh curve: given the subject's
measured alpha peak frequency, we read off the tau_inh that makes the model
oscillate at that frequency (see src/fitting.invert_peak_curve for the method
and the inversion convention). This is the model-side analogue of script 01:
01 measures the alpha peak in the data, 03 expresses that peak as a model
parameter so it can be compared across groups in script 05.
"""

import sys
from pathlib import Path

import pandas as pd

# Make the project root importable so `from src.fitting import ...` works.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.fitting import invert_peak_curve  # noqa: E402

PEAK_CURVE_CSV = REPO_ROOT / "results" / "peak_curve.csv"
FEATURES_CSV = REPO_ROOT / "results" / "features.csv"
FITTED_TAU_CSV = REPO_ROOT / "results" / "fitted_tau.csv"


def main():
    if not PEAK_CURVE_CSV.exists():
        raise FileNotFoundError(
            f"{PEAK_CURVE_CSV} not found. Run scripts/02_simulate_network.py first."
        )
    if not FEATURES_CSV.exists():
        raise FileNotFoundError(
            f"{FEATURES_CSV} not found. Run scripts/01_extract_features.py first."
        )

    curve = pd.read_csv(PEAK_CURVE_CSV)   # columns: tau_inh_ms, simulated_peak_hz
    feats = pd.read_csv(FEATURES_CSV)     # columns: subject_id, group, alpha_peak_hz, ...

    # Report curve coverage. Peaks outside the curve range would be clamped to
    # the nearest endpoint by the inversion, so flag them rather than hide them.
    lo, hi = curve.simulated_peak_hz.min(), curve.simulated_peak_hz.max()
    n_out = int(((feats.alpha_peak_hz < lo) | (feats.alpha_peak_hz > hi)).sum())
    print(f"Loaded {len(feats)} subjects; lookup curve covers {lo:.1f}-{hi:.1f} Hz.")
    if n_out:
        print(f"  WARNING: {n_out} subject(s) lie outside the curve range and were clamped.")
    else:
        print("  All subjects fall inside the curve range (no clamping).")

    # The fit: one vectorised call does every subject.
    fitted = invert_peak_curve(
        feats.alpha_peak_hz.values,
        curve.tau_inh_ms.values,
        curve.simulated_peak_hz.values,
    )

    out = pd.DataFrame({
        "subject_id": feats.subject_id,
        "group": feats.group,
        "fitted_tau_ms": fitted,
    })
    out.to_csv(FITTED_TAU_CSV, index=False, float_format="%.4f")
    print(f"\nWrote {len(out)} fitted tau values to "
          f"{FITTED_TAU_CSV.relative_to(REPO_ROOT)}")

    # Quick sanity print: PD has the slower alpha, so PD should get the larger
    # fitted tau_inh. If this comes out the other way, the inversion is flipped.
    med = out.groupby("group").fitted_tau_ms.median()
    for g, v in med.items():
        print(f"  median fitted tau_inh, {g:>8s}: {v:6.2f} ms")


if __name__ == "__main__":
    main()
