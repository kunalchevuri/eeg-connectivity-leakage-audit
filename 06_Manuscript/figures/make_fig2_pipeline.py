"""Pipeline and leakage-surface figure (Fig. 1 in the paper; file name kept for the build).

REVIEW 2026-09-27 (round 3): redrawn in the diagram-design grammar. One accent (red) marks only the leakage
points; the leakage-free path uses the secondary 'link' blue. Tags L1-L5 are mono pills, stage labels are
eyebrows, connectors are straight on a shared axis, labels never sit on a connector, and the key sits in a
strip below a hairline. Two rows, seven nodes each (density ~4/10). Double column, 7.16 in wide.

    python 06_Manuscript/figures/make_fig2_pipeline.py
"""
from pathlib import Path

import ieee_style as S
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
W, H = S.TEXT_W, 2.95
NW, NH, GAP, X0 = 0.84, 0.40, 0.155, 0.12
EYE_FS, PILL_FS = 7, 7   # advisor 2026-09-27 (flag d): eyebrow and pill text, were 6.0-6.3 and 6.5
xs = [X0 + i * (NW + GAP) for i in range(7)]


def row(ax, y, labels, roles, hatches=None):
    boxes = []
    for i, (lab, role) in enumerate(zip(labels, roles)):
        hatch = hatches[i] if hatches else None
        boxes.append(S.node(ax, xs[i], y, NW, NH, lab, role=role, hatch=hatch,
                            weight="bold" if role.startswith("focal") else "normal"))
    for i in range(6):
        S.arrow(ax, xs[i] + NW + 0.02, y + NH / 2, xs[i + 1] - 0.02, y + NH / 2)
    return boxes


def split(ax, x, y0, y1, label_y, color):
    ax.plot([x, x], [y0, y1], color=color, lw=1.0, ls=(0, (3, 2)), zorder=1)
    S.eyebrow(ax, x, label_y, "train | test split", color=color, ha="center", va="top", size=EYE_FS)


def bracket(ax, x0, x1, y, text, color):
    ax.plot([x0, x0, x1, x1], [y + 0.05, y, y, y + 0.05], color=color, lw=0.8, zorder=1)
    ax.text((x0 + x1) / 2, y - 0.04, text, ha="center", va="top", fontsize=7, color=color, style="italic")


def main():
    S.apply()
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

    # (a) leakage-free
    ya = 2.08
    ax.text(X0, ya + NH + 0.20, "(a)", fontsize=7.5, weight="bold", va="bottom", color=S.DD["ink"])
    S.eyebrow(ax, X0 + 0.22, ya + NH + 0.20, "Leakage-free ordering", size=EYE_FS)
    ax.text(X0 + 1.85, ya + NH + 0.20, "partition by subject, then fit every later step on the training fold",
            fontsize=7.2, color=S.DD["ink"], va="bottom")
    row(ax, ya, ["Raw EEG", "Filtering", "Partition\nby subject", "Epoching\n(per fold)",
                 "Connectivity\n(per fold)", "Threshold,\nnormalize\n(train only)", "Train, select\n(train only)"],
        ["backend", "backend", "focal_safe", "backend", "backend", "backend", "backend"])
    sx = xs[2] + NW + GAP / 2
    split(ax, sx, ya - 0.08, ya + NH + 0.10, ya - 0.10, S.DD["link"])
    bracket(ax, xs[3], xs[6] + NW, ya - 0.05, "statistics fit on the training fold only", S.DD["link"])

    # (b) leaking
    yb = 0.78
    ax.text(X0, yb + NH + 0.36, "(b)", fontsize=7.5, weight="bold", va="bottom", color=S.DD["ink"])
    S.eyebrow(ax, X0 + 0.22, yb + NH + 0.36, "Leaking ordering", size=EYE_FS)
    ax.text(X0 + 1.50, yb + NH + 0.36, "statistics computed on pooled data; partition made last, by epoch",
            fontsize=7.2, color=S.DD["ink"], va="bottom")
    roles = ["backend", "backend", "backend", "focal_leak", "focal_leak", "focal_leak", "focal_leak"]
    hatches = [None, None, None, None, None, "////", None]
    row(ax, yb, ["Raw EEG", "Filtering", "Epoching\n(pooled)", "Connectivity\n(all data)",
                 "Threshold,\nnormalize\n(all data)", "Partition\nby epoch", "Train, select\n(on test acc.)"],
        roles, hatches)
    for i, tag in ((3, "L2"), (4, "L3 L4"), (5, "L1"), (6, "L5")):
        cx = xs[i] + NW / 2
        S.pill(ax, cx, yb + NH + 0.13, tag, size=PILL_FS, w=0.40 if " " in tag else 0.26)
    sx = xs[5] + NW + GAP / 2
    split(ax, sx, yb - 0.08, yb + NH + 0.10, yb - 0.10, S.DD["accent"])
    bracket(ax, xs[2], xs[4] + NW, yb - 0.05, "computed on train + test before the split", S.DD["accent"])

    # key strip below a hairline (diagram-design legend rule)
    ax.plot([X0, xs[6] + NW], [0.36, 0.36], color=S.DD["rule"], lw=0.6)
    key = [("L1", "epoch-level split"), ("L2", "connectivity scope"), ("L3", "threshold selection"),
           ("L4", "normalization"), ("L5", "channel or band selection")]
    # measure each label with the renderer, then spread the entries evenly across the diagram width
    r = fig.canvas.get_renderer()
    texts = [ax.text(0, 0, txt, fontsize=7, va="center", color=S.DD["ink"]) for _, txt in key]
    inch = [tx.get_window_extent(r).width / fig.dpi for tx in texts]
    widths = [0.31 + w for w in inch]
    x0, x1 = X0, xs[6] + NW
    gap = (x1 - x0 - sum(widths)) / (len(key) - 1)
    x = x0
    for (tag, _), tx, w in zip(key, texts, widths):
        S.pill(ax, x + 0.13, 0.19, tag, size=PILL_FS, w=0.26)
        tx.set_position((x + 0.31, 0.19))
        x += w + gap
    out = HERE / "fig2_pipeline"
    fig.savefig(out.with_suffix(".pdf"), bbox_inches=None)
    fig.savefig(out.with_suffix(".png"), dpi=300, bbox_inches=None)
    print(f"Wrote {out.name}.pdf and .png at {W} x {H} in")


if __name__ == "__main__":
    main()
