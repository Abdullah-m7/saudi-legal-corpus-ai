#!/usr/bin/env python3
"""Generate the figure for the second-jurisdiction paper.

There is one figure, and the reason there is only one is worth stating.

The paper's finding is a composition: of the effects the service flags as not
applied to its displayed text, almost all are law that has not yet come into
force. Figure 1 shows that composition, in two panels on the same linear scale
--- the whole population, then the sliver that is not prospective, where the
three small categories become legible. A log scale would have fitted all four
bars comfortably and destroyed the finding, which is the disproportion itself.

The second figure this paper was going to carry does not exist, because the
data it would plot has one value. Every in-force unapplied effect in the modern
statute book --- all 99 with a commencement date --- came into force on the same
day, three weeks before the analysis date, in two related Acts. A distribution
of ninety-nine identical points is not a chart; it is a sentence, and the
article states it as one.

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


def figure_one(results):
    states = results["unincorporated"]["flagged_effects_by_state"]
    total = sum(states.values())
    rest = total - states.get("prospective", 0)

    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(6.8, 5.2),
        gridspec_kw={"height_ratios": [1, 1.4], "hspace": 0.62})

    panel(top, ORDER, states, total,
          f"All {total:,} effects the service flags as not applied "
          f"(per cent of that total)")
    panel(bottom, ORDER[1:], states, total,
          f"The same, excluding the prospective majority "
          f"({rest:,} effects)")
    bottom.set_xlabel("Effects")

    fig.suptitle("What a flag of “not applied” actually means\n"
                 "UK Public General Acts, 1988–2026",
                 fontsize=10, color=INK, x=0.015, ha="left", y=0.98)
    # Explicit margins, not tight_layout: with two-line y-labels it warns that
    # it cannot lay the axes out and then silently clips them, which is how the
    # first render lost the left half of every category name.
    fig.subplots_adjust(left=0.215, right=0.975, top=0.855, bottom=0.085,
                        hspace=0.55)
    for ext in ("png", "tiff", "eps"):
        fig.savefig(HERE / f"fig1_what_the_flag_means.{ext}",
                    dpi=300 if ext != "eps" else None,
                    format="eps" if ext == "eps" else None)
    plt.close(fig)
    return HERE / "fig1_what_the_flag_means.png"


def main():
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    print("wrote", figure_one(results))
    print("no second figure: the in-force effects share a single commencement "
          "date, so their\n  distribution has one value and belongs in the "
          "text, not a chart")


if __name__ == "__main__":
    main()
