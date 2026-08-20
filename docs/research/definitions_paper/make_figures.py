#!/usr/bin/env python3
"""Figures for the definitional-fragmentation paper.

Figure 1  The funnel from all defined terms to the legally significant
          residue, showing how much each filtering step removes.
Figure 2  Lexical similarity of shared substantive definitions against the
          hand-adjudicated verdict, showing that low lexical similarity does
          not imply substantive conflict.

Single-hue and print-safe. Run after definition_analysis.py:

    python3 docs/research/definitions_paper/make_figures.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "definition_analysis_results.json"

# Terms are labelled by English gloss and romanization: the journal's readers
# do not read Arabic script, and matplotlib does not shape right-to-left text.
GLOSS = {
    "الشخص": "person (al-shakhs)",
    "الترخيص": "licence (al-tarkhis)",
    "المرخص له": "licensee (al-murakhkhas lahu)",
    "المملكة": "the Kingdom (al-mamlakah)",
    "المستهلك": "consumer (al-mustahlik)",
    "التصريح": "permit (al-tasrih)",
    "النشاط": "activity (al-nashat)",
    "المنشأة": "establishment (al-munsha'ah)",
    "مقدم الخدمة": "service provider (muqaddim al-khidmah)",
    "الجهات ذات العلاقة": "relevant bodies (al-jihat dhat al-alaqah)",
    "الجهة المشرفة": "supervising body (al-jihah al-mushrifah)",
    "صاحب العمل": "employer (sahib al-amal)",
}

SERIES_1 = "#2a78d6"
SERIES_MUTED = "#9ec5f4"
INK = "#0b0b0b"
INK_2 = "#52514e"
SURFACE = "#fcfcfb"
GRID = "#e3e2df"

plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 9,
    "axes.edgecolor": GRID, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK_2, "ytick.color": INK_2,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def figure_one(r):
    steps = [
        ("Defined terms", r["corpus"]["terms_total"]),
        ("Substantive (non-indexical)", r["kind_split"]["substantive_terms"]),
        ("Shared by >1 instrument", r["multi_instrument"]["of_which_substantive"]),
        ("Lexically divergent", r["divergence_among_substantive"]["divergent"]),
    ]
    labels = [s[0] for s in steps][::-1]
    values = [s[1] for s in steps][::-1]

    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    y = range(len(values))
    ax.barh(y, values, height=0.6, color=SERIES_1, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels)
    ax.set_xlabel("Terms")
    ax.set_xscale("log")
    ax.set_xlim(1, max(values) * 2.2)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
    for i, v in enumerate(values):
        ax.text(v * 1.12, i, f"{v:,}", va="center", fontsize=8.5, color=INK)
    ax.set_title("From defined terms to the divergent residue\n"
                 "(log scale; each step is a filter, not a partition)",
                 fontsize=9.5, color=INK, loc="left", pad=10)
    fig.tight_layout()
    out = HERE / "fig1_funnel.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def figure_two(r):
    rows = r["hand_adjudication_of_most_shared_substantive_terms"]["assignments"]
    order = ["conflicting", "homonymous", "instrument_local", "indexical_missed",
             "harmonized"]
    pretty = {"conflicting": "Materially conflicting scope",
              "homonymous": "Homonymy (different concepts)",
              "instrument_local": "Instrument-local referent",
              "indexical_missed": "Indexical (missed by the filter)",
              "harmonized": "Harmonized (wording varies only)"}
    rows = sorted(rows, key=lambda x: (order.index(x["class"]), -x["instruments"]))
    rows = rows[::-1]

    labels = [GLOSS.get(x["term"], x["term"]) for x in rows]
    values = [x["instruments"] for x in rows]
    colors = [SERIES_1 if x["class"] == "conflicting" else SERIES_MUTED
              for x in rows]

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    y = range(len(rows))
    ax.barh(y, values, height=0.62, color=colors, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Instruments defining the term")
    ax.set_xlim(0, max(values) * 1.75)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
    for i, x in enumerate(rows):
        ax.text(x["instruments"] + max(values) * 0.02, i,
                pretty[x["class"]], va="center", fontsize=7.4,
                color=INK if x["class"] == "conflicting" else INK_2)
    ax.set_title("The twelve most widely shared substantive terms,\n"
                 "classified by hand (highlighted: materially conflicting)",
                 fontsize=9.5, color=INK, loc="left", pad=10)
    fig.tight_layout()
    out = HERE / "fig2_adjudication.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def main():
    r = json.load(open(RESULTS, encoding="utf-8"))
    print("wrote", figure_one(r))
    print("wrote", figure_two(r))


if __name__ == "__main__":
    main()
