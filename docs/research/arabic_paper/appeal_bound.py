#!/usr/bin/env python3
"""Does the extractor's blind spot move the appellate/first-instance gap?

coverage_sensitivity.py showed that the seven citation forms V.CITE cannot
see (MOJ_ARTICLE_GOLD.md) barely move the corpus-wide composition figures.
That is not enough for paper 9, whose claim is a *difference* between two
levels of court. A uniform miss rate cannot move a difference; a non-uniform
one can, and there is a specific reason to expect non-uniformity here.

An appellate bench restates the instrument the court below named and then
refers back to it — «من ذات النظام», «من ذات اللائحة». Anaphoric
back-reference is precisely the form the pattern misses, and appellate
reasons should carry more of it. If so, the appellate side of the comparison
is the more heavily under-counted, and the gap is measured on unequal footing.

This re-runs appeal_vs_first.py's paired design unchanged -- same records,
same reasons spans, same matcher -- with the permissive pattern from
coverage_sensitivity.py added, and reports both readings side by side. It is
a sensitivity check on a difference, not a replacement for the published
figure.

    python3 appeal_bound.py
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
sys.path.insert(0, str(HERE))
import match_instruments as M          # noqa: E402
import voice_attribution as V          # noqa: E402
from appeal_vs_first import reasons_span                      # noqa: E402
from coverage_sensitivity import EXTENDED, MARKS, NOT_ARTICLE, pairs  # noqa: E402

LEVELS = ("first", "appeal")


def share(c, keys):
    tot = sum(c.values())
    return 100 * sum(v for k, v in c.items() if k in keys) / tot if tot else 0.0


def main():
    index, order = M.build(REGISTRY)
    cited = {r: {lv: collections.Counter() for lv in LEVELS}
             for r in ("PUBLISHED", "BOUND")}
    both = paired = 0

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
            fr = reasons_span(text, *spans[0])
            ar = reasons_span(text, *spans[-1])
            if not fr or not ar:
                continue
            both += 1

            def level(i):
                if fr[0] <= i < fr[1]:
                    return "first"
                if ar[0] <= i < ar[1]:
                    return "appeal"
                return None

            last = M.Recent()
            for m in V.CITE.finditer(text):
                tid, kind = M.match(m.group(2), index, order, last)
                if kind == "named":
                    last.note(tid)
                lv = level(m.start())
                if tid and lv:
                    for reading in ("PUBLISHED", "BOUND"):
                        cited[reading][lv][tid] += 1

            # the extended pass runs on the same string with diacritics and
            # tatweel removed. Removing them shifts offsets, so the reasons
            # spans are recomputed on the stripped text rather than reused.
            plain = MARKS.sub("", text.replace("ـ", ""))
            pspans = V.parts(plain, s)
            if len(pspans) < 2:
                continue
            pfr = reasons_span(plain, *pspans[0])
            par = reasons_span(plain, *pspans[-1])
            if not pfr or not par:
                continue
            seen = {m.start() for m in V.CITE.finditer(plain)}
            last = M.Recent()
            for m in EXTENDED.finditer(plain):
                art, raw = pairs(m)
                if art is None:
                    continue
                if NOT_ARTICLE.search(plain[max(0, m.start() - 24):m.start()]):
                    continue
                tid, kind = M.match(raw, index, order, last)
                if kind == "named":
                    last.note(tid)
                if not tid or m.start() in seen:
                    continue
                i = m.start()
                lv = ("first" if pfr[0] <= i < pfr[1]
                      else "appeal" if par[0] <= i < par[1] else None)
                if lv:
                    cited["BOUND"][lv][tid] += 1

    out = {"paired": paired, "bothReasoned": both, "readings": {}}
    print(f"{paired:,} paired records; {both:,} carry reasons on both levels\n")
    print(f"{'':<10}{'citations':>12}{'procedural %':>15}{'top-5 %':>10}")
    for reading in ("PUBLISHED", "BOUND"):
        out["readings"][reading] = {}
        print(f"  [{reading}]")
        for lv in LEVELS:
            c = cited[reading][lv]
            top5 = {k for k, _ in c.most_common(5)}
            row = {"citations": sum(c.values()),
                   "instruments": len(c),
                   "proceduralShare": round(share(c, M.PROCEDURAL), 1),
                   "top5Share": round(share(c, top5), 1)}
            out["readings"][reading][lv] = row
            print(f"    {lv:<8}{row['citations']:>12,}"
                  f"{row['proceduralShare']:>15.1f}{row['top5Share']:>10.1f}")
        a = out["readings"][reading]["appeal"]["proceduralShare"]
        f = out["readings"][reading]["first"]["proceduralShare"]
        out["readings"][reading]["gap"] = round(a - f, 1)
        print(f"    {'gap':<8}{'':>12}{a - f:>+15.1f}")

    g0 = out["readings"]["PUBLISHED"]["gap"]
    g1 = out["readings"]["BOUND"]["gap"]
    out["gapMove"] = round(g1 - g0, 1)
    print(f"\nthe appellate/first-instance gap in procedural share moves "
          f"{g1 - g0:+.1f} points ({g0:+.1f} -> {g1:+.1f})")

    (HERE / "appeal_bound_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("wrote appeal_bound_results.json")


if __name__ == "__main__":
    main()
