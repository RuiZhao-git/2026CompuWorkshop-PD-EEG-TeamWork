# archive/

Historical material preserved from before the team-collaborative phase
of the project. Read-only. Do not run the scripts here; the canonical
pipeline lives at the top of the repo (`scripts/`, `src/`,
`notebooks/`).

## individual_prep_may_8/

Rui's solo exploration done before the 8 May presentation, kept as a
record of how the team's hypothesis and model choice were arrived at.

Contents:

- `scripts/`: six exploration scripts (sanity check, channel audit,
  PSD computation, group comparison, robust alpha-peak detection,
  single-node Wilson-Cowan demo). Superseded by `scripts/01..05` and
  `src/*.py` in the main repo.
- `figures/`: outputs of those scripts.
- `cache/` (git-ignored, kept local only): intermediate CSV / npz
  files produced by the scripts. Total ~18 MB. Regenerable from the
  scripts, not worth versioning.
- `hypothesis.md`, `meeting_prep.md`, `slide_content.md`: notes used
  during the 8 May presentation prep. The team's refined hypothesis
  (with the `alpha peak slowing` rewording) lives in the main
  `README.md` and `docs/plain_explanation.md`.

The 8 May slide deck itself is in `slides/08052026_slides/`, not here.
