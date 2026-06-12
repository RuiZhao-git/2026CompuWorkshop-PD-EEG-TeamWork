"""
draft_05_compare_tau.py   (TEMPORARY / BACKUP -- not part of the git repo)
==========================================================================

WHAT THIS FILE IS
-----------------
A reserve copy of pipeline step 05 ("group comparison on the fitted
model parameter") for the PD EEG project. Like the step-03 backup next
to it, it lives outside the repository, reads only, and writes its
outputs beside itself. Heavily commented so it can be handed to a
teammate as an explanation.

It depends on the output of step 03: it reads `fitted_tau.csv`, which
draft_03_fit_per_subject.py produced in this same folder.

======================================================================
1. WHAT THIS STEP TESTS
======================================================================
Step 04 already tested the hypothesis at the DATA level: it compared the
measured alpha peak (and theta / beta power) between PD and Control.

Step 05 is the MODEL-level twin of that test. After step 03 gave every
subject a fitted inhibitory time constant tau_inh, step 05 asks:

        is the fitted tau_inh systematically HIGHER in PD than in
        Control?

That is the model's way of saying "the alpha rhythm is slower in PD",
because in our model a higher tau_inh is exactly what produces a slower
oscillation. The headline result of the whole project is the size of
that group difference, the "+ delta tau_inh".

The test the team agreed on (see the Team-Task-4 slide):

        H0: tau_inh is the same in both groups.
        H1: tau_inh is HIGHER in PD than in Control.   (directional)
        One-sided Mann-Whitney U test, alpha = 0.05.

Why one-sided: we are not asking "is it different in any direction", we
predicted the direction in advance (PD slower -> higher tau). A one-sided
test spends all its sensitivity on that predicted direction.

Why Mann-Whitney rather than a t-test: same reason as step 04. These
values are not guaranteed normal, and a rank-based test is robust to
skew and outliers. (src/stats.py in the repo explains this too.)

======================================================================
2. AN IMPORTANT HONEST POINT ABOUT THIS TEST
======================================================================
The fitted tau_inh is, by construction, a MONOTONE re-mapping of the
measured alpha peak: step 03 just read tau off a curve that decreases
smoothly with the peak. A rank-based test (Mann-Whitney) only looks at
the ORDER of the values, and a monotone map does not change that order.

Consequence: the p-value step 05 gets for tau_inh is essentially the
SAME as the one step 04 got for the alpha peak. It is not numerically
identical here -- step 04 gives alpha_peak two-sided p = 0.00055, step
05 gives tau two-sided p = 0.00049 -- but only because the lookup curve
has small flat steps ("plateaus"), so a couple of distinct alpha peaks
map to the same fitted tau, which slightly changes how rank-ties are
counted. The ORDER of every subject is otherwise preserved, so the test
and the conclusion are the same. So step 05 is NOT independent new
evidence -- it re-expresses the data-level alpha-peak effect in the
model's own units (tau, in ms). That is still worth doing (it is the
"+ delta tau" headline, in interpretable units), but be ready if someone
asks "isn't this just your alpha-peak result again?". The honest answer
is yes, and the genuinely independent check is the synthetic-data
recovery test (does the fitting return a tau we put in), which is a
separate, still-open item.

The script prints both p-values side by side so this point is visible
rather than hidden.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

# ----------------------------------------------------------------------
# PATHS
# ----------------------------------------------------------------------
REPO_ROOT = Path("/Users/r.z/Desktop/2026CompuWorkshop-PD-EEG-modeling")

# Step 05 reads what step 03 produced. The step-03 backup wrote
# fitted_tau.csv into THIS folder, so we look here first; if you instead
# ran the real pipeline, point this at REPO_ROOT/results/fitted_tau.csv.
OUT_DIR = Path(__file__).resolve().parent
FITTED_TAU_CSV = OUT_DIR / "fitted_tau.csv"

# Outputs, again written beside this script (not into the repo).
SUMMARY_CSV = OUT_DIR / "group_comparison_tau.csv"
FIGURE_PNG = OUT_DIR / "compare_tau.png"

# Same group colours as the rest of the project (teal = Control, brick =
# PD) so that, if this is ever promoted, the figure matches the deck.
GROUP_COLOR = {"Control": "#0f766e", "PD": "#92400e"}


def rank_biserial(u_stat, n1, n2):
    """Effect size for Mann-Whitney U, in [-1, 1].

        r = 2 * U / (n1 * n2) - 1

    Computed with the PD group passed FIRST, so a positive r means
    "PD had the larger tau_inh", which is the direction we predicted.
    This is the same formula as src/stats.py uses, repeated here so this
    backup has no dependency on the repo's source code.
    """
    return 2.0 * u_stat / (n1 * n2) - 1.0


def make_boxplot(ax, control_vals, pd_vals):
    """Two-group box plot of tau_inh with individual subjects as dots.

    Mirrors the plotting style of scripts/04_compare_features.py so the
    figure looks like a sibling of the data-level figures.
    """
    box = ax.boxplot(
        [control_vals, pd_vals],
        tick_labels=["Control", "PD"],
        patch_artist=True,
        widths=0.55,
        medianprops=dict(color="black", linewidth=1.8),
        showfliers=False,   # we draw every point ourselves, below
    )
    for patch, group in zip(box["boxes"], ["Control", "PD"]):
        patch.set_facecolor(GROUP_COLOR[group])
        patch.set_alpha(0.5)
        patch.set_edgecolor(GROUP_COLOR[group])

    # Raw points with a little horizontal jitter so equal values do not
    # overplot. Fixed seed (0) so the figure is reproducible.
    rng = np.random.default_rng(0)
    for x_center, values, group in zip([1, 2],
                                       [control_vals, pd_vals],
                                       ["Control", "PD"]):
        jitter = rng.normal(0, 0.04, size=len(values))
        ax.scatter(x_center + jitter, values, s=14,
                   color=GROUP_COLOR[group], alpha=0.55, edgecolors="none")

    ax.set_title("fitted tau_inh (ms)", fontsize=11)
    ax.set_ylabel("tau_inh (ms)")
    ax.grid(alpha=0.25, axis="y")
    ax.set_axisbelow(True)


def main():
    if not FITTED_TAU_CSV.exists():
        raise FileNotFoundError(
            f"{FITTED_TAU_CSV} not found. Run draft_03_fit_per_subject.py "
            "first -- it writes fitted_tau.csv into this folder."
        )
    df = pd.read_csv(FITTED_TAU_CSV)

    # Split the fitted tau by group.
    control = df.loc[df.group == "Control", "tau_inh_ms"].values
    pd_vals = df.loc[df.group == "PD", "tau_inh_ms"].values
    n_c, n_p = len(control), len(pd_vals)

    # ------------------------------------------------------------------
    # The test. We pass PD FIRST so that:
    #   * alternative="greater" tests H1: tau(PD) > tau(Control);
    #   * the rank-biserial r is positive when PD > Control.
    # We also compute the two-sided p so we can show, side by side, that
    # it matches step 04's alpha-peak p (the monotone-mapping point).
    # ------------------------------------------------------------------
    u_one, p_one = mannwhitneyu(pd_vals, control, alternative="greater")
    u_two, p_two = mannwhitneyu(pd_vals, control, alternative="two-sided")
    r = rank_biserial(u_one, n_p, n_c)   # U is the same for both alternatives

    median_c, median_p = float(np.median(control)), float(np.median(pd_vals))

    # ------------------------------------------------------------------
    # Save a tidy one-row summary table (same spirit as
    # results/group_comparison.csv, but for the fitted model parameter).
    # ------------------------------------------------------------------
    summary = pd.DataFrame([{
        "parameter": "tau_inh_ms",
        "n_Control": n_c,
        "n_PD": n_p,
        "median_Control": median_c,
        "median_PD": median_p,
        "median_diff_PD_minus_Control": median_p - median_c,
        "u_statistic": float(u_one),
        "p_value_one_sided_PD_greater": float(p_one),
        "p_value_two_sided": float(p_two),
        "rank_biserial": float(r),
    }])
    summary.to_csv(SUMMARY_CSV, index=False, float_format="%.6f")

    # ------------------------------------------------------------------
    # Readable terminal report.
    # ------------------------------------------------------------------
    print(f"Fitted tau_inh: {n_c} Control, {n_p} PD")
    print(f"  median Control = {median_c:6.2f} ms")
    print(f"  median PD      = {median_p:6.2f} ms")
    print(f"  delta (PD - Control) = {median_p - median_c:+.2f} ms"
          "   <- this is the project's headline number")
    print(f"  Mann-Whitney U = {u_one:.1f}")
    print(f"  one-sided p (H1: PD > Control) = {p_one:.6g}")
    print(f"  two-sided p                    = {p_two:.6g}")
    print(f"  effect size (rank-biserial r)  = {r:+.3f}")
    decision = "reject H0" if p_one < 0.05 else "do not reject H0"
    print(f"  decision at alpha = 0.05 (one-sided): {decision}")
    print("\nNote: the two-sided p above closely matches (not exactly) the "
          "alpha_peak_hz p in results/group_comparison.csv,\nbecause fitted "
          "tau is a monotone re-mapping of the alpha peak; the small gap is "
          "rank-ties from the\ncurve's plateaus (see header, section 2).")
    print(f"\nWrote summary to {SUMMARY_CSV}")

    # ------------------------------------------------------------------
    # Figure.
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    make_boxplot(ax, control, pd_vals)
    fig.tight_layout()
    fig.savefig(FIGURE_PNG, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote figure to {FIGURE_PNG}")


if __name__ == "__main__":
    main()


# ======================================================================
# PROMOTING THIS TO THE REAL PIPELINE (only if a teammate cannot)
# ======================================================================
# 1. Save as  scripts/05_compare_tau.py.
# 2. Read the fitted file from the repo:
#        FITTED_TAU_CSV = REPO_ROOT / "results" / "fitted_tau.csv"
# 3. Write outputs into the repo:
#        SUMMARY_CSV = REPO_ROOT / "results" / "group_comparison_tau.csv"
#        FIGURE_PNG  = REPO_ROOT / "results" / "figures" / "compare_tau.png"
# 4. Optional: instead of the local rank_biserial copy, reuse the repo's
#    helper with  from src.stats import rank_biserial  (after adding
#    REPO_ROOT to sys.path, like scripts/04 does). The one-sided test
#    itself is not in src/stats.compare_groups, so keep the mannwhitneyu
#    call here, or extend compare_groups with an `alternative` argument.
