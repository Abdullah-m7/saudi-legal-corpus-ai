#!/usr/bin/env python3
"""Recompute the headline numbers independently and compare with the analysis.

Deliberately shares no code with analyse_uk.py. Two implementations that import
the same helper agree by construction, which proves nothing; this one counts
from the raw year files in the most obvious way available and then asks whether
the analysis reached the same place by its more careful route.

The comparison is only meaningful against a results file built from the same
collection, so this runs the analysis first. Comparing a live recomputation
against a stored snapshot while a sweep is still writing year files produces a
uniform mismatch that looks alarming and means nothing --- which is exactly what
it did the first time it was run.

    python3 docs/research/comparison_paper/verify_uk.py
"""

import glob
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
AS_OF = date.fromisoformat("2026-08-21")


def recompute():
    acts = []
    for f in sorted(glob.glob(str(HERE / "uk_collection" / "*.json"))):
        acts += json.load(open(f, encoding="utf-8")).get("acts") or []

    ok = [a for a in acts
          if a["retrieval"]["http_status"] == "200"
          or (a.get("retrieval_retry") or {}).get("http_status") == "200"]

    effects = affected = body = 0
    provisions, years = set(), {}
    for a in ok:
        # Both conditions, independently expressed. `RequiresApplied` alone
        # is what the withdrawn version of this study counted, and it is not
        # the measure: an effect marked prospective in ukm:InForce is enacted
        # but not commenced, so the service is right not to have applied it.
        live = [e for e in a.get("effects", [])
                if e.get("RequiresApplied") == "true"
                and e.get("InForceProspective") != "true"]
        affected += bool(live)
        effects += len(live)
        if isinstance(a.get("body_paragraphs"), int):
            body += a["body_paragraphs"]
        for e in live:
            if e.get("AffectedProvisions"):
                provisions.add((e.get("AffectedURI", a["id"]),
                                e["AffectedProvisions"]))
            y = e.get("AffectingYear", "")
            if y.isdigit():
                years[int(y)] = years.get(int(y), 0) + 1

    return {
        "acts listed": len(acts),
        "acts retrieved": len(ok),
        "acts affected": affected,
        "effects": effects,
        "distinct provisions": len(provisions),
        "body paragraphs": body,
        "effects 10+ years old":
            sum(c for y, c in years.items() if AS_OF.year - y >= 10),
    }


def from_analysis():
    subprocess.run([sys.executable, str(HERE / "analyse_uk.py"),
                    "--as-of", AS_OF.isoformat()],
                   check=True, capture_output=True)
    r = json.loads((HERE / "uk_analysis_results.json").read_text(encoding="utf-8"))
    c, u = r["coverage"], r["unincorporated"]
    return {
        "acts listed": c["acts_listed"],
        "acts retrieved": c["acts_retrieved"],
        "acts affected": u["acts_affected"],
        "effects": u["effects_requiring_application"],
        "distinct provisions": u["distinct_affected_provisions"],
        "body paragraphs": u["body_paragraphs_in_those_acts"],
        "effects 10+ years old":
            r["tail"]["affecting_instrument_10_or_more_years_old"]["effects"],
    }


def main():
    mine, theirs = recompute(), from_analysis()
    width = max(len(k) for k in mine)
    bad = []
    for key in mine:
        a, b = mine[key], theirs[key]
        flag = "ok " if a == b else "DIFF"
        print(f"  {flag} {key:<{width}}  independent {a:>7,}   analysis {b:>7,}")
        if a != b:
            bad.append(key)
    print("\n" + ("all figures agree" if not bad
                  else f"MISMATCH in: {', '.join(bad)}"))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
