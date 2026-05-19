"""
Step 2 — Compute power spectral density (PSD) for every subject and cache.

Method: Welch's method, 1-60 Hz, on the 60 common channels (see channel_audit.json).
Output: a single .npz with everything we need for Step 3.

Why Welch's method?
  Welch chops the signal into overlapping windows, FFTs each window, then averages.
  Compared to a single FFT of the whole recording, it's smoother and less noisy.
  This is the standard textbook way to estimate resting-state EEG power spectra.

Why 60 channels?
  10 subjects have FT9/PO3/PO4; 139 have Iz/I1/I2. We use the intersection
  (60 channels) so every subject has the same electrode layout.

Why 1-60 Hz?
  Below 1 Hz: noisy near the 0.5 Hz highpass cutoff.
  Above 60 Hz: notch filter at 50 Hz already chews this up; gamma>60 unreliable.
  Standard EEG bands fit comfortably inside 1-60 Hz.

Caching: PSD takes a few minutes for 149 subjects. We save once and re-use.
"""

from pathlib import Path
import json
import time

import numpy as np
import mne

DATA_ROOT = Path("/Users/r.z/Desktop/PD")
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PSD_FMIN, PSD_FMAX = 1.0, 60.0
N_FFT_SECONDS = 4  # 4-second Welch windows -> 0.25 Hz freq resolution


def main() -> None:
    audit = json.loads((CACHE_DIR / "channel_audit.json").read_text())
    common_channels = audit["common_channels"]
    per_subject_meta = audit["per_subject"]
    print(f"Using {len(common_channels)} common channels.")

    psd_list = []
    subject_ids = []
    groups = []
    freqs_ref = None

    t0 = time.time()
    for i, (subj, meta) in enumerate(per_subject_meta.items(), 1):
        group = meta["group"]
        fpath = DATA_ROOT / group / f"{subj}_preproc_raw.fif"
        raw = mne.io.read_raw_fif(fpath, preload=True, verbose="ERROR")

        # Restrict to common channels and re-order so every subject's array
        # has channels in the SAME order. Critical for stacking.
        raw.pick(common_channels)
        raw.reorder_channels(common_channels)

        n_fft = int(raw.info["sfreq"] * N_FFT_SECONDS)
        psd = raw.compute_psd(
            method="welch",
            fmin=PSD_FMIN,
            fmax=PSD_FMAX,
            n_fft=n_fft,
            n_overlap=n_fft // 2,
            verbose="ERROR",
        )
        data = psd.get_data()  # shape (n_channels, n_freqs), units V^2/Hz
        if freqs_ref is None:
            freqs_ref = psd.freqs
        else:
            assert np.allclose(psd.freqs, freqs_ref), f"freq grid mismatch for {subj}"

        psd_list.append(data)
        subject_ids.append(subj)
        groups.append(group)

        if i % 25 == 0 or i == len(per_subject_meta):
            elapsed = time.time() - t0
            print(f"  [{i}/{len(per_subject_meta)}] {subj} ({group})  elapsed={elapsed:.0f}s")

    psd_arr = np.stack(psd_list, axis=0)  # (n_subjects, n_channels, n_freqs)
    print(f"\nFinal PSD array shape: {psd_arr.shape}")
    print(f"Frequency range: {freqs_ref[0]:.2f} - {freqs_ref[-1]:.2f} Hz, n_freqs={len(freqs_ref)}")

    out = CACHE_DIR / "group_psd.npz"
    np.savez_compressed(
        out,
        psd=psd_arr,
        freqs=freqs_ref,
        channels=np.array(common_channels),
        subject_ids=np.array(subject_ids),
        groups=np.array(groups),
    )
    print(f"Saved: {out}  ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
