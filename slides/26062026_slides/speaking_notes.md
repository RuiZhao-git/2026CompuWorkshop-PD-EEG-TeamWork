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

Our hypothesis, based on the literature, was that compared to age-matched healthy
controls, Parkinson's patients at rest show three changes: the alpha peak
frequency slows down, theta-band power increases, and cortical beta-band power
decreases. This figure tests all three on 149 subjects. Each row is one feature.
The dot is the effect size and the line is its 95 percent confidence interval.
Left of the centre line means lower in Parkinson's, right means higher. Alpha
peak is clearly to the left, so it slows. Theta is to the right, so it increases.
Beta is to the left, so it decreases. All three intervals are well away from
zero, so all three predictions are confirmed. The grey one, alpha power, sits on
zero: it does not change, which is why we say alpha peak slowing and not alpha
power loss.

---

## Slide 2, The model

To explain this slowing we built a Wilson-Cowan network. On the left are eight
cortical nodes, all connected to each other. Inside each node, in the middle,
there is an excitatory population E and an inhibitory population I. E excites I,
and I inhibits E, and that back-and-forth produces the rhythm. The one parameter
we change is tau_inh, the inhibitory time constant, shown as the knob. On the
right are two real outputs of this model. In blue, with a short tau_inh of about
18 milliseconds, the network oscillates at about 9 hertz, the control rhythm. In
red, with a longer tau_inh of about 22 milliseconds, it oscillates at about 8
hertz. Same network, same time window, but the patient setting fits in fewer
cycles. So the slowing in the data corresponds, in the model, to a longer
inhibitory time constant, about three milliseconds longer in patients.

---

## Slide 3, Code & repository

On the left, the code in three steps: we fit each subject a tau from their
measured alpha peak, we build the model with that tau (the one number that
differs between healthy and patient), and we compare the groups with a one-sided
test. The terminal makes the point that every number in this talk comes from
running one script: step 05 gives the +3.25 ms group difference at p = 0.0002,
and step 06 confirms the fit is unbiased to about half a millisecond.

On the right, the repository: six numbered pipeline scripts, four reusable
modules, forty-six commits, on 149 subjects. Each of us worked on our own branch
and merged into main, which produces every result and this deck, fully
reproducible.

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
