"""
Step 1.5 — Channel audit across ALL 149 subjects.

The sanity check showed that not every subject has the same 63 channels
(some have Iz/I1/I2 in place of FT9/PO3/PO4). Before computing group-level
PSDs we need:
  - the channel SET each subject has
  - the INTERSECTION (channels present in every subject) — this is what we can
    compare across groups without dropping anybody
  - any subjects with weird counts that we should drop
Saves a small JSON summary to ../cache/channel_audit.json.
"""

from collections import Counter
from pathlib import Path
import json

import mne

DATA_ROOT = Path("/Users/r.z/Desktop/PD")
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def list_subjects(group: str) -> list[Path]:
    return sorted((DATA_ROOT / group).glob("*_preproc_raw.fif"))


def main() -> None:
    per_subject: dict[str, dict] = {}
    all_channels: Counter = Counter()
    n_total = 0

    for group in ("Control", "PD"):
        for fpath in list_subjects(group):
            subj = fpath.stem.replace("_preproc_raw", "")
            # Read header only (preload=False) — fast.
            raw = mne.io.read_raw_fif(fpath, preload=False, verbose="ERROR")
            chs = raw.ch_names
            per_subject[subj] = {
                "group": group,
                "n_channels": len(chs),
                "channels": chs,
                "sfreq": raw.info["sfreq"],
                "duration_s": float(raw.times[-1]),
            }
            all_channels.update(chs)
            n_total += 1

    # Intersection: channels present in every subject.
    common = {ch for ch, n in all_channels.items() if n == n_total}

    # Channels that are NOT in everyone (so they'll be dropped from group analysis).
    partial = {ch: n for ch, n in all_channels.items() if n != n_total}

    # Subjects whose channel count is unusual.
    counts = Counter(s["n_channels"] for s in per_subject.values())

    print(f"Total subjects: {n_total}")
    print(f"Channel-count distribution: {dict(counts)}")
    print(f"Common channels (in EVERY subject): {len(common)}")
    print(f"Channels missing in some subjects ({len(partial)}):")
    for ch, n in sorted(partial.items(), key=lambda x: -x[1]):
        print(f"  {ch}: present in {n}/{n_total}")

    summary = {
        "n_subjects": n_total,
        "channel_count_distribution": dict(counts),
        "common_channels": sorted(common),
        "n_common": len(common),
        "partial_channels": partial,
        "per_subject": per_subject,
    }
    out = CACHE_DIR / "channel_audit.json"
    with out.open("w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
