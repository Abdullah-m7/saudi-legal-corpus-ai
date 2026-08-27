#!/usr/bin/env python3
"""Two levels, one dispute: does the appellate bench cite differently?

13,924 published records carry both the first-instance judgment and the
appellate one. That is a paired design, and it removes the objection that
would sink a comparison between courts: the disputes are not different, they
are the same dispute seen twice. Whatever separates the two sets of citations
is the level, not the mix of cases.

The comparison is confined to each document's own reasons — the segment
between «الأسباب:» and «حكمت الدائرة» — because that is where a court says
what it is doing, and because paper 8 measures the same segment. Each
document is segmented on its own; see voice_attribution.parts.

Three measures, the same three the article uses at first instance: how much
of what is cited is procedural, how many distinct instruments are drawn on,
and how concentrated the citations are.
"""

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REGISTRY = REPO / "data" / "corpus_registry" / "corpus_registry.json"
sys.path.insert(0, str(HERE))

import match_instruments as M     # noqa: E402
import voice_attribution as V     # noqa: E402


def reasons_span(text, a, b):
    """The reasons of one document, or None where the headings are absent."""
    r = V.REASONS.search(text, a, b)
    k = V.RULING.search(text, r.end() if r else a, b)
    return (r.end(), k.start()) if r and k else None


def main():
    index, order = M.build(REGISTRY)
    cited = {"first": collections.Counter(), "appeal": collections.Counter()}
    both_reasoned = paired = 0

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            s = r.get("sections") or {}
            if not (s.get("judgmentTextofRulling") and
                    s.get("appealTextofRulling")):
                continue
            paired += 1
            text = r["text"]
            spans = V.parts(text, s)
            if len(spans) < 2:
                continue
            first, appeal = spans[0], spans[-1]
            fr = reasons_span(text, *first)
            ar_ = reasons_span(text, *appeal)
            if not fr or not ar_:
                continue
            both_reasoned += 1
            last = M.Recent()
            for m in V.CITE.finditer(text):
                tid, kind = M.match(m.group(2), index, order, last)
                if kind == "named":
                    last.note(tid)
                if not tid:
                    continue
                i = m.start()
                if fr[0] <= i < fr[1]:
                    cited["first"][tid] += 1
                elif ar_[0] <= i < ar_[1]:
                    cited["appeal"][tid] += 1

    print(f"{paired:,} paired records; {both_reasoned:,} carry reasons on "
          f"both levels ({both_reasoned/paired:.1%})\n")
    print(f"{'level':<12}{'citations':>10}{'instruments':>13}"
          f"{'procedural':>12}{'top-5 share':>13}")
    out = {"paired": paired, "both_reasoned": both_reasoned, "levels": {}}
    for key in ("first", "appeal"):
        c = cited[key]
        tot = sum(c.values())
        if not tot:
            continue
        proc = sum(v for k, v in c.items() if k in M.PROCEDURAL)
        top5 = sum(v for _, v in c.most_common(5))
        print(f"{key:<12}{tot:>10,}{len(c):>13}{proc/tot:>11.1%}"
              f"{top5/tot:>12.1%}")
        out["levels"][key] = {
            "citations": tot, "instruments": len(c),
            "procedural": 100 * proc / tot, "top5": 100 * top5 / tot,
            "by_instrument": dict(c.most_common(15)),
        }

    print("\nwhat each level reaches for, most first:")
    for key in ("first", "appeal"):
        tot = sum(cited[key].values())
        print(f"  — {key}")
        for tid, v in cited[key].most_common(6):
            print(f"      {v:>6,}  {100*v/tot:>5.1f}%  {tid}")

    (HERE / "appeal_vs_first_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote appeal_vs_first_results.json")


if __name__ == "__main__":
    main()
