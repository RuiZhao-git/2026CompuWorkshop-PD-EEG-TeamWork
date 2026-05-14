"""Wilson-Cowan network model.

Wrapper around neurolib's `WCModel` configured for our cortical-slowing
project. We use a network of N Wilson-Cowan units coupled all-to-all
with a single global coupling strength. Each unit is a pair (E, I) of
excitatory and inhibitory populations described by neurolib's standard
Wilson-Cowan equations.

The free parameter of the project is the inhibitory time constant
`tau_inh` (ms): larger `tau_inh` means inhibition responds more slowly,
which slows the network oscillation. Our hypothesis maps "PD vs
Control" to "larger vs smaller tau_inh".

Why these defaults
------------------
Empirically (we tested a parameter sweep on a single node), the
following choices give a clean, deterministic limit cycle whose peak
frequency varies smoothly and monotonically with `tau_inh` in the
alpha range:

    exc_ext   = 0.65   external drive to the excitatory population
    sigma_ou  = 0      no Ornstein-Uhlenbeck noise (deterministic)
    K_gl      = 0.6    neurolib default global coupling
    duration  = 8000   ms; long enough for transient to die and PSD
                       to converge

With these, `tau_inh ~ 19 ms` reproduces the Control alpha peak (~9 Hz)
and `tau_inh ~ 22 ms` reproduces the PD alpha peak (~8 Hz). The exact
mapping depends weakly on N (number of nodes) and is what
`scripts/02_simulate_network.py` measures.

Other model parameters (sigmoid slope, weights, excitatory time
constant `tau_exc`) are left at neurolib defaults. Changing them
moves the Hopf bifurcation and the alpha-range window, so we keep
them fixed.
"""

import numpy as np
from scipy.signal import welch


# ---------------------------------------------------------------------------
# Default parameters (used unless the caller overrides them)
# ---------------------------------------------------------------------------

# External drive to the excitatory population.
# Below ~0.5 the system has a stable fixed point and does not oscillate;
# 0.65 sits comfortably inside the oscillatory regime.
DEFAULT_EXC_EXT = 0.65

# Ornstein-Uhlenbeck noise amplitude (0 = deterministic limit cycle).
# Set to 0 so the peak frequency depends only on parameters, not on a
# noise realization. For exploratory work you can pass a small value
# (e.g. 0.05) to get noise-shaped output similar to real EEG.
DEFAULT_SIGMA_OU = 0.0

# Global coupling strength: scales the connectivity matrix.
DEFAULT_K_GL = 0.6

# Simulation duration in ms.
DEFAULT_DURATION_MS = 8000

# Transient discarded when computing the PSD.
DEFAULT_TRANSIENT_MS = 2000


# ---------------------------------------------------------------------------
# Network topology
# ---------------------------------------------------------------------------

def all_to_all_coupling(n_nodes):
    """Construct an N x N all-to-all coupling matrix (no self-loops).

    Parameters
    ----------
    n_nodes : int
        Number of nodes in the network.

    Returns
    -------
    Cmat : (n_nodes, n_nodes) ndarray of float
        Connectivity matrix. Cmat[i, j] = 1 if i != j, else 0.
        Inside neurolib this matrix is scaled by `K_gl`.
    Dmat : (n_nodes, n_nodes) ndarray of float
        Distance / delay matrix. All zeros = instantaneous coupling
        (no conduction delays). Reasonable for a phenomenological
        cortical model at this scale.
    """
    Cmat = np.ones((n_nodes, n_nodes), dtype=float) - np.eye(n_nodes)
    Dmat = np.zeros((n_nodes, n_nodes), dtype=float)
    return Cmat, Dmat


# ---------------------------------------------------------------------------
# Build and run a Wilson-Cowan network
# ---------------------------------------------------------------------------

def build_network(n_nodes, tau_inh, *,
                  exc_ext=DEFAULT_EXC_EXT,
                  sigma_ou=DEFAULT_SIGMA_OU,
                  K_gl=DEFAULT_K_GL,
                  duration_ms=DEFAULT_DURATION_MS):
    """Construct and configure a Wilson-Cowan network.

    Parameters
    ----------
    n_nodes : int
        Number of Wilson-Cowan units.
    tau_inh : float
        Inhibitory time constant in ms. The free parameter that
        controls oscillation speed.
    exc_ext, sigma_ou, K_gl, duration_ms : floats
        See the module docstring for what these mean and why the
        defaults are what they are. Pass overrides only when you have
        a specific reason.

    Returns
    -------
    model : neurolib.models.wc.WCModel
        Configured but not yet run. Call `model.run()`, then read
        `model.exc` (shape (n_nodes, n_samples)) and `model.t`.
    """
    # Imported lazily so this file can be read or partially imported
    # even on a machine without neurolib installed.
    from neurolib.models.wc import WCModel

    Cmat, Dmat = all_to_all_coupling(n_nodes)
    model = WCModel(Cmat=Cmat, Dmat=Dmat)
    model.params["tau_inh"] = tau_inh
    model.params["exc_ext"] = exc_ext
    model.params["sigma_ou"] = sigma_ou
    model.params["K_gl"] = K_gl
    model.params["duration"] = duration_ms
    return model


def run_and_get_excitatory(model):
    """Run the model and return its excitatory output.

    Returns
    -------
    t : (n_samples,) ndarray of float
        Time array in ms.
    exc : (n_nodes, n_samples) ndarray of float
        Excitatory-population activity per node per timepoint.
    """
    model.run()
    return np.asarray(model.t), np.asarray(model.exc)


# ---------------------------------------------------------------------------
# Spectral analysis of model output
# ---------------------------------------------------------------------------

def peak_frequency(signal, dt_ms,
                   transient_ms=DEFAULT_TRANSIENT_MS,
                   band=(3.0, 25.0)):
    """Frequency of maximum PSD inside `band`, after removing transient.

    Uses Welch's method with 2-second segments (matching what
    `src/features.py` does on the empirical EEG).

    Parameters
    ----------
    signal : 1-D ndarray
        Time series from one node (or averaged across nodes).
    dt_ms : float
        Simulation time step in ms (i.e. 1000/fs).
    transient_ms : float
        Initial portion to discard before computing the PSD.
    band : (float, float)
        Frequency window in which to look for the peak (Hz).

    Returns
    -------
    f_peak : float
        Frequency in Hz with the largest PSD value inside `band`.
        Returns NaN if `band` is empty after PSD computation.
    """
    fs_hz = 1000.0 / dt_ms
    n_skip = int(transient_ms / dt_ms)
    sig = signal[n_skip:] - signal[n_skip:].mean()

    nperseg = min(len(sig), int(2 * fs_hz))
    freqs, psd = welch(sig, fs=fs_hz, nperseg=nperseg)

    mask = (freqs >= band[0]) & (freqs <= band[1])
    if not mask.any():
        return float("nan")
    return float(freqs[mask][np.argmax(psd[mask])])


def network_peak_frequency(model, **kwargs):
    """Convenience: run `model`, average exc across nodes, return peak Hz.

    Because we use an all-to-all symmetric coupling, all nodes
    synchronize to the same oscillation, so the average is a sensible
    single summary of the network's rhythm.
    """
    _, exc = run_and_get_excitatory(model)
    avg_signal = exc.mean(axis=0)
    return peak_frequency(avg_signal, dt_ms=model.params["dt"], **kwargs)


def simulate_peak_frequency(n_nodes, tau_inh, **kwargs):
    """One-call helper: build a network, run it, return its peak Hz.

    Useful for parameter sweeps where you don't need direct access to
    the time series. Equivalent to
        model = build_network(n_nodes, tau_inh, **kwargs)
        f = network_peak_frequency(model)
    """
    build_kwargs = {k: kwargs.pop(k) for k in
                    ["exc_ext", "sigma_ou", "K_gl", "duration_ms"]
                    if k in kwargs}
    model = build_network(n_nodes, tau_inh, **build_kwargs)
    return network_peak_frequency(model, **kwargs)
