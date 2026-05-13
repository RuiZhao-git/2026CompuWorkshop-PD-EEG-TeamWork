# src/

Reusable Python modules. Anything in here can be imported from scripts and notebooks:

```python
from src.features import compute_psd
from src.model import build_network
from src.fitting import fit_tau_for_subject
```

## Files planned for this folder

| File | Purpose | Status |
|------|---------|--------|
| `features.py` | Functions to compute PSD, alpha peak frequency, band power from EEG | TBD |
| `model.py` | Wilson-Cowan network setup (wrapper around neurolib), simulation runners | TBD |
| `fitting.py` | Per-subject parameter inference: invert the peak-vs-tau curve to get tau_I | TBD |

## Conventions

- Every function has a short docstring with inputs, outputs, and a one-line description.
- Do not hard-code data paths in `src/`. Pass paths as arguments or read from the `PD_DATA_DIR` environment variable.
- Functions in `src/` should not print or plot unless that is their explicit purpose. Let the calling script or notebook handle output.

## What does NOT belong here

- Scripts that run a full analysis end-to-end. Those go in `scripts/`.
- Interactive exploration cells. Those go in `notebooks/`.
- Data files. Those stay local per machine.
