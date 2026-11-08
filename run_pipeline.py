"""One command from the finished rater sheets to a compiled paper.pdf.

    python run_pipeline.py                       # full run
    python run_pipeline.py --allow-missing-descriptive   # run even if rater A's descriptive fields are incomplete

Guards (the run stops, it never "fixes" anything):
  1. Each rater sheet's five leakage columns must be IDENTICAL to the as-received snapshot in
     04_Phase4_Coding/snapshots_pre_resolution/. Coding is closed; only evidence quotes may change
     (e.g. replacing a paraphrase with the verbatim sentence), and every changed quote is printed.
  2. Rater A's descriptive fields (dataset, n_subjects, connectivity_measure, architecture, accuracy, ...) must be
     filled, or the run stops unless --allow-missing-descriptive is given (Table I and RQ3 would have gaps).
  3. Every disagreement must be resolved in disagreement_resolution.csv (build_final_coding_sheet.py enforces this).

Steps: score_ratings.py -> [apply_recode.py, only if both recode sheets are complete] -> build_final_coding_sheet.py
-> build_results.py (analysis.py, figures, Table I, macros) -> sensitivity.py -> rq4.py -> make_macros.py -> LaTeX.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
CODING = ROOT / "04_Phase4_Coding"
SNAP = CODING / "snapshots_pre_resolution"
MAN = ROOT / "06_Manuscript"
SURFACES = ["split_unit", "connectivity_scope", "threshold_fit", "normalization_fit", "selection_fit"]
DESCRIPTIVE = ["dataset", "n_subjects", "connectivity_measure", "architecture", "accuracy"]
RATER_A = CODING / "rater_A_Kunal_2026-09-23.xlsx"
RATER_B = CODING / "rater_B_Leah_2026-09-23.xlsx"
RECODE_A = CODING / "FOR_KUNAL_RECODE/rater_A_Kunal_RECODE_2026-09-25.xlsx"
RECODE_B = CODING / "FOR_LEAH_RECODE/rater_B_Leah_RECODE_2026-09-25.xlsx"
MIKTEX = Path(r"C:\Users\ckche\AppData\Local\Programs\MiKTeX\miktex\bin\x64")


def sheet(path):
    xl = pd.ExcelFile(path)
    name = "Code" if "Code" in xl.sheet_names else "Rate"
    return pd.read_excel(xl, sheet_name=name, dtype=object).set_index("study_id")


def norm(v):
    return "" if pd.isna(v) else str(v).strip().lower()


def guard_unchanged(current, snapshot, who):
    cur, snap = sheet(current), sheet(snapshot)
    if list(cur.index) != list(snap.index):
        raise SystemExit(f"{who}: study IDs differ from the snapshot {snapshot.name}")
    changed = [(s, c, snap.loc[s, c], cur.loc[s, c]) for s in snap.index for c in SURFACES
               if norm(cur.loc[s, c]) != norm(snap.loc[s, c])]
    if changed:
        lines = "\n".join(f"  {s} {c}: {a!r} -> {b!r}" for s, c, a, b in changed)
        raise SystemExit(f"STOP: {who}'s leakage codes differ from the as-received snapshot. Coding is closed.\n{lines}")
    quotes = [s for s in snap.index if norm(cur.loc[s, "evidence_quote"]) != norm(snap.loc[s, "evidence_quote"])]
    print(f"  {who}: leakage codes identical to snapshot" + (f"; evidence quote changed for {quotes}" if quotes else ""))


def guard_descriptive(path, allow):
    df = sheet(path)
    miss = {c: df.index[df[c].isna()].tolist() for c in DESCRIPTIVE if c in df.columns}
    miss = {c: v for c, v in miss.items() if v}
    absent = [c for c in DESCRIPTIVE if c not in df.columns]
    if absent or miss:
        msg = f"rater A descriptive fields incomplete: absent {absent}; blank {miss}"
        if not allow:
            raise SystemExit("STOP: " + msg + "\n(accuracy may be blank only where advisor Q20 excludes the study; "
                             "rerun with --allow-missing-descriptive to proceed anyway)")
        print("  WARNING: " + msg)


def recode_complete(path):
    if not path.exists():
        return False
    df = pd.read_excel(path, sheet_name="Rate", dtype=object)
    return not df[SURFACES + ["evidence_quote", "protocol_coded"]].isna().any().any()


def run(args, cwd):
    print(f"\n$ {' '.join(str(a) for a in args)}")
    subprocess.run([sys.executable] + [str(a) for a in args], cwd=cwd, check=True)


def latex():
    exe = lambda n: str(MIKTEX / n) if (MIKTEX / f"{n}.exe").exists() else shutil.which(n) or n
    for cmd in ([exe("pdflatex"), "-interaction=nonstopmode", "paper"], [exe("bibtex"), "paper"],
                [exe("pdflatex"), "-interaction=nonstopmode", "paper"], [exe("pdflatex"), "-interaction=nonstopmode", "paper"]):
        subprocess.run(cmd, cwd=MAN, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = (MAN / "paper.log").read_text(encoding="latin-1")
    errors = len(re.findall(r"(?m)^!", log))
    try:
        import pymupdf
        doc = pymupdf.open(MAN / "paper.pdf")
        text = " ".join(p.get_text() for p in doc)
        print(f"\npaper.pdf: {len(doc)} pages, {errors} LaTeX errors, "
              f"{text.count('PENDING')} PENDING, {text.count('NOT ESTIMABLE')} NOT ESTIMABLE, {text.count('[CITE')} CITE markers")
    except ImportError:
        print(f"\npaper.pdf built, {errors} LaTeX errors")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-missing-descriptive", action="store_true")
    ap.add_argument("--rater-a", default=str(RATER_A))
    ap.add_argument("--rater-b", default=str(RATER_B))
    a = ap.parse_args()
    ra, rb = Path(a.rater_a), Path(a.rater_b)

    print("Guards:")
    guard_unchanged(ra, SNAP / "rater_A_Kunal_FINAL_as_received_2026-09-24.xlsx", "rater A")
    guard_unchanged(rb, SNAP / "rater_B_Leah_FINAL_as_received_2026-09-24.xlsx", "rater B")
    guard_descriptive(ra, a.allow_missing_descriptive)

    run(["score_ratings.py", "--a", ra, "--b", rb, "--out", "."], CODING)
    if recode_complete(RECODE_A) and recode_complete(RECODE_B):
        run(["apply_recode.py", "--a", RECODE_A, "--b", RECODE_B], CODING)
    else:
        print("\nRecode sheets absent or incomplete: no recode applied (option B, deviations_log row 17).")
    run(["build_final_coding_sheet.py"], CODING)
    run(["build_results.py"], ROOT / "05_Phase5_Analysis")
    run(["sensitivity.py"], ROOT / "05_Phase5_Analysis")
    run(["rq4.py"], ROOT / "05_Phase5_Analysis")
    run(["make_macros.py"], MAN)          # again, so the sensitivity macros are current
    latex()


if __name__ == "__main__":
    main()
