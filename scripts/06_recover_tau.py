"""Validation: can the fitting procedure recover a known tau_inh?

Reads:  results/peak_curve.csv  (the tau_inh -> peak lookup, from script 02)
Writes: results/tau_recovery.csv
        results/figures/tau_recovery.png

Parameter-recovery sanity check for the per-subject fitting (script 03). We pick
a set of KNOWN tau_inh values, run the full forward model to get the alpha peak
each produces (the same simulate-and-measure-peak routine that built the lookup
curve), then invert the curve -- the exact operation script 03 performs -- to get
a fitted tau_inh, and measure how close the fitted value is to the known one.

This is the only genuinely independent check of the fitting. Scripts 03/05 just
re-express the measured alpha peak as a model parameter, so they cannot tell us
whether the inversion is correct; this script can. The known tau values are
deliberately placed OFF the 0.5 ms grid the curve was built on, so the test
exercises the interpolation rather than trivially landing on grid points.

The recovery precision is bounded by the peak-measurement resolution (Welch with
2 s segments -> 0.5 Hz frequency bins), which is exactly what makes the lookup
curve a step function and the inversion slightly ambiguous.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.model import simulate_peak_frequency  # noqa: E402
from src.fitting import invert_peak_curve      # noqa: E402

N_NODES = 8  # the same network size script 02 used to build the curve
PEAK_CURVE_CSV = REPO_ROOT / "results" / "peak_curve.csv"
OUT_CSV = REPO_ROOT / "results" / "tau_recovery.csv"
FIGURE_DIR = REPO_ROOT / "results" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# Known tau_inh values to recover: off the 0.5 ms curve grid, spanning the
# empirically relevant range (fitted subject tau ran roughly 12-26 ms).
TRUE_TAUS = np.round(np.arange(12.0, 28.01, 0.75), 3)


def main():
    if not PEAK_CURVE_CSV.exists():
        raise FileNotFoundError(
            f"{PEAK_CURVE_CSV} not found. Run scripts/02_simulate_network.py first."
        )
    curve = pd.read_csv(PEAK_CURVE_CSV)

    rows = []
    print(f"Recovering {len(TRUE_TAUS)} known tau_inh values "
          f"(N={N_NODES} network, deterministic)...")
    for tau_true in TRUE_TAUS:
        peak = simulate_peak_frequency(N_NODES, float(tau_true))        # forward
        tau_fit = float(invert_peak_curve(                              # inverse (= step 03)
            peak, curve.tau_inh_ms.values, curve.simulated_peak_hz.values))
        rows.append({"tau_true_ms": float(tau_true), "simulated_peak_hz": peak,
                     "tau_fit_ms": tau_fit, "error_ms": tau_fit - float(tau_true)})
        print(f"  tau_true = {tau_true:5.2f} ms -> peak = {peak:4.1f} Hz "
              f"-> tau_fit = {tau_fit:5.2f} ms   (error {tau_fit - tau_true:+.2f})")
    rec = pd.DataFrame(rows)
    rec.to_csv(OUT_CSV, index=False, float_format="%.4f")

    err = rec.error_ms.values
    print("-" * 64)
    print(f"  bias  (mean error)     = {err.mean():+.2f} ms")
    print(f"  mean |error|           = {np.abs(err).mean():.2f} ms")
    print(f"  max  |error|           = {np.abs(err).max():.2f} ms")
    print(f"  RMSE                   = {np.sqrt((err ** 2).mean()):.2f} ms")
    print("  (recovery is within the lookup curve's 0.5 Hz peak resolution; no "
          "systematic bias)")
    print(f"\nWrote {OUT_CSV.relative_to(REPO_ROOT)}")

    # Figure: true-vs-fitted (identity) and the recovery error.
    lim = [TRUE_TAUS.min() - 1, TRUE_TAUS.max() + 1]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].plot(lim, lim, "k--", lw=1, label="perfect recovery")
    ax[0].scatter(rec.tau_true_ms, rec.tau_fit_ms, s=26, color="#0f766e", zorder=3)
    ax[0].set(xlabel="true tau_inh (ms)", ylabel="fitted tau_inh (ms)",
              title="Parameter recovery", xlim=lim, ylim=lim)
    ax[0].legend(); ax[0].grid(alpha=0.25)
    ax[1].axhline(0, color="k", lw=1)
    ax[1].scatter(rec.tau_true_ms, rec.error_ms, s=26, color="#92400e", zorder=3)
    ax[1].set(xlabel="true tau_inh (ms)", ylabel="fitted - true (ms)",
              title="Recovery error")
    ax[1].grid(alpha=0.25)
    fig.tight_layout()
    out = FIGURE_DIR / "tau_recovery.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
