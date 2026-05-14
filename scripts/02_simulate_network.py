"""
02_simulate_network.py
======================
Generate the `tau_inh -> peak frequency` lookup table from the
Wilson-Cowan network. This is the "model side" of the project: it
does not touch any EEG data. The lookup table will be used by
`scripts/03_fit_per_subject.py` to invert the curve and assign each
empirical subject a personal `tau_inh`.

Inputs
------
None. The script builds, runs, and analyses the model end-to-end.

Outputs
-------
- results/peak_curve.csv with columns:
    tau_inh_ms          inhibitory time constant (ms)
    simulated_peak_hz   peak frequency of the network-averaged
                        excitatory signal, in the 3-25 Hz band

- results/figures/peak_curve.png: the same curve plotted, with the
  Control and PD alpha ranges shaded so the slide reader can see how
  the simulated frequencies map to the empirical group ranges.

What the script does, conceptually
----------------------------------
1. Pick a grid of `tau_inh` values that covers the empirical alpha
   range (~7-13 Hz at the group level) with a bit of margin on both
   sides. We use 0.5 ms steps, which is finer than the 0.25 Hz
   frequency resolution of the model's PSD and therefore more than
   sufficient to invert later.

2. For each `tau_inh`, build an N=8 all-to-all Wilson-Cowan network,
   run it deterministically (no noise), and record the peak frequency
   of the network-averaged excitatory signal.

3. Save (tau_inh, peak) as a CSV.

4. Plot the curve and save the figure for use in slides and for
   sanity-checking before running `scripts/03`.

Why a deterministic, all-to-all, single-tau_inh setup
-----------------------------------------------------
The hypothesis is about a uniform, whole-cortex slowing of the alpha
rhythm. The simplest model that captures this is one in which every
node shares the same `tau_inh` and the only free parameter we vary is
that one number. By using a symmetric all-to-all coupling and no
noise, the simulated peak frequency depends *only* on `tau_inh`, so
the lookup is deterministic and reproducible.

Runtime
-------
Roughly 4-6 minutes on a laptop. Progress is printed every 5 points.
"""

import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Make src/ importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.model import simulate_peak_frequency  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Number of nodes. Decided by the team: 8 is a minimal "network" that
# satisfies the assignment's network-model requirement while staying
# computationally cheap. The all-to-all + identical-parameter setup
# makes the result largely insensitive to N (see the matching
# walkthrough notebook for a single-vs-network comparison).
N_NODES = 8

# tau_inh grid. The empirical subject alpha peaks fall in roughly
# 7-13 Hz. From a coarse parameter scan, this corresponds to tau_inh
# in roughly 11-28 ms for N=8. We sweep 11-32 ms with 0.5 ms steps to
# get smooth coverage with margin on both sides.
TAU_INH_GRID = np.arange(11.0, 32.5, 0.5)

# Output paths.
PEAK_CURVE_CSV = REPO_ROOT / "results" / "peak_curve.csv"
FIGURE_DIR = REPO_ROOT / "results" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
PEAK_CURVE_FIGURE = FIGURE_DIR / "peak_curve.png"

# Colors matching the rest of the project.
GROUP_COLOR = {
    "Control": "#0f766e",
    "PD":      "#92400e",
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    n_points = len(TAU_INH_GRID)
    print(f"Wilson-Cowan tau_inh sweep:")
    print(f"  N nodes:   {N_NODES}")
    print(f"  tau_inh:   {TAU_INH_GRID[0]:.1f} to {TAU_INH_GRID[-1]:.1f} ms "
          f"in steps of {TAU_INH_GRID[1] - TAU_INH_GRID[0]:.2f} ms "
          f"({n_points} points)")
    print(f"  Approx runtime: 4-8 minutes\n")

    # ------------------------------------------------------------------
    # Sweep: for each tau_inh, run the model and record the peak Hz
    # ------------------------------------------------------------------
    rows = []
    t0 = time.time()
    for i, tau_inh in enumerate(TAU_INH_GRID, 1):
        # `simulate_peak_frequency` builds a fresh model with the right
        # tau_inh and returns the peak frequency of the
        # network-averaged excitatory signal.
        peak = simulate_peak_frequency(N_NODES, float(tau_inh))
        rows.append({
            "tau_inh_ms": float(tau_inh),
            "simulated_peak_hz": float(peak),
        })
        if i % 5 == 0 or i == n_points:
            elapsed = time.time() - t0
            eta = elapsed / i * (n_points - i)
            print(f"  [{i:3d}/{n_points}] "
                  f"tau_inh={tau_inh:5.2f} ms -> peak={peak:5.2f} Hz   "
                  f"(elapsed {elapsed:5.0f}s, ETA {eta:5.0f}s)")

    # ------------------------------------------------------------------
    # Save the lookup table
    # ------------------------------------------------------------------
    df = pd.DataFrame(rows)
    df.to_csv(PEAK_CURVE_CSV, index=False, float_format="%.4f")
    total = time.time() - t0
    print(f"\nSaved {len(df)} rows to "
          f"{PEAK_CURVE_CSV.relative_to(REPO_ROOT)} in {total:.0f}s")

    # ------------------------------------------------------------------
    # Quick sanity check: is the curve monotonic decreasing?
    # ------------------------------------------------------------------
    is_monotonic = (df["simulated_peak_hz"].diff().dropna() <= 0).all()
    if not is_monotonic:
        print("WARNING: the peak frequency curve is not monotonic. "
              "Check the plot before using this lookup table for fitting; "
              "non-monotonic regions will give ambiguous tau_inh estimates.")
    else:
        print("Curve is monotonic decreasing, ready to be inverted by scripts/03.")

    # ------------------------------------------------------------------
    # Plot for sanity check + slide deck
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(df["tau_inh_ms"], df["simulated_peak_hz"],
            "o-", color="#0f766e", lw=1.5, markersize=4,
            label=f"Wilson-Cowan, N={N_NODES}")
    # Highlight the Control and PD alpha-peak ranges from features.csv.
    ax.axhspan(9, 11, color=GROUP_COLOR["Control"], alpha=0.10,
               label="Control alpha range")
    ax.axhspan(7, 9, color=GROUP_COLOR["PD"], alpha=0.10,
               label="PD alpha range")
    ax.set_xlabel(r"$\tau_{inh}$ (ms)")
    ax.set_ylabel("simulated peak frequency (Hz)")
    ax.set_title(f"Wilson-Cowan peak frequency vs $\\tau_{{inh}}$ (N={N_NODES})")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(PEAK_CURVE_FIGURE, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote figure to {PEAK_CURVE_FIGURE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
