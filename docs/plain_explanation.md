# Plain explanation

If you just joined or you got lost in the technical details, start here. A from-scratch walkthrough of the whole project with as little jargon as possible.

## What we are doing

We have 149 people's resting-state EEG (49 healthy + 100 PD). We want to test one hypothesis:

> **PD patients' brain rhythms are slower than healthy people's.**

We test this **twice**:

| | What it does | Conclusion looks like |
|---|---|---|
| **First pass: look at the data directly** | Measure rhythm speed from each subject's EEG, compare PD vs Control | "PD is 1 Hz slower than Control" |
| **Second pass: through a model** | Build a small math model of a brain region, find the parameter value that matches each subject, then compare | "PD's inhibitory response is 3 ms slower than Control's" |

The first pass answers "what does the data say". The second pass translates that into "how much one model parameter differs", which is closer to a biological mechanism. The assignment asks for both.

## First pass: look at the data directly

**Step 1.** `scripts/01_extract_features.py` *(done)*

Open each subject's `.fif` file and compute 4 numbers per subject:

- alpha peak frequency (how fast the brain rhythm runs)
- alpha, theta, beta relative band powers (how much energy sits in each frequency band)

149 subjects collapse into one small table, `results/features.csv`.

**Step 2.** `scripts/04_compare_features.py` *(done)*

Statistically compare PD vs Control on each of those numbers. We already see:

- alpha rhythm is slower in PD (significant)
- theta power is higher in PD (significant)
- beta power is lower in PD (significant)
- alpha relative power is unchanged (we use this to justify rewording our hypothesis to "alpha peak slowing" rather than "alpha decrease")

That finishes the first pass. The data supports our hypothesis direction.

## Second pass: through a model

**Step 3.** `src/model.py` *(done)*

A small mathematical model of cortex called Wilson-Cowan. Think of it as **a box with a knob**:

- The knob is called `tau_inh` (inhibitory time constant)
- Turn the knob up → the rhythm produced by the box becomes slower
- Turn the knob down → the rhythm becomes faster

Biologically, `tau_inh` corresponds to how long inhibitory neurons take to respond. A larger value means slower inhibition, which slows the whole oscillating circuit.

**Step 4.** `scripts/02_simulate_network.py` *(done)*

We don't have a formula that tells us what frequency the box produces at a given knob position. The model is nonlinear and has no analytic solution. So we **make a translation table**:

- Knob at 11 ms → run model → measure 13.5 Hz
- Knob at 14 ms → measure 11.5 Hz
- Knob at 19 ms → 9 Hz
- Knob at 22 ms → 8 Hz
- ... 43 entries in total

Saved as `results/peak_curve.csv`. This step looks dry but it is the **dictionary the next step needs**.

**Step 5.** `scripts/03_fit_per_subject.py` *(to be written, see roles)*

Now invert the dictionary. For each subject, look up their measured alpha peak frequency and read off the knob value that would produce it in the model:

- Subject PD1234, measured 8.7 Hz → look up → knob ~ 21 ms
- Subject Control1001, measured 9.5 Hz → look up → knob ~ 19 ms

Each of the 149 subjects ends up with one personal `tau_inh` value. Saved as `results/fitted_tau.csv`.

**Step 6.** group comparison on `fitted_tau.csv` *(to be written)*

Same operation as Step 2, **but on the knob values instead of the frequencies**. PD's `tau_inh` distribution vs Control's `tau_inh` distribution. Significant? By how many ms on average?

The final conclusion is then:

> **"PD patients' inhibitory time constant is on average X ms longer than healthy controls'."**

That sentence is the concrete `+x` in the assignment diagram (Healthy model + `+x` → PD model).

## The whole picture in one diagram

```
raw EEG (149 .fif files)
       │ step 1
       v
   features.csv  ─────────────────────────┐
       │                                   │
       │ step 2                            │ step 5
       v                                   │ (reverse lookup)
  group_comparison.csv                     │
  (FIRST PASS DONE,                        v
   data-level result)             fitted_tau.csv
                                           │
                                           │ step 6
                                           v
                                  (SECOND PASS DONE,
                                   model-level result)


  Wilson-Cowan model (src/model.py)
       │ steps 3 + 4 (sweep the knob)
       v
  peak_curve.csv ──┘
  (translation table: knob value ↔ frequency)
```

A higher-resolution version of this diagram lives at `docs/figures/pipeline.png`.

## Three things that are easy to get confused about

**1. Why not just compare frequencies, why bother with the model?**

The direct comparison tells us "PD is slower". The model tells us "in our simplified picture of cortex, this slowing corresponds to inhibitory neurons being X ms slower". The second statement **translates a phenomenon into a mechanism**. That mechanism lives only inside our simplified model, but the model has biological motivation, and putting a concrete number on `+x` is exactly what the assignment asks for.

**2. What exactly is `tau_inh`?**

It is the knob in the model. Biologically it represents the time constant of the inhibitory population: how slowly inhibitory neurons recover after being driven. Larger value means slower inhibition, which slows the whole oscillating excitatory-inhibitory circuit. It is the simplest single-parameter explanation for PD's alpha slowing in our framework.

**3. Why can't we just write a formula `tau_inh -> frequency`?**

Because the Wilson-Cowan equations are nonlinear and have no closed-form solution for the oscillation frequency. The only way to know "knob = 21 ms produces what frequency?" is to run the simulation. That is why step 4 exists.

## Where things stand right now

| Step | File | Status |
|------|------|--------|
| 1 | `scripts/01_extract_features.py`, `src/features.py` | done |
| 2 | `scripts/04_compare_features.py`, `src/stats.py` | done |
| 3 | `src/model.py` | done |
| 4 | `scripts/02_simulate_network.py` | done |
| 5 | `scripts/03_fit_per_subject.py`, `src/fitting.py` | to be written by a teammate |
| 6 | group test on `fitted_tau.csv` | to be written by a teammate |

For the walkthrough notebooks see `notebooks/`. For per-folder documentation see the `README.md` inside each folder.
