# Team inputs for the Outlook + Take-aways slides (parked, not yet designed)

Raw teammate contributions collected for the two team-owned slides
(Outlook / open challenges, and What we took away). This is a holding file:
the content still has to be rewritten into slide language and designed to
match the deck. Do not paste verbatim.

Status: Jan in. The Outlook slide is now DESIGNED from his content as a hero figure
(`figures/outlook.svg` via `outlook.gen.py`: 3 paired limit -> next-step rows). Take-aways
slide still open, missing: Rui, Melissa, Friedrich.

---

## Jan, Outlook content (he supplied the whole Outlook slide)

### Current challenges
1. Functional degeneracy / identifiability: many different parameter settings can
   produce the same output, so the fit re-expresses the data but cannot rule out
   alternative mechanisms (e.g. weaker excitatory-to-excitatory coupling w_EE, or a
   changed external input drive).
2. Coarse frequency resolution: tau_inh is swept in discrete coarse steps
   (~0.5 to 1 ms), so the frequency is stepped too, giving an inherent fitting error
   (the ~0.5 ms recovery error). Fix: continuous gradient-based optimisation instead
   of a discrete lookup table.

### Future directions
1. Replace the 8-node all-to-all uniform wiring with a full whole-brain atlas weighted
   by a real structural connectivity matrix.
2. Sweep a multi-dimensional parameter space, not just tau_inh: also tau_E, local
   synaptic weights (w_EE, w_EI, w_IE), and global coupling gain g. Moves from a
   single alpha-generator toward a fuller cortical-dynamics simulation.
3. Link to pharmacology: correlate each patient's fitted tau_inh with clinical
   records, in particular tested ON vs OFF L-Dopa, to see whether fitted tau_inh
   "speeds back up" on medication.

### Jan, personal take-away
> This course taught me that you do not have to be a master programmer to
> meaningfully contribute to, and clinically interpret, advanced computational
> research.

---

## Review flags (Rui to resolve before this goes on a slide)

- Strong content overall, deeper than the old skeleton. Degeneracy and the L-Dopa
  idea are the two best points.
- Written as discussion prose with un-introduced notation (tau_E, w_EE/w_EI/w_IE, g).
  Must be cut to short slide bullets and plain language (deck audience are novices).
- Check: does our dataset actually carry ON/OFF medication labels? If not, the L-Dopa
  point is "needs a different dataset", not something we can run.
- tau_inh is GABAergic, L-Dopa is dopaminergic: the link is indirect, keep it as a
  speculative future direction, not a direct mechanism.
- Tension to reconcile: "add more free parameters" (future #2) worsens the very
  degeneracy named in challenge #1, unless we also fit more targets (full spectrum / FC)
  to constrain them. Present them as linked.
- Keep the +/-0.5 ms story consistent with slide 5 (there it is a success vs the
  +3.25 ms effect; here it is framed as a coarse-resolution limit). Both true; word it
  so it does not read as self-contradiction.
- Typos in the source: "continious", and a broken quote in the degeneracy sentence.
