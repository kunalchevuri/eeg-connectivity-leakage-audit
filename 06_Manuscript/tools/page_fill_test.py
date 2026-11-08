"""Project the final page count before the prose exists.

Copies 06_Manuscript to a temp folder, pads every section to SCALE x its old budget with words drawn from
our own prose, adds realistic Table I / Fig. 3 / Fig. 4 (synthetic codes, real DOIs) and N_REFS references,
compiles, and prints the page count. Never modifies the real manuscript. See word_budget_MLESP.md.

    python 06_Manuscript/tools/page_fill_test.py 0.75 40
"""
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf

REAL = Path(__file__).resolve().parents[2]
MIK = Path(r"C:\Users\ckche\AppData\Local\Programs\MiKTeX\miktex\bin\x64")
SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
N_REFS = int(sys.argv[2]) if len(sys.argv) > 2 else 40
F = Path(tempfile.gettempdir()) / "eeg_page_fill" / f"run_{SCALE}_{int(time.time() * 1000)}"
BUDGET = {"section_I_body.tex": 545, "section_II_body.tex": 770, "section_III_body.tex": 1045,
          "section_IV_body.tex": 1135, "section_V_body.tex": 1180, "table_II_body.tex": 455,
          "section_VII_body.tex": 410, "section_VIII_body.tex": 135}

shutil.copytree(REAL / "06_Manuscript", F / "06_Manuscript",
                ignore=shutil.ignore_patterns("*.aux", "*.bbl", "*.blg", "*.log", "paper.pdf", "tools"))
(F / "07_References").mkdir(parents=True)
shutil.copy(REAL / "07_References/bib_keys.csv", F / "07_References")
(F / "04_Phase4_Coding").mkdir(parents=True)
M = F / "06_Manuscript"

key = pd.read_csv(REAL / "04_Phase4_Coding/study_id_key_2026-09-23.csv")
rng = np.random.default_rng(1)
n = len(key)
pick = lambda opts: rng.choice(opts, n)
pd.DataFrame({"study_id": key.study_id, "doi": key.doi, "dataset": pick(["MODMA", "Mumtaz (HUSM)", "PRED+CT", "own"]),
              "n_subjects": rng.integers(40, 130, n), "connectivity_measure": pick(["PLV", "PLI", "coherence", "Pearson"]),
              "architecture": pick(["CNN", "GCN", "CNN-LSTM", "GNN+GRU"]), "split_unit": pick(["subject", "epoch", "unclear"]),
              "connectivity_scope": pick(["within-fold", "whole-dataset", "unclear"]),
              "threshold_fit": pick(["within-fold", "none", "unclear"]),
              "normalization_fit": pick(["within-fold", "whole-dataset", "unclear"]),
              "selection_fit": pick(["none", "whole-dataset", "unclear"]), "accuracy": rng.uniform(78, 99.7, n).round(1),
              "leakage_rating": pick(["free", "possible", "likely", "unclear"])}
             ).to_csv(F / "04_Phase4_Coding/coding_sheet_FINAL.csv", index=False)
for s in ("build_table1.py", "figures/make_fig3_rq1.py", "figures/make_fig4_rq3.py"):
    subprocess.run([sys.executable, str(M / s)], check=True, stdout=subprocess.DEVNULL)

src = " ".join((REAL / "06_Manuscript" / f).read_text(encoding="utf-8") for f in
               ("section_I_body.tex", "section_III_body.tex", "section_IV_body.tex", "section_VII_body.tex"))
src = re.sub(r"(?m)^%.*$", "", src)
src = re.sub(r"\\[a-zA-Z]+\*?(\[[^]]*\])?(\{[^}]*\})?", " ", src)
WORDS = re.findall(r"[A-Za-z][A-Za-z'-]*", src)


def filler(k):
    return " ".join(rng.choice(WORDS, k)) + "."


def words(t):
    t = re.sub(r"(?m)^%.*$", "", t)
    t = re.sub(r"\\begin\{(figure\*?|table\*?)\}.*?\\end\{\1\}", "", t, flags=re.S)
    t = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", "", t, flags=re.S)
    t = re.sub(r"\\(CITE|PENDING)\{[^{}]*\}", "", t)
    t = re.sub(r"\\[a-zA-Z]+\*?(\{[^}]*\})?", "", t)
    return len(re.findall(r"[A-Za-z0-9%'-]+", t))


for f, b in BUDGET.items():
    p = M / f
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"\\PENDING\{[^{}]*\}", "", t)
    t = re.sub(r"\\CITE\{[^{}]*\}", r"\\cite{nunez1997}", t)
    need = int(b * SCALE) - words(t)
    if need > 0:
        t += "\n\n" + filler(need) + "\n"
    p.write_text(t, encoding="utf-8")

paper = (M / "paper.tex").read_text(encoding="utf-8")
paper = paper.replace(r"\bibliography{references}", "\\nocite{*}\n\\bibliography{references}")
(M / "paper.tex").write_text(paper, encoding="utf-8")
macros = (M / "macros_counts.tex").read_text(encoding="utf-8")
macros = re.sub(r"\\textbf\{\[(PENDING|NOT ESTIMABLE)[^]]*\]\}", "0.62", macros)
(M / "macros_counts.tex").write_text(macros, encoding="utf-8")

bib = (M / "references.bib").read_text(encoding="utf-8")
bib = re.sub(r"\s*note = \{+UNVERIFIED[^}]*\}+,?", "", bib)
for i in range(max(0, N_REFS - bib.count("\n@"))):
    bib += (f"\n@article{{dummy{i},\n  author = {{Author, A. and Author, B. and Author, C. and Author, D.}},\n"
            f"  title = {{A representative title about {' '.join(rng.choice(WORDS, 8))}}},\n"
            f"  journal = {{IEEE Transactions on Neural Systems and Rehabilitation Engineering}},\n"
            f"  volume = {{31}}, number = {{4}}, pages = {{1012--1023}}, year = {{2023}}, doi = {{10.1109/TNSRE.2023.{1000 + i}}}\n}}\n")
(M / "references.bib").write_text(bib, encoding="utf-8")

for cmd in (["pdflatex", "-interaction=nonstopmode", "paper.tex"], ["bibtex", "paper"],
            ["pdflatex", "-interaction=nonstopmode", "paper.tex"], ["pdflatex", "-interaction=nonstopmode", "paper.tex"]):
    subprocess.run([str(MIK / (cmd[0] + ".exe"))] + cmd[1:], cwd=M, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
doc = pymupdf.open(M / "paper.pdf")
print(f"SCALE={SCALE} refs={N_REFS}: {len(doc)} pages; last page has {len(doc[-1].get_text().split())} words "
      f"(copy in {F})")
