"""
Step 3b — Robust individual alpha peak detection.

The naive argmax in 7-13 Hz produces an artefact: subjects without a clear
alpha peak get pinned to the lower edge (7 Hz), inflating the apparent
"slowing" effect in PD. Fix it by requiring an actual local maximum with
some prominence; if none exists, mark as NaN.

Method:
  - For each subject, average PSD across posterior channels.
  - Convert to log10 power for peak detection (peaks more visible on log scale).
  - Use scipy.signal.find_peaks within 6-14 Hz (a bit wider than alpha proper
    so true peaks near the edge are still caught), with a prominence threshold
    relative to the local 1/f slope.
  - If multiple peaks found, take the most prominent one. If none, NaN.

We then redo the group test on subjects who actually have a detectable peak.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
FIG_DIR = Path(__file__).resolve().parent.parent / "figures" / "03_compare"
FIG_DIR.mkdir(parents=True, exist_ok=True)

POSTERIOR_CH = ["O1", "Oz", "O2", "PO7", "PO8", "POz", "P3", "Pz", "P4"]
SEARCH_RANGE = (6.0, 14.0)
PROMINENCE_DB = 0.5  # peak must rise at least 0.5 dB above local trend


def detect_alpha_peak(freqs: np.ndarray, psd_1d: np.ndarray) -> float | None:
    """Return the alpha peak frequency in Hz, or None if no peak is detected."""
    log_psd = 10 * np.log10(psd_1d + 1e-30)
    mask = (freqs >= SEARCH_RANGE[0]) & (freqs <= SEARCH_RANGE[1])
    f_loc = freqs[mask]
    p_loc = log_psd[mask]

    # Detrend by subtracting a linear fit (rough 1/f removal in log-log-ish way).
    # In dB vs Hz the 1/f looks roughly linear, so this works fine.
    coeffs = np.polyfit(f_loc, p_loc, 1)
    p_flat = p_loc - np.polyval(coeffs, f_loc)

    peaks, props = find_peaks(p_flat, prominence=PROMINENCE_DB)
    if len(peaks) == 0:
        return None
    # Pick the most prominent one
    best = peaks[np.argmax(props["prominences"])]
    return float(f_loc[best])


def main() -> None:
    blob = np.load(CACHE_DIR / "group_psd.npz", allow_pickle=True)
    psd = blob["psd"]
    freqs = blob["freqs"]
    channels = blob["channels"].tolist()
    subject_ids = blob["subject_ids"]
    groups = blob["groups"]

    post_idx = [channels.index(ch) for ch in POSTERIOR_CH if ch in channels]
    post_psd = psd[:, post_idx, :].mean(axis=1)  # (n_subj, n_freq)

    rows = []
    for i, subj in enumerate(subject_ids):
        peak_hz = detect_alpha_peak(freqs, post_psd[i])
        rows.append({
            "subject": str(subj),
            "group": str(groups[i]),
            "alpha_peak_hz": peak_hz if peak_hz is not None else np.nan,
            "peak_detected": peak_hz is not None,
        })
    df = pd.DataFrame(rows)
    df.to_csv(CACHE_DIR / "alpha_peak_robust_per_subject.csv", index=False)

    # Detection rate per group
    print("Detection rates:")
    for g in ("Control", "PD"):
        sub = df[df.group == g]
        n_det = sub["peak_detected"].sum()
        print(f"  {g}: {n_det}/{len(sub)} subjects with detectable alpha peak ({n_det/len(sub)*100:.0f}%)")

    # Group comparison on subjects WITH a detected peak
    df_det = df.dropna(subset=["alpha_peak_hz"])
    ctrl = df_det.loc[df_det.group == "Control", "alpha_peak_hz"].to_numpy()
    pdv = df_det.loc[df_det.group == "PD", "alpha_peak_hz"].to_numpy()
    if len(ctrl) > 0 and len(pdv) > 0:
        U, p = stats.mannwhitneyu(pdv, ctrl, alternative="two-sided")
        print(f"\nDetected-peak subjects only:")
        print(f"  Control: median={np.median(ctrl):.2f} Hz  mean={np.mean(ctrl):.2f}  n={len(ctrl)}")
        print(f"  PD:      median={np.median(pdv):.2f} Hz  mean={np.mean(pdv):.2f}  n={len(pdv)}")
        print(f"  Mann-Whitney U={U:.0f}, p={p:.4g}")
    else:
        U, p = np.nan, np.nan

    # Also compare DETECTION RATES — a subject with no detectable alpha peak
    # could itself be informative.
    n_ctrl_det = df.loc[df.group == "Control", "peak_detected"].sum()
    n_pd_det = df.loc[df.group == "PD", "peak_detected"].sum()
    n_ctrl = (df.group == "Control").sum()
    n_pd = (df.group == "PD").sum()
    odds, p_fisher = stats.fisher_exact(
        [[n_ctrl_det, n_ctrl - n_ctrl_det],
         [n_pd_det, n_pd - n_pd_det]]
    )
    print(f"\nFisher exact on peak-detection rate: odds={odds:.2f}, p={p_fisher:.4g}")

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    bins = np.arange(6, 14.25, 0.25)
    axes[0].hist(ctrl, bins=bins, alpha=0.6,
                 label=f"Control (median={np.median(ctrl):.2f} Hz, n={len(ctrl)})", color="C0")
    axes[0].hist(pdv, bins=bins, alpha=0.6,
                 label=f"PD (median={np.median(pdv):.2f} Hz, n={len(pdv)})", color="C3")
    axes[0].set_xlabel("Individual alpha peak frequency (Hz)")
    axes[0].set_ylabel("# subjects")
    if not np.isnan(p):
        axes[0].set_title(f"Posterior alpha peak (detected only)\nU={U:.0f}, p={p:.3g}")
    axes[0].legend()

    cats = ["Control", "PD"]
    detected = [n_ctrl_det, n_pd_det]
    missing = [n_ctrl - n_ctrl_det, n_pd - n_pd_det]
    x = np.arange(len(cats))
    axes[1].bar(x, detected, label="peak detected", color="C2")
    axes[1].bar(x, missing, bottom=detected, label="no peak", color="lightgrey")
    for i, (d, m) in enumerate(zip(detected, missing)):
        total = d + m
        axes[1].text(i, total + 0.5, f"{d}/{total}\n({d/total*100:.0f}%)",
                     ha="center", va="bottom", fontsize=10)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(cats)
    axes[1].set_ylabel("# subjects")
    axes[1].set_title(f"Alpha peak detectability\nFisher p={p_fisher:.3g}")
    axes[1].legend()

    fig.suptitle("Robust alpha peak detection (find_peaks, prominence ≥ 0.5 dB)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "alpha_peak_robust.png", dpi=130)
    plt.close(fig)
    print(f"\nFigure saved: {FIG_DIR / 'alpha_peak_robust.png'}")


if __name__ == "__main__":
    main()
