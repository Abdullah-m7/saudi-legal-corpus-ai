#!/usr/bin/env python3
"""Generate the figures for the provenance paper.

Figure 1  What it took to obtain the text: the five kinds of friction the
          build record documents, as a share of articles and of instruments.
          Both are shown because they answer different questions --- how much
          of the corpus is affected, and how many instruments are.
Figure 2  The verification tiers, weighted by article. The tiers are ordinal
          (strongest to weakest evidence), so they take a single-hue
          sequential ramp rather than categorical colours; that also survives
          greyscale printing, which a four-hue stack would not.

Deterministic over the analysis results. Run from the repository root, after
provenance_analysis.py:

    python3 docs/research/provenance_paper/make_figures.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "provenance_analysis_results.json"

# Categorical slots 1 and 2 for the two series in figure 1, and four steps of
# the sequential blue ramp for the ordinal tiers in figure 2.
SERIES_1 = "#2a78d6"
SERIES_2 = "#eb6834"
RAMP = ["#0d366b", "#2a78d6", "#86b6ef", "#cde2fb"]
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

LABELS = {
    "official_source_unreachable": "Official source\nunreachable",
    "reached_through_a_web_archive": "Reached through\na web archive",
    "single_source_only": "Single source only",
    "required_optical_or_visual_reconstruction": "Needed optical or\nvisual reconstruction",
    "defect_in_the_official_source": "Defect in the\nofficial source",
}

TIER_LABELS = {
    "TIER_1_PRIMARY_MULTI_SOURCE": "Two or more official sources",
    "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED": "One official, cross-checked",
    "TIER_3_SECONDARY_MULTI_SOURCE_ONLY": "Official unreachable;\nsecondary only",
    "TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE": "Single source or\nmixed confidence",
}


def figure_one(results):
    m = results["provenance_layer"]["measures"]
    keys = list(LABELS)
    keys.sort(key=lambda k: m[k]["article_share"])
    articles = [m[k]["article_share"] * 100 for k in keys]
    tracks = [m[k]["track_share"] * 100 for k in keys]

    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    y = range(len(keys))
    h = 0.36
    ax.barh([i + h / 2 for i in y], articles, height=h, color=SERIES_1,
            zorder=3, label="of articles")
    ax.barh([i - h / 2 for i in y], tracks, height=h, color=SERIES_2,
            zorder=3, label="of instruments")

    ax.set_yticks(list(y))
    ax.set_yticklabels([LABELS[k] for k in keys], fontsize=8.4)
    ax.set_xlabel("Share of the corpus (%)")
    ax.set_xlim(0, max(max(articles), max(tracks)) * 1.30)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for i, (a, t) in enumerate(zip(articles, tracks)):
        ax.text(a + 0.5, i + h / 2, f"{a:.1f}%", va="center", fontsize=8,
                color=INK)
        ax.text(t + 0.5, i - h / 2, f"{t:.1f}%", va="center", fontsize=8,
                color=INK_2)

    ax.legend(handles=[Patch(facecolor=SERIES_1, label="Share of articles"),
                       Patch(facecolor=SERIES_2, label="Share of instruments")],
              loc="lower right", frameon=False, fontsize=8.2,
              handlelength=1.1, handleheight=1.1)
    n = results["provenance_layer"][
        "articles_whose_status_is_a_provenance_statement"]
    ax.set_title("What it took to obtain the official text\n"
                 f"({n:,} articles whose build record names its sources)",
                 fontsize=9.5, color=INK, loc="left", pad=10)
    fig.tight_layout()
    fig.savefig(HERE / "fig1_access.png", dpi=300)
    fig.savefig(HERE / "fig1_access.tiff", dpi=300)
    fig.savefig(HERE / "fig1_access.eps", format="eps")
    plt.close(fig)
    return HERE / "fig1_access.png"


def figure_two(results):
    t = results["verification_tiers"]
    order = list(TIER_LABELS)
    shares = [t["article_share_by_tier"][k] * 100 for k in order]
    counts = [t["articles_by_tier"][k] for k in order]

    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    left = 0.0
    for share, colour in zip(shares, RAMP):
        ax.barh([0], [share], left=left, height=0.44, color=colour,
                edgecolor=SURFACE, linewidth=1.6, zorder=3)
        left += share

    # Only segments with room take an inside label; every value appears in the
    # legend, so a narrow segment loses nothing by staying blank.
    left = 0.0
    for share, colour in zip(shares, RAMP):
        if share >= 8:
            dark = colour in RAMP[:2]
            ax.text(left + share / 2, 0, f"{share:.1f}%", ha="center",
                    va="center", fontsize=9,
                    color=SURFACE if dark else INK)
        left += share

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.45, 0.45)
    ax.set_yticks([])
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xticklabels([f"{v}%" for v in (0, 20, 40, 60, 80, 100)],
                       fontsize=8.2)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0)

    ax.legend(handles=[Patch(facecolor=c,
                             label=f"{TIER_LABELS[k]} — {sh:.1f}%"
                             .replace("\n", " "))
                       for k, c, sh in zip(order, RAMP, shares)],
              loc="upper left", bbox_to_anchor=(0.0, -0.30), ncol=2,
              frameon=False, fontsize=8, handlelength=1.1, handleheight=1.1,
              columnspacing=1.4, labelspacing=0.5)

    weak = t["share_without_a_cross_verified_official_primary"] * 100
    ax.set_title("Strength of the evidence behind the text, by article\n"
                 f"({weak:.1f}% has no cross-verified official primary)",
                 fontsize=9.5, color=INK, loc="left", pad=10)
    fig.tight_layout()
    fig.savefig(HERE / "fig2_tiers.png", dpi=300)
    fig.savefig(HERE / "fig2_tiers.tiff", dpi=300)
    fig.savefig(HERE / "fig2_tiers.eps", format="eps")
    plt.close(fig)
    return HERE / "fig2_tiers.png"


def main():
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    print("wrote", figure_one(results))
    print("wrote", figure_two(results))


if __name__ == "__main__":
    main()
