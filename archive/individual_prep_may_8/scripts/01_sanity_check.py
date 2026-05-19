"""
Step 1 — Sanity check.

Load a couple of subjects from each group and check:
- channel layout (which electrodes are present, are they all the same across subjects?)
- sampling rate (should be 125 Hz per the README)
- recording duration
- whether the data looks reasonable (no flat channels, no obvious artifacts)
- raw trace plot (first 10 s of a few channels) and PSD plot per subject

Outputs go to ../figures/01_sanity/ as PNGs.
"""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")  # headless: just save PNGs, don't open windows
import matplotlib.pyplot as plt
import mne

# Force MNE to use matplotlib (not Qt) for raw browser plots so we can savefig().
mne.viz.set_browser_backend("matplotlib")

DATA_ROOT = Path("/Users/r.z/Desktop/PD")
FIG_DIR = Path(__file__).resolve().parent.parent / "figures" / "01_sanity"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Pick 2 from each group as a quick visual check
SAMPLES = {
    "Control": ["Control1001", "Control1051"],
    "PD": ["PD1001", "PD1051"],
}


def summarize(raw: mne.io.BaseRaw, label: str) -> dict:
    info = raw.info
    summary = {
        "label": label,
        "n_channels": len(info["ch_names"]),
        "ch_names": info["ch_names"],
        "sfreq": info["sfreq"],
        "duration_s": raw.times[-1],
        "highpass": info["highpass"],
        "lowpass": info["lowpass"],
    }
    return summary


def plot_one(raw: mne.io.BaseRaw, label: str) -> None:
    # Raw trace: first 10 s, all channels stacked.
    fig = raw.copy().crop(tmin=0, tmax=10).plot(
        n_channels=len(raw.ch_names),
        show=False,
        scalings="auto",
        title=f"{label} — first 10 s",
    )
    fig.savefig(FIG_DIR / f"{label}_raw10s.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    # PSD: 1–60 Hz is plenty for resting-state. Welch via compute_psd().
    psd = raw.compute_psd(method="welch", fmin=1, fmax=60, n_fft=int(raw.info["sfreq"] * 4))
    fig = psd.plot(show=False, average=False)
    fig.suptitle(f"{label} — PSD per channel")
    fig.savefig(FIG_DIR / f"{label}_psd.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    all_summaries = []
    for group, subjects in SAMPLES.items():
        for subj in subjects:
            fpath = DATA_ROOT / group / f"{subj}_preproc_raw.fif"
            print(f"\n=== Loading {fpath.name} ===")
            raw = mne.io.read_raw_fif(fpath, preload=True, verbose="ERROR")
            s = summarize(raw, subj)
            all_summaries.append(s)
            print(
                f"  channels: {s['n_channels']}  sfreq: {s['sfreq']} Hz  "
                f"duration: {s['duration_s']:.1f} s  "
                f"highpass: {s['highpass']} Hz  lowpass: {s['lowpass']} Hz"
            )
            plot_one(raw, subj)

    # Cross-check: are channel sets identical across subjects?
    ch_sets = [tuple(s["ch_names"]) for s in all_summaries]
    if len(set(ch_sets)) == 1:
        print("\nAll sampled subjects share the SAME channel set.")
        print(f"Channels ({len(ch_sets[0])}): {list(ch_sets[0])}")
    else:
        print("\nWARNING: channel sets differ across subjects!")
        for s in all_summaries:
            print(f"  {s['label']}: {s['ch_names']}")

    # And same sampling rate?
    sfreqs = {s["sfreq"] for s in all_summaries}
    print(f"\nSampling rates seen: {sfreqs}")

    print(f"\nFigures saved to: {FIG_DIR}")


if __name__ == "__main__":
    main()
