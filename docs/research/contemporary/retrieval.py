#!/usr/bin/env python3
"""Does speaker mixing change what a retrieval system would learn as important?

A concrete, LLM-free version of the paper's implication for legal AI. Rank the
statutory articles of the contemporary corpus three ways -- by their frequency
in the full judgment text, in the court's reasons only, and in the parties'
arguments only -- and ask whether a system trained or grounded on the first
would surface the same law as one grounded on the second.

    python3 retrieval.py
"""
import collections
import gzip
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYER = HERE / "authority_mentions.jsonl.gz"
OUT = HERE / "retrieval_results.json"
YEARS = {1444, 1445, 1446}


def rank():
    full, court, party = (collections.Counter() for _ in range(3))
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q") or r["y"] not in YEARS:
                continue
            if r.get("art") is None:
                continue
            k = f"{r['inst']}:{r['art']}"
            full[k] += 1
            if r["role"] == "court_reasoning":
                court[k] += 1
            elif r["role"] in ("party_argument", "recital"):
                party[k] += 1
    return full, court, party


def spearman(a, b, keys):
    ra = {k: i for i, (k, _) in enumerate(a.most_common())}
    rb = {k: i for i, (k, _) in enumerate(b.most_common())}
    xs = [(ra[k], rb[k]) for k in keys if k in ra and k in rb]
    n = len(xs)
    if n < 3:
        return None
    mx = sum(x for x, _ in xs) / n
    my = sum(y for _, y in xs) / n
    num = sum((x - mx) * (y - my) for x, y in xs)
    den = math.sqrt(sum((x - mx) ** 2 for x, _ in xs)
                    * sum((y - my) ** 2 for _, y in xs))
    return round(num / den, 3) if den else None


def main():
    full, court, party = rank()
    keys = set(full) | set(court) | set(party)
    res = {"articlesTotal": len(keys),
           "citations": {"full": sum(full.values()), "court": sum(court.values()),
                         "party": sum(party.values())}}
    for k, n in (("10", 10), ("50", 50), ("100", 100)):
        f = {x for x, _ in full.most_common(n)}
        c = {x for x, _ in court.most_common(n)}
        p = {x for x, _ in party.most_common(n)}
        res[f"overlap@{k}"] = {
            "full_vs_court": len(f & c), "full_vs_party": len(f & p),
            "court_vs_party": len(c & p),
            "inCourtNotFull": sorted(c - f)[:8],
            "inFullNotCourt": sorted(f - c)[:8]}
    res["spearman"] = {
        "full_vs_court": spearman(full, court, keys),
        "full_vs_party": spearman(full, party, keys),
        "court_vs_party": spearman(court, party, keys)}
    res["topByView"] = {
        "full": [[k, v] for k, v in full.most_common(10)],
        "court": [[k, v] for k, v in court.most_common(10)],
        "party": [[k, v] for k, v in party.most_common(10)]}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    print(f"{len(keys):,} distinct articles; citations "
          f"full {sum(full.values()):,} / court {sum(court.values()):,} / "
          f"party {sum(party.values()):,}\n")
    print(f"{'k':<6}{'full∩court':>12}{'full∩party':>13}{'court∩party':>14}")
    for k in ("10", "50", "100"):
        o = res[f"overlap@{k}"]
        print(f"  {k:<4}{o['full_vs_court']:>12}{o['full_vs_party']:>13}"
              f"{o['court_vs_party']:>14}")
    print(f"\nSpearman over all articles: {res['spearman']}")
    print(f"\ntop 10, full text vs court reasoning:")
    for (a, x), (b, y) in zip(res["topByView"]["full"], res["topByView"]["court"]):
        print(f"  {a:<46}{x:>7,}   |   {b:<46}{y:>7,}")
    print(f"\nin the court's top 50 but NOT the full-text top 50: "
          f"{res['overlap@50']['inCourtNotFull']}")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
