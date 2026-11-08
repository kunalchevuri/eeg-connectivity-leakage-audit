# Full texts still needed

**Updated 2026-09-23 after screening R001, R082, R086, R089, R092.**

**Corpus: 12 included. Blueprint exit condition is ≥15. You need 3 more.**

31 records are still pending full text: 7 free, 24 paywalled.

## 1. The 7 free ones — do these first (no login)

Save into `03_Phase3_Corpus/fulltexts/` using the exact `save_as` name in
`DOWNLOAD_THESE_12_FREE.csv`, which also carries the links and per-paper notes.

| rank | save as | why it's worth getting |
|---|---|---|
| 85 | `R085_Song_2026.pdf` | likely include — microstate functional connectivity |
| 55 | `R055_Baths_2021.pdf` | likely — correlation matrices + RNN; check the classifier is deep learning |
| 9 | `R009_Cong_2020.pdf` | maybe — FC present; check the classifier is deep learning |
| 50 | `R050_Liu_2024.pdf` | maybe — check depression is a target class |
| 77 | `R077_Yasin_2025.pdf` | maybe — relapse prediction, not MDD vs HC |
| 74 | `R074_Wang_2025.pdf` | maybe — unipolar vs bipolar, not depression vs control |
| 52 | `R052_Haufe_2022.pdf` | probably exclude — grab last |

**Realistic expectation: these 7 yield roughly 2–4 includes.** That may just reach 15,
or leave you 1 short. Two of the last five free papers I predicted as "very likely
include" turned out to fail criterion 2 once I read the methods, so treat the verdicts
above as leads, not counts.

## 2. Then paywalled, highest-yield first

Full links in `fulltexts_TO_DOWNLOAD.csv`. These 24 are pending:

> 5, 10, 27, 33, 36, 42, 48, 57, 58, 59, 61, 65, 66, 68, 71, 72, 73, 79, 87, 88, 93, 96, 98, 100

Best bets by title — all describe a connectivity step feeding a deep model:

| rank | short title | publisher |
|---|---|---|
| 10 | EEG depression recognition using improved graph CNN | Elsevier |
| 87 | Depressive disorders recognition by FC using GCN on EEG microstates | IEEE |
| 88 | Brain module-based weighted hypergraph convolutional network | Elsevier |
| 98 | STGE-Former: spatial-temporal graph-enhanced transformer | IEEE |
| 100 | Spatial-temporal GNN for MDD detection | IEEE |
| 66 | ACM-GNN: adaptive cluster-oriented modularity GNN | IEEE |
| 36 | EEG depression recognition combining functional brain network | IEEE |
| 48 | Directed brain network analysis, source reconstruction + graph theory | Elsevier |

George Mason library access covers IEEE Xplore (confirmed 2026-09-24). It does **not** cover every Elsevier journal — Computers in Biology and Medicine is not subscribed — so use GMU interlibrary loan for those.

## 3. If you still fall short of 15

Blueprint §7.1: *"If fewer than 15 survive, run one supplementary search in IEEE Xplore
and PubMed and add what qualifies."* That is the sanctioned fallback — it is not a
deviation, and it is already flagged in `prisma_counts.csv`. Tell me and I'll build the
supplementary search.

## Stop rule (WITHDRAWN 2026-09-24)

**This rule is not in the blueprint and should not have been proposed.** It left 23 screened-in reports unassessed. See deviations log #14 and advisor question 22; the current retrieval list is `RETRIEVAL_OPTIONS_2026-09-24.csv`.

~~Once included ≥ 15, stop downloading and move to Phase 4 coding.~~
