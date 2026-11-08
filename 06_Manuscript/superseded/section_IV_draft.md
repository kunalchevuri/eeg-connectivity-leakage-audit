# Section IV — Methods (DRAFT, AI-written; Kunal and advisor to edit)

Budget (MLESP recompute): IV-A 270 · IV-B 270 · IV-C 320 · IV-D 270 = 1,135 words.

Markers used below:
- `[PENDING Qn]` — wording depends on the advisor's answer to question n in `08_Admin/advisor_questions.md`.
- `[N]`, `[k]` etc. — numbers that must be pasted in from `03_Phase3_Corpus/prisma_counts.csv` or the analysis output, never typed by hand.
- `[CITE: …]` — a reference Kunal must find, open and log in `07_References/reference_verification_log.csv` (blueprint §12). No reference has been inserted.

---

## IV-A. Search and screening

The starting corpus was the 100 most-cited articles returned by a Web of Science search [PENDING Q11: query string, search date, and total hits — 321 per the cohort's records — must be recovered or stated as unavailable]. Records were screened in two stages, title and abstract followed by full text, against six inclusion criteria, all of which had to hold: (1) EEG is the primary modality; (2) a functional or effective connectivity measure is computed — coherence, PLV, PLI, correlation, Granger causality, mutual information, or a graph derived from one; (3) a deep learning model is applied to those connectivity features; (4) the study performs classification or severity prediction for depression or MDD; (5) at least one quantitative performance metric is reported; and (6) the work is peer-reviewed, in English, and published in 2015 or later. Reviews, surveys, unreviewed preprints, studies using only raw signal or spectral power without a connectivity step, and studies using only classical machine learning were excluded. [PENDING Q14: add one sentence stating that criterion 2 requires at least one edge weight to depend on the recorded signals, if the advisor adopts that rule.]

Because fewer than 15 of the 100 records survived full-text screening, we ran one supplementary search, as the protocol specifies, in [PENDING: OpenAlex and PubMed as run; IEEE Xplore to be added if run manually] on [date]. [PENDING Q13: one sentence on how candidates the search identified but that could not be retrieved were handled.] Counts and exclusion reasons at each stage are shown in Fig. 1. [N] studies were included.

*(≈250 words)*

---

## IV-B. Extraction fields

For each included study we completed a fixed coding sheet whose columns were defined before any study was coded and not changed afterwards. Descriptive fields recorded the citation and DOI; the dataset used (MODMA, PRED+CT, the Mumtaz resting-state dataset, a private cohort, or other); total, MDD and control sample sizes; the connectivity measure; the frequency bands analysed; and the architecture family (CNN, LSTM, CNN-LSTM, GCN, GAT, transformer, or other).

Pipeline fields recorded whether recordings were segmented into epochs and, if so, how many epochs each subject contributed; the partitioning unit (subject, epoch, or unclear); and the validation strategy (holdout, k-fold, leave-one-subject-out, external, or unclear). Four further fields recorded, for each of leakage surfaces L2 to L5, whether the corresponding step — connectivity estimation, thresholding, normalization, and channel or band selection — was stated to be fit within the training fold, fit on the whole dataset, not performed, or unclear.

Performance fields recorded reported accuracy and any other reported metrics. Where a study reported more than one accuracy, [PENDING Q16: state the rule — provisionally, the figure given in the abstract, with other reported protocols recorded alongside].

Every leakage-relevant field carries an evidence quote: the sentence from the paper on which the coding rests. A field with no supporting sentence was coded unclear. Coding drew only on the published text: authors were not contacted, and code repositories were consulted only where the paper itself directed the reader to them.

*(≈270 words)*

---

## IV-C. Rating scheme and decision rules

Each study received one of four leakage-risk ratings, applied from reported methods alone:

- **Leakage-free** — partitioning is stated to be at subject level, and connectivity estimation, thresholding and normalization are each stated to be confined to the training fold or not performed.
- **Leakage-possible** — subject-level partitioning is stated, but at least one of L2 to L5 is not clearly described as within-fold.
- **Leakage-likely** — partitioning is at epoch level, or a preprocessing step is explicitly described as applied to the full dataset before partitioning.
- **Unclear** — the partitioning unit is not stated.

Unclear is treated as a category in its own right rather than as missing data, because its prevalence is itself a result for RQ1.

Raters did not assign the rating directly. They coded the partitioning unit and the four surface fields, and the rating was derived from those fields by a fixed rule implemented in code, so that both raters' ratings follow from the same decision logic. Where the rules overlap, [PENDING Q5 and Q6: state precedence — as implemented, leakage-likely takes precedence over leakage-possible, and L5 is not required for leakage-free, matching the protocol's wording].

Two interpretive conventions were fixed before coding and given to both raters in identical written instructions. A threshold applied to each matrix using only that matrix's own values, and normalization computed within each segment, were coded as within-fold, since neither draws on other samples; batch-normalization layers inside a network were not treated as a preprocessing step. [PENDING Q17: confirm both conventions.] Where a decision would have required extended reasoning, the field was coded unclear.

*(≈290 words)*

---

## IV-D. Rater procedure and analysis plan

Two raters coded every included study independently, without discussion, working from identical written instructions. Percentage agreement and Cohen's κ on the four-level rating were computed before any disagreement was discussed [PENDING Q7: "unweighted", since the categories are not ordinal]. Disagreements were then resolved with a third, senior researcher as tiebreaker [PENDING Q18: name the role once authorship is settled; keep it anonymous for double-blind review]; both pre- and post-resolution ratings are reported. A κ below 0.4 was pre-specified as indicating that the scheme is too subjective to use as defined.

The analysis was specified, and its code written, before accuracies were examined. RQ1, RQ2 and RQ4 are descriptive, and no confirmatory hypothesis test is performed for them. For RQ1 we report the proportion of studies in each reporting category, overall and for each leakage surface, with Wilson 95% confidence intervals. For RQ2 we report percentage agreement and κ, with a 95% confidence interval from 10,000 bootstrap resamples of studies.

RQ3 is the only confirmatory analysis. We report median accuracy and interquartile range for each rating stratum and compare the leakage-likely and leakage-free strata with a two-sided Mann-Whitney U test, and all strata with a Kruskal-Wallis test. Each test is accompanied by Cliff's δ with a 10,000-resample bootstrap confidence interval. The smallest effect of interest was set in advance at 3 percentage points of median accuracy; a smaller difference is reported as a null result, and no subgroup was searched for an effect. Because small datasets may both favour weaker partitioning and yield higher accuracy, accuracy by rating is also reported stratified by sample-size tercile. All resampling used a fixed seed [CODE: 20260923] so that every reported value can be regenerated from the coding sheet.

*(≈280 words)*
