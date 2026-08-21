#!/usr/bin/env python3
"""Generate the figures for the second-jurisdiction paper.

Figure 1  How old the amendments are that the service has not yet applied to
          the text it displays, in bands. The publisher's own target is three
          months from coming into force, so the first band is already outside
          it; the question the figure answers is how much sits far beyond.
Figure 2  Whether those records are neglected or merely queued: when the
          service last revised each affected Act, against how old the oldest
          amendment it has still not applied is.

Two deliberate departures from the obvious choices.

Figure 1 uses **one colour, not the sequential ramp**. The bands are ordered,
which tempts a ramp, but bar length already carries the magnitude; colouring by
band would encode the same ordering twice and imply a second variable that does
not exist. The ramp belongs in figure 2, where cell colour *is* the magnitude
and nothing else carries it.

Figure 2's ramp is continuous rather than five fixed steps. Its relative
luminance runs 0.038 to 0.743 without reversing, so it survives greyscale
printing --- but the fixed steps are unevenly spaced in luminance (gaps of 0.05
at the dark end against 0.30 at the light end), which would read as uneven
magnitude. Interpolating between the endpoints avoids that. Cells carry printed
counts as well, which is also the required relief for the light end of any
sequential ramp: at the palest steps the contrast against the surface falls
below 3:1, so colour alone cannot be the only encoding.

Deterministic over the analysis results. Run from the repository root, after
analyse_uk.py:

    python3 docs/research/comparison_paper/make_figures.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "uk_analysis_results.json"

SERIES_1 = "#2a78d6"
RAMP_DARK = "#0d366b"
RAMP_LIGHT = "#cde2fb"
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

BAND_ORDER = ["under 5 years", "5-9", "10-19", "20-29", "30 or more"]
BAND_LABELS = {
    "under 5 years": "under 5 years",
    "5-9": "5 to 9 years",
    "10-19": "10 to 19 years",
    "20-29": "20 to 29 years",
    "30 or more": "30 years or more",
}


def figure_one(results):
    bands = results["effects_by_age_band_of_affecting_instrument"]
    total = sum(bands.values()) or 1
    values = [bands.get(k, 0) for k in BAND_ORDER]

    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    y = range(len(BAND_ORDER))
    ax.barh(list(y), values, height=0.6, color=SERIES_1, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels([BAND_LABELS[k] for k in BAND_ORDER], fontsize=8.6)
    ax.invert_yaxis()
    ax.set_xlabel("Amendments enacted but not incorporated")
    ax.set_xlim(0, max(values) * 1.22 if values else 1)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for i, v in enumerate(values):
        ax.text(v + max(values) * 0.015, i, f"{v:,}  ({v / total * 100:.0f}%)",
                va="center", fontsize=8.2, color=INK)

    ax.set_title("Age of the amending instrument, for amendments the service\n"
                 "has not applied to the text it displays "
                 f"({total:,} amendments)",
                 fontsize=9.5, color=INK, loc="left", pad=10)
    fig.tight_layout()
    for ext in ("png", "tiff", "eps"):
        fig.savefig(HERE / f"fig1_age_bands.{ext}",
                    dpi=300 if ext != "eps" else None,
                    format="eps" if ext == "eps" else None)
    plt.close(fig)
    return HERE / "fig1_age_bands.png"


def figure_two(results):
    cross = results["acts_by_last_revised_year_and_oldest_effect_decade"]
    if not cross:
        return None
    cells = [(int(k.split("|")[0]), int(k.split("|")[1]), v)
             for k, v in cross.items()]
    # Every year between the first and last, not only the years that happen to
    # have data. Plotting the occupied years alone would put 2019 next to 2022
    # and present a gap as continuity --- a time axis that lies about its own
    # spacing.
    years = list(range(min(y for y, _, _ in cells),
                       max(y for y, _, _ in cells) + 1))
    decades = sorted({d for _, d, _ in cells})
    grid = [[0] * len(years) for _ in decades]
    for y, d, v in cells:
        grid[decades.index(d)][years.index(y)] = v

    cmap = LinearSegmentedColormap.from_list("seq", [RAMP_LIGHT, RAMP_DARK])
    # An empty cell is not a small value. Left to the ramp it takes the palest
    # step and reads as "a few"; masked, it takes the surface and reads as
    # nothing, which is what it is.
    cmap.set_bad(SURFACE)
    masked = [[(v if v else float("nan")) for v in row] for row in grid]

    fig, ax = plt.subplots(figsize=(6.9, 0.52 * len(decades) + 2.3))
    top = max(v for _, _, v in cells)
    import numpy as np
    ax.imshow(np.ma.masked_invalid(np.array(masked, dtype=float)),
              cmap=cmap, aspect="auto", vmin=0, vmax=top)

    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([str(y) if y % 2 == 0 else "" for y in years],
                       fontsize=8, rotation=45, ha="right")
    ax.set_yticks(range(len(decades)))
    ax.set_yticklabels([f"{d}-{d + 9} years" if d else "under 10 years"
                        for d in decades], fontsize=8.4)
    ax.set_xlabel("Year the service last revised the Act")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)

    # Printed counts are the relief the palest cells need: below about 3:1
    # against the surface, colour alone stops being readable.
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v:
                ax.text(c, r, str(v), ha="center", va="center", fontsize=7.6,
                        color=SURFACE if v > top * 0.55 else INK)

    # The last column is a part-year, and saying so matters in the direction
    # that works against the reading: it holds the most Acts despite covering
    # the fewest months.
    ax.set_title("Maintained, and still out of date\n"
                 "Affected Acts by when the service last revised them and how "
                 f"old\ntheir oldest unapplied amendment is "
                 f"({years[-1]} is a part-year, to {results['as_of']})",
                 fontsize=9.5, color=INK, loc="left", pad=10)
    fig.tight_layout()
    for ext in ("png", "tiff", "eps"):
        fig.savefig(HERE / f"fig2_maintained_and_stale.{ext}",
                    dpi=300 if ext != "eps" else None,
                    format="eps" if ext == "eps" else None)
    plt.close(fig)
    return HERE / "fig2_maintained_and_stale.png"


def main():
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    print("wrote", figure_one(results))
    print("wrote", figure_two(results))


if __name__ == "__main__":
    main()
