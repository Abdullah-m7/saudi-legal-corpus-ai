#!/usr/bin/env python3
"""Generate the figures for the second-jurisdiction paper.

Two figures, not one panelled image. An earlier version put both panels in a
single file, which the target journal forbids outright: "Do not submit ...
different images or graphs combined into one, as this affects accessibility."
The prohibition is right on its own terms --- a screen reader, and anyone
following a caption, meets a combined image as one undifferentiated object ---
so the panels are separate files with separate captions, and the manuscript
carries the comparison in prose instead.

Figure 1  The composition of the flagged effects, all four states on one linear
          scale. The disproportion is the finding, so the scale stays linear; a
          logarithmic axis would fit all four bars comfortably and destroy it.
Figure 2  The same, excluding the prospective majority, where the three smaller
          categories become legible.

The journal's artwork rules set different thresholds by kind of image, and
these are bar charts: line drawings, not photographs. As bitmaps they would
need 1000 dpi and 7480 pixels at full page width, which the 300 dpi raster
outputs here do not meet. As vector drawings they need neither - the rules ask
only for EPS or PDF. So PDF is the format that goes to the journal, and it is
what the manuscript includes: vector, resolution-independent, and native to
pdflatex, which cannot read EPS at all.

PNG and TIFF are still written, for reading in the repository and for any
venue that asks for a raster.

Deterministic over the analysis results. Run from the repository root, after
analyse_uk.py:

    python3 docs/research/comparison_paper/make_figures.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "uk_analysis_results.json"

SERIES_1 = "#2a78d6"
INK = "#0b0b0b"
INK_2 = "#52514e"
SURFACE = "#fcfcfb"
GRID = "#e3e2df"

plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 9,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})

ORDER = [
    ("prospective", "Prospective\n(no date)"),
    ("commencement_scheduled", "Commencement\nscheduled, future"),
    ("in_force", "In force now,\nnot applied"),
    ("in_force_undated", "In force,\nno date"),
]


def panel(ax, keys, states, total, title):
    labels = [lab for k, lab in keys]
    values = [states.get(k, 0) for k, _ in keys]
    y = range(len(keys))
    ax.barh(list(y), values, height=0.58, color=SERIES_1, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8.2)
    ax.invert_yaxis()
    # Headroom for the value labels, which sit outside the bars. The first
    # render clipped "93.0% of all flagged" against the right edge; the label
    # is shorter now and the margin larger.
    ax.set_xlim(0, max(values) * 1.42)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    for i, v in enumerate(values):
        ax.text(v + max(values) * 0.018, i,
                f"{v:,}   {v / total * 100:.1f}%",
                va="center", fontsize=8.4, color=INK)
    ax.set_title(title, fontsize=9.2, color=INK, loc="left", pad=8)


def draw(keys, states, total, title, subtitle, stem, height):
    labels = [lab for k, lab in keys]
    values = [states.get(k, 0) for k, _ in keys]

    # Full page width at the journal's minimum of 2244 px: 7.6 in at 300 dpi
    # gives 2280, which clears it without inflating the file.
    fig, ax = plt.subplots(figsize=(7.6, height))
    y = range(len(keys))
    ax.barh(list(y), values, height=0.58, color=SERIES_1, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8.6)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.42)
    ax.set_xlabel("Effects")
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    for i, v in enumerate(values):
        ax.text(v + max(values) * 0.018, i, f"{v:,}   {v / total * 100:.1f}%",
                va="center", fontsize=8.6, color=INK)

    ax.set_title(f"{title}\n{subtitle}", fontsize=9.6, color=INK, loc="left",
                 pad=10)
    fig.subplots_adjust(left=0.215, right=0.975, top=0.80, bottom=0.17)
    for ext in ("pdf", "eps", "png", "tiff"):
        fig.savefig(HERE / f"{stem}.{ext}", dpi=300 if ext in ("png", "tiff") else None)
    plt.close(fig)
    return HERE / f"{stem}.png"


def figures(results):
    states = results["unincorporated"]["flagged_effects_by_state"]
    total = sum(states.values())
    rest = total - states.get("prospective", 0)
    a = draw(ORDER, states, total,
             "What a flag of \u201cnot applied\u201d actually means",
             f"All {total:,} flagged effects, UK Public General Acts "
             f"1988\u20132026",
             "fig1_all_flagged_effects", 3.0)
    b = draw(ORDER[1:], states, total,
             "The same, excluding the prospective majority",
             f"{rest:,} effects; percentages remain of the full {total:,}",
             "fig2_excluding_prospective", 2.9)
    return a, b


def main():
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    for path in figures(results):
        print("wrote", path.name)
    print("two separate files: the journal forbids combining graphs into one "
          "image")


if __name__ == "__main__":
    main()
