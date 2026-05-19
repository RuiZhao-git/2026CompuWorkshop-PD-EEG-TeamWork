"""
Step 3 — Group comparison: PD vs Control.

Computes:
  1. Group-mean PSDs (mean across subjects, per channel, per freq).
  2. Band power per subject per channel for the 5 canonical EEG bands.
     Band power = integral of PSD over the band freqs (sum * df).
     Reported as RELATIVE band power (band / total 1-45 Hz power) so we
     normalize away overall amplitude differences between subjects.
  3. Individual alpha peak frequency (IAF): freq of maximum power in 7-13 Hz,
     averaged over posterior electrodes (where alpha is strongest).
  4. Mann-Whitney U test (PD vs Control) per channel x band, plus FDR correction
     per band (Benjamini-Hochberg). Mann-Whitney is non-parametric so it doesn't
     assume normal distributions, which band powers usually aren't.

Plots:
  - figures/03_compare/group_mean_psd_global.png
      Group-mean PSDs averaged across all channels (one curve per group).
  - figures/03_compare/group_mean_psd_posterior.png
      Same but only posterior channels (where alpha lives).
  - figures/03_compare/band_power_violin.png
      Violin/strip plots of relative band power per group, per band, averaged
      over all channels.
  - figures/03_compare/topomap_<band>.png  (one per band)
      Two topomaps: PD mean and Control mean, plus a difference map.
  - figures/03_compare/alpha_peak_hist.png
      Histogram of individual alpha peak frequency per group.

Outputs:
  - cache/band_power_per_subject.csv  (subject, group, channel, band, abs, rel)
  - cache/group_stats.csv             (channel, band, U, p_raw, p_fdr)
  - cache/alpha_peak_per_subject.csv  (subject, group, alpha_peak_hz)
"""

from pathlib import Path
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import mne

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
FIG_DIR = Path(__file__).resolve().parent.parent / "figures" / "03_compare"
FIG_DIR.mkdir(parents=True, exist_ok=True)

BANDS = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 45.0),
}
TOTAL_BAND = (1.0, 45.0)  # for relative band power
ALPHA_SEARCH = (7.0, 13.0)
POSTERIOR_CH = ["O1", "Oz", "O2", "PO7", "PO8", "POz", "P3", "Pz", "P4"]


def band_power(psd: np.ndarray, freqs: np.ndarray, fmin: float, fmax: float) -> np.ndarray:
    """Integrate PSD between fmin and fmax (per channel/subject)."""
    mask = (freqs >= fmin) & (freqs <= fmax)
    df = float(np.median(np.diff(freqs)))
    return psd[..., mask].sum(axis=-1) * df


def benjamini_hochberg(p: np.ndarray) -> np.ndarray:
    """BH FDR correction. Returns adjusted p-values."""
    p = np.asarray(p)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    adj = ranked * n / (np.arange(n) + 1)
    # Enforce monotonicity from the back.
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out = np.empty_like(adj)
    out[order] = np.clip(adj, 0, 1)
    return out


def make_info(channels: list[str]) -> mne.Info:
    """Build a basic Info with standard 10-20 montage so we can plot topomaps."""
    info = mne.create_info(ch_names=list(channels), sfreq=125.0, ch_types="eeg")
    montage = mne.channels.make_standard_montage("standard_1005")
    info.set_montage(montage, match_case=False, on_missing="warn")
    return info


def main() -> None:
    blob = np.load(CACHE_DIR / "group_psd.npz", allow_pickle=True)
    psd = blob["psd"]                      # (n_subj, n_ch, n_freq), V^2/Hz
    freqs = blob["freqs"]                  # (n_freq,)
    channels = blob["channels"].tolist()   # list of 60 names
    subject_ids = blob["subject_ids"]
    groups = blob["groups"]
    print(f"Loaded PSDs: {psd.shape}, freqs {freqs[0]:.2f}-{freqs[-1]:.2f} Hz")
    print(f"Subjects: Control={int((groups == 'Control').sum())}, PD={int((groups == 'PD').sum())}")

    is_ctrl = groups == "Control"
    is_pd = groups == "PD"

    # ---------- 1) Group-mean PSDs ----------
    psd_log = 10 * np.log10(psd + 1e-30)  # dB scale, easier on the eyes
    mean_ctrl = psd_log[is_ctrl].mean(axis=0)  # (n_ch, n_freq)
    mean_pd = psd_log[is_pd].mean(axis=0)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(freqs, mean_ctrl.mean(axis=0), label=f"Control (n={is_ctrl.sum()})", color="C0")
    ax.plot(freqs, mean_pd.mean(axis=0), label=f"PD (n={is_pd.sum()})", color="C3")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power (dB re 1 V²/Hz)")
    ax.set_title("Group-mean PSD (averaged over all 60 channels)")
    ax.axvspan(8, 13, color="grey", alpha=0.1, label="alpha")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "group_mean_psd_global.png", dpi=130)
    plt.close(fig)

    # Posterior-only view (alpha is strongest here)
    post_idx = [channels.index(ch) for ch in POSTERIOR_CH if ch in channels]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(freqs, mean_ctrl[post_idx].mean(axis=0), label=f"Control (n={is_ctrl.sum()})", color="C0")
    ax.plot(freqs, mean_pd[post_idx].mean(axis=0), label=f"PD (n={is_pd.sum()})", color="C3")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power (dB re 1 V²/Hz)")
    ax.set_title(f"Group-mean PSD over posterior channels {POSTERIOR_CH}")
    ax.axvspan(8, 13, color="grey", alpha=0.1, label="alpha")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "group_mean_psd_posterior.png", dpi=130)
    plt.close(fig)

    # ---------- 2) Band power per subject per channel ----------
    total_pow = band_power(psd, freqs, *TOTAL_BAND)  # (n_subj, n_ch)

    rows_bp = []
    band_rel = {}  # band -> (n_subj, n_ch) relative power
    for band_name, (lo, hi) in BANDS.items():
        bp = band_power(psd, freqs, lo, hi)
        rel = bp / total_pow
        band_rel[band_name] = rel
        for i_subj in range(psd.shape[0]):
            for i_ch, ch in enumerate(channels):
                rows_bp.append({
                    "subject": str(subject_ids[i_subj]),
                    "group": str(groups[i_subj]),
                    "channel": ch,
                    "band": band_name,
                    "abs_power": float(bp[i_subj, i_ch]),
                    "rel_power": float(rel[i_subj, i_ch]),
                })
    df_bp = pd.DataFrame(rows_bp)
    df_bp.to_csv(CACHE_DIR / "band_power_per_subject.csv", index=False)
    print(f"Saved band_power_per_subject.csv ({len(df_bp)} rows)")

    # ---------- 3) Mann-Whitney U per channel x band (on RELATIVE power) ----------
    rows_stats = []
    for band_name in BANDS:
        rel = band_rel[band_name]
        ps_band = []
        us_band = []
        for i_ch, ch in enumerate(channels):
            ctrl_vals = rel[is_ctrl, i_ch]
            pd_vals = rel[is_pd, i_ch]
            U, p = stats.mannwhitneyu(pd_vals, ctrl_vals, alternative="two-sided")
            ps_band.append(p)
            us_band.append(U)
        p_fdr = benjamini_hochberg(np.array(ps_band))
        for i_ch, ch in enumerate(channels):
            rows_stats.append({
                "channel": ch,
                "band": band_name,
                "U": float(us_band[i_ch]),
                "p_raw": float(ps_band[i_ch]),
                "p_fdr": float(p_fdr[i_ch]),
                "ctrl_median": float(np.median(rel[is_ctrl, i_ch])),
                "pd_median": float(np.median(rel[is_pd, i_ch])),
                "diff_pd_minus_ctrl": float(np.median(rel[is_pd, i_ch]) - np.median(rel[is_ctrl, i_ch])),
            })
    df_stats = pd.DataFrame(rows_stats)
    df_stats.to_csv(CACHE_DIR / "group_stats.csv", index=False)
    print(f"Saved group_stats.csv ({len(df_stats)} rows)")

    # Quick text summary of significant electrodes per band
    print("\n--- Channels significant after FDR (p_fdr < 0.05) ---")
    for band_name in BANDS:
        sub = df_stats[(df_stats.band == band_name) & (df_stats.p_fdr < 0.05)]
        print(f"  {band_name}: {len(sub)} / {len(channels)} channels significant")
        if len(sub):
            sample = sub.sort_values("p_fdr").head(5)
            for _, r in sample.iterrows():
                direction = "PD>Ctrl" if r["diff_pd_minus_ctrl"] > 0 else "PD<Ctrl"
                print(f"    {r['channel']:<6}  p_fdr={r['p_fdr']:.4f}  {direction}  Δrel={r['diff_pd_minus_ctrl']:+.4f}")

    # ---------- 4) Violin plots of relative band power averaged across channels ----------
    fig, axes = plt.subplots(1, len(BANDS), figsize=(3 * len(BANDS), 4), sharey=False)
    for ax, (band_name, _) in zip(axes, BANDS.items()):
        rel = band_rel[band_name]
        ctrl_avg = rel[is_ctrl].mean(axis=1)
        pd_avg = rel[is_pd].mean(axis=1)
        parts = ax.violinplot([ctrl_avg, pd_avg], showmedians=True)
        for body, color in zip(parts["bodies"], ("C0", "C3")):
            body.set_facecolor(color)
            body.set_alpha(0.4)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(["Control", "PD"])
        ax.set_title(band_name)
        ax.set_ylabel("Relative power" if band_name == "delta" else "")
        # Test on the channel-averaged value too
        U, p = stats.mannwhitneyu(pd_avg, ctrl_avg, alternative="two-sided")
        ax.text(0.5, 0.95, f"U={U:.0f}\np={p:.3g}", transform=ax.transAxes,
                ha="center", va="top", fontsize=9)
    fig.suptitle("Relative band power (averaged over all 60 channels) — PD vs Control")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "band_power_violin.png", dpi=130)
    plt.close(fig)

    # ---------- 5) Topomaps per band ----------
    info = make_info(channels)
    for band_name in BANDS:
        rel = band_rel[band_name]
        ctrl_topo = rel[is_ctrl].mean(axis=0)  # (n_ch,)
        pd_topo = rel[is_pd].mean(axis=0)
        diff_topo = pd_topo - ctrl_topo

        fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))
        vmax = max(np.abs(ctrl_topo).max(), np.abs(pd_topo).max())
        mne.viz.plot_topomap(ctrl_topo, info, axes=axes[0], show=False,
                             cmap="viridis", vlim=(0, vmax))
        axes[0].set_title(f"Control mean\n{band_name}")
        mne.viz.plot_topomap(pd_topo, info, axes=axes[1], show=False,
                             cmap="viridis", vlim=(0, vmax))
        axes[1].set_title(f"PD mean\n{band_name}")
        dvmax = float(np.abs(diff_topo).max())
        mne.viz.plot_topomap(diff_topo, info, axes=axes[2], show=False,
                             cmap="RdBu_r", vlim=(-dvmax, dvmax))
        axes[2].set_title("PD - Control")
        fig.suptitle(f"Relative {band_name} power")
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"topomap_{band_name}.png", dpi=130)
        plt.close(fig)

    # ---------- 6) Individual alpha peak frequency ----------
    af_lo, af_hi = ALPHA_SEARCH
    af_mask = (freqs >= af_lo) & (freqs <= af_hi)
    # Average PSD across posterior channels first, then find argmax in 7-13 Hz.
    post_psd = psd[:, post_idx, :].mean(axis=1)  # (n_subj, n_freq)
    peak_freqs = freqs[af_mask][np.argmax(post_psd[:, af_mask], axis=1)]
    df_peak = pd.DataFrame({
        "subject": subject_ids,
        "group": groups,
        "alpha_peak_hz": peak_freqs,
    })
    df_peak.to_csv(CACHE_DIR / "alpha_peak_per_subject.csv", index=False)

    U, p = stats.mannwhitneyu(
        df_peak.loc[df_peak.group == "PD", "alpha_peak_hz"],
        df_peak.loc[df_peak.group == "Control", "alpha_peak_hz"],
        alternative="two-sided",
    )
    ctrl_med = float(df_peak.loc[df_peak.group == "Control", "alpha_peak_hz"].median())
    pd_med = float(df_peak.loc[df_peak.group == "PD", "alpha_peak_hz"].median())
    print(f"\nAlpha peak (posterior channels):  Control median={ctrl_med:.2f} Hz   PD median={pd_med:.2f} Hz")
    print(f"  Mann-Whitney U={U:.0f}, p={p:.4g}")

    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.arange(7, 13.25, 0.25)
    ax.hist(df_peak.loc[df_peak.group == "Control", "alpha_peak_hz"], bins=bins,
            alpha=0.5, label=f"Control (median={ctrl_med:.2f} Hz)", color="C0")
    ax.hist(df_peak.loc[df_peak.group == "PD", "alpha_peak_hz"], bins=bins,
            alpha=0.5, label=f"PD (median={pd_med:.2f} Hz)", color="C3")
    ax.set_xlabel("Individual alpha peak frequency (Hz)")
    ax.set_ylabel("# subjects")
    ax.set_title(f"Posterior alpha peak  —  U={U:.0f}, p={p:.3g}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "alpha_peak_hist.png", dpi=130)
    plt.close(fig)

    print(f"\nFigures saved to: {FIG_DIR}")


if __name__ == "__main__":
    main()
