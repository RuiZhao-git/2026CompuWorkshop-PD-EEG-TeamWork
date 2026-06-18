# scripts/

Numbered end-to-end pipeline scripts. Each one runs from the command line and produces files in `results/`.

## Files planned for this folder

| File | Reads from | Writes to | Status |
|------|-----------|-----------|--------|
| `01_extract_features.py` | EEG .fif files in `$PD_DATA_DIR` | `results/features.csv` | done by Rui |
| `02_simulate_network.py` | (no input, runs the model) | `results/peak_curve.csv` | done by Rui |
| `03_fit_per_subject.py` | `results/features.csv` and `results/peak_curve.csv` | `results/fitted_tau.csv` | done |
| `04_compare_features.py` | `results/features.csv` | `results/group_comparison.csv` + box plots | done by Rui |
| `05_compare_tau.py` | `results/fitted_tau.csv` | `results/group_comparison_tau.csv` + box plots | done |
| `06_recover_tau.py` | `results/peak_curve.csv` (+ runs the model) | `results/tau_recovery.csv` + recovery figure | done |

`features.csv` columns: `subject_id, group, alpha_peak_hz, alpha_power, theta_power, beta_power`
(Powers are RELATIVE band powers, i.e. band integral divided by total power in 1-45 Hz. Computed on the average PSD over posterior channels O/PO/P.)
`peak_curve.csv` columns: `tau_inh_ms, simulated_peak_hz`
`fitted_tau.csv` columns: `subject_id, group, fitted_tau_ms`
`tau_recovery.csv` columns: `tau_true_ms, simulated_peak_hz, tau_fit_ms, error_ms`
`group_comparison.csv` and `group_comparison_tau.csv` columns: `feature, n_Control, n_PD, median_Control, median_PD, median_diff, u_statistic, p_value, rank_biserial`

## Conventions

- Each script is runnable from the repo root: `python scripts/NN_name.py`
- Each script imports its helper functions from `src/`, does not redefine them
- Each script prints progress so you can tell what stage it is on
- Each script writes its output to `results/` and does not depend on cwd

## Adding a new pipeline stage

1. Number it according to where it fits in the order (e.g., `04_...`)
2. Add a row to the table above with its inputs and outputs
3. Make sure its outputs land in `results/`
