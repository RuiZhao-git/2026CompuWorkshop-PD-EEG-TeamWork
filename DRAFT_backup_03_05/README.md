# DRAFT / backup: PD EEG pipeline steps 03 and 05

**Temporary helper folder**, kept on its own inside the repo and deliberately
**not merged into the pipeline** (`scripts/` / `src/` are untouched). These are
heavily-commented reference copies of the two steps assigned to teammates
(03 = per-subject fitting, 05 = group comparison on the fitted tau). Consult
them or fall back on them if a teammate gets stuck. Throwaway: delete the whole
folder once the real `scripts/03` and `scripts/05` exist.

## Files
- `draft_03_fit_per_subject.py` — fits each subject a `tau_inh` by inverting
  the `tau -> peak` lookup curve (`results/peak_curve.csv`). Writes
  `fitted_tau.csv` here.
- `draft_05_compare_tau.py` — Control vs PD group test on the fitted `tau_inh`
  (one-sided Mann-Whitney, H1: PD higher). Reads `fitted_tau.csv`, writes
  `group_comparison_tau.csv` and `compare_tau.png` here.

Both are heavily commented so they can double as an explanation.

## Run
```
/Users/r.z/miniforge3/envs/pd_eeg/bin/python draft_03_fit_per_subject.py
/Users/r.z/miniforge3/envs/pd_eeg/bin/python draft_05_compare_tau.py
```
They only READ from the repo (`peak_curve.csv`, `features.csv`); the repo is
never modified. If you move to another machine, edit the one `REPO_ROOT` line
at the top of each file.

## Result (current data)
- Fitted `tau_inh` median: Control 18.25 ms, PD 21.50 ms → **Δtau = +3.25 ms**.
- One-sided p = 0.00025 (reject H0); two-sided p = 0.00049.
- That two-sided p is essentially the alpha-peak p from step 04 (0.00055),
  because fitted tau is a monotone re-mapping of the alpha peak. The model-level
  test re-expresses the data-level effect in tau units; it is not independent
  evidence. The independent check is the (still-open) synthetic-data recovery test.

## To promote into the real pipeline
See the "PROMOTING THIS TO THE REAL PIPELINE" block at the bottom of each script.
