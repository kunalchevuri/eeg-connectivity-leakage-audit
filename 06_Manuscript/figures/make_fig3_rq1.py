"""Fig. 3 - Reporting completeness by leakage surface (blueprint Sec 10, Section V-B).

REVIEW 2026-09-27: redrawn for print; round 3 recolored in the figures4papers semantic palette
(green = training data only, red = held-out data used, light gray = not performed, dotted = not reported). Every segment is labeled with its study count and percentage; segments
too narrow for a label are labeled outside the bar. Categories differ in luminance and the "not reported"
category is hatched, so the figure reads in grayscale. Reads coding_sheet_FINAL.csv only; nothing typed by hand.

    python 06_Manuscript/figures/make_fig3_rq1.py
"""
from pathlib import Path

import ieee_style
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

HERE = Path(__file__).parent
FINAL = HERE.parents[1] / "04_Phase4_Coding/coding_sheet_FINAL.csv"

SURFACES = [("L1 partition", "split_unit"), ("L2 connectivity", "connectivity_scope"),
            ("L3 threshold", "threshold_fit"), ("L4 normalization", "normalization_fit"),
            ("L5 selection", "selection_fit")]
CATEGORY = {"within-fold": "safe", "subject": "safe", "whole-dataset": "leak", "epoch": "leak",
            "none": "none", "unclear": "unclear"}
SEGMENTS = [  # key, legend label, hatch, text color
    ("safe", "Training data only", "", "black"),
    ("leak", "Used held-out data", "", "white"),
    ("none", "Not performed", "", "black"),
    ("unclear", "Not reported", "....", "black"),
]


def main():
    if not FINAL.exists():
        print(f"{FINAL} does not exist yet - Fig. 3 not built.")
        return
    ieee_style.apply()
    df = pd.read_csv(FINAL)
    n = len(df)
    counts = []
    for _, col in SURFACES:
        cats = df[col].astype(str).str.strip().str.lower().map(CATEGORY).fillna("unclear")
        counts.append({k: int((cats == k).sum()) for k, *_ in SEGMENTS})

    fig, ax = plt.subplots(figsize=(3.05, 1.75))
    ys = list(range(len(SURFACES)))[::-1]
    for y, c in zip(ys, counts):
        left, outside = 0.0, []
        for key, _, hatch, tcol in SEGMENTS:
            k = c[key]
            if k == 0:
                continue
            w = 100 * k / n
            ax.barh(y, w, left=left, height=0.64, color=ieee_style.CATEGORY[key], hatch=hatch,
                    edgecolor=ieee_style.DD["ink"], lw=0.6)
            pct = f"{round(100 * k / n)}%"
            if w >= 30:
                ax.text(left + w / 2, y, f"{k} ({pct})", ha="center", va="center", fontsize=7.5, color=tcol)
            elif w >= 12:
                bbox = dict(boxstyle="square,pad=0.08", fc="white", ec="none") if hatch else None
                ax.text(left + w / 2, y, f"{k}\n{pct}", ha="center", va="center", fontsize=6.8,
                        color=tcol, linespacing=0.9, bbox=bbox)
            else:
                outside.append(f"{k} ({pct})")
            left += w
        if outside:
            ax.text(101.5, y, ", ".join(outside),
                    ha="left", va="center", fontsize=7)
    ax.set_yticks(ys)
    ax.set_yticklabels([s for s, _ in SURFACES])
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 20))
    ax.set_xlabel(f"Studies (%), n = {n}")
    ax.set_ylim(-0.55, len(SURFACES) - 0.45)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    handles = [Patch(facecolor=ieee_style.CATEGORY[k], edgecolor=ieee_style.DD["ink"], lw=0.6, hatch=h, label=l)
               for k, l, h, _ in SEGMENTS]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=2, frameon=False,
              handlelength=1.3, handleheight=0.9, columnspacing=0.9, borderaxespad=0.2)
    out = HERE / "fig3_rq1"
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(out.with_suffix(".png"), dpi=300)
    print(f"wrote {out.name}.pdf/.png (n={n}); counts={counts}")


if __name__ == "__main__":
    main()
