# Flag: criterion 2 when the graph is built from electrode geometry (R089, R092)

**Status:** provisional decision recorded as `exclude?` in `screening_log.csv`.
Needs KC's confirmation and, because it sets a precedent for the rest of screening,
Dr. Aledhari's ruling (advisor question 14).
**Raised:** 2026-09-23, during full-text screening.

## The criterion

Blueprint §7.1, inclusion criterion 2 — the study must:

> Compute a functional or effective connectivity measure (coherence, PLV, PLI,
> correlation, Granger causality, mutual information, **or a graph derived from one**)

and the matching exclusion is:

> studies using only raw signal or spectral power **without a connectivity step**

## What these two papers actually compute

Both build a channel × channel adjacency matrix by running k-nearest-neighbours over
the **3-D scalp coordinates of the electrodes**. The edge weights never touch the
recorded signal.

**R089** (Algorithm 3, "Construction of Channel-Channel Relations Matrix"):

> Input: electrodes.tsv, k, threshold (thr), S
> Initiate electrode coordinates matrix C = {C1 … C16} ∈ R^16×3
> D(i,j) = sqrt(sum((Ci[d] − Cj[d])²)) # Compute pairwise distance Euclidean distance
> between all pairs of channels

**R092** (Eq. 1 and surrounding text):

> Each electrode Eᵢ … is represented by its 3D spatial coordinates. The pairwise
> distance between the electrodes is calculated and given as D(Eᵢ, Eⱼ)
> Aᵢⱼ = 1, if j ∈ KNN(i) or i ∈ KNN(j); 0 otherwise

In both, the **node features** are statistical, temporal and spectral descriptors
computed per channel in isolation — mean, Lempel–Ziv complexity, Higuchi fractal
dimension, detrended fluctuation analysis, and band powers. None of these is a
pairwise quantity either.

So neither paper computes coherence, PLV, PLI, correlation, Granger causality or
mutual information anywhere, and the graph is not derived from any of them.

Worth noting that R092 makes the criticism itself, then does the thing it criticises:

> Existing studies capture the channel-channel relations purely based on spatial
> proximity, that is connections between channels that are close in space but not
> necessarily functionally relevant … Thus, it is necessary to capture the functional
> connections that are relevant to the synchronized brain activity

## The argument each way

**For excluding (recommended).** The edge set is fixed by the electrode montage. Two
subjects wearing the same cap get the same adjacency matrix regardless of their brain
activity. Nothing pairwise is estimated from data, so there is no connectivity
estimation step for the audit to examine — and L2 (connectivity estimation scope) and
L3 (threshold selection) are undefined for these papers. Including them would put
studies in the corpus that the leakage taxonomy cannot rate.

**For including.** Both describe themselves throughout as brain-network and functional
connectivity work, and a reader scanning titles and abstracts would take them as
in-scope. Excluding them means the audit is silent on a class of paper that claims the
connectivity label without earning it.

## Proposed decision rule (the part that needs the advisor's sign-off)

> **Criterion 2 is met only if at least one edge weight in the graph depends on the
> recorded signals.** A graph whose edges are fixed by electrode positions, montage
> geometry, or an anatomical atlas alone does not satisfy criterion 2, whatever the
> paper calls it.

This rule is stable across the calls already made in the corpus:

| Rank | Edge weights come from | Rule says | Logged as |
|---|---|---|---|
| R023 | PLV between channel signals | include | include |
| R032 | PLI between channel signals | include | include |
| R082 | PLV + Pearson correlation between ROI signals | include | include |
| R086 | mutual information between channel signals | include | include |
| R001 | GPDC / dDTF fitted to the signals | include | include |
| R049 | Pearson-correlation adjacency | include | include? |
| R034 | adaptive topology learned from the signals | include | include? |
| R019 | attention weights learned from the signals | include | include? |
| **R089** | **Euclidean distance between electrode coordinates** | **exclude** | **exclude?** |
| **R092** | **Euclidean distance between electrode coordinates** | **exclude** | **exclude?** |

The three `include?` rows sit above the line because their edges, though learned rather
than computed by a named estimator, are still functions of the recorded data. That is
the distinction the rule turns on, and it is the same distinction the leakage taxonomy
needs: if edges are learned from data, they can leak; if edges are geometry, they cannot.

## If the advisor rules the other way

Including both would take the corpus from 12 to 14 and would require:
- a sentence in Section IV-B defining what counted as a connectivity measure;
- `n/a` rather than `unclear` for L2/L3 on geometric-graph studies, so they do not
  inflate the "insufficient reporting" proportion in RQ1;
- the independence caveat in `FLAG_R089_R092_overlap.md` applied before both are
  counted.
