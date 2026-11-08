"""Fig. 4 - Reported accuracy by leakage-risk rating (blueprint Sec 10, Section V-D).

REVIEW 2026-09-27: redrawn for print; round 3 recolored in the figures4papers palette (rating colors
green/blue/red/gray, same semantics as Fig. 3), with black-edged markers so shape still carries the tercile. One jittered point per study (never a bar of means); a line at each
stratum median, labeled with its value; the interquartile range as a thin bar where a stratum has >= 4
studies; individual values labeled where a stratum has <= 3 studies. Marker shape encodes sample-size tercile,
computed as in analysis.py. Reads coding_sheet_FINAL.csv only.

    python 06_Manuscript/figures/make_fig4_rq3.py
"""
from pathlib import Path

import ieee_style
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
FINAL = HERE.parents[1] / "04_Phase4_Coding/coding_sheet_FINAL.csv"
RATINGS = [("free", "Free"), ("possible", "Possible"), ("likely", "Likely"), ("unclear", "Unclear")]
MARKERS = {"small": "o", "medium": "s", "large": "^"}
SEED = 20260923


def main():
    if not FINAL.exists():
        print(f"{FINAL} does not exist yet - Fig. 4 not built.")
        return
    ieee_style.apply()
    df = pd.read_csv(FINAL)
    df["leakage_rating"] = df["leakage_rating"].astype(str).str.strip().str.lower()
    df["accuracy"] = pd.to_numeric(df["accuracy"], errors="coerce")
    df["n_subjects"] = pd.to_numeric(df["n_subjects"], errors="coerce")
    n_missing = int(df["accuracy"].isna().sum())
    df = df.dropna(subset=["accuracy"])
    df["tercile"] = pd.qcut(df["n_subjects"], 3, labels=["small", "medium", "large"], duplicates="drop")
    edges = df.groupby("tercile", observed=True)["n_subjects"].agg(["min", "max"])

    rng = np.random.default_rng(SEED)
    fig, ax = plt.subplots(figsize=(3.72, 1.8))
    ax.grid(axis="y", color="0.9", lw=0.5, zorder=0)
    for i, (r, _) in enumerate(RATINGS):   # faint band in each rating color (figures4papers light tints)
        ax.axvspan(i - 0.45, i + 0.45, color=ieee_style.RATING[r], alpha=0.07, lw=0, zorder=0)
    ticklabels = []
    for i, (r, lab) in enumerate(RATINGS):
        g = df[df["leakage_rating"] == r].sort_values("accuracy")
        ticklabels.append(f"{lab}\n(n = {len(g)})")
        if not len(g):
            continue
        med = g["accuracy"].median()
        if len(g) >= 4:
            q1, q3 = g["accuracy"].quantile([0.25, 0.75])
            ax.plot([i + 0.28, i + 0.28], [q1, q3], color="black", lw=0.8, zorder=2)
            ax.plot([i + 0.25, i + 0.31], [q1, q1], color="black", lw=0.8, zorder=2)
            ax.plot([i + 0.25, i + 0.31], [q3, q3], color="black", lw=0.8, zorder=2)
        ax.plot([i - 0.2, i + 0.2], [med, med], color=ieee_style.DD["ink"], lw=1.6, zorder=2)
        ticklabels[-1] += f"\nMdn {med:.1f}"   # median value printed under the tick
        last_label_y = -np.inf
        for _, row in g.iterrows():                       # sorted by accuracy, so labels stack upward
            m = MARKERS.get(row["tercile"], "x") if pd.notna(row["tercile"]) else "x"
            x = i + rng.uniform(-0.12, 0.12)
            ax.scatter(x, row["accuracy"], marker=m, s=20, facecolor=ieee_style.RATING[r], alpha=0.9,
                       edgecolor=ieee_style.DD["ink"], lw=0.6, zorder=3)
            if len(g) <= 3:                               # small strata: label every value, no overlaps
                ly = max(row["accuracy"], last_label_y + 1.5)
                last_label_y = ly
                ax.text(i + 0.26, ly, f"{row['accuracy']:.1f}", ha="left", va="center",
                        fontsize=6.5, color="0.25")
    ax.set_xticks(range(len(RATINGS)))
    ax.set_xticklabels(ticklabels, linespacing=1.0)
    ax.set_xlim(-0.6, len(RATINGS) - 0.25)
    ax.set_ylim(75, 101.5)
    ax.set_yticks(range(75, 101, 5))
    ax.set_ylabel("Reported accuracy (%)")
    ax.set_xlabel("Leakage-risk rating from reported methods")
    ax.spines[["top", "right"]].set_visible(False)
    handles = [Line2D([], [], marker=mk, ls="", mfc="white", mec=ieee_style.DD["ink"], ms=4.5,
                      label=f"{t} ({int(edges.loc[t, 'min'])}–{int(edges.loc[t, 'max'])})")
               for t, mk in MARKERS.items() if t in edges.index]
    ax.legend(handles=handles, title="Sample-size tercile (subjects)", title_fontsize=7,
              loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False,
              handletextpad=0.3, columnspacing=0.8, handlelength=1.4, borderaxespad=0.2)
    out = HERE / "fig4_rq3"
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(out.with_suffix(".png"), dpi=300)
    note = f"; {n_missing} study without an eligible accuracy omitted" if n_missing else ""
    print(f"wrote {out.name}.pdf/.png (n={len(df)}{note})")


if __name__ == "__main__":
    main()
