"""Extract per-subject EEG features from all .fif files.

Reads:  every *_preproc_raw.fif under $PD_DATA_DIR/Control and $PD_DATA_DIR/PD
Writes: results/features.csv

Output columns:
    subject_id, group, alpha_peak_hz, alpha_power, theta_power, beta_power

`alpha_peak_hz` is the frequency of maximum PSD in 7-13 Hz, averaged across
posterior channels (O, PO, P region).
`*_power` columns are RELATIVE band powers (band integral divided by total
power in 1-45 Hz), so values are dimensionless and comparable across
subjects.
"""

import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# Make the project root importable so `from src.features import ...` works
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.features import extract_subject_features  # noqa: E402


def main():
    load_dotenv(REPO_ROOT / ".env")
    data_dir = os.environ.get("PD_DATA_DIR")
    if not data_dir:
        raise RuntimeError(
            "PD_DATA_DIR is not set. Copy .env.example to .env and set the path."
        )
    data_dir = Path(data_dir)

    fif_files = sorted(
        list((data_dir / "Control").glob("*_preproc_raw.fif"))
        + list((data_dir / "PD").glob("*_preproc_raw.fif"))
    )
    if not fif_files:
        raise RuntimeError(f"No *_preproc_raw.fif files found under {data_dir}")

    print(f"Found {len(fif_files)} files. Extracting features...")

    rows = []
    for i, fif in enumerate(fif_files, 1):
        try:
            row = extract_subject_features(fif)
        except Exception as exc:
            print(f"  [{i:3d}/{len(fif_files)}] FAILED {fif.name}: {exc}")
            continue
        rows.append(row)
        if i % 10 == 0 or i == len(fif_files):
            print(f"  [{i:3d}/{len(fif_files)}] {fif.name} -> "
                  f"alpha_peak={row['alpha_peak_hz']:.2f} Hz")

    df = pd.DataFrame(rows)
    out_path = REPO_ROOT / "results" / "features.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, float_format="%.6f")

    print(f"\nSaved {len(df)} rows to {out_path}")
    print("\nGroup summary:")
    print(df.groupby("group")[["alpha_peak_hz", "alpha_power",
                                "theta_power", "beta_power"]].describe().T)


if __name__ == "__main__":
    main()
