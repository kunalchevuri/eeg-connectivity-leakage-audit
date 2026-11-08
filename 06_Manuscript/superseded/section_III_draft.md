# Section III — Leakage in Connectivity Pipelines (DRAFT, ~1150 words per blueprint budget)

Status: first draft, does not depend on the corpus. Kunal/advisor to edit prose and confirm notation before pasting into the IEEE template. Cite Fig. 2 as the reference figure for III-B.

## III-A. Pipeline formalization and connectivity measures

Let x_i(t) denote the signal recorded at channel i, i = 1,…,N, and let T denote the number of samples in an epoch. A connectivity-based classifier does not operate on x_i(t) directly; it operates on a matrix **A** ∈ ℝ^(N×N) derived from x_i(t) through a chain of steps — filtering, epoching, connectivity estimation, thresholding, normalization — each of which is fit on some subset of the data. The central methodological question this audit asks of each study is which subset that was.

**Magnitude-squared coherence.** Between channels i and j at frequency f,

  C_ij(f) = |S_ij(f)|² / (S_ii(f) · S_jj(f))

where S_ij(f) is the cross-spectral density between x_i and x_j. *Leakage point:* S_ij is estimated over a window of data. If that window spans samples from both the training and test partitions, or is averaged across subjects before the partition is applied, the resulting estimate — and every feature derived from it — carries information from outside the training fold.

**Phase locking value.** Over T samples, with Δφ_ij(t) the instantaneous phase difference between channels i and j,

  PLV_ij = (1/T) · |Σ_t exp(j·Δφ_ij(t))|

PLV is bounded in [0, 1] and is estimated within a single epoch, which limits (but does not eliminate) the L2 leakage route: pooling epochs across subjects before computing PLV still leaks.

**Phase lag index.** PLI discounts zero-lag coupling that would otherwise be dominated by volume conduction:

  PLI_ij = |⟨sign(Δφ_ij(t))⟩|

**Graph construction.** Any of the above yields a weighted adjacency matrix **A** ∈ ℝ^(N×N). Matrices are frequently binarized at a threshold τ, or reduced to their top-k edges by weight:

  A_ij^bin = 1 if A_ij > τ, else 0

*Leakage point:* if τ (or k) is chosen from the distribution of A_ij values pooled across the full dataset — a common way to fix a target graph density — τ is a parameter fit on data that includes the test set.

## III-B. The leakage taxonomy (L1–L5)

Fig. 2 shows two orderings of the same six-step pipeline: raw EEG, filtering, epoching, connectivity estimation, thresholding/normalization, and model training. In the leakage-free ordering (Fig. 2a), the train/test partition is applied immediately after filtering, and every later step is computed separately within each fold. In the leaking ordering (Fig. 2b), the partition is applied last, after epoching, connectivity estimation, and threshold/normalization statistics have already been computed from the pooled dataset — so information from the test set has already shaped the features the model is trained on before the model ever sees a train/test split. We formalize five points at which this can occur:

- **L1 — Epoch-level partitioning.** A recording contributes many epochs, each treated as an independent sample. If the train/test (or cross-validation fold) assignment is made at the epoch level rather than the subject level, epochs from the same subject can appear on both sides. *Leakage-free condition:* every epoch from a given subject is assigned entirely to one side of the partition.
- **L2 — Connectivity estimation scope.** Coherence, PLV, PLI, or another measure is estimated from a window of data. *Leakage-free condition:* the window used for any one estimate lies entirely within one fold, and no estimate is pooled or averaged across subjects before the partition is applied.
- **L3 — Threshold selection.** A binarization threshold τ or an edge-count k is applied to the connectivity matrix. *Leakage-free condition:* τ or k is chosen using training-fold statistics only (or held fixed a priori on theoretical grounds), never from a distribution pooled across the full dataset.
- **L4 — Feature normalization.** Matrices or derived features are standardized or rescaled. *Leakage-free condition:* normalization statistics (mean, variance, min/max) are computed on the training fold and then applied, unchanged, to the test fold.
- **L5 — Channel or band selection.** A subset of electrodes or frequency bands is chosen for the final model. *Leakage-free condition:* the subset is chosen a priori or from training-fold performance only, never by comparing candidate subsets against test-set accuracy.

Table I documents the criterion under which each surface occurs; Table II (Section VI) converts these into a reader-facing checklist.

## III-C. Why EEG subject signatures make L1 severe

L1 deserves separate emphasis because EEG carries strong subject-specific signatures that are independent of pathology: individual alpha frequency, skull conductance, electrode impedance, and head geometry all vary between people and are stable within a single recording session. A classifier trained on epochs from a subject who also appears in the test set does not need to learn anything about depression to score well on that subject's test epochs — it can achieve high accuracy by recognizing the individual and recalling their label. This is not a subtle statistical nuance: the literature under audit typically pairs a small number of subjects (tens) with a large number of epochs per subject (often hundreds), which is exactly the regime in which within-subject information dominates a shuffled split. The effect is compounded, not replaced, by L2–L5: even under subject-level partitioning, a connectivity or threshold estimate computed from the whole dataset can still transfer test information into the training features (Section III-B).
