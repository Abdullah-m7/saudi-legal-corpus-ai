#!/usr/bin/env python3
"""Generate the figures for the legislative-churn paper.

Figure 1  The instruments that changed most, split by how they changed. The
          split matters: some instruments are amended, some are hollowed out
          by repeal, one is mostly additions --- and a single "changed" bar
          would hide that.
Figure 2  Mean churn rate across three citation tiers.

Both carry direct value labels, so magnitude survives greyscale printing, and
figure 1 carries a legend so identity is never colour alone. Deterministic
over the analysis results. Run from the repository root, after
amendment_analysis.py:

    python3 docs/research/amendment_paper/make_figures.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "amendment_analysis_results.json"

# Categorical slots 1-3 of the validated reference palette, checked as a set
# for this chart: all-pairs CVD delta-E 9.2, normal-vision 24.0, lightness band
# and chroma floor both pass. Aqua sits below 3:1 against the surface, which is
# why every bar carries a visible total and the segments carry a legend.
AMENDED = "#2a78d6"
REPEALED = "#eb6834"
ADDED = "#1baf7a"
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

SHORT = {
    "Law of Sharia Procedure": "Sharia Procedure Law",
    "Implementing Regulation of the Saudi Arabian VAT Law": "VAT Regulation",
    "Implementing Regulation of the Saudi Arabian Income Tax Law":
        "Income Tax Regulation",
    "Implementing Regulation of the Privatization Law":
        "Privatization Regulation",
    "Implementing Regulation of the Commercial Agencies Law":
        "Commercial Agencies Regulation",
    "Certified/Accredited Valuers Law": "Accredited Valuers Law",
    "Saudi Arabian Civil Status Law": "Civil Status Law",
}


def figure_one(results):
    cc = results["churn_concentration"]
    rows = cc["most_changed_instruments"][:12]
    shown = sum(r["changed"] for r in rows)
    remainder = cc["changed_articles_total"] - shown
    others = cc["instruments"] - len(rows)
    rows = list(reversed(rows))

    labels = [SHORT.get(r["title_en"], (r["title_en"] or r["track_id"])[:30])
              for r in rows]
    amended = [r["amended"] for r in rows]
    repealed = [r["repealed"] for r in rows]
    added = [r["added"] for r in rows]
    totals = [r["changed"] for r in rows]

    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    y = range(len(rows))
    # A surface-coloured edge puts a visible gap between adjacent segments.
    common = dict(height=0.62, zorder=3, edgecolor=SURFACE, linewidth=1.4)
    ax.barh(y, amended, color=AMENDED, **common)
    ax.barh(y, repealed, left=amended, color=REPEALED, **common)
    ax.barh(y, added, left=[a + r for a, r in zip(amended, repealed)],
            color=ADDED, **common)

    ax.set_yticks(list(y))
    ax.set_yticklabels(labels)
    ax.set_xlabel("Articles no longer in their original form")
    ax.set_xlim(0, max(totals) * 1.22)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for i, total in enumerate(totals):
        ax.text(total + max(totals) * 0.015, i, str(total), va="center",
                fontsize=8.5, color=INK)

    ax.legend(handles=[Patch(facecolor=AMENDED, label="Amended"),
                       Patch(facecolor=REPEALED, label="Repealed"),
                       Patch(facecolor=ADDED, label="Added")],
              loc="lower right", frameon=False, fontsize=8.2,
              handlelength=1.1, handleheight=1.1)

    ax.set_title(
        "The twelve most changed instruments, by how they changed\n"
        f"(the other {others} instruments hold {remainder} between them)",
        fontsize=9.5, color=INK, loc="left", pad=10)
    fig.tight_layout()
    fig.savefig(HERE / "fig1_churn.png", dpi=300)
    fig.savefig(HERE / "fig1_churn.eps", format="eps")
    # The journal's preferred artwork formats are PS, JPEG, TIFF or Word, at
    # 300 dpi for colour; EPS is not on that list, so ship TIFF as well.
    fig.savefig(HERE / "fig1_churn.tiff", dpi=300)
    plt.close(fig)
    return HERE / "fig1_churn.png"


def figure_two(results):
    cac = results["churn_against_citation"]
    tiers = [
        (f"Not cited\n({cac['uncited_instruments']} instruments)",
         cac["mean_churn_rate_uncited"]),
        (f"Cited\n({cac['cited_instruments']} instruments)",
         cac["mean_churn_rate_cited"]),
        ("15 most cited", cac["mean_churn_rate_top_15_most_cited"]),
    ]
    labels = [t[0] for t in tiers]
    values = [t[1] * 100 for t in tiers]

    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    x = range(len(tiers))
    ax.bar(x, values, width=0.56, color=SERIES_1, zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8.4)
    ax.set_ylabel("Mean share of articles changed (%)")
    ax.set_ylim(0, max(values) * 1.28)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="x", length=0)

    for i, v in enumerate(values):
        ax.text(i, v + max(values) * 0.03, f"{v:.1f}%", ha="center",
                fontsize=8.8, color=INK)

    ax.set_title("Instruments other instruments rely on change more\n"
                 f"({cac['instruments_compared_min_20_articles']} instruments "
                 "of at least 20 articles)",
                 fontsize=9.5, color=INK, loc="left", pad=10)
    fig.tight_layout()
    fig.savefig(HERE / "fig2_citation_tiers.png", dpi=300)
    fig.savefig(HERE / "fig2_citation_tiers.eps", format="eps")
    fig.savefig(HERE / "fig2_citation_tiers.tiff", dpi=300)
    plt.close(fig)
    return HERE / "fig2_citation_tiers.png"


def main():
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    print("wrote", figure_one(results))
    print("wrote", figure_two(results))


if __name__ == "__main__":
    main()
