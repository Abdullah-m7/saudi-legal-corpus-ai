#!/usr/bin/env python3
"""Generate the figures for the citation-network paper.

Figure 1  Horizontal citations received by the most-cited instruments, with
          the number of distinct citing instruments shown alongside, so that
          depth (many citations from few sources) is visibly separated from
          breadth (citations from many sources).
Figure 2  Domain-to-domain citation flows as a single-hue sequential heatmap.

Both are single-hue and print-safe in greyscale. Deterministic over the
analysis results. Run from the repository root, after network_analysis.py:

    python3 docs/research/network_paper/make_figures.py
"""

import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "network_analysis_results.json"

# Sequential blue ramp, steps 100 -> 700 (validated reference palette).
BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
        "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281",
        "#0d366b"]
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
    "Saudi Companies Law": "Companies Law",
    "Saudi Labor Law": "Labour Law",
    "Capital Market Law": "Capital Market Law",
    "Law of Sharia Procedure": "Sharia Procedure Law",
    "Bankruptcy Law": "Bankruptcy Law",
    "Law of Criminal Procedure": "Criminal Procedure Law",
    "Environmental Law": "Environmental Law",
    "Real Estate In-Kind Registration Law": "Real Estate Registration Law",
    "Telecommunications and Information Technology Act":
        "Telecommunications Act",
    "Electronic Transactions Law": "Electronic Transactions Law",
    "Law of the Judiciary": "Judiciary Law",
    "Law of the Board of Grievances": "Board of Grievances Law",
}

DOMAIN_SHORT = {
    "Courts, procedure and enforcement": "Courts & procedure",
    "Commercial and corporate": "Commercial",
    "Financial and capital markets": "Financial",
    "Civil, personal status and property": "Civil & property",
    "Health, environment and safety": "Health & environment",
    "Energy, industry and infrastructure": "Energy & infrastructure",
    "Criminal justice, security and civil status": "Criminal & security",
    "Technology, data, telecommunications and IP": "Technology & IP",
    "Education, culture, media and civil society": "Education & culture",
    "Labor and social insurance": "Labour",
    "Tax and zakat": "Tax & zakat",
    "Constitutional and administrative": "Constitutional",
}


def figure_one(results):
    rows = results["vertical_vs_horizontal"]["horizontal_most_cited"][:12]
    rows = list(reversed(rows))
    labels = [SHORT.get(r["title_en"], r["title_en"][:32]) for r in rows]
    cites = [r["citations"] for r in rows]
    sources = [r["distinct_citing_instruments"] for r in rows]

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    y = range(len(rows))
    ax.barh(y, cites, height=0.62, color=SERIES_1, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels)
    ax.set_xlabel("Horizontal citations received")
    ax.set_xlim(0, max(cites) * 1.28)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)

    # Direct labels: total, then the breadth figure that qualifies it.
    for i, (c, s) in enumerate(zip(cites, sources)):
        ax.text(c + max(cites) * 0.02, i, f"{c}", va="center",
                fontsize=8.5, color=INK)
        ax.text(c + max(cites) * 0.09, i, f"(from {s})", va="center",
                fontsize=7.6, color=INK_2)
    ax.set_title(
        "Citations received from other instrument families\n"
        "(parenthesis: number of distinct citing instruments)",
        fontsize=9.5, color=INK, loc="left", pad=10)
    fig.tight_layout()
    out = HERE / "fig1_hubs.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def figure_two(results):
    flows_raw = results["domain_flows"]["all_flows"]
    pairs = defaultdict(int)
    domains = set()
    for key, v in flows_raw.items():
        a, b = key.split(" -> ")
        pairs[(a, b)] = v
        domains.update((a, b))

    order = sorted(domains, key=lambda d: -sum(
        v for (x, y), v in pairs.items() if x == d or y == d))
    n = len(order)
    matrix = [[pairs.get((order[i], order[j]), 0) for j in range(n)]
              for i in range(n)]

    cmap = LinearSegmentedColormap.from_list("blue_seq", BLUE)
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    vmax = max(max(r) for r in matrix)
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=vmax)

    labels = [DOMAIN_SHORT.get(d, d) for d in order]
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Cited domain", fontsize=9)
    ax.set_ylabel("Citing domain", fontsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)

    # Cell values: dark ink on light cells, surface ink on dark cells.
    for i in range(n):
        for j in range(n):
            v = matrix[i][j]
            if v:
                ax.text(j, i, str(v), ha="center", va="center", fontsize=7.2,
                        color=SURFACE if v > vmax * 0.55 else INK)
    ax.set_xticks([x - 0.5 for x in range(1, n)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, n)], minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=2)

    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cb.set_label("Citations", fontsize=8)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=7.5)
    ax.set_title("Citation flows between legal domains", fontsize=9.5,
                 color=INK, loc="left", pad=10)
    fig.tight_layout()
    out = HERE / "fig2_domain_flows.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def main():
    results = json.load(open(RESULTS, encoding="utf-8"))
    print("wrote", figure_one(results))
    print("wrote", figure_two(results))


if __name__ == "__main__":
    main()
