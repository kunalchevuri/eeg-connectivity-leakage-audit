"""Pre-fill the DESCRIPTIVE columns of Kunal's completed rater sheet from objective_metadata_extracted.csv
(AI-extracted, ai_use_log.md). Writes a COPY; the original workbook is never modified.

Run only AFTER the rater's leakage columns are complete: descriptive fields do not enter kappa, but the
leakage columns must be the rater's own unaided work.

  - accuracy follows advisor rule (c) (Q16); accuracy_abstract (far right) holds the abstract figure.
  - Blue cells  = pre-filled by AI. KC must check each one against the PDF before it is used.
  - Orange cells = deliberately left blank; the cell comment says what KC must decide.
  - epoching, epochs_per_subject and split_strategy are never pre-filled (evaluation design; KC codes them).
  - Leakage columns, evidence_quote, rater and notes are not touched.

    python 04_Phase4_Coding/prefill_descriptive.py
"""
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.comments import Comment
from copy import copy

from openpyxl.styles import PatternFill

HERE = Path(__file__).parent
SRC = HERE / "rater_A_Kunal_2026-09-23_completed.xlsx"
OUT = HERE / "rater_A_Kunal_2026-09-23_completed_PREFILLED.xlsx"
BLUE = PatternFill("solid", fgColor="BDD7EE")
ORANGE = PatternFill("solid", fgColor="F8CBAD")
AUTHOR = "AI prefill"

# (value, note). value None = left blank for KC; the note says why. Accuracy = the ABSTRACT figure
# (coding rule), checked against each PDF's abstract on 2026-09-24.
Q = "advisor Q20 (which task/dataset) pending"
P = {
    "S01": dict(dataset=("Mumtaz", ""), n_subjects=(None, "Paper says 64 (Participants) and 63 (Discussion/Table 6). Decide which."),
                n_mdd=(None, "Paper says 34 (Participants) and 33 (Discussion/Table 6). Decide which."), n_control=(30, ""),
                connectivity_measure=(None, "GPDC + dDTF (MVAR effective connectivity). Granger or other? Your call."),
                frequency_bands=("delta, theta, alpha, beta1, beta2, beta3, beta, gamma", ""),
                architecture=("CNN-LSTM", "Best of five compared (1DCNN-LSTM) = the abstract model."),
                accuracy=(99.24, "Abstract. Table gives 99.245 +/- 1.152.")),
    "S02": dict(dataset=("private", "Own Lanzhou data, available on request."), n_subjects=(48, ""), n_mdd=(24, "Mild depression."),
                n_control=(24, ""), connectivity_measure=("coherence", "Four measures compared; coherence is the abstract model."),
                frequency_bands=("delta, theta, alpha, beta, gamma", ""), architecture=("CNN", ""), accuracy=(80.74, "Abstract.")),
    "S03": dict(dataset=("Mumtaz", ""), n_subjects=(57, "57 analysed (58 downloadable)."),
                n_mdd=(None, "30 MDD / 28 HC downloadable but 57 analysed; paper may not say which one was dropped."),
                n_control=(None, "See n_mdd."), connectivity_measure=("other", "Learned by multi-head self-attention."),
                frequency_bands=("full band 0.1-70 Hz; delta, theta, alpha, beta, gamma", ""),
                architecture=(None, "Self-attention + two-branch depthwise CNN. CNN, transformer or other? Your call."),
                accuracy=(91.06, "Abstract. Paper also reports a subject-dependent 98.45; (initial pass coded this protocol).")),
    "S04": dict(dataset=("Mumtaz", ""), n_subjects=(64, ""), n_mdd=(34, ""), n_control=(30, ""), connectivity_measure=("PLV", ""),
                frequency_bands=("delta, theta, alpha, beta, low gamma, high gamma", ""), architecture=("CNN", "Multilayer deep CNN (MDCNN)."),
                accuracy=(97.27, "Abstract.")),
    "S05": dict(dataset=("MODMA", ""), n_subjects=(53, ""), n_mdd=(24, ""), n_control=(29, ""), connectivity_measure=("PLI", ""),
                frequency_bands=("delta, theta, alpha, beta, gamma, full band", ""),
                architecture=("CNN-LSTM", "LSTM (temporal) + 2D-CNN on PLI (spatial), fused."),
                accuracy=(96.33, "Abstract ('highest of'). Paper reports tenfold AND LOSO; (initial pass coded this protocol).")),
    "S06": dict(dataset=(None, "Two datasets (PRED+CT and own). Which is primary? " + Q),
                n_subjects=(None, "63 (public) + 40 (own); depends on dataset choice."), n_mdd=(None, "33 / 18; depends on dataset choice."),
                n_control=(None, "30 / 22; depends on dataset choice."), connectivity_measure=("other", "Learnable channel-correlation + electrode-distance adjacency."),
                frequency_bands=("broadband", ""), architecture=(None, "GNN + GRU (GCGRU). GCN or other? Your call."),
                accuracy=(None, "Abstract gives AUROC only (83 / 99). Table: 77.78 public / 95.61 own. " + Q)),
    "S07": dict(dataset=(None, "Mumtaz, PRED+CT and combined. Which is primary? " + Q),
                n_subjects=(None, "99 combined (55 Mumtaz + 44 PRED+CT analysed); depends on dataset choice."),
                n_mdd=(None, "50 combined; depends on dataset choice."), n_control=(None, "49 combined; depends on dataset choice."),
                connectivity_measure=("other", "P-MSWC: fusion of PLV and wavelet coherence."),
                frequency_bands=("0.5-70 Hz (225 bins); delta, theta, alpha, beta, gamma", ""),
                architecture=("CNN", "Lightweight CNN, Inception + CBAM attention."),
                accuracy=(None, "Abstract says 99.92 / 97.86 but Tables 4-5 say 99.87 / 97.16 / 93.93. Which counts? " + Q)),
    "S08": dict(dataset=(None, "Three: MODMA, Mumtaz (MPHCE), EDR. Which is primary? " + Q), n_subjects=(None, "53 / 48 / 107."),
                n_mdd=(None, "24 / 23 / 40."), n_control=(None, "29 / 25 / 67."),
                connectivity_measure=(None, "PLV and PLI both used. Pick one or 'other'."),
                frequency_bands=("delta, theta, alpha, beta, gamma", ""), architecture=("GCN", "Multi-granularity GCN."),
                accuracy=(None, "No accuracy in abstract. Table III: 99.68 / 98.44 / 96.72. " + Q)),
    "S09": dict(dataset=("MODMA", "EEG + speech subsets."), n_subjects=(53, "EEG subset."), n_mdd=(24, "EEG subset."), n_control=(29, "EEG subset."),
                connectivity_measure=("correlation", "Pearson correlation of wavelet features -> adjacency."),
                frequency_bands=("n/a (DWT wavelet features)", ""),
                architecture=(None, "Multi-head-attention GCN + ViT. GCN, transformer or other? Your call."),
                accuracy=(89.03, "Abstract. NOTE: multimodal EEG + speech, not EEG alone (sensitivity analysis S3 drops this study).")),
    "S10": dict(dataset=("MODMA", "Also non-MDD datasets, not used here."), n_subjects=(53, ""), n_mdd=(24, ""), n_control=(29, ""),
                connectivity_measure=("correlation", ""), frequency_bands=("broadband 0.5-44 Hz", ""),
                architecture=(None, "Module tested with GCN, GraphSAGE and GAT. Which one? " + Q),
                accuracy=(None, "No MDD accuracy in abstract. Table 3: GCN 98.06 / GraphSAGE 98.50 / GAT 98.80. " + Q)),
    "S11": dict(dataset=(None, "Five datasets; depression classified in OpenNeuro ds003474 and an in-house DASS-21 set. Which one?"),
                n_subjects=(None, "122 (ds003474) or 29 (DASS-21 set); depends on dataset choice."),
                n_mdd=(None, "Not stated as a count."), n_control=(None, "Not stated as a count."),
                connectivity_measure=("correlation", "Static and time-resolved Pearson correlation."),
                frequency_bands=(None, "Not extracted; check the paper."), architecture=("LSTM", "RNN (LSTM)."),
                accuracy=(None, "Abstract gives a range (74-88%). Tables: 88.64 (ds003474), 34.75 (DASS-21). " + Q)),
    "S12": dict(dataset=("private", "Own auditory-oddball data."),
                n_subjects=(None, "67 total incl. 22 chronic-pain patients; 45 if only depression + HC. Depends on task (task_type.csv: multiclass). " + Q),
                n_mdd=(22, ""), n_control=(23, "HC only; 22 chronic-pain patients are a third group."), connectivity_measure=("PLI", ""),
                frequency_bands=("wide band, delta, theta, alpha, beta, gamma", ""), architecture=("CNN", ""),
                accuracy=(None, "Abstract: 79.64 (PLI, theta) and 85.01 (raw EEG, not connectivity). Multiclass task. " + Q)),
    "S13": dict(dataset=("PRED+CT", "OpenNeuro ds003478."), n_subjects=(120, "122 recruited, 2 excluded."), n_mdd=(46, "BDI >= 13."),
                n_control=(74, "BDI < 7."),
                connectivity_measure=(None, "PLV (graph metrics) AND Pearson correlation (GCN adjacency). Pick one or 'other'."),
                frequency_bands=("theta, alpha, beta, gamma", ""),
                architecture=(None, "Transformer -> GCN -> domain adaptation. GCN, transformer or other? Your call."),
                accuracy=(85.33, "Abstract.")),
    "S14": dict(dataset=("Mumtaz", ""), n_subjects=(64, ""), n_mdd=(34, ""), n_control=(30, ""),
                connectivity_measure=("other", "Normalized mutual information."),
                frequency_bands=("delta, theta, alpha, beta, gamma (final model: beta + gamma)", ""),
                architecture=("CNN", "Attention-mechanism CNN (AM-CNN)."), accuracy=(97.22, "Abstract.")),
    "S15": dict(dataset=(None, "Two: MODMA and PRED+CT. Which is primary? " + Q), n_subjects=(None, "53 / 119."), n_mdd=(None, "24 / 44."),
                n_control=(None, "29 / 75."), connectivity_measure=("correlation", ""),
                frequency_bands=("delta, theta, alpha, beta", ""), architecture=("GCN", ""),
                accuracy=(None, "Abstract gives both: 98.30 (MODMA) and 96.51 (PRED+CT). " + Q)),
    "S16": dict(dataset=("Mumtaz", ""), n_subjects=(64, ""), n_mdd=(34, ""), n_control=(30, ""),
                connectivity_measure=("other", "Adaptive learned global graph + local functional-region graph."),
                frequency_bands=(None, "Not extracted; check the paper."), architecture=("GCN", "Local-Global GCN."),
                accuracy=(99.30, "Abstract.")),
    "S17": dict(dataset=(None, "HUSM cohort, 'part of' the Mumtaz 2017 data, obtained on request. Mumtaz or other? Your call."),
                n_subjects=(60, ""), n_mdd=(30, ""), n_control=(30, ""),
                connectivity_measure=(None, "Partial directed coherence (MVAR). Granger, coherence or other? Decide the same way as S01."),
                frequency_bands=("0-40 Hz, 64 bins (no named bands)", ""), architecture=("CNN", "3D CNN."), accuracy=(100, "Abstract.")),
    "S18": dict(dataset=("Mumtaz", ""), n_subjects=(64, ""), n_mdd=(34, ""), n_control=(30, ""), connectivity_measure=("PLV", ""),
                frequency_bands=("delta, theta, alpha, beta, low gamma, high gamma", ""),
                architecture=("GCN", "Six-branch Chebyshev GCN (CN-GCN)."), accuracy=(99.29, "Abstract.")),
}
# ADVISOR RULING 2026-09-24 (Q16): `accuracy` = the proposed model under the MOST SUBJECT-INDEPENDENT protocol the
# paper reports (rule c), results tables over a contradicting abstract; the abstract's headline figure moves to a
# second field, `accuracy_abstract` (rule a, sensitivity analysis S4). The P entries above hold the ABSTRACT figure.
RECODE = "Rule (c): set this from YOUR recode (protocol_coded in FOR_KUNAL_RECODE), not from the abstract."
RULE_C = {
    "S01": (99.245, "Rule (c): results table (99.245 +/- 1.152); the abstract rounds it to 99.24."),
    "S02": (80.74, "Rule (c): check the paper reports only this one evaluation; if so it equals the abstract."),
    "S03": (91.06, "Rule (c): LOSO, the most subject-independent protocol reported; both raters' initial codes describe it."),
    "S04": (97.27, "Rule (c): single protocol; equals the abstract."),
    "S05": (96.33, "OPTION B (proposed deviation, deviations_log row 17): not recoded; accuracy for the protocol both raters coded (sample-level tenfold after band/region selection), so rating and accuracy match. Rule (c) would use LOSO. Pending advisor OK."),
    "S06": (None, "Protocol: the individual-based five-fold split both raters coded. Which dataset (77.78 public / 95.61 own): " + Q),
    "S07": (None, "Rule (c): use the RESULTS TABLES, not the abstract: 99.87 (Mumtaz) / 93.93 (PRED+CT) / 97.16 (combined). Which dataset: " + Q),
    "S08": (None, "Protocol: neither evaluation states a subject split (tie); codes unchanged. Which dataset (Table III: 99.68 / 98.44 / 96.72): " + Q),
    "S09": (89.03, "Rule (c): single protocol; equals the abstract. Multimodal EEG + speech (sensitivity S3)."),
    "S10": (None, "Which architecture's result (GCN 98.06 / GraphSAGE 98.50 / GAT 98.80, Table 3): " + Q),
    "S11": (None, "Which dataset/task (88.64 ds003474 binary vs 34.75 DASS-21 multiclass): " + Q),
    "S12": (None, "Three-class task (79.64, PLI theta): " + Q),
    "S13": (85.33, "Rule (c): single protocol; equals the abstract."),
    "S14": (97.22, "Rule (c): single protocol (sample-level tenfold); equals the abstract."),
    "S15": (None, "Which dataset (98.30 MODMA / 96.51 PRED+CT): " + Q),
    "S16": (99.30, "Rule (c): single protocol (9:1 split); equals the abstract."),
    "S17": (100, "Rule (c): single protocol (subject-level 50/50); equals the abstract."),
    "S18": (99.29, "Rule (c): single protocol (tenfold; the 9:1 is the fold ratio); equals the abstract."),
}
FIELDS = ["dataset", "n_subjects", "n_mdd", "n_control", "connectivity_measure", "frequency_bands", "architecture", "accuracy",
          "accuracy_abstract"]


def main():
    wb = load_workbook(SRC)
    ws = wb["Code"]
    head = {c.value: c.column for c in ws[1]}
    if "accuracy_abstract" not in head:   # appended at the far right so no dropdown column shifts
        col = ws.max_column + 1
        ws.cell(row=1, column=col, value="accuracy_abstract").font = copy(ws.cell(row=1, column=head["accuracy"]).font)
        head["accuracy_abstract"] = col
    for sid in P:
        P[sid]["accuracy_abstract"] = P[sid]["accuracy"]
        P[sid]["accuracy"] = RULE_C[sid]
    filled = blank = 0
    for row in ws.iter_rows(min_row=2):
        sid = row[head["study_id"] - 1].value
        if sid not in P:
            continue
        for f in FIELDS:
            cell = ws.cell(row=row[0].row, column=head[f])
            if cell.value not in (None, ""):
                continue  # never overwrite anything KC typed
            val, note = P[sid][f]
            if val is None:
                cell.fill = ORANGE
                cell.comment = Comment("LEFT BLANK: " + note, AUTHOR)
                blank += 1
            else:
                cell.value = val
                cell.fill = BLUE
                cell.comment = Comment("AI prefill, CHECK against PDF. " + note, AUTHOR)
                filled += 1
    wb.save(OUT)
    print(f"{filled} cells pre-filled (blue), {blank} left blank for you (orange). Wrote {OUT.name}")


if __name__ == "__main__":
    main()
