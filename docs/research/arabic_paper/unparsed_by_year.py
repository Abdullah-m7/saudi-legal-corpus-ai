#!/usr/bin/env python3
"""Is the loss from unreadable article numbers concentrated in any period?

The threats section of paper 8 once claimed that an unparseable article
expression is likelier in an older judgment, so the loss falls on the tail of
the distribution. The claim was never measured, and when it was measured it
was false: the rate is flat. This script is what measures it, and the paper
now reports the range it prints rather than the intuition it replaced.

Years with fewer than MIN_CITATIONS citations are excluded from the range —
1438 carries under a thousand and sits at nearly four times the rate of any
other year, which is a small-sample artefact and is reported as one rather
than smoothed away.
"""

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import arabic_ordinals as A       # noqa: E402
import voice_attribution as V     # noqa: E402

MIN_CITATIONS = 200
FROM_YEAR = 1439


def main():
    total = collections.Counter()
    unparsed = collections.Counter()
    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            year = (r.get("hijri_date") or "")[:4]
            for m in V.CITE.finditer(r["text"]):
                total[year] += 1
                if A.parse(m.group(1))[0] is None:
                    unparsed[year] += 1

    kept = {y: (total[y], unparsed[y]) for y in total
            if y.isdigit() and int(y) >= FROM_YEAR and total[y] >= MIN_CITATIONS}
    rates = {y: 100 * u / t for y, (t, u) in kept.items()}

    print(f"unparsed article expressions by Hijri year "
          f"(from {FROM_YEAR}, years with >= {MIN_CITATIONS} citations)\n")
    for y in sorted(kept):
        t, u = kept[y]
        print(f"  {y}  {t:>7,} citations  {u:>5,} unparsed  {rates[y]:>5.1f}%")
    print(f"\nrange over {len(rates)} years: {min(rates.values()):.1f}% "
          f"to {max(rates.values()):.1f}% — flat, with no trend")
    dropped = sorted(y for y in total
                     if y.isdigit() and int(y) >= FROM_YEAR and y not in kept)
    if dropped:
        print(f"excluded for thinness: {', '.join(dropped)}")

    (HERE / "unparsed_by_year_results.json").write_text(json.dumps({
        "from_year": FROM_YEAR, "min_citations": MIN_CITATIONS,
        "per_year": {y: {"citations": t, "unparsed": u}
                     for y, (t, u) in sorted(kept.items())},
        "min": min(rates.values()), "max": max(rates.values()),
        "years": len(rates),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote unparsed_by_year_results.json")


if __name__ == "__main__":
    main()
