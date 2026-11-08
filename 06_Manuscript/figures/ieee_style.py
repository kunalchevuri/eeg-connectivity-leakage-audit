"""Shared figure style for all four figures (REVIEW 2026-09-27, round 3).

Combines two published design systems, adapted to an IEEE two-column page:
- Data plots follow figures4papers (github.com/ChenLiu-1996/figures4papers, scientific-figure-making skill):
  its semantic palette (blue = key/safe, greens = positive, reds = contrast/risk, neutral = background),
  top/right spines off, frameless legends, black bar edges, values printed in place, tight y-limits,
  hatching for print-safe separation.
- Diagrams follow diagram-design (github.com/cathrynlavery/diagram-design, style-guide.md): one accent reserved
  for the 1-2 focal elements (here: the leakage points), semantic node treatments instead of decoration,
  mono uppercase "eyebrow" labels for tags, labels never on connectors, legend as a strip below a hairline,
  no shadows, low density.
Sizes are scaled for print: text lands at 7-8 pt at the size LaTeX places the figure. Fonts are embedded as
TrueType (pdf.fonttype 42), which IEEE PDF eXpress accepts. Every color also differs in luminance, so each
figure still reads in grayscale.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

COL_W, TEXT_W = 3.5, 7.16

# figures4papers semantic palette (api.md / design-theory.md)
F4P = {
    "blue_main": "#0F4D92", "blue_secondary": "#3775BA",
    "green_1": "#DDF3DE", "green_2": "#AADCA9", "green_3": "#8BCF8B",
    "red_1": "#F6CFCB", "red_2": "#E9A6A1", "red_strong": "#B64342",
    "neutral": "#CFCECE", "gray": "#767676", "dark": "#4D4D4D", "ink": "#272727",
    "teal": "#42949E", "violet": "#9A4D8E",
}

# diagram-design semantic roles (style-guide.md), with the accent mapped to the figures4papers red
DD = {
    "paper": "#FFFFFF",          # print: pure white page (IEEE), not the web skin's white-smoke
    "ink": "#2D3142", "muted": "#4F5D75", "soft": "#7A8399", "rule": "#BFC0C0",
    "accent": F4P["red_strong"], "accent_tint": "#FBEDEB",
    "link": F4P["blue_main"], "link_tint": "#E7EEF7",
    "external_fill": "#F6F6F7", "external_stroke": "#A9AEBB",
}

# category colors shared by Fig. 3 (and the pipeline figure's meaning): safe / leak / not performed / unclear
CATEGORY = {
    "safe": F4P["green_3"],       # luminance ~0.73
    "leak": F4P["red_strong"],    # ~0.33
    "none": "#E4E4E4",            # ~0.89
    "unclear": "#FFFFFF",         # white + dot hatch
}
# rating colors for Fig. 4 (same semantics: green = leakage-free ... red = leakage-likely)
RATING = {"free": "#3E8E47", "possible": F4P["blue_secondary"], "likely": F4P["red_strong"],
          "unclear": F4P["gray"]}

SANS = ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"]
MONO = ["Liberation Mono", "DejaVu Sans Mono"]


def apply():
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": SANS, "font.monospace": MONO,
        "mathtext.fontset": "dejavusans",
        "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
        "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.8, "axes.edgecolor": DD["ink"], "axes.labelcolor": DD["ink"],
        "xtick.color": DD["ink"], "ytick.color": DD["ink"],
        "xtick.major.width": 0.8, "ytick.major.width": 0.8, "xtick.major.size": 3, "ytick.major.size": 3,
        "legend.frameon": False, "hatch.linewidth": 0.5,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "savefig.dpi": 600, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    })


# ---- diagram primitives (diagram-design) -------------------------------------------------------------
NODE = {  # role -> (fill, stroke, linewidth, linestyle, text color)
    "backend": ("#FFFFFF", DD["ink"], 0.8, "-", DD["ink"]),
    "focal_safe": (DD["link_tint"], DD["link"], 1.2, "-", DD["link"]),
    "focal_leak": (DD["accent_tint"], DD["accent"], 1.2, "-", DD["accent"]),
    "external": (DD["external_fill"], DD["external_stroke"], 0.7, "-", DD["muted"]),
    "limitation": (DD["accent_tint"], DD["accent"], 0.9, (0, (3, 2)), DD["accent"]),
}


def node(ax, x, y, w, h, text, role="backend", size=7.5, weight="normal", align="center", hatch=None, r=0.035):
    fill, stroke, lw, ls, tcol = NODE[role]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", facecolor=fill,
                                edgecolor=stroke, linewidth=lw, linestyle=ls, hatch=hatch, zorder=2))
    tx = x + w / 2 if align == "center" else x + 0.06
    t = ax.text(tx, y + h / 2, text, ha=align, va="center", fontsize=size, color=tcol, weight=weight,
                linespacing=1.12, zorder=4)
    if hatch:  # keep label legible over hatching
        t.set_bbox(dict(boxstyle="round,pad=0.12,rounding_size=0.03", fc=fill, ec="none"))
    return (x, y, w, h)


def eyebrow(ax, x, y, text, color=None, size=6.3, ha="left", va="bottom"):
    """Mono, uppercase, tracked tag (diagram-design 'eyebrow')."""
    ax.text(x, y, text.upper(), ha=ha, va=va, fontsize=size,
            family="monospace", color=color or DD["muted"], zorder=4)


def pill(ax, cx, cy, text, color=None, size=6.5, w=0.30, h=0.15):
    color = color or DD["accent"]
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.07",
                                facecolor=color, edgecolor="none", zorder=5))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=size, family="monospace", weight="bold",
            color="white", zorder=6)


def arrow(ax, x0, y0, x1, y1, color=None, lw=0.8):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=3,
                arrowprops=dict(arrowstyle="-|>,head_length=0.35,head_width=0.18", lw=lw,
                                color=color or DD["muted"], shrinkA=0, shrinkB=0))
