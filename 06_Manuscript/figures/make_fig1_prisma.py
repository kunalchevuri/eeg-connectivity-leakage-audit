"""Fig. 1 - PRISMA-style screening flow (blueprint Section 10, IV-A).

Every number is read from 03_Phase3_Corpus/prisma_counts.json, which regenerate_prisma.py builds from the
screening log. Nothing here is typed by hand, so the figure cannot disagree with the log.

    python 03_Phase3_Corpus/regenerate_prisma.py
    python 06_Manuscript/figures/make_fig1_prisma.py

Single IEEE column (3.5 in), vector PDF.
REVIEW 2026-09-27 (round 3): redrawn in the diagram-design flowchart grammar: rectangles for stages, muted
"external" boxes for exclusions, one dashed accent box for the retrieval gap (the main limitation), a blue focal
box for the final corpus, stage eyebrows, and arrows that never carry labels.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).parent
D = json.loads((HERE.parents[1] / "03_Phase3_Corpus" / "prisma_counts.json").read_text(encoding="utf-8"))
W, S_ = D["wos"], D["supplementary"]

SHORT = {  # log wording -> figure wording
    "other (not depression classification/severity)": "not a depression task",
    "classical ML only / no DL classifier": "no deep-learning model",
    "other (pre-2015 or not peer-reviewed)": "pre-2015 or unreviewed",
    "review/survey": "review or survey",
    "other (not EEG primary)": "EEG not primary",
    "no connectivity step": "no connectivity step",
    "no signal-derived connectivity": "no signal-derived\n   connectivity",
}


def reason_lines(reasons):
    return "\n".join(f" {SHORT.get(k, k)}: {n}" for k, n in reasons.items())


import ieee_style as S
S.apply()
FIG_W, FIG_H = 3.5, 4.0
fig = plt.figure(figsize=(FIG_W, FIG_H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

LX, LW = 0.26, 1.42          # main column (left margin holds the stage eyebrows)
RX, RW = 1.86, 1.60          # exclusion column
FS = 8          # advisor 2026-09-27 (flag d): box text, was 7.2
STAGE_FS = 7    # advisor 2026-09-27 (flag d): stage labels, was 5.8


def box(x, y, w, h, text, role="backend", align="center", weight="normal"):
    return S.node(ax, x, y, w, h, text, role=role, size=FS, align=align, weight=weight)


def down(b1, b2, x=None):
    x = b1[0] + b1[2] / 2 if x is None else x
    S.arrow(ax, x, b1[1], x, b2[1] + b2[3])


def right(src, dst):
    y = src[1] + src[3] / 2
    S.arrow(ax, src[0] + src[2], y, dst[0], y)


# stage eyebrows, rotated in the left margin
for y0, y1, lab in ((3.50, 3.95, "Ident."), (1.87, 3.37, "Screening"), (0.18, 1.71, "Included")):
    ax.plot([0.12, 0.12], [y0, y1], color=S.DD["rule"], lw=0.8)
    ax.text(0.07, (y0 + y1) / 2, lab.upper(), rotation=90, ha="center", va="center", fontsize=STAGE_FS,
            family="monospace", color=S.DD["muted"])

b0 = box(LX, 3.50, LW, 0.45, "Web of Science: 100\nmost-cited records\n(query: see text)")
b1 = box(LX, 2.97, LW, 0.40, f"Records screened\n(title/abstract)\nn = {W['records_screened']}")
x1 = box(RX, 2.97, RW, 0.98, f"Excluded, n = {W['excluded_title_abstract']}\n" + reason_lines(W["excluded_title_abstract_reasons"]),
         role="external", align="left")
b2 = box(LX, 2.43, LW, 0.40, f"Reports sought\nfor retrieval\nn = {W['reports_sought']}")
x2 = box(RX, 2.45, RW, 0.36, f"Not retrieved, n = {W['reports_not_retrieved']}\n(retrieval stopped early)",
         role="limitation")
b3 = box(LX, 1.87, LW, 0.40, f"Reports assessed\nfor eligibility\nn = {W['reports_assessed']}")
x3 = box(RX, 1.62, RW, 0.70, f"Excluded, n = {W['excluded_full_text']}\n" + reason_lines(W["excluded_full_text_reasons"]),
         role="external", align="left")
b4 = box(LX, 1.37, LW, 0.34, f"Included from\nWeb of Science, n = {W['included']}")

s0 = box(RX, 0.84, RW, 0.62,
         "Supplementary search\n(OpenAlex, PubMed)\n"
         f"sought {S_['reports_sought']}; not retrieved {S_['reports_not_retrieved']};\n"
         f"assessed {S_['reports_assessed']}; included {S_['included']}")
tot = box(LX, 0.18, RX + RW - LX, 0.42, f"Studies included in the audit, n = {D['included_total']}",
          role="focal_safe", weight="bold")

down(b0, b1); down(b1, b2); down(b2, b3); down(b3, b4)
down(b4, tot)
down(s0, tot)
for src, dst in ((b1, x1), (b2, x2), (b3, x3)):
    right(src, dst)

out = HERE / "fig1_prisma"
fig.savefig(out.with_suffix(".pdf"), bbox_inches=None)
fig.savefig(out.with_suffix(".png"), dpi=300, bbox_inches=None)
print(f"wrote {out.name}.pdf/.png  (included_total={D['included_total']})")
