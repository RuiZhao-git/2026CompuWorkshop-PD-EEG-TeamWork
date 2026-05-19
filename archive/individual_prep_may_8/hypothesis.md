# Candidate hypotheses — PD vs Control resting-state EEG

Course: Computational Neurology, SoSe 2026 — Team Task 2 (EEG/PD group)
Dataset: 49 Control + 100 PD, 63-channel resting EEG @ 125 Hz, ~4–5 min/subject
(Anjum et al. 2024, *npj Parkinson's Disease*).

All findings below come from our own analysis: Welch PSD per subject, relative
band power per channel, Mann–Whitney U test per channel × band with
Benjamini–Hochberg FDR within each band, plus posterior individual alpha peak
frequency (find_peaks with prominence ≥ 0.5 dB, averaged over O1/Oz/O2/PO7/PO8/POz/P3/Pz/P4).

## Empirical findings driving the hypotheses

| Feature | PD vs Control | Effect size / location | Notes |
|---|---|---|---|
| **Theta (4–8 Hz) relative power** | **PD > Control** | All 60/60 channels FDR-sig, max central/parietal | Strongest, most diffuse finding |
| **Posterior alpha peak frequency** | **PD slower** | Ctrl 9.50 Hz vs PD 8.50 Hz, p = 0.002 | Detected in 49/49 Ctrl, 98/100 PD |
| **Beta (13–30 Hz) relative power** | PD < Control | 43/60 channels FDR-sig, central/parietal max | Significant but smaller effect |
| **Gamma (30–45 Hz) relative power** | PD < Control | 30/60 channels FDR-sig, frontal max | Effect weaker, near notch limit |
| Alpha (8–13 Hz) total relative power | NS | Topo redistribution: frontal ↑, posterior ↓ | Power conserved, just moves |
| Delta (1–4 Hz) | NS | — | Likely limited by 0.5 Hz highpass |

The unifying observation is **EEG slowing**: in PD, the resting-state spectrum
is shifted toward lower frequencies — more low-frequency power, less
high-frequency power, and the alpha oscillator itself runs ~1 Hz slower.
This matches the classic PD literature (e.g., Bosboom et al. 2006; Soikkeli
et al. 1991) and aligns with the cognitive-impairment story in the bundled
Anjum et al. paper (which uses MoCA, not the PD/Ctrl contrast directly, but
the same slowing logic applies).

---

## Candidate hypothesis 1 — **Posterior alpha peak slowing**

**H1.** *In Parkinson's disease, the posterior individual alpha peak frequency
(IAF) is reduced compared to age-matched healthy controls.*

**Justification.** The IAF over occipito-parietal channels is robustly ~1 Hz
slower in PD in our data (Ctrl 9.50 Hz, PD 8.50 Hz, U = 1658, p = 0.002,
n = 49 + 98 with detected peaks). Slowing of the posterior dominant rhythm is
one of the oldest and most reproducible findings in PD EEG. It is also the
finding that maps most cleanly to a single model parameter: in cortical
neural-mass models (e.g., Wilson–Cowan, Jansen–Rit) the alpha-band peak is set
by the recurrent inhibitory time constant, so "healthy → PD" can be
implemented as a +Δτ shift on one variable.

## Candidate hypothesis 2 — **Diffuse theta excess**

**H2.** *Resting-state EEG in PD shows globally elevated relative theta
(4–8 Hz) power across the cortex compared to controls.*

**Justification.** Every one of the 60 common electrodes shows higher relative
theta power in PD after FDR correction; the channel-averaged effect is
p ≈ 3×10⁻⁶. The topographic map is essentially uniform, with the strongest
effect over central-parietal cortex. This is the single largest effect in
our data. It is partly mechanistically related to H1 (when individual alpha
slows below 8 Hz, its power is counted as theta), but the effect is broader
than alpha alone — it appears in subjects whose alpha peak is still ≥ 8 Hz
too. This is consistent with the EEG-slowing pattern described for cognitive
decline in PD by Anjum et al.

## Candidate hypothesis 3 — **Beta deficit over sensorimotor cortex**

**H3.** *Resting-state cortical beta (13–30 Hz) power is reduced in PD
relative to controls, most prominently over central–parietal sensorimotor
electrodes.*

**Justification.** 43/60 channels show reduced relative beta in PD after FDR;
the topomap difference is sharply blue over central–parietal sites (CP/P/C
rows). Beta is the canonical "Parkinsonian" frequency (excessive subthalamic
beta is the classic LFP/DBS finding). Cortically, however, the *relative*
direction is reduced rather than increased — likely because cortical beta
expresses dopaminergic modulation differently from subcortical beta, and
because relative-power normalization shifts mass toward the elevated theta
band.

---

## Recommendation: pursue **H1 (alpha peak slowing)** as the primary hypothesis

**Reasoning (in order of importance for this assignment):**

1. **Cleanest mapping to the model-fitting framework the brief asks for.** The
   assignment's diagram is *Healthy model → +Δparameter → PD model*, with
   parameter inference per subject. A single neural-mass cortical oscillator
   (Wilson–Cowan, Jansen–Rit, or even a coupled-oscillator surrogate) has one
   tunable parameter — the inhibitory/excitatory time constant — that directly
   sets the alpha peak frequency. This gives the team a 1-parameter,
   per-subject model fit that is genuinely tractable for a workshop.

2. **Robust and easy to summarise.** A single number per subject (peak Hz),
   detected in essentially everyone, with an obvious 1 Hz group difference.

3. **Resting-state, cortical-only — fits the data we were given.** The brief
   warns that we have only resting cortical data; the alpha rhythm is a
   resting cortical phenomenon par excellence.

4. **Hypothesis 2 (theta excess) is the strongest effect in the data**, but it
   is partly an artefact of H1 (slowed alpha leaking across the 8 Hz band
   boundary) and harder to fit to a single model parameter without invoking
   additional sources. If asked, frame H2 as a *predicted consequence* of H1
   rather than a competing hypothesis.

5. **Hypothesis 3 (beta deficit)** is real in our data but harder to model in
   a purely cortical, resting framework — most theoretical work on PD beta
   centres on cortico-basal ganglia loops, which the brief explicitly rules
   out (no deep structures, no connectivity).

---

## Proposed model-fitting plan (sketch, for slide 2)

**Model.** A single cortical neural-mass oscillator (Jansen–Rit or
Wilson–Cowan) producing an alpha-band rhythm. One free parameter:
the inhibitory time constant τ_i (higher τ_i ⇒ slower peak frequency).

**Healthy model.** Set τ_i so that the simulated PSD's alpha peak matches the
Control group median (≈ 9.5 Hz).

**PD model.** Healthy model + Δτ_i, with Δτ_i fit so the simulated peak
matches PD group median (≈ 8.5 Hz).

**Parameter inference.** For each subject, find τ_i that minimises the
distance between the simulated alpha-band PSD and the subject's measured
posterior PSD (e.g., least-squares over 6–14 Hz). The distribution of fitted
τ_i should separate PD from controls.

**Sanity checks.** (i) Re-test τ_i distributions by group with Mann–Whitney.
(ii) Confirm that the model's predicted theta/alpha *power ratio* (which
follows mechanically from a slower alpha peak crossing the 8 Hz boundary)
matches what we observe empirically in H2.
