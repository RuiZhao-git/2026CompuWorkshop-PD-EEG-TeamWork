"""Non-parametric group comparison utilities.

Functions used by `scripts/04_compare_features.py` and by the matching
exploratory notebook.

We use non-parametric (rank-based) tests rather than t-tests because
features derived from a power spectrum are typically skewed and not
normally distributed. The Mann-Whitney U test compares the medians (or
more precisely, the rank distributions) of two groups and is robust to
outliers and to non-normal shapes.
"""

import numpy as np
from scipy.stats import mannwhitneyu


def rank_biserial(u_stat, n1, n2):
    """Rank-biserial correlation, an effect size for Mann-Whitney U.

    Definition matching scipy's U convention (U counts the number of
    pairs in which the first sample's value exceeds the second's):

        r = 2 * U / (n1 * n2) - 1,   r in [-1, 1]

    The sign reflects which group was passed first to `mannwhitneyu`:
    positive r means the first group had systematically larger values
    than the second. Conventional interpretation: |r| around 0.1, 0.3,
    0.5 maps to small, medium, large effects.

    Parameters
    ----------
    u_stat : float
        U statistic returned by scipy.stats.mannwhitneyu.
    n1, n2 : int
        Sample sizes of the two groups, in the same order that was
        passed to mannwhitneyu.
    """
    return 2.0 * u_stat / (n1 * n2) - 1.0


def compare_groups(df, feature, group_col="group",
                   group_a="Control", group_b="PD"):
    """Compare two groups on one numeric feature with Mann-Whitney U.

    Parameters
    ----------
    df : pandas.DataFrame
        Long-form table with one row per subject. Must contain `feature`
        and `group_col` columns.
    feature : str
        Column name of the numeric feature to compare.
    group_col : str
        Column name that labels each subject's group.
    group_a, group_b : str
        Group labels. The U statistic is computed with `group_a` first,
        so the sign of the resulting rank-biserial r is interpreted as
        "positive means group_a had larger values than group_b".

    Returns
    -------
    dict with keys:
        feature, n_<a>, n_<b>, median_<a>, median_<b>, median_diff,
        u_statistic, p_value, rank_biserial.
    """
    values_a = df.loc[df[group_col] == group_a, feature].values
    values_b = df.loc[df[group_col] == group_b, feature].values

    u_stat, p_val = mannwhitneyu(values_a, values_b, alternative="two-sided")

    return {
        "feature": feature,
        f"n_{group_a}": int(len(values_a)),
        f"n_{group_b}": int(len(values_b)),
        f"median_{group_a}": float(np.median(values_a)),
        f"median_{group_b}": float(np.median(values_b)),
        "median_diff": float(np.median(values_a) - np.median(values_b)),
        "u_statistic": float(u_stat),
        "p_value": float(p_val),
        "rank_biserial": float(rank_biserial(u_stat, len(values_a), len(values_b))),
    }


def p_value_stars(p):
    """Conventional significance-level notation: ***, **, *, or 'ns'."""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"
