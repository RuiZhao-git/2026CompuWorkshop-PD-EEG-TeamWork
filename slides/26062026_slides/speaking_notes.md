# Speaking notes, final presentation (26.06)

Verbatim spoken script, one block per slide. Read it as-is; the content matches
exactly what is on each slide. No greetings or filler. These are also embedded as
presenter notes in `26062026_slides.md` (visible in VS Code Marp presenter view).

---

## Title

This is our final presentation on cortical EEG slowing in resting-state
Parkinson's disease. We will show our hypothesis, the model we built, how the
code turns a healthy model into a patient model, the statistical result, where
we would go next, and what each of us took from the course.

---

## Slide 1, Hypotheses

Our three predictions from the literature, all in one figure: the average
posterior power spectrum, controls in blue, patients in coral, with the standard
error shaded. You can read the three changes straight off the curves. In the
theta band, four to eight hertz, the patient curve sits above the control curve,
so theta power is higher. Around the alpha peak the patient curve is shifted to
the left, so the alpha rhythm slows. In the beta band, thirteen to thirty hertz,
the control curve is above the patient curve, so beta power is lower. The line
below gives the numbers: on 149 subjects the alpha peak drops from 9.25 to 8.00
hertz, theta up and beta down are both highly significant. We list a fourth
prediction too, alpha power, greyed out because it is a null result: alpha power
does not change. That null is the point, the change is in frequency, not
amplitude, which is why we say alpha peak slowing rather than alpha loss.

---

## Slide 2, The model

To explain the slowing we built a Wilson-Cowan network. The left panel is the
mechanism: eight cortical nodes, all coupled, and inside each one an excitatory
population E and an inhibitory population I. E excites I, I inhibits E, and that
back-and-forth produces the rhythm. The inhibition has a time constant, tau_inh,
and that is the one knob we turn. The middle panel is the dial: it shows how
tau_inh sets the frequency. Turn the knob up and the alpha peak drops smoothly all
the way down the curve. Control sits near 18 milliseconds and 9.25 hertz; the
patient setting is about three and a quarter milliseconds longer and brings the
rhythm down to 8 hertz, the slowing we measured in the data. The right panel shows
what that looks like: two real simulated waveforms at those two settings, control
in blue and patient in coral, same window, but the patient rhythm fits in fewer
cycles. So in the model the entire
healthy-to-patient change is one number.

---

## Slide 3, Code & repository

Across the top is the pipeline: the resting EEG of 149 people flows through six
numbered scripts, from extracting the features, to fitting each person a model
parameter from their alpha peak, to comparing the two groups. The three smaller
scripts below build the lookup curve the fit uses, test the data directly, and
validate the fit on synthetic data. The point to land is the highlighted box: the
model is built once, and only one number turns a healthy model into a patient one,
the inhibitory time constant tau_inh.

On the lower left is the repository, organised into the numbered scripts, the
reusable modules, and a results folder that every run writes into. Below it, a
terminal makes the reproducibility concrete: every number in this talk is the real
output of running one script, and each run writes the exact file you see.

On the lower right is the version control: we developed on branches merged into
main, fifty commits in total, and main reproduces every result and this deck.

---

## Slide 4, Does the model separate patients from controls?

Now we test the model the same way we tested the data. The left panel shows the
fitted tau_inh for every subject, controls in blue, patients in red. The patient
median is about three and a quarter milliseconds higher, and a one-sided
Mann-Whitney test gives a p-value of about 0.0002, so the groups are clearly
separated in the model parameter. The natural worry is that this is just an
artefact of the fitting. The right panel rules that out. We simulated the model
at known tau values and fitted them back. The points sit on the diagonal, the
fit is unbiased, and its precision is about half a millisecond, far smaller than
the three-millisecond group difference. So the separation is real, not a fitting
artefact.

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
