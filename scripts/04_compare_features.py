"""
04_compare_features.py
======================
Direct, data-level test of the team's hypothesis. For each feature we
extracted in script 01, compare the PD group to the Control group and
report whether the two distributions differ.

Inputs
------
- results/features.csv  (produced by scripts/01_extract_features.py)

Outputs
-------
- stdout: a one-line summary per feature, with significance stars
- results/group_comparison.csv: a tidy summary table, one row per feature
- results/figures/compare_all.png: 4 features as box plots, side by side
- results/figures/compare_<feature>.png: one box plot per feature, sized
  for slides

What the script does, conceptually
----------------------------------
1. Load `features.csv`. It contains 149 rows, one per participant, with
   the group label (Control or PD) and the four EEG features we extracted.
2. For each of the four features, run a Mann-Whitney U test comparing
   the PD group against the Control group.
       - Why Mann-Whitney, not a t-test? Features derived from a power
         spectrum are typically skewed (not normal). Mann-Whitney does
         not assume normality and compares the ranks of the values, so
         it is robust to skew and outliers.
3. For each feature also compute the rank-biserial correlation as an
   effect size. The U statistic alone depends on sample sizes and is
   hard to read; the rank-biserial r is in [-1, 1] and easier to
   interpret.
4. Make a box plot per feature with the individual subjects shown as
   jittered dots so the underlying distribution is visible.
5. Save everything under `results/`.

How this fits into the project
------------------------------
This script is the *data-level* hypothesis test. It does not use the
Wilson-Cowan model at all. Scripts 02 and 03 are the *model-level*
analogue: they fit the model parameter tau_I per subject and then
compare tau_I distributions across groups. The two views should agree.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Make the project root importable so `from src.stats import ...` works.
# This script lives in scripts/, src/ lives parallel to it.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.stats import compare_groups, p_value_stars  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration: paths, features to compare, colors
# ---------------------------------------------------------------------------

FEATURES_CSV = REPO_ROOT / "results" / "features.csv"
SUMMARY_CSV = REPO_ROOT / "results" / "group_comparison.csv"
FIGURE_DIR = REPO_ROOT / "results" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# Which columns of features.csv to compare between PD and Control.
# These are exactly the four numeric columns produced by script 01.
FEATURES_TO_COMPARE = [
    "alpha_peak_hz",   # frequency (Hz) of the dominant rhythm in 7-13 Hz
    "alpha_power",     # relative band power in 8-13 Hz
    "theta_power",     # relative band power in 4-8 Hz
    "beta_power",      # relative band power in 13-30 Hz
]

# Consistent colors for the two groups across all figures, matching the
# rest of the project (teal for control / excitatory, brick for PD /
# inhibitory).
GROUP_COLOR = {
    "Control": "#0f766e",
    "PD":      "#92400e",
}


# ---------------------------------------------------------------------------
# Plotting helper
# ---------------------------------------------------------------------------

def make_boxplot(ax, df, feature):
    """Draw a 2-group box plot of `feature` on the given axis.

    The box shows median, IQR, and whiskers. Individual subject values
    are scattered as small jittered points so the reader can see the
    underlying distribution (skew, density, outliers, n).
    """
    ctrl = df.loc[df.group == "Control", feature].values
    pdat = df.loc[df.group == "PD", feature].values

    # The actual box plot. `showfliers=False` hides matplotlib's outlier
    # markers because we are going to plot every individual point anyway.
    box = ax.boxplot(
        [ctrl, pdat],
        tick_labels=["Control", "PD"],
        patch_artist=True,
        widths=0.55,
        medianprops=dict(color="black", linewidth=1.8),
        showfliers=False,
    )
    # Color the two box patches.
    for patch, group in zip(box["boxes"], ["Control", "PD"]):
        patch.set_facecolor(GROUP_COLOR[group])
        patch.set_alpha(0.5)
        patch.set_edgecolor(GROUP_COLOR[group])

    # Overlay raw points with a small horizontal jitter so two subjects
    # with the same value don't perfectly overplot.
    rng = np.random.default_rng(0)
    for x_center, values, group in zip([1, 2], [ctrl, pdat], ["Control", "PD"]):
        jitter = rng.normal(0, 0.04, size=len(values))
        ax.scatter(
            x_center + jitter, values,
            s=14, color=GROUP_COLOR[group], alpha=0.55, edgecolors="none",
        )

    ax.set_title(feature, fontsize=11)
    ax.grid(alpha=0.25, axis="y")
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Sanity check: features.csv has to exist. If not, tell the user to
    # run the extraction step first.
    if not FEATURES_CSV.exists():
        raise FileNotFoundError(
            f"{FEATURES_CSV} not found. "
            "Run scripts/01_extract_features.py first to produce it."
        )

    # Load the per-subject feature table.
    df = pd.read_csv(FEATURES_CSV)
    n_control = int((df.group == "Control").sum())
    n_pd = int((df.group == "PD").sum())
    print(f"Loaded {len(df)} subjects: {n_control} Control, {n_pd} PD\n")

    # -----------------------------------------------------------------
    # Run the statistical test for every feature and collect results
    # -----------------------------------------------------------------
    rows = [compare_groups(df, f) for f in FEATURES_TO_COMPARE]
    summary = pd.DataFrame(rows)
    summary.to_csv(SUMMARY_CSV, index=False, float_format="%.6f")

    # -----------------------------------------------------------------
    # Print a readable, aligned summary to the terminal
    # -----------------------------------------------------------------
    print("Group comparison, Mann-Whitney U (two-sided):")
    print("-" * 78)
    print(f"  {'feature':>15s}  {'Ctrl median':>11s}  "
          f"{'PD median':>10s}  {'p-value':>10s}  {'r':>7s}")
    print("-" * 78)
    for r in rows:
        print(f"  {r['feature']:>15s}  "
              f"{r['median_Control']:11.3f}  "
              f"{r['median_PD']:10.3f}  "
              f"{r['p_value']:10.4g}  "
              f"{r['rank_biserial']:+7.3f}  "
              f"{p_value_stars(r['p_value'])}")
    print("-" * 78)
    print("Significance: *** p<0.001, ** p<0.01, * p<0.05, ns = not significant")
    print("Effect size r: positive means Control had larger values, negative PD did.")
    print(f"\nWrote tidy summary table to "
          f"{SUMMARY_CSV.relative_to(REPO_ROOT)}")

    # -----------------------------------------------------------------
    # Combined figure: all four features as small panels
    # -----------------------------------------------------------------
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.5))
    for ax, feature in zip(axes, FEATURES_TO_COMPARE):
        make_boxplot(ax, df, feature)
    fig.suptitle("PD vs Control: per-subject EEG features",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    out_combined = FIGURE_DIR / "compare_all.png"
    fig.savefig(out_combined, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote combined figure to "
          f"{out_combined.relative_to(REPO_ROOT)}")

    # -----------------------------------------------------------------
    # One figure per feature, sized for placement in slide layouts
    # -----------------------------------------------------------------
    for feature in FEATURES_TO_COMPARE:
        fig, ax = plt.subplots(figsize=(4.2, 4.2))
        make_boxplot(ax, df, feature)
        fig.tight_layout()
        out = FIGURE_DIR / f"compare_{feature}.png"
        fig.savefig(out, dpi=140, bbox_inches="tight")
        plt.close(fig)
    print(f"Wrote per-feature figures to "
          f"{FIGURE_DIR.relative_to(REPO_ROOT)}/compare_<feature>.png")


if __name__ == "__main__":
    main()
