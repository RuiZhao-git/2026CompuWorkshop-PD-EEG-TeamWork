"""EEG feature extraction.

Functions for computing PSD, alpha peak frequency, and band power
from resting-state EEG data.
"""

from pathlib import Path

import mne
import numpy as np
from scipy.signal import welch

# Posterior channel set used for alpha-band features.
# Alpha is strongest over occipital and parietal cortex at rest.
POSTERIOR_CHANNELS = [
    "O1", "Oz", "O2",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
]

# Canonical frequency bands (Hz).
BANDS = {
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
}

# Search window for the alpha peak. Slightly wider than the canonical
# alpha band so that a slowed alpha rhythm (e.g. 7.5 Hz) is still found.
ALPHA_PEAK_SEARCH = (7.0, 13.0)


def load_raw(fif_path):
    """Load a preprocessed MNE Raw file. Returns the Raw object."""
    return mne.io.read_raw_fif(fif_path, preload=True, verbose="ERROR")


def compute_average_psd(raw, channels=None, nperseg=None):
    """Compute Welch PSD averaged across the selected channels.

    Parameters
    ----------
    raw : mne.io.Raw
    channels : list of str, optional
        Channel names to include. If None, uses POSTERIOR_CHANNELS
        intersected with the channels actually present in `raw`.
    nperseg : int, optional
        Welch segment length. Defaults to 4 seconds of samples.

    Returns
    -------
    freqs : ndarray of shape (n_freqs,)
    psd : ndarray of shape (n_freqs,)  averaged PSD across channels
    used_channels : list of str  channels actually used
    """
    if channels is None:
        channels = POSTERIOR_CHANNELS
    used = [ch for ch in channels if ch in raw.ch_names]
    if not used:
        raise ValueError(f"None of {channels} found in raw.ch_names")

    data = raw.get_data(picks=used)        # (n_ch, n_samples)
    fs = raw.info["sfreq"]
    if nperseg is None:
        nperseg = int(4 * fs)              # 4 s segments -> 0.25 Hz resolution

    freqs, psd_per_ch = welch(data, fs=fs, nperseg=nperseg, axis=-1)
    psd = psd_per_ch.mean(axis=0)
    return freqs, psd, used


def alpha_peak_hz(freqs, psd, search_band=ALPHA_PEAK_SEARCH):
    """Find the frequency of maximum PSD inside `search_band`."""
    mask = (freqs >= search_band[0]) & (freqs <= search_band[1])
    return float(freqs[mask][np.argmax(psd[mask])])


_trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz


def band_power(freqs, psd, fmin, fmax):
    """Integrate the PSD over [fmin, fmax] using the trapezoidal rule."""
    mask = (freqs >= fmin) & (freqs <= fmax)
    return float(_trapz(psd[mask], freqs[mask]))


def relative_band_powers(freqs, psd, bands=BANDS, total_band=(1.0, 45.0)):
    """Return a dict of band: relative_power.

    Relative power = band_power / total_power_in(total_band).
    Using relative power makes values comparable across subjects (it
    cancels out overall amplitude differences from cap impedance, etc.).
    """
    total = band_power(freqs, psd, *total_band)
    return {name: band_power(freqs, psd, fmin, fmax) / total
            for name, (fmin, fmax) in bands.items()}


def extract_subject_features(fif_path):
    """Run the full feature extraction on one .fif file.

    Returns a dict with subject_id, group, alpha_peak_hz, and relative
    band powers for theta / alpha / beta.
    """
    fif_path = Path(fif_path)
    raw = load_raw(fif_path)
    freqs, psd, _ = compute_average_psd(raw)

    rel = relative_band_powers(freqs, psd)
    return {
        "subject_id": fif_path.stem.replace("_preproc_raw", ""),
        "group": "PD" if fif_path.stem.startswith("PD") else "Control",
        "alpha_peak_hz": alpha_peak_hz(freqs, psd),
        "alpha_power": rel["alpha"],
        "theta_power": rel["theta"],
        "beta_power": rel["beta"],
    }
