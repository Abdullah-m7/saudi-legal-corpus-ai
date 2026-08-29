#!/usr/bin/env python3
"""What is in the judgment corpus, and what does the project's claim rest on?

Computed from the corpus, not asserted. The project has repeatedly described
its judicial side as «Saudi judgments»; this measures how far that name is
carried by the evidence, along the axes a reader would check: which body
decided, at what level, where, and when.

    python3 audit.py   ->  coverage.json  (and a table on stdout)

Population semantics matter and are kept explicit. Every record here comes
from one publisher -- the Ministry of Justice legal gateway -- and one
publication decision. Nothing in this file may be read as a census of Saudi
adjudication; it is a census of what that gateway publishes.
"""

import collections
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX = HERE.parent / "arabic_paper" / "judgments_index.jsonl"
OUT = HERE / "coverage.json"

# The gateway's courtType is the degree of adjudication, not the subject.
# Verified against the live endpoint on 29 August 2026: querying courtTypes
# 1, 2 and 3 returns 33,632 / 15,393 / 1,739 and the court names in each are
# mixed by subject and uniform by level.
LEVEL = {1: "first instance", 2: "appeal", 3: "supreme"}
COMMERCIAL = "المحكمة التجارية"


def rows():
    for line in INDEX.open(encoding="utf-8"):
        line = line.strip()
        if line:
            yield json.loads(line)


def shares(counter, total):
    return [{"key": k, "n": n, "share": round(100 * n / total, 2)}
            for k, n in counter.most_common()]


def main():
    recs = list(rows())
    n = len(recs)
    court = collections.Counter((r.get("courtName") or "?").strip() for r in recs)
    level = collections.Counter(LEVEL.get(r.get("courtType"), f"unmapped:{r.get('courtType')}")
                                for r in recs)
    city = collections.Counter((r.get("city") or "?").strip() for r in recs)
    year = collections.Counter(r.get("hijriYear") for r in recs)
    appeal = collections.Counter(bool(r.get("isAppeal")) for r in recs)

    commercial = sum(v for k, v in court.items() if k == COMMERCIAL or "التجاري" in k)
    # Herfindahl over publishing bodies, and its inverse: the number of
    # equally-sized courts that would give the same concentration. Reported
    # because «one court is 95 per cent» understates how little the rest is,
    # not because a diversity index is decorative.
    hhi = sum((v / n) ** 2 for v in court.values())

    out = {
        "source": "Ministry of Justice legal gateway (laws-gateway.moj.gov.sa)",
        "populationSemantics": (
            "One publisher, one publication decision. A census of what this "
            "gateway publishes, not of Saudi adjudication."
        ),
        "records": n,
        "commercialCourt": commercial,
        "commercialShare": round(100 * commercial / n, 2),
        "nonCommercial": n - commercial,
        "publishingBodies": len(court),
        "herfindahl": round(hhi, 4),
        "effectiveBodies": round(1 / hhi, 2),
        "byCourt": shares(court, n),
        "byLevel": shares(level, n),
        "byCity": shares(city, n)[:15],
        "byHijriYear": sorted(({"year": y, "n": c} for y, c in year.items()),
                              key=lambda d: (d["year"] is None, d["year"])),
        "carriesAppellateDecision": {str(k): v for k, v in appeal.items()},
        "subjectField": None,
        "subjectFieldNote": (
            "The gateway exposes no subject or case-type field. Subject can "
            "only be inferred from the deciding court, which is why the "
            "commercial share is also the subject profile."
        ),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{n:,} records from one publisher\n")
    print(f"commercial court            {commercial:,}  ({out['commercialShare']}%)")
    print(f"everything else             {n - commercial:,}")
    print(f"publishing bodies           {len(court)}")
    print(f"effective bodies (1/HHI)    {out['effectiveBodies']}\n")
    print(f"{'court':<44}{'n':>8}{'share':>9}")
    for r in out["byCourt"]:
        print(f"{r['key'][:43]:<44}{r['n']:>8}{r['share']:>8}%")
    print(f"\n{'level':<44}{'n':>8}{'share':>9}")
    for r in out["byLevel"]:
        print(f"{r['key']:<44}{r['n']:>8}{r['share']:>8}%")
    print(f"\ntop cities: " + ", ".join(f"{r['key']} {r['share']}%" for r in out["byCity"][:5]))
    yrs = [d for d in out["byHijriYear"] if d["year"]]
    print(f"hijri years: {yrs[0]['year']}–{yrs[-1]['year']}, "
          f"{sum(d['n'] for d in yrs if d['year'] >= 1441)/n:.1%} from 1441 on")


if __name__ == "__main__":
    main()
