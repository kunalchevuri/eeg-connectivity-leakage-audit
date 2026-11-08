# Revision notes — pre-submission review of 2026-09-27

Scope: writing, structure, and compliance changes only. **No number, rating, code, or analysis was changed.** Every number in the paper is still a generated macro from `macros_counts.tex`.
All new or rewritten text is AI-drafted (Claude, Anthropic, 2026-09-27) and must go through the Human Authorship Pass. **[Corrected 2026-09-27]** There was no such section below; the pass is recorded in `08_Admin/human_authorship_pass.md`. It is covered by the revised Acknowledgment.

## How to build

```
cd 06_Manuscript
export BSTINPUTS=template/IEEEtran/bibtex:        # needed if IEEEtran.bst is not on your TeX path
pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper
python tools/preflight.py
```

There are two builds.

| File | Switch | Pages | Purpose |
|---|---|---|---|
| `paper.pdf` | `\decisionsacceptedfalse` | 9 | Review build. All 10 advisor-dependent notes print, so preflight fails by design. |
| `paper_layoutcheck.pdf` | `\decisionsacceptedtrue` | **8 (full; a few lines spare once the 3 UNVERIFIED notes go)** | Shows the paper fits once the defaults below are accepted. |

**[Corrected 2026-09-27]** The Decisions table was signed off on 2026-09-27, and `paper.tex` now sets `\decisionsacceptedtrue`. There is one build, `paper.pdf`: 8 pages, 0 LaTeX errors, preflight with zero FAIL lines. `paper_layoutcheck.pdf` is not in the repository.

To submit, set `\decisionsacceptedtrue` in `paper.tex`, and only after the Decisions table is signed off. Then fill the `[AUTHOR: ...]` field, remove the three `UNVERIFIED` notes after opening those papers, rebuild, and run preflight. Removing the notes frees 2–3 reference lines. Filling in the model version adds about one line. **Re-check that the page count is still 8.**

## Decisions the switch commits you to (advisor or authors must accept in writing)

| Marker | Default already written into the text | If rejected |
|---|---|---|
| Q22 (IV-A, VII) | Corpus closed at 18; the 24 unassessed WoS reports and 11 unretrieved supplementary reports are disclosed as a limitation | Options (a) or (b) cannot be done tonight; move to DL4BBDA |
| Q20 (IV-B) | Primary RQ3 uses binary depression-vs-control tasks only; all tasks go to sensitivity analysis | Flip `advisor_rulings.json`, rerun `run_pipeline.py`, re-read "% RECHECK" sentences |
| Q21 (V-D) | Report all four sensitivity analyses (S1–S4) | Delete the sentences for those not approved |
| S05 (IV-B, V-C) | Kept on the protocol both raters coded, with the matching accuracy | Recode S05; rerun |
| S11 (V-C) | Rater A's code stands as the tiebreak placeholder | Enter the advisor's tiebreak; rerun; re-read RECHECK sentences |
| Q11 (IV-A, VII) | The query is described as not recoverable (a limitation) | Insert the query string and date if the poster team supplies them |
| "confirm after reading each review" (II-B) | No cited review examines the pre-split connectivity pipeline | **Check Luna-Guevara 2026 in full; it uses QUADAS-2 and discusses feature selection.** If it covers L5, narrow the sentence to L2–L4 |

## Change log

| ID | File | Change | Linked finding |
|---|---|---|---|
| C1 | paper.tex (abstract) | Rewritten: states the main finding (no whole-dataset L2–L4 step reported; risk at L1 and L5), removes the 98.7% vs 88.9% headline that rested on 2 studies, and adds κ and the L5 figure | Claims vs. evidence; mock reviews R1–R3 |
| C2 | section_I_body.tex | RQ1–RQ4 stated (they were used but never defined) | Structure audit |
| C3 | section_II_body.tex, section_III_body.tex, references.bib | Added design precedents for rating leakage from reported methods (wen2020, young2025) and contemporaneous MDD-cohort evidence for L1 (sahuc2026). Cut the Yagis random-label clause to offset length | Landscape: missing closest work |
| C4 | section_V_body.tex, section_VII_body.tex | RQ4 result moved from Discussion to Results; the Discussion now only points to it | No new result in the Discussion |
| C5 | section_VIII_body.tex | Conclusion aligned with the new abstract | Consistency |
| C6 | paper.tex (Acknowledgment) | Rewritten to the IEEE AI-content policy: names the systems, the sections, and the level of use. Added an author field for the model version. **[Corrected 2026-09-27]** The section was lost when the Overleaf copy was set up. It was restored with the model line and four corrections, and the advisor approved it on 2026-09-27 | IEEE policy; integrity |
| C7 | references.bib, 07_References/build_bib.py | Fixed jia2025's empty author and zhang2025's "&amp;"; the builder now skips empty author records and unescapes HTML. Three new entries carry UNVERIFIED notes | Reference audit |
| C8 | paper.tex | `\decisionsaccepted` switch and `\AUTHORINPUT` macro | Deadline workflow |
| C9 | section_V_body.tex | RQ3: states that the leakage-free median is the midpoint of two accuracies | Statistics review |
| C10 | IV, V, VI, VII, II, I, III | Space: measure counts deferred to Table I; checklist, geometric-graph, and duplicated protocol sentences condensed; PLI and binarization equations inlined; screening flow (now Fig. 2) at 0.86 column width; pipeline (now Fig. 1) at 0.88 text width **[Corrected 2026-09-27]** (was: "Fig. 1 at 0.86 column width; Fig. 2 at 0.94 text width"); two redundant Discussion sentences removed | 9 → 8 pages |

The redline is in `manuscript_changes.diff`, and every edited spot carries a `% REVIEW 2026-09-27 (Cn)` comment. **[Corrected 2026-09-27]** Three of these comments sat mid-line and hid the sentences after them: in V-C, the tiebreak sentence and rating distribution; in VII, the E4 limitation; and in IV-B, "Coding drew only on the published text". All three were restored. Every comment now sits on its own line.

**Not changed (author or advisor call):**
- Contribution list wording (blueprint-fixed)
- Title
- Table I per-study ratings (advisor ruling Q9)
- Figure content

## Must be verified by an author before submission

1. **young2025** (doi 10.3390/diagnostics15182348). Confirm it supports "three leakage-risk tiers, 44 studies, accuracy highest where risk highest."
2. **sahuc2026** (doi 10.5281/zenodo.20630665). Confirm the depression cohort is included and that inflation from shared subjects is shown for it.
3. **wen2020** (Medical Image Analysis 63:101694). Metadata is from memory: check the authors, volume, and pages, and confirm it labels leakage per surveyed study.
4. **racz2026.** I could only find the medRxiv preprint (10.64898/2025.12.04.25341680). Confirm the Translational Psychiatry DOI resolves, and add volume and article number, or cite the preprint.
5. `07_References/reference_verification_log.csv` still shows R27–R35 as "n", while the AI log says the author opened them. Update the CSV so it matches the Acknowledgment's claim.
6. Fill in the model and version in the Acknowledgment from `08_Admin/ai_use_log.md`.

## Entry to append to 08_Admin/ai_use_log.md

| 2026-09-27 | Claude (claude.ai) | Pre-submission review of the repository zip; recompiled (found 9 pages and 10 PENDING markers); web checks of the IEEE AI policy, Luna-Guevara 2026, Racz 2026 (preprint only), and new closest work (Young 2025, Sahuc 2026, Kunjan 2021). Revised manuscript changes C1–C10 (abstract, RQ paragraph, Acknowledgment, three added references, RQ4 moved, space cuts), builder patch | No number, rating, or analysis changed; builds 8 pages with defaults accepted, 0 LaTeX errors | Authors: authorship pass on all new text; open the three new references; advisor accepts the Decisions table |

## Round 2 (2026-09-27): figures, captions, core-idea figure, IEEE format

### Files changed, all rounds

Every hand-written LaTeX file was edited: `paper.tex`, `section_I`, `II`, `III`, `IV`, `V`, `VII`, `VIII`, `table_II_body.tex`, and `references.bib`.

Generated files:
- `table_I_body.tex` was changed through `build_table1.py`. It regenerates byte-identical from the coding sheet.
- `macros_counts.tex` was not changed. No number changed.

Scripts:
- `figures/ieee_style.py` is new.
- All four `make_fig*.py` scripts and `07_References/build_bib.py` were updated.

### Figures (F1–F4)

**All figures**
- Every figure is now set in a Times-metric serif (Liberation Serif), matching the IEEEtran body text; the earlier builds used DejaVu Sans/Serif. **[Corrected 2026-09-27]** Superseded by Round 3: `figures/ieee_style.py` uses Liberation Sans and Liberation Mono.
- Fonts are embedded as TrueType, which IEEE PDF eXpress accepts.
- Each figure is sized so text prints at about 7–8 pt.
- Colors differ in luminance, so every category reads in grayscale.
- Every figure is still generated from the coding sheet or PRISMA counts.

**Per figure**

| Figure | What changed |
|---|---|
| F3, reporting completeness (now Fig. 3) | Every segment is labeled with count and percentage; narrow segments are labeled outside the bar. Surfaces are named on the y-axis, the x-axis reads "Studies (%), n = 18", and the legend sits above the plot. |
| F4, accuracy by rating (now Fig. 4) | The x-axis is titled "Leakage-risk rating from reported methods", and each tick shows n and the median. Individual values are printed for strata with three or fewer studies. The IQR bar appears where n ≥ 4. The legend gives the tercile subject ranges. |
| F1/F2, PRISMA and pipeline | Font only; the layout is unchanged. **[Corrected 2026-09-27]** Superseded by Round 3, which redrew both. |

### Captions and text (E1–E5)

| ID | Change |
|---|---|
| E1 | The pipeline and leakage-surface figure moved into Section I-B and is cited there. It is now **Fig. 1**, at the top of page 2, and serves as the paper's core-idea figure. The PRISMA figure becomes Fig. 2. All references are `\ref`-based, so numbering updated automatically. |
| E2 | Captions updated for Figs. 3–4 to describe the new labels, n, median, and IQR. "Gen." is defined in the Table II caption. The Table I caption now says "the Study column gives the reference number", replacing "ID links to the full reference". |
| E3 | Methods now states the coding rule for silent steps, taken from `QUICK_GUIDE_both_raters.txt`: an unmentioned threshold, rescaling, or selection was coded not performed; a step mentioned without saying which data it was fit on was coded unclear. |
| E4 | AI-drafted screening is now stated as a limitation in Section VII. |
| E5 | Availability sentence added. It carries an `[AUTHOR: ...]` field: give an anonymized repository link, for example anonymous.4open.science, or keep "released on acceptance". **[Corrected 2026-09-27]** Filled: "released on acceptance". |
| C10b | The per-surface Results sentences were condensed, because Fig. 3 now prints every count. |
| Abstract | "κ" replaced by "kappa", because IEEE Xplore abstracts should avoid special symbols. **Paste the abstract into CyberChair as plain text.** |

### IEEE format audit (layout build)

| Check | Result |
|---|---|
| Class | IEEEtran `[conference]`, letter paper, 612 × 792 pt |
| Pages | 8 (with defaults accepted) |
| Fonts | All fonts embedded and subset (body Type 1 Nimbus Roman; math Computer Modern; figures TrueType Liberation Serif). No Type 3. **[Corrected 2026-09-27]** Figures use Liberation Sans/Mono (Round 3). Figs. 1–2 were regenerated in Round 5 on a machine without Liberation fonts, so they use the metric-equivalent Arial and DejaVu Sans Mono. All fonts are embedded; there are no Type 3 fonts. |
| Text block | x = 49–563 pt, y = 51–719 pt, within the template margins |
| Running headers or page numbers | None (correct for submission) |
| Overfull boxes | None; a few harmless underfull boxes |
| Section headings, "Index Terms", and caption styles | IEEEtran defaults (tables captioned above, figures below) |
| References | IEEEtran.bst |

**Optional polish:** use IEEE journal-name abbreviations (IEEEabrv.bib). This is not required for the workshop.

**Still to do:** run the final PDF through IEEE PDF eXpress if the camera-ready instructions require it (usually at camera-ready, not at submission).

### Title options (authors decide)

The results locate the detectable risk at the split (L1) and at selection (L5), not in connectivity construction. "Before the Split" is memorable, but it slightly oversells the connectivity-specific finding.

| # | Title | Note |
|---|---|---|
| 1 | Before the Split: Auditing Data Leakage and Reporting Gaps in EEG Connectivity Deep Learning for Depression Detection | Keeps the brand, adds the actual finding |
| 2 | Split by Subject, Report the Pipeline: A Leakage Audit of EEG Connectivity Deep Learning for Depression | Memorable, and states the two recommendations |
| 3 | Can We Trust 99%? A Leakage Audit of EEG Connectivity Deep Learning for Depression Detection | Catchy; risks sounding accusatory toward named studies |
| 4 | Where Test Data Leaks In: Auditing EEG Connectivity Pipelines for Depression Detection | Short; keeps the connectivity angle |

**Recommendation:** option 1 (least risky), or option 2 (most memorable and accurate).

## Round 3 (2026-09-27): all four figures redrawn after figures4papers and diagram-design

Sources studied (cloned 2026-09-27):
- `github.com/ChenLiu-1996/figures4papers`: the `scientific-figure-making` skill (api.md, design-theory.md, common-patterns.md) and the `figure_Brainteaser` scripts.
- `github.com/cathrynlavery/diagram-design`: `skills/diagram-design` (SKILL.md taste gate, style-guide.md, type-flowchart.md).

No code or assets were copied. The design rules were re-implemented in `figures/ieee_style.py`.

### What was adopted from each repository

| From | Rule | Where |
|---|---|---|
| figures4papers | Semantic palette (blue = key/safe, greens = positive, reds = risk/contrast, neutral = background) | All figures |
| figures4papers | Top/right spines off, frameless legends, ink edges on bars | Figs. 3–4 |
| figures4papers | Values printed in place | Fig. 3 counts and %; Fig. 4 medians and small-stratum values |
| figures4papers | Tightened y-range (75–101%) | Fig. 4 |
| figures4papers | Hatching for print-safe separation | "Not reported" (dots) in Fig. 3; the epoch partition in Fig. 1 |
| diagram-design | One accent reserved for focal elements | Red marks only the leakage points (Fig. 1) and the retrieval gap (Fig. 2) |
| diagram-design | Secondary "link" blue for the leakage-free path and the final corpus | Figs. 1–2 |
| diagram-design | Semantic node roles (backend, focal, external, dashed limitation) instead of decoration | Figs. 1–2 |
| diagram-design | Mono uppercase eyebrow labels | Stage labels, split labels, L1–L5 pills |
| diagram-design | Labels never on connectors; straight connectors on a shared axis | Figs. 1–2 |
| diagram-design | Key as a strip below a hairline; density about 4/10; no shadows | Fig. 1 |

### Adaptations for IEEE print

- **Page and fonts:** pure white paper instead of the web skin's white-smoke. Liberation Sans (Arial/Helvetica metrics) and Liberation Mono replace Geist and Instrument Serif, which are not installed here; they are embedded as TrueType.
- **Text size:** 7–8 pt at the size LaTeX places each figure. **[Corrected 2026-09-27]** At the placed widths (0.86 and 0.88), the smallest labels in Figs. 1–2 printed at about 5–5.5 pt. Round 5 raised them.
- **Grayscale:** every category also differs in luminance. Checked by converting the figures to grayscale.

### Figure-by-figure

| Paper figure | File | Change |
|---|---|---|
| Fig. 1, pipeline | `make_fig2_pipeline.py` | Redrawn as a two-lane diagram. Blue marks the focal partition in (a). Red boxes with L-pills mark the leakage points in (b), and the epoch partition is hatched. Brackets show "fit on training fold only" versus "computed on train + test before the split". Key strip measured by the renderer. The figure is 0.25 in shorter than before. |
| Fig. 2, screening flow | `make_fig1_prisma.py` | PRISMA stage eyebrows (Ident., Screening, Included). Exclusions are muted "external" boxes. "Not retrieved, n = 24 (retrieval stopped early)" is a dashed red box. The final corpus is a blue focal box. All counts are still read from `prisma_counts.json`. |
| Fig. 3, reporting completeness | `make_fig3_rq1.py` | Green = training data only, red = held-out data used, light gray = not performed, dotted white = not reported. Counts and % in every segment. |
| Fig. 4, accuracy by rating | `make_fig4_rq3.py` | Points filled by rating color (green free, blue possible, red likely, gray unclear) on faint rating bands. Marker shape = tercile. Medians shown as ink bars and printed under each rating. |

### Captions and paper

- Captions for Figs. 1, 2 and 4 were updated to describe the new encodings.
- **Layout build:** 8 pages, about 3 lines spare on the last page. Preflight fails only on the 3 intended UNVERIFIED notes and the 2 AUTHOR fields. **[Corrected 2026-09-27]** The Overleaf copy had about 20 lines spare, because the Acknowledgment was missing. For the final state, see Round 5.

## Round 4 (2026-09-27): title

The title is changed in `paper.tex` to the authors' choice, with no colon and not starting with "Before".

**New title:** Auditing Data Leakage and Reporting Gaps in EEG Connectivity Deep Learning for Depression Detection

**Was:** Before the Split: Auditing Connectivity-Pipeline Leakage in Deep Learning for EEG-Based Depression Detection

- Enter the new title in CyberChair exactly as above.
- The Round 2 title-options table is superseded.
- Nothing else in the paper refers to "Before the Split".

## Round 5 (2026-09-27, KC): decisions applied and notes corrected to match the files

These were applied per the advisor's email of 2026-09-27, 14:03.

**Decisions**
- Every Decisions-table default was accepted.
- S11: rater A's code stands (tiebreak ruling). S05: as in the defaults table. Both are recorded in `08_Admin/deviations_log.md`, rows 25–26.

**Acknowledgment**
- Restored and approved. It names the model as "Claude (Anthropic; Claude Code and claude.ai, with Opus 5, Opus 5.5 and Sonnet 5)".
- To make room, two cuts were made:
  - P1: the Section VI item-to-surface sentence.
  - P2: the Section VII "connectivity label" paragraph.

**Text changes**
- The three hidden sentences are restored. No text in any `.tex` file follows a `%` comment on the same line.
- Sahuc 2026: two Mumtaz MDD cohorts. Evidence-quote sentence: one quote per study per rater. RQ4 rho now prints a true minus sign.
- Flags a–e:
  - RQ4: "an imprecise estimate".
  - RQ3: the two leakage-free values are given. They come from the new macro `\AccFreeValues`, generated in `build_results.py`.
  - VII: the sentence on coding unmentioned steps.
  - Figure text: Fig. 2 box text is 8 pt and its stage labels 7 pt. Fig. 1 eyebrow and pill text is 7 pt. Nothing overflows its box.
  - Introduction and abstract wording. The portal text is `PORTAL_title_abstract_plaintext.txt`.
- Availability: "released on acceptance".

**References**
- Racz & Csukly is cited as Translational Psychiatry, in press, with its DOI.
- KC opened young2025, sahuc2026 and wen2020. The UNVERIFIED notes are removed, and the verification log has rows R27–R38.
- Luna-Guevara does not cover selection before partitioning, so II-B is unchanged.

**Page fit**
- The approved additions made the paper one line over 8 pages. The larger figure fonts were not the cause, because both diagrams are fixed-size, so reducing them could not help.
- Instead, the references follow IEEE style for more than six authors (first author + et al.), through IEEEtran.bst's control entry. No text was cut.
- Result: 8 pages, 0 LaTeX errors, all fonts embedded, no author metadata, preflight with zero FAIL lines.

---

# Camera-ready pass of 2026-11-07 (MLESP 2026, paper S02212)

Accepted 2026-10-25: one Accept (R2), one Weak Reject (R1). Camera-ready and registration both due
**Nov 8, 2026**. No second review, so reviewer comments are advisory.

Official requirements, read from the portal and recorded in `08_Admin/camera_ready_requirements.md`
(the conference website has no camera-ready page). Eight steps, all at
`wi-lab.com/cyberchair/2026/bibm26/scripts/final.php?subarea=S02`: eCopyright form, IEEE PDF eXpress,
PDF upload, registration receipt, and an in-person declaration.

## Build

```
cd 06_Manuscript
python ../05_Phase5_Analysis/reviewer_response.py     # once, after run_pipeline.py
python make_macros.py
pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper
python tools/preflight.py paper.pdf --camera-ready --max-pages 9
```

`--camera-ready` inverts the anonymity checks (author names must now be PRESENT), and adds the two IEEE PDF
eXpress checks: every font embedded and subset, page size US Letter 612x792 pt. Both pass.

**State: 9 pages, 0 LaTeX errors.** Preflight leaves exactly two FAILs, both of which are Kunal's:

1. `UNVERIFIED` x2 - open the TRIPOD+AI and CLAIM originals and remove the notes from `references.bib`.
2. `AUTHOR:` x5 - three author emails, the repository URL and the Zenodo DOI.

## The page count: resolved at 8, nothing purchased

**Final state: 8 pages, 0 LaTeX errors, within the limit. No extra pages were bought.**

The decision was made on 2026-11-07: no purchase. Dr. Aledhari had written on 2026-11-04 that UNT would not
release his faculty travel fund for the registration because he is not travelling, so spending $100 on pages
while the $800+ registration is unfunded made no sense.

Getting from 10 pages to 8 without losing the reviewer response, in the order the cuts were made:

1. Condensed Sections I, II, IV, VI, VII and VIII (blueprint Sec 9 cut priority). No citation or claim dropped.
2. Shrank Fig. 1 (0.88 -> 0.74 textwidth), Fig. 2 (0.86 -> 0.80 columnwidth), Fig. 3 (1.0 -> 0.95). Both the
   pipeline and the PRISMA figure were rendered and checked; still legible.
3. Removed **Fig. 4** (accuracy by rating) - the figure for a comparison the paper calls uninformative, which
   R2 (W2) asked to be demoted. Restorable in one line.
4. Shortened the reference author lists (`CTLmax_names_forced_etal` 6 -> 2). No reference removed.
5. Folded Author Contributions into the Acknowledgment; Index Terms 8 -> 5.
6. Removed the two new references (TRIPOD+AI, CLAIM), which were the last overflow. Both are now named in
   Section VI without a citation - which blueprint Sec 12 requires anyway, since no author had opened them.

**Sections III and V were not cut**, per blueprint Sec 9. The reviewer-response content all survived; only its
wording was compressed.

## Reviewer-response change log

| ID | Where | Change | Reviewer item |
|---|---|---|---|
| CR1 | V-C, IV-B, abstract, VII, VIII | Worst-case bound on the not-reported convention: leakage-free falls 3 -> **0**, leakage-likely unchanged at 10, epoch-level proportion unaffected | R1 1-3; R2 W6, Q4 |
| CR2 | V-C | Per-surface kappa with bootstrap CIs. L1 **0.91**, L3 0.87, L4 0.69, L5 **0.36**, L2 undefined (no variation) | R2 W4, Q3 |
| CR3 | V-A | Cluster bootstrap and one-per-cluster bounds over 5 datasets and 16 groups; epoch-level interval widens to 0-68% | R2 W8, Q6 |
| CR4 | V-B | RQ4 demoted to a hypothesis; permutation p = 0.031, Fisher exact p = 0.11. No Firth regression, with the reason stated | R2 W9 |
| CR5 | III-B | Explicit out-of-scope paragraph: ICA, ASR, re-referencing, interpolation, matrix normalization. Checklist described as necessary, not sufficient | R2 W5, Q5 |
| CR6 | VI | Relation to TRIPOD+AI, CLAIM and Brookshire et al., and what the checklist adds. Two new UNVERIFIED references | R2 W11, Q7 |
| CR7 | abstract, Fig. 2 caption, I-B, II-B | Citation-ranked caveat added to the abstract; flow diagram retitled PRISMA-style and marked as not a systematic review's; priority claim softened | R1 2; R2 W1, W12, Q1 |
| CR8 | abstract | Leads with the partitioning result | R2 W7 |
| CR9 | VII | Availability released now, not on acceptance; evidence quotes offered as the per-surface exemplars | R2 W13, W10, Q8 |
| CR10 | V-D | The 3-vs-2 leakage-free counts reconciled in the text (the third study is three-class). Fig. 3 cell counts re-derived against the text: consistent | R2 W14 |
| CR11 | paper.tex, VII | Author contribution statement names the two raters and the tiebreaker; the absence of an independent rater stated as a limitation | R2 W3 |
| CR12 | IV-D | The four new analyses declared post hoc and reviewer-requested | integrity |
| CR13 | I-A, II-A, II-B, II-C | Condensed for space. No citation or claim dropped | blueprint Sec 9 |
| CR14 | IV, V, VII | The nine resolved advisor `\PENDING` markers deleted from the source (all were ruled on before submission). The three inside `\IfFileExists` fallbacks for Table I and Figs. 3-4 are build safeguards and were kept | housekeeping |

## Not changed

- Every pre-specified result, every coded field, every rating.
- Table I, Table II's eight items (blueprint-fixed), the title, the contribution list.
- Fig. 1 content, Fig. 3 and Fig. 4 content. Fig. 1 scale only.
