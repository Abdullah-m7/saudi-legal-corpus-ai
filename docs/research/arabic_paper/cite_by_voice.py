#!/usr/bin/env python3
"""Who cites the statute — the court, or the parties?

The concentration measured in applied_law.py counts every citation in a
judgment's text. But a judgment's text is not one voice. It opens with the
statement of the case, which carries the parties' arguments as the court
reports them, and only later reaches the bench's own reasoning.

The API cannot make this distinction: judgmentFacts, judgmentReasons and
judgmentRuling exist as fields and are null in all 50,666 records, exactly
like isAppeal. Everything arrives in one block.

The documents carry their own structure instead. Saudi commercial judgments
run الوقائع → الأسباب → حكمت الدائرة, and this segments on those headings and
counts citations separately in each part.

Segments
  recital     from the start (or الوقائع) to the الأسباب heading
  reasoning   from الأسباب to حكمت الدائرة
  operative   from حكمت الدائرة to the end

An earlier version called the first segment *pleadings*, which was wrong.
الوقائع is written by the court, and much of it is the court's own procedural
narration — «وتشير الدائرة إلى أنها عقدت هذه الجلسة التحضيرية بناءً على
المادة التسعين». Reading that as an argument put to the court overstates the
bar's citation practice and understates the bench's. The segment is counted
here for what it is, and split by attribution: how many of its citations sit
in a sentence whose actor is the court. See voice_attribution.py.

A judgment whose headings are missing or out of order is not segmented and
is counted as unsegmentable rather than forced into a shape it does not have.

Matching is match_instruments.match, so a citation naming نظام المحاكم
التجارية is counted against the law and not against its implementing
regulation. Anaphoric references are resolved in document order across the
whole judgment, which is why the text is scanned once and each citation
assigned to a segment by its offset rather than each segment scanned alone.
"""

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REGISTRY = REPO / "data" / "corpus_registry" / "corpus_registry.json"
sys.path.insert(0, str(HERE))

import match_instruments as M      # noqa: E402
import voice_attribution as V      # noqa: E402

CITE = V.CITE
PROCEDURAL = M.PROCEDURAL
SEGMENTS = ("recital", "reasoning", "operative")


def bounds(text):
    """(end of الوقائع, start of the operative part) or None."""
    r = V.REASONS.search(text)
    k = V.RULING.search(text, r.end() if r else 0)
    if not r or not k:
        return None
    return r.start(), k.start()


def main():
    index, order = M.build(REGISTRY)
    counts = {k: collections.Counter() for k in SEGMENTS}
    attribution = collections.Counter()
    recital_proc = collections.Counter()
    n = segmented = 0

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            n += 1
            text = json.loads(line)["text"]
            b = bounds(text)
            if not b:
                continue
            segmented += 1
            last = M.Recent()
            for m in CITE.finditer(text):
                tid, kind = M.match(m.group(2), index, order, last)
                if kind == "named":
                    last.note(tid)
                if not tid:
                    continue
                seg = ("recital" if m.start() < b[0]
                       else "reasoning" if m.start() < b[1] else "operative")
                counts[seg][tid] += 1
                if seg == "recital":
                    who = ("court" if V.attribute(text, m.start())[0] == "court"
                           else "other")
                    attribution[who] += 1
                    recital_proc[(who, tid in PROCEDURAL)] += 1

    print(f"{n:,} judgments; {segmented:,} segmented ({segmented/n:.1%}); "
          f"{n-segmented:,} lack the headings and are excluded\n")
    print(f"{'segment':<12} {'citations':>10} {'instruments':>12} "
          f"{'procedural':>11} {'top-10 share':>13}")
    for key in SEGMENTS:
        c = counts[key]
        tot = sum(c.values())
        if not tot:
            print(f"{key:<12} {0:>10}")
            continue
        proc = sum(v for k, v in c.items() if k in PROCEDURAL)
        top10 = sum(v for _, v in c.most_common(10))
        print(f"{key:<12} {tot:>10,} {len(c):>12} "
              f"{proc/tot:>10.1%} {top10/tot:>12.1%}")

    rec = sum(attribution.values())
    print(f"\ninside الوقائع: {attribution['court']:,} of {rec:,} citations "
          f"({attribution['court']/rec:.1%}) sit in a sentence whose actor is "
          f"the court.\nThe cue is lexical and its precision was 37 of 40 on a "
          f"hand-read sample, so this is a floor, not a partition.")

    print("\nprocedural share inside الوقائع, by who is speaking:")
    for who in ("court", "other"):
        a, b = recital_proc[(who, True)], recital_proc[(who, False)]
        print(f"  {who:<6} {a:>7,} procedural of {a+b:>7,}  {a/(a+b):>6.1%}")
    print("The court's own narration is almost purely procedural, so leaving "
          "it inside\nthe segment flatters the procedural share there: the "
          "contrast with the\nreasoning is sharper once it is taken out, not "
          "weaker.")

    print("\nmost-cited, by segment:")
    for key in ("recital", "reasoning"):
        print(f"  — {key}")
        for tid, v in counts[key].most_common(6):
            print(f"      {v:>7,}  {tid}")

    (HERE / "cite_by_voice_results.json").write_text(json.dumps(
        {"judgments": n, "segmented": segmented,
         "counts": {k: dict(v) for k, v in counts.items()},
         "recital_attribution": dict(attribution),
         "recital_procedural": {f"{w}_{'proc' if p else 'other'}": v
                                for (w, p), v in recital_proc.items()}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote cite_by_voice_results.json")


if __name__ == "__main__":
    main()
