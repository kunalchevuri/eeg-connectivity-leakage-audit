# Section I — Introduction (DRAFT, AI-written; Kunal and advisor to edit)

Budget (MLESP recompute): I-A 270 · I-B 270 · I-C 225 = 770 words.
Per blueprint §9, if the paper runs long, cut here and in Section II first — never Section III or V.

Markers: `[CITE: …]` = a reference Kunal must find, personally open, and log (blueprint §12). **None has been inserted; do not replace a marker with a reference you have not read.** `[date]`, `[databases]` = fill from `02_Phase2_Gap_Search/search_log.csv` once the manual searches are run.

---

## I-A. Clinical motivation

Major depressive disorder is among the leading causes of disability worldwide [CITE: WHO or Global Burden of Disease estimate], yet its diagnosis still rests on clinical interview and self-report scales, which depend on the patient's account and the clinician's judgment [CITE: diagnostic reliability of structured interview / DSM field trials]. An objective physiological marker would support diagnosis, and electroencephalography (EEG) is an attractive candidate: it is inexpensive, non-invasive, portable, and resolves neural activity on the millisecond scale [CITE: EEG in psychiatric assessment review].

Depression is increasingly understood as a disorder of interaction between brain regions rather than of any single region [CITE: network model of depression, e.g. resting-state connectivity meta-analysis]. Functional connectivity — the statistical dependence between signals recorded at different sites, estimated with measures such as coherence, the phase-locking value, or the phase lag index — offers a way to capture that interaction from scalp EEG. Deep learning has made it practical to learn from connectivity matrices directly, treating them as images for convolutional networks or as graphs for graph neural networks, without hand-selecting network features. A substantial literature now applies these models to distinguishing people with MDD from healthy controls, and many studies report classification accuracies above 90% [CITE: a review of DL for EEG depression detection — cite a review, not individual studies].

*(≈210 words — room for one more sentence of clinical context if needed)*

---

## I-B. The verification problem

Accuracies of this magnitude would be clinically meaningful if they held. Whether they hold depends on something a reader usually cannot check: whether any information from the test data reached the model during training. This is data leakage, and in neuroimaging machine learning it has been shown to inflate reported performance substantially [CITE: connectome-based ML leakage study — Rosenblatt et al. 2024 is the candidate; open and verify first].

Recent reviews of EEG-based depression detection have examined how studies partition their data — random holdout, subject-dependent testing, leave-one-subject-out or external validation [CITE: existing validation-practice review(s), see closest_prior_art.md]. That is the right question about the split. But a connectivity model does not consume raw EEG. It consumes a connectivity matrix, built through a chain of steps that each run before the split: recordings are segmented into epochs, connectivity is estimated, matrices are thresholded into graphs, values are normalized, and channels or frequency bands are selected. Each step can carry test information into training if it draws on data beyond the training fold. Most papers do not report the order of these steps, which leaves the leakage question unanswerable from the paper alone.

Prior reviews audit how these studies split their data. This work audits what happens to the data before it is split. To our knowledge, based on searches of [databases] through [date], no prior review has audited connectivity-pipeline construction as a leakage surface in this literature.

*(≈250 words)*

---

## I-C. Contributions

Already in `paper.tex`, worded exactly as blueprint §4 specifies. Do not paraphrase. The only edit is replacing *N* with the final count from `prisma_counts.csv`.
