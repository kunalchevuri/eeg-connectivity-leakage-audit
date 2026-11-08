"""One-command results build: runs the pre-registered analysis.py, then adds the two
headline proportions the abstract quotes directly (PctUnclearAny, PctEpoch) into
results/summary.json so make_macros.py can pick them up.

This script does not touch analysis.py's confirmatory logic (RQ2/RQ3) - it only reads
analysis.py's own RQ1 output columns to compute two descriptive rollups. If that
definition ever needs to change, log it in 08_Admin/deviations_log.md first.

    PctEpoch      = % of studies with split_unit == "epoch" (L1), read straight off
                    analysis.py's rq1_l1 output.
    PctUnclearAny = % of studies where at least one of L2 to L5 (connectivity scope, threshold,
                    normalization, selection) is "unclear" - ADVISOR RULING 2026-09-24 (Q8), which
                    replaced the provisional L2-L4 definition. L1 gets its own headline number
                    (PctEpoch). Q8 also asks for the same figure per surface: that is RQ1's
                    per-surface output (rq1_*.csv, Fig. 3).

Usage (from 04_Phase4_Coding, after coding_sheet_FINAL.csv and both *_scored.csv exist):
    python ../05_Phase5_Analysis/build_results.py
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CODING = ROOT / "04_Phase4_Coding"
HERE = Path(__file__).parent
OUT = HERE / "results"

REQUIRED = ["coding_sheet_FINAL.csv", "rater_A_scored.csv", "rater_B_scored.csv"]
PREPROCESSING_SURFACES = ["L2 connectivity estimation scope", "L3 threshold selection",
                           "L4 feature normalization"]


SURF = {"Split": "split_unit", "Scope": "connectivity_scope", "Thresh": "threshold_fit",
        "Norm": "normalization_fit", "Select": "selection_fit"}


def text_numbers(final):
    """Counts and percentages quoted in the Results prose (Section V), so none is typed by hand.
    Keys must match TEXT_KEYS in 06_Manuscript/make_macros.py. Accuracy is NOT touched here (that is RQ3)."""
    n = len(final)
    low = lambda c: final[c].astype(str).str.strip().str.lower() if c in final.columns else pd.Series("", index=final.index)
    pc = lambda mask: int(round(100 * float(mask.mean()))) if n else None
    t = {"Nstudies": n}
    r = low("leakage_rating")
    for k in ("free", "possible", "likely", "unclear"):
        t["N" + k.capitalize()] = int((r == k).sum())
        t["Pct" + k.capitalize()] = pc(r == k)
    t["Ntiebreak"] = int((low("rating_source") == "advisor_tiebreak").sum())
    # RQ1 per surface (post-resolution sheet)
    t["PctSubject"] = pc(low("split_unit") == "subject")
    for name, col in SURF.items():
        v = low(col)
        t["PctUnclear" + name] = pc(v == "unclear")
        if name != "Split":
            t["PctWhole" + name] = pc(v == "whole-dataset")
            t["PctWithin" + name] = pc(v == "within-fold")
        if name in ("Thresh", "Norm", "Select"):
            t["PctNone" + name] = pc(v == "none")
    # RQ2 per-surface agreement on the INITIAL pass (the pre-resolution statistic)
    a = pd.read_csv(CODING / "rater_A_scored.csv").set_index("study_id")
    b = pd.read_csv(CODING / "rater_B_scored.csv").set_index("study_id")
    for name, col in SURF.items():
        t["Agree" + name] = int((a[col].astype(str).str.strip().str.lower() == b.loc[a.index, col].astype(str).str.strip().str.lower()).sum())
    ai = pd.read_csv(CODING / "agreement_pre_resolution.csv")
    t["NdisagreeInitial"] = int((~ai["agree"]).sum())
    rec = CODING / "agreement_recoded.csv"
    if rec.exists():
        ar = pd.read_csv(rec)
        sub = ar[ar["recoded"]]
        t["Nrecoded"], t["AgreeRecoded"] = len(sub), int(sub["agree"].sum())
    # V-A corpus description (descriptive fields as verified by rater A)
    ns = pd.to_numeric(final.get("n_subjects"), errors="coerce").dropna()
    if len(ns):
        t["NsubjMedian"], t["NsubjMin"], t["NsubjMax"] = int(ns.median()), int(ns.min()), int(ns.max())
    t["NsubjMissing"] = int(n - len(ns))
    d = low("dataset")
    for k, lab in (("mumtaz", "Mumtaz"), ("modma", "MODMA"), ("pred+ct", "PREDCT"), ("private", "Private"), ("other", "Other")):
        t["Data" + lab] = int((d == k).sum())
    cm = low("connectivity_measure")
    for k, lab in (("plv", "PLV"), ("pli", "PLI"), ("coherence", "Coh"), ("correlation", "Corr"), ("granger", "Granger"), ("other", "Other")):
        t["Conn" + lab] = int((cm == k).sum())
    ar_ = low("architecture")
    t["ArchCNN"] = int(ar_.isin(["cnn", "lstm", "cnn-lstm"]).sum())
    t["ArchGNN"] = int(ar_.isin(["gcn", "gat"]).sum())
    t["ArchTransformer"] = int((ar_ == "transformer").sum())
    t["ArchOther"] = int(n - t["ArchCNN"] - t["ArchGNN"] - t["ArchTransformer"])
    key = pd.read_csv(CODING / "study_id_key_2026-09-23.csv")[["study_id", "wos_rank"]]
    yrs = pd.concat([pd.read_csv(ROOT / f"03_Phase3_Corpus/{f}", dtype=str)[["wos_rank", "year"]]
                     for f in ("screening_log.csv", "supplementary_records.csv")]).drop_duplicates("wos_rank")
    yrs["wos_rank"] = yrs["wos_rank"].astype(int)
    y = final[["study_id"]].merge(key, on="study_id").merge(yrs, on="wos_rank", how="left")["year"].astype(float)
    if y.notna().all() and len(y):
        t["YearMin"], t["YearMax"] = int(y.min()), int(y.max())
    return t


def fmt_p(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}" if p < 0.01 else f"p = {p:.2f}"


def text_stats(final, summary):
    """Formatted statistics quoted in Section V (strings, emitted verbatim by make_macros.py FMT_KEYS).
    Wilson intervals use analysis.py's own wilson(); RQ3 values come from analysis.py's output unchanged."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("analysis", HERE / "analysis.py")
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    f = {}
    n = len(final)
    low = lambda c: final[c].astype(str).str.strip().str.lower()

    def ci(mask, key):
        _, lo, hi = A.wilson(int(mask.sum()), n)
        if n:
            f[key + "Lo"], f[key + "Hi"] = f"{100 * lo:.0f}", f"{100 * hi:.0f}"

    ci(low("split_unit") == "epoch", "PctEpoch")
    unclear_any = pd.Series(False, index=final.index)
    for c in ("connectivity_scope", "threshold_fit", "normalization_fit", "selection_fit"):
        unclear_any |= low(c).eq("unclear")
    ci(unclear_any, "PctUnclearAny")
    for k in ("free", "possible", "likely", "unclear"):
        ci(low("leakage_rating") == k, "Pct" + k.capitalize())

    strata_path = OUT / "rq3_accuracy_by_rating.csv"
    if strata_path.exists():
        st = pd.read_csv(strata_path).set_index("rating")
        f["NaccStudies"] = str(int(st["n"].sum()))
        for r in st.index:
            R = r.capitalize()
            f["Nacc" + R] = str(int(st.loc[r, "n"]))
            if st.loc[r, "n"] > 0:
                f["Med" + R + "Fmt"] = f"{st.loc[r, 'median']:.1f}"
                f["IQR" + R] = f"{st.loc[r, 'q1']:.1f}--{st.loc[r, 'q3']:.1f}"
        # Advisor 2026-09-27 (flag b): give the individual values, not an IQR, for the two leakage-free studies.
        acc = pd.to_numeric(final["accuracy"], errors="coerce")
        vals = sorted(acc[(low("leakage_rating") == "free") & acc.notna()])
        f["AccFreeValues"] = " and ".join(f"{v:.1f}%" for v in vals)
    lvf = summary.get("rq3", {}).get("likely_vs_free")
    if isinstance(lvf, dict):
        f["MWU"] = f"{lvf['mann_whitney_U']:.1f}"
        f["MWp"] = fmt_p(lvf["p_two_sided"])
        f["CliffLo"], f["CliffHi"] = (f"{v:.2f}" for v in lvf["cliffs_delta_ci"])
        f["MedDiff"] = f"{lvf['median_diff_pp']:.1f}"
        f["MedDiffLo"], f["MedDiffHi"] = (f"{v:.1f}" for v in lvf["median_diff_ci"])
        f["SESOIverdict"] = ("smaller than" if lvf["within_SESOI_report_null"] else "at least as large as")
    kw = summary.get("rq3", {}).get("kruskal_wallis_all_strata")
    if isinstance(kw, dict):
        f["KWH"], f["KWp"], f["KWk"] = f"{kw['H']:.2f}", fmt_p(kw["p"]), str(int(kw["k_groups"]))
    conf = OUT / "confounding_rating_by_size_tercile.csv"
    if conf.exists():
        ct = pd.read_csv(conf).set_index("size_tercile")
        for t in ("small", "medium", "large"):
            for r in ("likely", "free"):
                v = int(ct.loc[t, r]) if (t in ct.index and r in ct.columns) else 0
                f["N" + r.capitalize() + t.capitalize()] = str(v)
    return {k: (v.replace("-", "$-$", 1) if isinstance(v, str) and v.startswith("-") else v).replace("--$-$", "--$-$")
            for k, v in f.items()}


def main():
    missing = [f for f in REQUIRED if not (CODING / f).exists()]
    if missing:
        raise SystemExit(
            f"Cannot build results yet - missing from {CODING}: {missing}\n"
            f"Run (in order) score_ratings.py, resolve any disagreements with the advisor, "
            f"then build_final_coding_sheet.py.")

    cmd = [sys.executable, str(HERE / "analysis.py"),
           "--final", str(CODING / "coding_sheet_FINAL.csv"),
           "--rater-a", str(CODING / "rater_A_scored.csv"),
           "--rater-b", str(CODING / "rater_B_scored.csv"),
           "--out", str(OUT)]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=HERE)

    final = pd.read_csv(CODING / "coding_sheet_FINAL.csv")
    n = len(final)

    l1 = pd.read_csv(OUT / "rq1_l1.csv") if (OUT / "rq1_l1.csv").exists() else None
    # rq1 filenames come from analysis.py's SURFACES dict, keyed by the first word ("L1", "L2", ...)
    pct_epoch = None
    if l1 is not None:
        row = l1.loc[l1["category"] == "epoch"]
        pct_epoch = float(row["prop"].iloc[0]) * 100 if len(row) else None
    if pct_epoch is None:
        s = final["split_unit"].astype(str).str.strip().str.lower()
        pct_epoch = 100 * (s == "epoch").mean() if n else None

    cols = ["connectivity_scope", "threshold_fit", "normalization_fit", "selection_fit"]
    present = [c for c in cols if c in final.columns]
    if len(present) < len(cols):
        print(f"warning: coding_sheet_FINAL.csv is missing {set(cols) - set(present)}; "
              f"PctUnclearAny computed from the columns that are present.")
    unclear_any = pd.Series(False, index=final.index)
    for c in present:
        unclear_any |= final[c].astype(str).str.strip().str.lower().eq("unclear")
    pct_unclear_any = 100 * unclear_any.mean() if n else None

    summary_path = OUT / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    summary["abstract"] = {"PctEpoch": pct_epoch, "PctUnclearAny": pct_unclear_any, "n_studies": n}

    # analysis.py writes RQ3 strata medians to CSV only, and nests cliffs_delta under
    # likely_vs_free - flatten both into summary["rq3"] here (analysis.py itself is not
    # touched) so make_macros.py's simple lookups find them.
    strata_path = OUT / "rq3_accuracy_by_rating.csv"
    rq3 = summary.get("rq3", {})
    if strata_path.exists():
        strata = pd.read_csv(strata_path).set_index("rating")["median"]
        if "likely" in strata.index:
            rq3["median_likely"] = strata["likely"]
        if "free" in strata.index:
            rq3["median_free"] = strata["free"]
    lvf = rq3.get("likely_vs_free")
    if isinstance(lvf, dict) and "cliffs_delta" in lvf:
        rq3["cliffs_delta"] = lvf["cliffs_delta"]
    summary["rq3"] = rq3
    summary["text"] = text_numbers(final)
    summary["text_fmt"] = text_stats(final, summary)

    summary_path.write_text(json.dumps(summary, indent=2, default=float))

    print(f"\nAbstract rollups: PctEpoch={pct_epoch:.0f}%  PctUnclearAny={pct_unclear_any:.0f}%  (n={n})")
    print(f"Wrote {summary_path}")

    # Everything downstream in the manuscript, so one command leaves nothing stale.
    man = ROOT / "06_Manuscript"
    for script in (man / "figures/make_fig3_rq1.py", man / "figures/make_fig4_rq3.py",
                   man / "build_table1.py", man / "make_macros.py"):
        subprocess.run([sys.executable, str(script)], check=True, cwd=script.parent,
                       stdout=subprocess.DEVNULL if script.name == "make_macros.py" else None)
    print("Rebuilt Fig. 3, Fig. 4, Table I and macros_counts.tex. Next: recompile paper.tex.")


if __name__ == "__main__":
    main()
