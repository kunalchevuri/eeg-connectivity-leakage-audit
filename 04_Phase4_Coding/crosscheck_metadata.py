"""Side-by-side check of KC's descriptive entries against the AI-extracted metadata.

RUN ONLY AFTER KC HAS FINISHED CODING (rater independence). Descriptive fields only: dataset,
sample sizes, connectivity measure, architecture, accuracy. Leakage columns are never compared,
since the AI file deliberately has none.

Neither side is presumed correct. A flagged row means "open the paper and decide", and KC's
sheet is what gets corrected if he was wrong. The AI file is never copied into the coding sheet.

    python 04_Phase4_Coding/crosscheck_metadata.py
    -> 04_Phase4_Coding/crosscheck_KC_vs_extracted.xlsx
"""
import re
import sys
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

HERE = Path(__file__).parent
SHEET = HERE / "rater_A_Kunal_2026-09-23.xlsx"
META = HERE / "objective_metadata_extracted.csv"
KEY = HERE / "study_id_key_2026-09-23.csv"
OUT = HERE / "crosscheck_KC_vs_extracted.xlsx"
NUMERIC = ["n_subjects", "n_mdd", "n_control", "accuracy"]
TEXT = ["dataset", "connectivity_measure", "architecture"]
ALIASES = {"mumtaz": ["mumtaz", "husm", "mphce"], "pred+ct": ["pred+ct", "pred", "unm", "new mexico", "cavanagh", "edr"],
           "modma": ["modma"], "private": ["own", "private", "not public", "in-house"],
           "correlation": ["correlation", "pearson"], "plv": ["plv", "phase-locking", "phase locking"],
           "pli": ["pli"], "coherence": ["coherence"], "granger": ["granger", "pdc", "dtf"],
           "gcn": ["gcn", "graph conv", "gnn"], "gat": ["gat"], "cnn": ["cnn", "convolutional"],
           "lstm": ["lstm", "rnn"], "cnn-lstm": ["cnn-lstm", "cnn", "lstm"], "transformer": ["transformer", "vit"]}


def numbers(text):
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", str(text))]


def check_numeric(kc, ai):
    if pd.isna(kc) or str(kc).strip() == "":
        return "KC blank"
    try:
        v = float(kc)
    except ValueError:
        return "KC not a number"
    return "match" if any(abs(v - x) < 0.05 for x in numbers(ai)) else "CHECK"


def check_text(kc, ai):
    if pd.isna(kc) or str(kc).strip() == "":
        return "KC blank"
    k = str(kc).strip().lower()
    if k == "other":
        return "KC 'other' - see notes"
    return "match" if any(a in str(ai).lower() for a in ALIASES.get(k, [k])) else "CHECK"


def main():
    kc = pd.read_excel(SHEET, sheet_name="Code")
    filled = kc["split_unit"].notna().sum()
    if filled < len(kc):
        if "--force" not in sys.argv:
            raise SystemExit(f"Only {filled}/{len(kc)} rows have split_unit filled. Finish coding before "
                             f"cross-checking (or pass --force).")
    key = pd.read_csv(KEY)[["study_id", "wos_rank"]]
    meta = pd.read_csv(META)
    df = kc.merge(key, on="study_id").merge(meta, on="wos_rank", how="left", suffixes=("_kc", "_ai"))

    rows = []
    for _, r in df.iterrows():
        for f in NUMERIC + TEXT:
            kv, av = r.get(f"{f}_kc"), r.get(f"{f}_ai")
            status = check_numeric(kv, av) if f in NUMERIC else check_text(kv, av)
            rows.append({"study_id": r["study_id"], "wos_rank": r["wos_rank"], "field": f,
                         "KC_entry": kv, "AI_extracted": av, "status": status,
                         "resolution (KC: from the paper)": ""})
    out = pd.DataFrame(rows)
    with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
        out.to_excel(xw, sheet_name="crosscheck", index=False)
        ws = xw.sheets["crosscheck"]
        flag = PatternFill("solid", fgColor="F4CCCC")
        for c, w in zip("ABCDEFG", [9, 9, 20, 22, 70, 18, 40]):
            ws.column_dimensions[c].width = w
        for row in ws.iter_rows(min_row=2):
            row[4].alignment = Alignment(wrap_text=True, vertical="top")
            if row[5].value == "CHECK":
                for cell in row:
                    cell.fill = flag
        for cell in ws[1]:
            cell.font = Font(bold=True)
    n = (out["status"] == "CHECK").sum()
    print(f"Wrote {OUT.name}: {len(out)} field comparisons, {n} flagged CHECK (red).")
    print("Automatic matching is loose: 'match' means KC's value appears somewhere in the AI text. Skim those too.")


if __name__ == "__main__":
    main()
