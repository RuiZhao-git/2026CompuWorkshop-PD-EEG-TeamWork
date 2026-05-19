My hypothesis

> **In Parkinson's disease, the dominant posterior theta–alpha (7–13 Hz)
> oscillation has a lower peak frequency at rest than in age-matched healthy
> controls — i.e., the resting alpha rhythm is slowed.**


## Important caveat

The Anjum paper's primary outcome is **MoCA score**, not PD vs Ctrl directly.
So my hypothesis is a *transitive* prediction: paper says higher MoCA →
faster oscillation; PD subjects have lower MoCA than controls; therefore PD
should show a slower oscillation. This is a reasonable inference but not a
direct replication target — the team should be aware that the paper does not
formally test the PD-vs-Ctrl frequency contrast.

## Why this hypothesis fits the data we were given

- It's about a **resting-state cortical oscillation** — exactly what the
  brief allows ("only resting state, only cortical").
- It needs only the standard 10-20 EEG montage (which we have).
- It boils down to one number per subject (the peak frequency in 7–13 Hz),
  which the team can extract from the data straightforwardly.
- The 125 Hz sampling rate and ~5-minute recordings are easily sufficient
  for this frequency range.

## How the model fitting could look

A single-parameter cortical neural-mass oscillator (e.g., Wilson–Cowan or
Jansen–Rit) generates an alpha-band rhythm whose peak frequency is set by
the inhibitory time constant τᵢ.

- *Healthy model:* tune τᵢ so simulated peak ≈ Control group median.
- *PD model:* same model + Δτᵢ so simulated peak ≈ PD group median.
- *Per-subject parameter inference:* find τᵢ that minimises the distance
  between the simulated and measured posterior PSD around 7–13 Hz.

This realises the brief's "Healthy model + Δparameter → PD model" diagram
with one biophysically interpretable parameter.

