# Flag: near-identical methods and results in two separately-authored papers (R089, R092)

**Status:** observation for KC and Dr. Aledhari. Not a finding, not an allegation.
**Raised:** 2026-09-23, during full-text screening.
**Bearing on the paper:** none at present — both are provisionally excluded under
criterion 2 (see `FLAG_criterion2_spatial_adjacency.md`). It matters only if either is
later included, because the two could not then be treated as independent observations.

## The two records

| | R089 | R092 |
|---|---|---|
| Title | A Novel EEG-Based Hypergraph Convolution Network for Depression Detection | A noval 4D graph temporal brain network model for EEG-based depression detection |
| Authors | Sudipta Priyadarshinee, Madhumita Panda | Priyanka Gautam, Nisha Chaurasia |
| Affiliation | Gangadhar Meher University, Sambalpur, Odisha | Dr B R Ambedkar NIT Jalandhar, Punjab |
| Venue | IEEE Access 13 (2025) 185771–185789 | Health Inf Sci Syst 14:68 (2026) |
| DOI | 10.1109/ACCESS.2025.3614269 | 10.1007/s13755-026-00463-w |

The author sets and institutions are disjoint. No shared author.

## Values that coincide

Every row below was read directly from the two PDFs in `fulltexts/`.

| Item | R089 | R092 |
|---|---|---|
| Dataset | OpenNeuro ds003478 v1.1.0 | OpenNeuro ds003478 v1.1.0 |
| Subjects | 42 (22 MDD / 20 HC) | 42 (22 MDD / 20 HC) |
| Run selection | run-02 only, "higher quality and reduced noise" | run-02 only, "higher quality and reduced noise" |
| Channels | 16: Fp1 Fp2 F3 F4 C3 C4 P3 P4 O1 O2 F7 F8 T3 T4 T5 T6 | identical list, identical order |
| Recording length | 184.092 s | 184.092 s |
| Resampling | 500 → 200 Hz | 500 → 200 Hz |
| ICA | 16 components, 14 retained | 14 components |
| Window / stride | 6000 samples / 3000 overlap | 6000 samples / 3000 overlap |
| Segments | 490 (232 MDD, 248 HC) | 490 (232 MDD, 248 HC) |
| Node features | 8: mean, LZC, HFD, DFA + band powers | 8: mean, LZC, HFD, DFA + band powers |
| Adjacency | KNN on Euclidean distance between electrode 3D coordinates | same construction |
| Optimal K | 4 | 4 |
| K sweep accuracy | 76.8 / 83.67 / 80.4 / 79.5 / 75.6 at K = 2/4/6/8/10 | same curve, same peak (Fig. 9) |
| Hidden dim | 64 optimal | 64 optimal |
| Batch / dropout / loss | 40 / 0.7 / BCEWithLogitsLoss | 40 / 0.7 / BCEWithLogitsLoss |
| Hardware | Nvidia Tesla T4, 15 GB VRAM, 51 GB RAM, Colab Pro | identical sentence |
| Backbone | GCGRU (graph convolution + GRU) | GCGRU (graph convolution + GRU) |
| Adjacency figure | Fig. 3(a), titled "Adjacency Matrix for sub-001_run-02_signal" | Fig. 5(a), same title, same appearance |
| Headline accuracy | 83% | 83.67% |
| Proposed-model AUC | 0.88 | 0.88 |

Both papers also carry the **same arithmetic slip**: 232 + 248 = 480, not the 490
segments each reports.

## Where they differ

- R089 adds a subject–subject hypergraph (HGCN) and masked relational learning (MRL).
- R092 adds channel-wise Graph Temporal Max Pooling (GTMP) and a subject-level
  aggregation giving a second accuracy of 88.10%.
- Hidden-dimension sweeps are close but not identical
  (R089: 69.00/84.00/75.51/74.49/73.47; R092: 68.49/83.5/74/75/72).

So they are not the same paper — but the shared substrate (identical preprocessing,
identical segment counts, identical hyperparameter sweeps, identical hardware sentence,
apparently the same adjacency figure) goes well beyond what reuse of a public dataset
explains on its own.

## What to do with it

1. **No action needed now.** Both sit at `exclude?` on criterion 2, so neither enters N.
2. **If either is later included**, do not count both as independent observations —
   raise with Dr. Aledhari first (advisor question 15).
3. **Do not name either study in the manuscript.** The blueprint's standing rule —
   never name an individual study as an example — covers this, and this observation is
   about provenance rather than leakage, so it is outside the paper's scope entirely.
4. Anything said about this outside the project team should wait for the advisor.
