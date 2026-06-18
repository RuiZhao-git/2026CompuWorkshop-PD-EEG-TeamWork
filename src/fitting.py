"""Per-subject parameter inference for the Wilson-Cowan model.

Invert the simulated peak-frequency-vs-`tau_inh` curve produced by script 02 to
assign each subject the inhibitory time constant `tau_inh` that would make the
model oscillate at that subject's measured alpha peak frequency.

Inversion convention
--------------------
The forward curve (`tau_inh` -> simulated alpha peak) is monotonic but COARSE:
the simulated peak is resolved in 0.5 Hz steps, so several `tau_inh` values map
to the same peak (the curve has flat steps / plateaus). The inverse is therefore
not unique: one measured peak corresponds to a small RANGE of `tau_inh`.

We resolve this with a single, fixed convention -- linear interpolation over the
curve sorted by peak (`numpy.interp`) -- so the result is deterministic and
reproducible across runs and machines. Group comparisons (script 05) are
unaffected by the choice of convention, because the mapping is monotonic and so
preserves the ordering of subjects, and the rank-based test depends only on that
ordering.
"""

import numpy as np


def invert_peak_curve(measured_peak_hz, curve_tau_ms, curve_peak_hz):
    """Map measured alpha peak frequencies to fitted `tau_inh` by curve inversion.

    Parameters
    ----------
    measured_peak_hz : float or array-like of float
        One subject's alpha peak frequency (Hz), or an array of them.
    curve_tau_ms : array-like of float
        The `tau_inh` grid from script 02 (the lookup curve's tau column).
    curve_peak_hz : array-like of float
        The simulated alpha peak each `tau_inh` produced, aligned element by
        element with `curve_tau_ms`.

    Returns
    -------
    float or numpy.ndarray
        Fitted `tau_inh` (ms) for each input peak.

    Notes
    -----
    `numpy.interp` requires its sample x-coordinates to be increasing, so we sort
    the curve by peak ascending before interpolating peak -> tau. Peaks outside
    the curve range are clamped to the nearest endpoint (`numpy.interp` does not
    extrapolate); the calling script reports whether any subject was clamped.
    """
    curve_tau_ms = np.asarray(curve_tau_ms, dtype=float)
    curve_peak_hz = np.asarray(curve_peak_hz, dtype=float)

    order = np.argsort(curve_peak_hz)
    peak_sorted = curve_peak_hz[order]
    tau_sorted = curve_tau_ms[order]

    return np.interp(measured_peak_hz, peak_sorted, tau_sorted)
