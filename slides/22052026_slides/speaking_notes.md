# Speaking notes, 22.05.2026 presentation

One block per slide and per subheader. Read or paraphrase. Pure content,
no filler. Written for a beginner audience, so terms are spelled out.

---

## Slide 1, Title

This is a progress update on our project, which models the cortical EEG slowing we expect to see in Parkinson's disease at rest.

---

## Slide 2, Hypothesis (refined)

### What we predict

Our hypothesis is that, compared to age-matched healthy controls, Parkinson's disease patients at rest show three things: a slowing of the alpha peak frequency in the 8 to 13 Hz band, an increase in theta-band power in the 4 to 8 Hz band, and a decrease in cortical beta-band power in the 13 to 30 Hz band. Together these describe what is generally called EEG slowing.

### Refinement based on data

We initially wrote the alpha part as "decreased alpha power". When we ran the group comparison on 149 subjects, that turned out not to match the data: the alpha power, measured as the share of total EEG power falling in the alpha band, is essentially the same in both groups. What actually changed was the alpha peak frequency, which dropped from a median of 9.25 Hz in controls to 8.00 Hz in PD, significant at p less than 0.001. So we refined the wording to "alpha peak slowing" to reflect what the data actually shows. The four box plots at the bottom of the slide show, in order, the alpha peak frequency, alpha relative power, theta power and beta power.

---

## Slide 3, Model: Wilson-Cowan network

### Network

We use a Wilson-Cowan model configured as a network of 8 cortical nodes. Each node represents one small piece of cortex, and contains two interacting neural populations: an excitatory group, labelled E, and an inhibitory group, labelled I. Their interaction produces an oscillation in the alpha range. The figure on the right shows the network at the top, and one of the nodes opened up at the bottom so you can see the E and I populations inside.

### Free parameter

The model has many internal parameters, but we only vary one: tau_inh, the inhibitory response time. Larger tau_inh slows the oscillation down, smaller tau_inh speeds it up. By turning just this one knob, we can simulate the alpha slowing our hypothesis predicts.

### Simplifications

We made three simplifying choices that you can see listed on the slide. All 8 nodes share the same parameter values, which matches our assumption that the slowing is uniform across cortex. The nodes are coupled all-to-all, meaning every node is connected to every other. And the simulation runs without random noise, so the output depends only on tau_inh.

---

## Slide 4, Status and next steps

### Done

We have completed four pieces, marked with green checkmarks in the pipeline diagram on the right. First, feature extraction across all 149 participants, producing one alpha peak frequency and three relative band powers per subject. Second, the group comparison on those features, where all three predicted directions came out significant at p less than 0.001. Third, the Wilson-Cowan network was implemented and verified to produce an alpha-range oscillation, both at single-node level and with 8 nodes. Fourth, we ran the model many times, each time with a different tau_inh between 11 and 32 ms, and recorded the peak frequency it produced. That gives us a lookup table connecting each tau_inh value to a peak frequency.

### Remaining

Three pieces remain, marked in the diagram with yellow TBD badges. The per-subject fitting step will take each participant's measured alpha peak and use the lookup curve to assign them a personal tau_inh. The model-level group test will then compare the PD and Control distributions of those fitted tau_inh values, in the same way we did for the raw features. Finally, we will express the result as a single shift in tau_inh that takes the healthy model to the PD model.

---

## Slide 5, Current challenge

### A test we should run

There is a test we should run on our fitting procedure but have not yet done. The figure on the right shows the idea. We pick a tau_inh value ourselves, for example 18 milliseconds. Then we use the Wilson-Cowan model to generate a synthetic EEG signal at that tau_inh. Then we run the same fitting procedure on that synthetic signal. If the procedure is working correctly, it should return roughly 18 milliseconds, the same value we started with. The check here is whether the number coming out of the fitting matches the number we put into the model. We are not comparing EEG signals, we are comparing one tau_inh value to another.

### Why this matters

The reason this matters is that we have not yet done this test on our fitting procedure. Until we do, when we see a difference in fitted tau_inh between PD and Control on the real data, we cannot be sure that difference reflects a real biological effect rather than an error made by the procedure itself. Running the synthetic-data test would close that gap. We have not yet decided how to design this test in a way that is informative without expanding the project's scope, and we would value input on this.
