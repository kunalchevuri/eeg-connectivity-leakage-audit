"""Build the Phase 4 rater workbooks from the final screening log (blueprint §7.3-7.4, §13 Phase 4).

Run after full-text screening is final (only rows with decision == "include" are used):
    python make_rater_sheets.py

Outputs (date-stamped, never overwritten):
    rater_A_Kunal_<date>.xlsx  - full coding sheet (every §7.3 field)
    rater_B_Leah_<date>.xlsx   - instructions + the leakage fields only

Study IDs S01, S02, ... are assigned in WoS rank order and are identical in both files.
leakage_rating is NOT typed by raters: score_ratings.py derives it mechanically from the
coded fields using the §7.4 rules, so both raters' ratings come from the same rule.
"""

import datetime
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).parent
ROOT = HERE.parent
TODAY = datetime.date.today().isoformat()

CHOICES = {
    "split_unit": ["subject", "epoch", "unclear"],
    "connectivity_scope": ["within-fold", "whole-dataset", "unclear"],
    "threshold_fit": ["within-fold", "whole-dataset", "none", "unclear"],
    "normalization_fit": ["within-fold", "whole-dataset", "none", "unclear"],
    "selection_fit": ["within-fold", "whole-dataset", "none", "unclear"],
    "epoching": ["yes", "no", "unclear"],
    "split_strategy": ["holdout", "k-fold", "LOSO", "external", "unclear"],
    "dataset": ["MODMA", "PRED+CT", "Mumtaz", "private", "other"],
    "connectivity_measure": ["coherence", "PLV", "PLI", "correlation", "Granger", "other"],
    "architecture": ["CNN", "LSTM", "CNN-LSTM", "GCN", "GAT", "transformer", "other"],
}
FULL_FIELDS = ["study_id", "citation", "doi", "dataset", "n_subjects", "n_mdd", "n_control",
               "connectivity_measure", "frequency_bands", "architecture", "epoching",
               "epochs_per_subject", "split_unit", "split_strategy", "connectivity_scope",
               "threshold_fit", "normalization_fit", "selection_fit", "accuracy",
               "other_metrics", "leakage_rating", "rater", "evidence_quote"]
LEAH_FIELDS = ["study_id", "citation", "pdf_file", "split_unit", "connectivity_scope",
               "threshold_fit", "normalization_fit", "selection_fit", "evidence_quote",
               "notes (optional)"]

# Every example sentence below is INVENTED. None comes from a paper in the corpus: quoting a real
# study here would answer that row for the rater and contaminate the agreement statistic.
INSTRUCTIONS = [
    ("HOW TO RATE THE PAPERS - read this once, about 10 minutes", True),
    ("You do not need to know anything about brains, EEG or machine learning. You are a careful reader "
     "looking for a handful of specific sentences. Everything you need is on this tab.", False),
    ("", False),

    ("1. WHAT THIS PROJECT IS (the 60-second version)", True),
    ("Lots of published papers claim a computer can detect depression from brainwave recordings (EEG) with "
     "over 95% accuracy. We are checking whether those papers describe their methods clearly enough for a "
     "reader to tell if that accuracy is real - or if it could be inflated by a common mistake called 'leakage'.", False),
    ("We are NOT deciding whether any paper is right or wrong. We are only recording what each paper SAYS it did.", False),
    ("", False),

    ("2. THE ONE IDEA YOU NEED: LEAKAGE", True),
    ("A computer model learns from a 'training' set of data, then gets graded on a separate 'test' set it has "
     "never seen. The grade only means something if the test is truly new to it.", False),
    ("Analogy: a student studies from practice questions, then sits the exam. If some exam questions were "
     "secretly in the practice set, the student scores 98% - not because they learned, but because they saw "
     "the answers. That is leakage.", False),
    ("Why it matters here: every person's brainwaves are as distinctive as a fingerprint. Researchers usually "
     "chop each person's recording into many short pieces. If pieces from the SAME PERSON end up in both the "
     "training set and the test set, the model can learn to recognise the person instead of detecting "
     "depression - and it will look far more accurate than it really is.", False),
    ("Your job is to find, in each paper, the sentences that tell us whether this could have happened.", False),
    ("", False),

    ("3. WHAT YOU DO, STEP BY STEP", True),
    ("Step 1. Go to the 'Rate' tab. Each row is one paper. The 'pdf_file' column tells you which PDF to open "
     "(they are in the 'papers' folder).", False),
    ("Step 2. Do NOT read the whole paper. Jump to the Methods section - usually called 'Methods', "
     "'Materials and Methods', 'Experiments', 'Experimental Setup' or 'Evaluation'.", False),
    ("Step 3. Use Ctrl+F to search for the words listed under each column below. That is the fast way.", False),
    ("Step 4. Pick one answer from the dropdown in each of the 5 columns (click the cell, click the arrow).", False),
    ("Step 5. Copy one sentence from the paper and paste it into 'evidence_quote' - the sentence your "
     "'split_unit' answer is based on. Paste it exactly as written.", False),
    ("Step 6. Move to the next row. Aim for about 10 minutes per paper. Save as you go.", False),
    ("", False),

    ("4. THE FIVE COLUMNS - what each one asks, and what to pick", True),
    ("", False),

    ("COLUMN: split_unit  -  'Was each person kept entirely on one side of the split?'", True),
    ("   Ctrl+F for:  subject   participant   leave-one   LOSO   fold   cross-validation   split   segment   epoch   window   sample", False),
    ("   subject  = the paper says PEOPLE were divided between training and test, so no person is on both sides.", False),
    ("        e.g. 'We used leave-one-subject-out cross-validation.'", False),
    ("        e.g. 'Subjects were randomly assigned to the training set (80%) or the test set (20%).'", False),
    ("        e.g. 'No participant appeared in both the training and test sets.'", False),
    ("   epoch  = the paper cut recordings into small pieces and then split or shuffled THE PIECES, so one "
     "person's pieces can land on both sides.", False),
    ("        e.g. 'The 6,000 segments were randomly divided into 70% training and 30% testing.'", False),
    ("        e.g. 'All samples were pooled and 10-fold cross-validation was applied.'", False),
    ("        Tip: if the paper first says it cut data into 'segments', 'epochs', 'windows' or 'samples', and "
     "later splits 'the samples' or 'the data' with no mention of subjects - that is epoch.", False),
    ("   unclear  = you cannot tell which.", False),
    ("        e.g. 'Ten-fold cross-validation was used to evaluate the model.'  (says nothing about people vs pieces)", False),
    ("   IF THE PAPER TESTS ITS MODEL MORE THAN ONE WAY (e.g. both leave-one-subject-out AND 10-fold): answer for "
     "the way that produced the accuracy number in the ABSTRACT, and write the other way in 'notes'.", False),
    ("", False),

    ("COLUMN: connectivity_scope  -  'Were the brain-connection numbers calculated separately for each piece or person?'", True),
    ("   Background: these papers measure how strongly different parts of the brain are 'in sync' and put those "
     "numbers in a grid (a 'connectivity matrix' or 'adjacency matrix'). You're asking where those numbers came from.", False),
    ("   Ctrl+F for:  connectivity   adjacency   matrix   PLV   PLI   coherence   correlation   average   all subjects   group", False),
    ("   within-fold  = each grid is calculated from one piece or one person's OWN data. This is the normal case.", False),
    ("        e.g. 'PLV was computed between every pair of channels for each 2-second segment.'", False),
    ("   whole-dataset  = the numbers are averaged or pooled ACROSS people, or calculated once from everyone's data.", False),
    ("        e.g. 'A single adjacency matrix was built by averaging the correlation matrices of all subjects.'", False),
    ("        e.g. 'The group-level connectivity graph was used for every sample.'", False),
    ("   unclear  = the paper doesn't say.", False),
    ("", False),

    ("COLUMN: threshold_fit  -  'Did they cut out weak connections? If so, how was the cut-off chosen?'", True),
    ("   Ctrl+F for:  threshold   top   strongest   sparsity   binar   retain   keep   percent   %", False),
    ("   none  = they didn't cut anything; all connection values go into the model.", False),
    ("   within-fold  = a fixed cut applied to each grid on its own, OR the paper says the cut-off was chosen using "
     "training data only.", False),
    ("        e.g. 'In each matrix, the strongest 30% of connections were retained.'", False),
    ("        e.g. 'Connections with values above 0.3 were kept.'", False),
    ("   whole-dataset  = the cut-off was picked by trying different values on all the data, or from an average across people.", False),
    ("        e.g. 'Thresholds from 0.1 to 0.9 were tested and 0.4 gave the best accuracy.'  (and no mention of using only training data)", False),
    ("   unclear  = they cut connections but you can't tell how the cut-off was chosen.", False),
    ("", False),

    ("COLUMN: normalization_fit  -  'Did they rescale the numbers? If so, using which data?'", True),
    ("   Ctrl+F for:  normaliz   standardiz   z-score   scal   min-max   mean   variance", False),
    ("   IMPORTANT: IGNORE 'batch normalization'. That is a part inside the neural network and does not count here.", False),
    ("   none  = no rescaling is mentioned (apart from batch normalization, which you ignore).", False),
    ("   within-fold  = each piece is rescaled using only its own values, OR the paper says the scaling was "
     "calculated from the training data only.", False),
    ("        e.g. 'Each segment was z-scored.'   e.g. 'Scaling parameters were fitted on the training set and applied to the test set.'", False),
    ("   whole-dataset  = the whole dataset was rescaled together before splitting.", False),
    ("        e.g. 'All features were standardised to zero mean and unit variance before cross-validation.'", False),
    ("        e.g. 'The entire dataset was min-max normalised.'", False),
    ("   unclear  = they rescaled but don't say over what data.", False),
    ("        e.g. 'The features were normalised.'  (full stop, nothing more)", False),
    ("", False),

    ("COLUMN: selection_fit  -  'Did they pick only some channels or frequency bands? If so, how?'", True),
    ("   Background: 'channels' = the electrodes on the head. 'Bands' = frequency ranges with names like delta, "
     "theta, alpha, beta, gamma.", False),
    ("   Ctrl+F for:  select   selected   best   optimal   channel   electrode   band   significant   p <", False),
    ("   none  = they used all channels and bands, or picked them in advance for a stated reason.", False),
    ("        e.g. 'We analysed five standard bands: delta, theta, alpha, beta and gamma.'", False),
    ("   within-fold  = the paper says the picking was done using training data only.", False),
    ("   whole-dataset  = they compared results across channels or bands and made the best one their main model, "
     "or picked features by a statistical test on all the data.", False),
    ("        e.g. 'The gamma band achieved the highest accuracy and was therefore used for all further experiments.'", False),
    ("        e.g. 'Features showing a significant group difference (p < 0.05) were selected as input.'", False),
    ("        Note: simply REPORTING a separate result for each band is not selection. It only counts if the best "
     "one then becomes their headline model.", False),
    ("   unclear  = they selected something but you can't tell how.", False),
    ("", False),

    ("COLUMN: evidence_quote", True),
    ("   Paste the exact sentence your split_unit answer is based on. If you picked 'unclear', paste the closest "
     "sentence you found (e.g. 'Ten-fold cross-validation was used'). If there truly is nothing, write 'nothing found'.", False),
    ("", False),

    ("COLUMN: notes (optional)", True),
    ("   Anything worth flagging: a second way they tested the model, a sentence that confused you, a page number. Keep it short.", False),
    ("", False),

    ("5. THREE RULES - these matter more than anything else", True),
    ("RULE 1 - WORK ALONE. Don't look at Kunal's sheet or talk to him about any paper until you have both "
     "finished. The paper reports how often the two of you agreed. If you influence each other, that number becomes meaningless.", False),
    ("RULE 2 - ONLY WHAT THE PAPER SAYS. Don't guess what they probably did. Don't look at their code on GitHub. "
     "Don't email the authors. If the paper doesn't say it, it doesn't count.", False),
    ("RULE 3 - 'UNCLEAR' IS A REAL ANSWER. Most of these papers genuinely don't say. If you've looked for a "
     "minute and can't find it, pick 'unclear' and move on. That's a finding, not a failure - it is literally "
     "what this project is measuring.", False),
    ("", False),

    ("6. WHEN YOU'RE DONE", True),
    ("Save the file and send it to Kunal. Please don't edit it after sending. You do not need to calculate "
     "anything - the overall rating for each paper is worked out automatically from your dropdowns.", False),
    ("", False),
    ("If something in these instructions is confusing, ask Kunal about THE INSTRUCTIONS - just not about any "
     "particular paper.", False),
]


def load_included():
    s = pd.read_csv(ROOT / "03_Phase3_Corpus" / "screening_log.csv", dtype=str).fillna("")
    inc = s[s["decision (include/exclude)"].str.strip().isin(["include", "include?"])].copy()
    inc["wos_rank"] = inc["wos_rank"].astype(int)
    inc = inc.sort_values("wos_rank").reset_index(drop=True)
    wos = pd.read_csv(ROOT / "source_materials" / "thinkneuro_drive" /
                      "WoS_Top100_Updated_Extraction_2026-09-23.csv").set_index("Rank")
    # Records added by the Section 7.1 supplementary search live outside the WoS top-100 sheet.
    supp_path = ROOT / "03_Phase3_Corpus" / "supplementary_records.csv"
    supp = (pd.read_csv(supp_path, dtype=str).set_index("wos_rank")
            if supp_path.exists() else pd.DataFrame())
    pdfs = {int(p.name[1:4]): p.name for p in (ROOT / "03_Phase3_Corpus" / "fulltexts").glob("R*.pdf")}
    rows = []
    for i, r in inc.iterrows():
        if r.wos_rank in wos.index:
            w = wos.loc[r.wos_rank]
            cite = f"{w['Senior Author']} (senior), {w['Year']}, {w['Source Title'].title()}: {w['Article Title']}"
            doi = w["DOI"]
        else:
            s = supp.loc[str(r.wos_rank)]
            cite = f"{s['senior_author']} (senior), {s['year']}, {s['source']}: {s['title']}  [supplementary search]"
            doi = s["doi"]
        rows.append({"study_id": f"S{i + 1:02d}", "wos_rank": r.wos_rank,
                     "citation": cite, "doi": doi,
                     "pdf_file": pdfs.get(r.wos_rank, "MISSING - get PDF")})
    return pd.DataFrame(rows)


INPUT_FIELDS = {"split_unit", "connectivity_scope", "threshold_fit", "normalization_fit",
                "selection_fit", "evidence_quote", "notes (optional)"}


def add_instructions(ws):
    ws.title = "Instructions"
    ws.column_dimensions["A"].width = 150
    for i, (text, bold) in enumerate(INSTRUCTIONS, 1):
        cell = ws.cell(row=i, column=1, value=text)
        cell.font = Font(bold=bold, size=14 if i == 1 else 11)
        cell.alignment = Alignment(wrap_text=True, vertical="top")


def add_sheet(ws, df, fields, choices):
    header_fill = PatternFill("solid", fgColor="DDDDDD")
    input_header = PatternFill("solid", fgColor="FFD966")   # yellow = you fill these in
    input_cell = PatternFill("solid", fgColor="FFF2CC")
    for c, f in enumerate(fields, 1):
        cell = ws.cell(row=1, column=c, value=f)
        cell.font = Font(bold=True)
        cell.fill = input_header if f in INPUT_FIELDS else header_fill
        ws.column_dimensions[cell.column_letter].width = 60 if f in ("citation", "evidence_quote") else 20
    for r, (_, row) in enumerate(df.iterrows(), 2):
        for c, f in enumerate(fields, 1):
            if f in row:
                ws.cell(row=r, column=c, value=row[f])
            if f in INPUT_FIELDS:
                ws.cell(row=r, column=c).fill = input_cell
            ws.cell(row=r, column=c).alignment = Alignment(wrap_text=True, vertical="top")
    last = len(df) + 1
    for c, f in enumerate(fields, 1):
        if f in choices:
            dv = DataValidation(type="list", formula1='"' + ",".join(choices[f]) + '"', allow_blank=True)
            col = ws.cell(row=1, column=c).column_letter
            dv.add(f"{col}2:{col}{max(last, 2)}")
            ws.add_data_validation(dv)
    ws.freeze_panes = "B2"


def main():
    df = load_included()
    if df.empty:
        raise SystemExit("No studies marked 'include' in screening_log.csv yet.")

    # Both raters get the identical Instructions tab: kappa is only meaningful if both apply the same rules.
    wb = Workbook()
    add_instructions(wb.active)
    add_sheet(wb.create_sheet("Rate"), df, LEAH_FIELDS, CHOICES)
    out_b = HERE / f"rater_B_Leah_{TODAY}.xlsx"
    wb.save(out_b)

    wb = Workbook()
    add_instructions(wb.active)
    df_a = df.copy()
    df_a["rater"] = "KC"
    df_a["leakage_rating"] = "(computed by score_ratings.py)"
    add_sheet(wb.create_sheet("Code"), df_a, FULL_FIELDS + ["pdf_file", "notes (optional)"], CHOICES)
    out_a = HERE / f"rater_A_Kunal_{TODAY}.xlsx"
    wb.save(out_a)

    df[["study_id", "wos_rank", "doi", "pdf_file"]].to_csv(HERE / f"study_id_key_{TODAY}.csv", index=False)
    print(f"{len(df)} included studies -> {out_a.name}, {out_b.name}")


if __name__ == "__main__":
    main()
