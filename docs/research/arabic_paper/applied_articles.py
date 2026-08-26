#!/usr/bin/env python3
"""Which articles of the statute book does a court ever apply?

The instrument-level join said 113 of 291 instruments are ever cited and ten
of them carry 94% of the citations. This asks the same question one level
down, where it bites harder: an instrument counted as "applied" may be
applied through two of its ninety-six articles.

Article numbers are read by arabic_ordinals.py, which parses 98% of them.
Four in ten are spelled out — «الخامسة والتسعون بعد المائة» — so a parser
that handled only digits would have measured three articles in ten and called
it a census.

The denominator is the registry's own article count per instrument, 15,855
across 290 tracks. A cited article number above an instrument's count is
recorded as out-of-range rather than dropped: it usually means the judgment
cites the implementing regulation while naming the parent law, and that is
worth knowing rather than hiding.
"""

import collections
import json
import re
from pathlib import Path

import arabic_ordinals as A
import match_instruments as M

HERE = Path(__file__).resolve().parent
REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
CITE = re.compile(
    r"الماد[ةه]\s*\(?\s*([^\)\n]{1,40}?)\s*\)?\s*من\s+((?:نظام|لائحة|النظام|اللائحة)[^\.،؛\n\)]{0,60})")


def main():
    index, order = M.build(REGISTRY)
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    tracks = reg["tracks"]
    tracks = list(tracks.values()) if isinstance(tracks, dict) else tracks
    size = {}
    for t in tracks:
        rc = t.get("record_counts") or {}
        v = rc.get("arabic_articles") or rc.get("total")
        if isinstance(v, int) and v > 0:
            size[t["track_id"]] = v

    hits = collections.defaultdict(collections.Counter)   # track -> article -> n
    unparsed = out_of_range = total = 0
    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            last = None
            for art, raw in CITE.findall(json.loads(line)["text"]):
                total += 1
                tid, kind = M.match(raw, index, order, last)
                if not tid:
                    continue
                if kind == "named":
                    last = tid
                num, _ = A.parse(art)
                if num is None:
                    unparsed += 1
                    continue
                if tid in size and num > size[tid]:
                    out_of_range += 1
                    continue
                hits[tid][num] += 1

    cited_articles = sum(len(v) for v in hits.values())
    universe = sum(size.values())
    covered_universe = sum(size[t] for t in hits if t in size)
    print(f"{total:,} citations")
    print(f"  article number unparsed   {unparsed:,}")
    print(f"  above the instrument's own article count  {out_of_range:,}")
    print(f"\nregistry: {universe:,} articles across {len(size)} instruments")
    print(f"  articles cited at least once: {cited_articles:,} "
          f"({cited_articles/universe:.2%} of the statute book)")
    print(f"  within the {len(hits)} instruments that are cited at all, "
          f"which hold {covered_universe:,} articles: "
          f"{cited_articles/covered_universe:.1%}")

    flat = collections.Counter()
    for tid, arts in hits.items():
        for a, c in arts.items():
            flat[(tid, a)] = c
    ranked = flat.most_common()
    tot = sum(flat.values())
    print(f"\nconcentration over {len(ranked):,} distinct articles "
          f"({tot:,} citations)")
    for k in (1, 5, 10, 20, 50, 100):
        print(f"  top {k:>3}: {sum(c for _, c in ranked[:k])/tot:>6.1%}")
    print("\nmost-applied articles:")
    for (tid, a), c in ranked[:12]:
        print(f"   {c:>6,}  المادة {a:<5} {tid}")

    print("\nhow thinly an 'applied' instrument is applied:")
    rows = sorted(((t, len(v), size.get(t, 0)) for t, v in hits.items()),
                  key=lambda r: -sum(hits[r[0]].values()))[:10]
    for tid, used, have in rows:
        share = f"{used/have:.0%}" if have else "—"
        print(f"   {used:>4} of {have:<5} articles ({share:>4})  {tid}")

    (HERE / "applied_articles_results.json").write_text(json.dumps(
        {"citations": total, "unparsed": unparsed, "out_of_range": out_of_range,
         "registry_articles": universe, "articles_cited": cited_articles,
         "by_instrument": {t: dict(v) for t, v in hits.items()},
         "instrument_sizes": size}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote applied_articles_results.json")


if __name__ == "__main__":
    main()
