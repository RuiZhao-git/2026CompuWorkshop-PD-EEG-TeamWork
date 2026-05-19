"""
Wilson-Cowan oscillator — minimal alpha-rhythm demo.

Goal: show that one Wilson-Cowan node, with biologically-reasonable
parameters, produces a ~10 Hz oscillation; and that slowing the inhibitory
time constant tau_I shifts the peak frequency down — exactly the
"healthy -> PD" transformation we hypothesise.

Outputs (figures/04_model/):
  wc_healthy_timeseries.png   — model output E(t), 1 second
  wc_healthy_psd.png          — power spectrum, peak should be ~ alpha
  wc_tau_sweep.png            — peak freq vs tau_I (the "knob")
  wc_fit_demo.png             — given a target peak freq, find the tau_I
                                that produces it (illustrates per-subject fit)
"""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import welch

FIG_DIR = Path(__file__).resolve().parent.parent / "figures" / "04_model"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Wilson-Cowan equations
# ---------------------------------------------------------------------------

def sigmoid(x, a, theta):
    """S-shaped activation. Wilson 1999 convention: S(0) = 0."""
    return 1.0 / (1.0 + np.exp(-a * (x - theta))) - 1.0 / (1.0 + np.exp(a * theta))


def wilson_cowan_rhs(t, y, p):
    """The two ODEs."""
    E, I = y
    in_E = p["w_EE"] * E - p["w_EI"] * I + p["P"]
    in_I = p["w_IE"] * E - p["w_II"] * I + p["Q"]
    dE = (-E + sigmoid(in_E, p["a_E"], p["theta_E"])) / p["tau_E"]
    dI = (-I + sigmoid(in_I, p["a_I"], p["theta_I"])) / p["tau_I"]
    return [dE, dI]


# Wilson 1999 textbook parameters (oscillatory regime).
# Time constants in SECONDS; weights are dimensionless.
HEALTHY = dict(
    a_E=1.3, theta_E=4.0,
    a_I=2.0, theta_I=3.7,
    w_EE=16.0, w_EI=12.0, w_IE=15.0, w_II=3.0,
    P=1.25, Q=0.0,
    tau_E=0.010,   # 10 ms — fast excitatory response
    tau_I=0.012,   # 12 ms — chosen so default output ≈ 9.5 Hz (alpha)
)


def simulate(p, T=5.0, fs=2000):
    """Integrate the model for T seconds. Returns (t, E, I)."""
    t_eval = np.arange(0, T, 1.0 / fs)
    sol = solve_ivp(
        wilson_cowan_rhs, (0, T), [0.1, 0.05],
        args=(p,), t_eval=t_eval, rtol=1e-7, atol=1e-9, method="RK45",
    )
    return sol.t, sol.y[0], sol.y[1]


def peak_frequency(E, fs=2000, transient=1.0, fband=(5, 25)):
    """PSD via Welch on E(t), return frequency of the peak in fband."""
    n_skip = int(transient * fs)
    sig = E[n_skip:] - E[n_skip:].mean()
    freqs, psd = welch(sig, fs=fs, nperseg=int(2 * fs))
    band = (freqs >= fband[0]) & (freqs <= fband[1])
    return freqs[band][np.argmax(psd[band])], freqs, psd


# ---------------------------------------------------------------------------
# 1) One run with healthy parameters
# ---------------------------------------------------------------------------

t, E, I = simulate(HEALTHY)
peak_h, freqs_h, psd_h = peak_frequency(E)
print(f"Healthy params → peak frequency ≈ {peak_h:.2f} Hz")

fig, ax = plt.subplots(figsize=(8, 3.5))
mask = (t >= 1.0) & (t < 2.0)
ax.plot(t[mask], E[mask], color="C0", label="E (excitatory)")
ax.plot(t[mask], I[mask], color="C3", alpha=0.7, label="I (inhibitory)")
ax.set_xlabel("time (s)")
ax.set_ylabel("activity")
ax.set_title(f"Wilson-Cowan output, healthy parameters  (peak ≈ {peak_h:.1f} Hz)")
ax.legend()
fig.tight_layout()
fig.savefig(FIG_DIR / "wc_healthy_timeseries.png", dpi=130)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
ax.semilogy(freqs_h, psd_h, color="C0")
ax.axvspan(8, 13, color="grey", alpha=0.15, label="alpha (8-13 Hz)")
ax.axvline(peak_h, color="C3", ls="--", label=f"peak = {peak_h:.2f} Hz")
ax.set_xlim(0, 30)
ax.set_xlabel("frequency (Hz)")
ax.set_ylabel("power (a.u.)")
ax.set_title("Wilson-Cowan PSD, healthy parameters")
ax.legend()
fig.tight_layout()
fig.savefig(FIG_DIR / "wc_healthy_psd.png", dpi=130)
plt.close(fig)


# ---------------------------------------------------------------------------
# 2) Sweep tau_I (the "knob") and record peak frequency
# ---------------------------------------------------------------------------

# Restrict to the monotonic regime (the model has a bifurcation around tau_I ≈ 23 ms
# where it jumps to a different oscillatory mode; the alpha-band region we care
# about lives entirely below that, in 10-18 ms).
tau_I_values = np.linspace(0.010, 0.018, 25)  # 10 ms to 18 ms
peaks = []
for tau_I in tau_I_values:
    p = {**HEALTHY, "tau_I": tau_I}
    _, E_sweep, _ = simulate(p, T=4.0)
    pk, _, _ = peak_frequency(E_sweep)
    peaks.append(pk)
peaks = np.array(peaks)

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(tau_I_values * 1000, peaks, "o-", color="C0")
ax.axhspan(9, 11, color="C0", alpha=0.10, label="healthy alpha (9-11 Hz)")
ax.axhspan(7, 9, color="C3", alpha=0.10, label="PD-typical alpha (7-9 Hz)")
ax.set_xlabel(r"inhibitory time constant $\tau_I$ (ms)  ← the model 'knob'")
ax.set_ylabel("simulated peak frequency (Hz)")
ax.set_title(r"Peak frequency vs $\tau_I$  —  longer inhibition → slower oscillation")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / "wc_tau_sweep.png", dpi=130)
plt.close(fig)
print(f"tau_I sweep: {tau_I_values[0]*1000:.0f}-{tau_I_values[-1]*1000:.0f} ms "
      f"→ peak {peaks[0]:.1f}-{peaks[-1]:.1f} Hz")


# ---------------------------------------------------------------------------
# 3) Per-subject fit illustration: given a target peak freq, find tau_I
# ---------------------------------------------------------------------------

def fit_tau_I(target_peak_hz, tau_I_grid, peak_grid):
    """Linear interpolation: find tau_I that makes simulated peak = target."""
    # Ensure peak_grid is monotonic-ish; sort to be safe
    order = np.argsort(peak_grid)[::-1]
    return float(np.interp(target_peak_hz, peak_grid[order][::-1], tau_I_grid[order][::-1]))


target_ctrl = 9.5  # Control group median we'd see in real data
target_pd = 8.5    # PD group median

tau_I_ctrl = fit_tau_I(target_ctrl, tau_I_values, peaks)
tau_I_pd = fit_tau_I(target_pd, tau_I_values, peaks)
print(f"\nTo match Control median (≈{target_ctrl} Hz)  →  tau_I = {tau_I_ctrl*1000:.1f} ms")
print(f"To match PD median      (≈{target_pd} Hz)  →  tau_I = {tau_I_pd*1000:.1f} ms")
print(f"Δtau_I (the '+x' in the brief's diagram) ≈ {(tau_I_pd - tau_I_ctrl)*1000:.1f} ms")

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(tau_I_values * 1000, peaks, "o-", color="grey", alpha=0.7,
        label="model: peak vs τ_I")
ax.axhline(target_ctrl, color="C0", ls=":", alpha=0.7)
ax.axhline(target_pd, color="C3", ls=":", alpha=0.7)
ax.axvline(tau_I_ctrl * 1000, color="C0", ls=":", alpha=0.7)
ax.axvline(tau_I_pd * 1000, color="C3", ls=":", alpha=0.7)
ax.plot([tau_I_ctrl * 1000], [target_ctrl], "o", color="C0", markersize=12,
        label=f"Control fit: τ_I = {tau_I_ctrl*1000:.1f} ms (peak {target_ctrl} Hz)")
ax.plot([tau_I_pd * 1000], [target_pd], "o", color="C3", markersize=12,
        label=f"PD fit: τ_I = {tau_I_pd*1000:.1f} ms (peak {target_pd} Hz)")
ax.annotate("", xy=(tau_I_pd * 1000, target_pd), xytext=(tau_I_ctrl * 1000, target_ctrl),
            arrowprops=dict(arrowstyle="->", color="black", lw=1.5))
ax.text((tau_I_ctrl + tau_I_pd) * 500, (target_ctrl + target_pd) / 2,
        f"  +Δτ_I ≈ {(tau_I_pd - tau_I_ctrl)*1000:.1f} ms",
        fontsize=11, va="center")
ax.set_xlabel(r"$\tau_I$ (ms)")
ax.set_ylabel("peak frequency (Hz)")
ax.set_title(r"Per-subject fit: invert the curve to get $\tau_I$ from measured alpha peak")
ax.legend(loc="upper right", fontsize=9)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / "wc_fit_demo.png", dpi=130)
plt.close(fig)

print(f"\nFigures saved to: {FIG_DIR}")
