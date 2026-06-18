"""Model-level group comparison: fitted tau_inh, PD vs Control.

Reads:  results/fitted_tau.csv  (from script 03)
Writes: results/group_comparison_tau.csv
        results/figures/compare_tau.png

This is the model-level twin of script 04. Script 04 tests the hypothesis on the
measured features (alpha peak, band powers); script 05 tests it on the fitted
model parameter tau_inh. The team's pre-registered test is one-sided -- H1: PD
has the LARGER tau_inh (slower inhibition -> slower alpha) -- Mann-Whitney U at
alpha = 0.05.

Note on interpretation: fitted tau_inh is a monotone re-mapping of the measured
alpha peak (script 03 reads it off a curve), so this test re-expresses the
data-level alpha-peak effect in model-parameter units. It is not independent
evidence; the genuinely independent check is a synthetic-data recovery test
(simulate at a known tau_inh, confirm the fit returns it), which is future work.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.stats import compare_groups, p_value_stars  # noqa: E402

FITTED_TAU_CSV = REPO_ROOT / "results" / "fitted_tau.csv"
SUMMARY_CSV = REPO_ROOT / "results" / "group_comparison_tau.csv"
FIGURE_DIR = REPO_ROOT / "results" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# Same group colours as script 04 (teal = Control, brick = PD).
GROUP_COLOR = {"Control": "#0f766e", "PD": "#92400e"}


def make_boxplot(ax, df, feature):
    """Two-group box plot of `feature` with individual subjects as jittered dots.

    Mirrors the plotting style of scripts/04_compare_features.py so the figures
    look like a matched pair.
    """
    ctrl = df.loc[df.group == "Control", feature].values
    pdat = df.loc[df.group == "PD", feature].values

    box = ax.boxplot(
        [ctrl, pdat], tick_labels=["Control", "PD"], patch_artist=True,
        widths=0.55, medianprops=dict(color="black", linewidth=1.8),
        showfliers=False,
    )
    for patch, group in zip(box["boxes"], ["Control", "PD"]):
        patch.set_facecolor(GROUP_COLOR[group])
        patch.set_alpha(0.5)
        patch.set_edgecolor(GROUP_COLOR[group])

    rng = np.random.default_rng(0)
    for x_center, values, group in zip([1, 2], [ctrl, pdat], ["Control", "PD"]):
        ax.scatter(x_center + rng.normal(0, 0.04, size=len(values)), values,
                   s=14, color=GROUP_COLOR[group], alpha=0.55, edgecolors="none")

    ax.set_title(feature, fontsize=11)
    ax.grid(alpha=0.25, axis="y")
    ax.set_axisbelow(True)


def main():
    if not FITTED_TAU_CSV.exists():
        raise FileNotFoundError(
            f"{FITTED_TAU_CSV} not found. Run scripts/03_fit_per_subject.py first."
        )
    df = pd.read_csv(FITTED_TAU_CSV)
    n_control = int((df.group == "Control").sum())
    n_pd = int((df.group == "PD").sum())
    print(f"Loaded fitted tau for {len(df)} subjects: {n_control} Control, {n_pd} PD\n")

    # One-sided test. compare_groups passes Control first, so the directional
    # hypothesis "PD > Control" is the alternative "Control is less than PD".
    row = compare_groups(df, "fitted_tau_ms", alternative="less")
    summary = pd.DataFrame([row])
    summary.to_csv(SUMMARY_CSV, index=False, float_format="%.6f")

    pd_minus_control = row["median_PD"] - row["median_Control"]
    print("Model-level group comparison, fitted tau_inh "
          "(Mann-Whitney U, one-sided H1: PD > Control):")
    print("-" * 70)
    print(f"  median Control = {row['median_Control']:6.2f} ms")
    print(f"  median PD      = {row['median_PD']:6.2f} ms")
    print(f"  PD - Control   = {pd_minus_control:+6.2f} ms   "
          "<- the model-level effect size, in ms")
    print(f"  U = {row['u_statistic']:.1f}   "
          f"p = {row['p_value']:.4g} {p_value_stars(row['p_value'])}   "
          f"rank-biserial r = {row['rank_biserial']:+.3f}")
    print("-" * 70)
    print(f"Wrote tidy summary to {SUMMARY_CSV.relative_to(REPO_ROOT)}")

    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    make_boxplot(ax, df, "fitted_tau_ms")
    ax.set_ylabel("fitted tau_inh (ms)")
    fig.tight_layout()
    out = FIGURE_DIR / "compare_tau.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote figure to {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
