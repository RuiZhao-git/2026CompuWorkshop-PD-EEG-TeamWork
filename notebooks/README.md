# notebooks/

Interactive Jupyter notebooks for exploration, plotting, and sanity checks.

## Naming convention

Prefix each file with two digits and your initials so notebooks from different people do not collide:

- `01_AA_data_exploration.ipynb`
- `02_BB_wc_parameter_sweep.ipynb`
- `03_CC_fit_diagnostics.ipynb`

## Conventions

- Clear all cell outputs before committing (Kernel -> Restart & Clear Output). Notebook diffs are unreadable when outputs are included.
- Import functions from `src/` rather than redefining them inline.
- If a notebook produces something the whole team needs, move the relevant code into `src/` or a script.

## What does NOT belong here

- Reusable function definitions. Those go in `src/`.
- Pipeline stages that must run reproducibly. Those go in `scripts/`.
