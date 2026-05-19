# Slide content — EEG/PD group, Team Task 2 (08.05)

Two slides. Bullet content only — someone else will assemble the deck.
Suggested figures (already in `figures/03_compare/`) noted in *italics* under
each slide.

---

## Slide 1 — Hypothesis: PD shows a slowed cortical alpha rhythm

**Title.** PD vs healthy controls in resting EEG: cortical oscillations slow down

**What we did to narrow the hypothesis space**
- Computed Welch PSD on 149 subjects (49 Ctrl, 100 PD), 60 common electrodes
- Compared 5 canonical bands (δ, θ, α, β, γ) and individual alpha peak
  frequency, PD vs Ctrl, Mann–Whitney U with FDR correction per band

**What we found (3 candidate effects)**
- **Theta (4–8 Hz) ↑ in PD**, all 60/60 electrodes FDR-significant — strongest
  but partly explained by alpha slowing
- **Posterior alpha peak frequency ↓ in PD**: 9.5 → 8.5 Hz, p = 0.002
- **Beta (13–30 Hz) ↓ in PD**, 43/60 electrodes, central–parietal max — real,
  but harder to model with cortex-only data

**Hypothesis we propose to pursue (H1)**
- *In Parkinson's disease, the posterior individual alpha peak frequency is
  reduced compared to age-matched healthy controls (≈ 1 Hz slowing).*

**Why this one**
- Cleanest mapping to the assignment's "healthy model + Δparameter → PD model"
  framework — single parameter (oscillator time constant) sets alpha peak
- One robust number per subject, detected in 49/49 Ctrl and 98/100 PD
- Fits the constraints: resting-state, cortical-only data
- The diffuse theta excess (H2) and reduced beta/gamma fall out as
  *predicted consequences* of slowing, not as separate hypotheses

*Suggested figure: `group_mean_psd_posterior.png` (PD vs Ctrl posterior PSD,
shows the alpha peak shifted left) + `alpha_peak_robust.png` (left panel: PD
distribution shifted ~1 Hz lower).*

---

## Slide 2 — How we'd fit the model

**Model.** Single cortical neural-mass oscillator producing an alpha rhythm
(e.g., Jansen–Rit or Wilson–Cowan). One free parameter: inhibitory time
constant τ_i (larger τ_i → slower peak).

**Healthy → PD via one parameter**
- *Healthy model:* fit τ_i so simulated PSD peak = Ctrl group median ≈ 9.5 Hz
- *PD model:* same model + Δτ_i so simulated peak = PD group median ≈ 8.5 Hz
- Δτ_i is the "+x" in the assignment's diagram

**Per-subject parameter inference**
- For each subject, find τ_i that minimises distance between simulated and
  measured posterior PSD over 6–14 Hz (least-squares is enough)
- Compare τ_i distributions: Ctrl vs PD with Mann–Whitney U

**Validation / sanity checks**
- Slower alpha (lower peak Hz) should mechanically push spectral mass below
  8 Hz → predicts the diffuse theta excess we observed (H2)
- Check that fitted τ_i separates PD from Ctrl as well as the raw peak
  frequency does

**Scope and caveats — the things we are NOT doing**
- No source localisation (head-surface only)
- No connectivity / network analysis (single-channel-region oscillator)
- No ML / classifier (LEAPD-style); this is a generative model fit
- 6 of 63 electrodes (FT9, PO3, PO4, Iz, I1, I2) excluded so all 149 subjects
  share the same 60-channel layout
- Group sizes asymmetric (49 Ctrl vs 100 PD); no demographic matching
  attempted at this stage

*Suggested figure: small schematic of the parameter-shift idea
(healthy oscillator → +Δτ_i → PD oscillator), plus `topomap_theta.png` as
evidence that the predicted consequence (theta excess) is in fact present.*
