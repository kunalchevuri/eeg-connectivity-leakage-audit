"""Apply the Q16 recode (advisor ruling 2026-09-24) on top of the initial coding pass.

Q16: the recorded accuracy is the proposed model's result under the most subject-independent protocol
the paper reports, and the leakage codes must describe that same protocol. The initial pass followed the
abstract's headline number, so rows whose paper reports more than one protocol were recoded by BOTH
raters, independently (RECODE_INSTRUCTIONS.txt).

Inputs  rater_A_scored.csv, rater_B_scored.csv         initial pass (score_ratings.py) - kappa source, never modified
        FOR_KUNAL_RECODE/rater_A_Kunal_RECODE_*.xlsx   rater A's recoded rows
        FOR_LEAH_RECODE/rater_B_Leah_RECODE_*.xlsx     rater B's recoded rows
Outputs rater_A_scored_recoded.csv, rater_B_scored_recoded.csv
            = initial pass with the recoded rows' five surface codes, evidence quote and notes replaced,
              leakage_rating recomputed by score_ratings.apply_rules, plus columns recoded / protocol_coded
        agreement_recoded.csv  = rating agreement across all studies after the recode (feeds the tiebreak)

The initial-pass kappa stays the pre-resolution agreement statistic; agreement on the recoded rows is
reported alongside it (deviations_log.md row 17).

    python apply_recode.py --a FOR_KUNAL_RECODE/rater_A_Kunal_RECODE_2026-09-25.xlsx \
                           --b FOR_LEAH_RECODE/rater_B_Leah_RECODE_2026-09-25.xlsx
"""
import argparse
from pathlib import Path

import pandas as pd

from score_ratings import apply_rules

HERE = Path(__file__).parent
SURFACES = ["split_unit", "connectivity_scope", "threshold_fit", "normalization_fit", "selection_fit"]
REPLACED = SURFACES + ["evidence_quote", "notes (optional)"]


def read_recode(path):
    df = pd.read_excel(path, sheet_name="Rate", dtype=object)
    blank = df[SURFACES + ["evidence_quote", "protocol_coded"]].isna()
    if blank.any().any():
        rows = df.loc[blank.any(axis=1), "study_id"].tolist()
        raise SystemExit(f"{path}: recode incomplete (blank dropdown, evidence_quote or protocol_coded) for {rows}")
    return df.set_index("study_id")


def apply(initial_csv, recode_xlsx, out_csv):
    base = pd.read_csv(HERE / initial_csv).set_index("study_id")
    rec = read_recode(HERE / recode_xlsx)
    unknown = sorted(set(rec.index) - set(base.index))
    if unknown:
        raise SystemExit(f"{recode_xlsx}: study_ids not in the initial pass: {unknown}")
    out = base.copy()
    out["recoded"] = False
    out["protocol_coded"] = ""
    for sid, r in rec.iterrows():
        for c in REPLACED:
            if c in rec.columns:
                out.loc[sid, c] = r[c]
        out.loc[sid, "recoded"] = True
        out.loc[sid, "protocol_coded"] = r["protocol_coded"]
    out["leakage_rating_initial"] = base["leakage_rating"]
    out["leakage_rating"] = out.apply(apply_rules, axis=1)
    out.reset_index().to_csv(HERE / out_csv, index=False)
    return out, set(rec.index)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="rater A recode workbook")
    ap.add_argument("--b", required=True, help="rater B recode workbook")
    args = ap.parse_args()

    a, ra = apply("rater_A_scored.csv", args.a, "rater_A_scored_recoded.csv")
    b, rb = apply("rater_B_scored.csv", args.b, "rater_B_scored_recoded.csv")
    if ra != rb:
        raise SystemExit(f"The raters recoded different rows: A {sorted(ra)}, B {sorted(rb)}. Both must recode the same rows.")

    m = pd.DataFrame({"leakage_rating_a": a["leakage_rating"], "leakage_rating_b": b["leakage_rating"]})
    m["agree"] = m["leakage_rating_a"] == m["leakage_rating_b"]
    m["recoded"] = m.index.isin(ra)
    m.rename_axis("study_id").reset_index().to_csv(HERE / "agreement_recoded.csv", index=False)

    sub = m[m["recoded"]]
    print(f"Recoded rows: {sorted(ra)}. Rating agreement on the recoded rows: {int(sub['agree'].sum())}/{len(sub)}.")
    for sid in sorted(ra):
        ch_a = a.loc[sid, "leakage_rating_initial"] != a.loc[sid, "leakage_rating"]
        ch_b = b.loc[sid, "leakage_rating_initial"] != b.loc[sid, "leakage_rating"]
        print(f"  {sid}: A {a.loc[sid, 'leakage_rating_initial']} -> {a.loc[sid, 'leakage_rating']}{' (changed)' if ch_a else ''}; "
              f"B {b.loc[sid, 'leakage_rating_initial']} -> {b.loc[sid, 'leakage_rating']}{' (changed)' if ch_b else ''}")
    dis = m.index[~m["agree"]].tolist()
    print(f"Disagreements after the recode (all go to the advisor tiebreak): {dis or 'none'}")
    print("Wrote rater_A_scored_recoded.csv, rater_B_scored_recoded.csv, agreement_recoded.csv")
    print("Next: python build_final_coding_sheet.py   (it uses the *_recoded files when they exist)")


if __name__ == "__main__":
    main()
