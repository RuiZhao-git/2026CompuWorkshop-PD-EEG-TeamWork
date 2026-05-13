# results/

Generated outputs from the pipeline scripts.

## Files planned for this folder

| File | Produced by | Description |
|------|-------------|-------------|
| `features.csv` | `scripts/01_extract_features.py` | Per-subject features: alpha peak frequency + relative band powers (theta, alpha, beta), computed on the average PSD over posterior channels |
| `peak_curve.csv` | `scripts/02_simulate_network.py` | Model peak frequency for a grid of tau_I values |
| `fitted_tau.csv` | `scripts/03_fit_per_subject.py` | Per-subject fitted tau_I |
| `figures/` | various | Plots produced during analysis |

## Commit policy

- Small CSVs (a few hundred rows): OK to commit, makes review easier
- Small figures (PNG under 1 MB): OK to commit
- Large arrays, intermediate caches, anything over 10 MB: do NOT commit, let teammates regenerate locally

Everything in this folder should be regenerable from `scripts/` plus the local data.
