# Speaking notes, final presentation (26.06)

Speaking cues, one block per slide, in bullet form. Expand each point in your own
words while presenting; the bullets match what is on each slide. These same cues
are embedded as presenter notes in `26062026_slides.md` (VS Code Marp presenter
view). Slides up to "Does the model separate ..." are written here; Outlook and
Take-aways are owned by the team.

---

## Title

- Final presentation: cortical EEG slowing in resting-state Parkinson's.
- Plan: hypothesis, the model, the code, the result, outlook, take-aways.

---

## Slide 1, Hypotheses

- One figure: average posterior power spectrum, Control (blue) vs PD (coral), ±SEM.
- Read the three predicted changes straight off the curves:
  - theta (4 to 8 Hz): PD curve above Control, so theta power is higher.
  - alpha peak: PD curve shifted left, so the rhythm slows.
  - beta (13 to 30 Hz): Control curve above PD, so beta power is lower.
- Numbers, 149 subjects: alpha peak 9.25 to 8.00 Hz; theta up and beta down both
  highly significant.
- Fourth prediction, greyed out: alpha power is a null, it does not change.
- The point: the change is in frequency, not amplitude, so we say alpha slowing,
  not alpha loss.

---

## Slide 2, The model

- A Wilson-Cowan network explains the slowing.
- Left, the mechanism: 8 coupled nodes; in each, E excites I and I inhibits E, and
  that loop produces the rhythm. The inhibition has a time constant, tau_inh, the
  one knob we turn.
- Middle, the dial: tau_inh sets the frequency; turn it up and the alpha peak drops
  down the curve.
  - Control about 18 ms to 9.25 Hz; PD about +3.25 ms longer to 8 Hz, the slowing
    we measured.
- Right, the rhythm: two real simulated waveforms; same window, PD fits in fewer
  cycles.
- Takeaway: the whole healthy-to-patient change is one number.

---

## Slide 3, Code & repository

- Top, the pipeline: the EEG of 149 people flows through six numbered scripts:
  extract features, fit each person a tau from their alpha peak, compare the groups.
  (02 builds the lookup curve, 04 tests the data directly, 06 validates the fit.)
  - Key box: the model is built once; one number, tau_inh, turns healthy into patient.
- Lower-left, the repository: numbered scripts, reusable modules, a results folder
  every run writes into.
  - Terminal: every number in this talk is the real output of one script, and each
    run writes the exact file shown.
- Lower-right, version control: branches merged into main, fifty commits; main
  reproduces every result and this deck.

---

## Slide 4, Does the model separate patients from controls?

- The model-level result, told honestly.
- Left, the separation: fitted tau_inh per subject. Medians +3.25 ms apart
  (Control 18.25, PD 21.5), highly significant. But the distributions overlap, so
  this separates the groups on average, not individual patients. It re-expresses
  the measured alpha slowing in model units.
- Right, parameter recovery: put a known tau in, fit it back; the points land on
  the diagonal, so the fit is unbiased, with a typical error of about half a
  millisecond.
- What the model adds: not new statistical evidence, but the mechanistic reading
  plus this validated, unbiased fit.

---

## Slide 5, Outlook and open challenges

A few honest limitations and where we would go next. On the challenges side: the
fitting only resolves tau to about half a millisecond, because the frequency
curve is measured in coarse steps. The model-level test re-expresses the
alpha-peak effect in model units rather than being independent evidence. And the
model reproduces the alpha slowing but not the theta and beta changes, because we
only varied one parameter on a simplified, identical, all-to-all network. For
future work: constrain tau with more than the peak, for example by fitting the
whole spectrum or the functional connectivity. Let the model also account for the
theta and beta changes. Use a real structural connectome with regional
differences. And relate the fitted tau to clinical measures like disease severity
or medication.

---

## Slide 6, What we took away

Each of us says our single biggest take-away from the course.
(Each member states their own take-away in one sentence. Replace the four
placeholders on the slide before the talk.)

---

## Appendix, Per-subject distributions (only if asked)

For reference, the full per-subject distributions behind the effect sizes. The
box shows the median and quartiles, the dots are individual subjects. Alpha peak
shifts down in patients, theta up, beta down, and alpha power is unchanged.

---

## Appendix, Effect sizes (only if asked)

The same four features as standardised effect sizes: rank-biserial correlation
with a 95 percent bootstrap confidence interval. Alpha peak, theta, and beta all
sit well away from zero in the predicted direction; alpha power sits on zero.
