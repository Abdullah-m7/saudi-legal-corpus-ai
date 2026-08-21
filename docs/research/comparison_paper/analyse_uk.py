#!/usr/bin/env python3
"""Measure what the UK statute book says about its own currency.

Reads the collection produced by collect_uk.py and reports, for the Public
General Acts covered, how much of the text the service displays is known by the
service not to reflect the law in force.

Three disciplines carried over from the earlier papers in this series.

*Report the denominator.* Every share names what it is a share of, and Acts
that could not be retrieved are counted and excluded rather than quietly
dropped, because a missing Act is a hole in coverage and looks exactly like an
Act with no unapplied effects if nobody says so.

*Do not conflate two measures.* `unapplied_total` counts every effect in the
block; `unapplied_requiring_application` counts those the service marks
`RequiresApplied="true"`. Only the second means "this text is out of date".
The first is the number a hurried reading would take, and it is larger. Both
are reported, and the difference between them is reported too.

*Count provisions and Acts separately.* An Act with 96 unapplied effects and an
Act with one are both "an affected Act". The per-provision figure is the one
that answers how much law is involved; the per-Act figure answers how wide the
problem is. Paper 5's Saudi numbers have the same two units, and the two are
not interchangeable in either jurisdiction.

Read-only and deterministic. Run from the repository root:

    python3 docs/research/comparison_paper/analyse_uk.py
"""

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE = HERE / "uk_collection"
OUT = HERE / "uk_analysis_results.json"

def load():
    years, acts = [], []
    for path in sorted(STORE.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        years.append(data["year"])
        for act in data.get("acts") or []:
            act["_year"] = data["year"]
            acts.append(act)
    return years, acts


def retrieved(act):
    """True if the Act's metadata was obtained, on the first or second attempt."""
    return (act["retrieval"]["http_status"] == "200"
            or act.get("retrieval_retry", {}).get("http_status") == "200")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=date.today().isoformat(),
                    help="date the collection is treated as current at "
                         "(YYYY-MM-DD); recorded in the results")
    as_of = date.fromisoformat(ap.parse_args().as_of)
    years, acts = load()
    if not acts:
        raise SystemExit("no collection found --- run collect_uk.py first")

    got = [a for a in acts if retrieved(a)]
    lost = [a for a in acts if not retrieved(a)]
    recovered = [a for a in got if a.get("retrieval_retry")]

    # An effect only means "the displayed text is out of date" when the service
    # marks it as still requiring application.
    def live_effects(act):
        return [e for e in act.get("effects", [])
                if e.get("RequiresApplied") == "true"]

    affected = [a for a in got if live_effects(a)]
    all_effects = [e for a in got for e in live_effects(a)]
    every_effect = [e for a in got for e in a.get("effects", [])]

    # Provisions, not effects: several effects can name the same provision, and
    # counting effects would overstate how much text is involved.
    provisions = set()
    for a in got:
        for e in live_effects(a):
            p = e.get("AffectedProvisions")
            if p:
                provisions.add((e.get("AffectedURI", a["id"]), p))

    # `AffectingYear` is the year of the instrument making the amendment, and
    # it is NOT the date the amendment took effect. The Transport Act 1982
    # amends the Road Traffic Act 1988: provisions never commenced in 1982
    # bite, when commenced, on a later consolidating Act. Effects whose
    # affecting instrument predates the Act they affect are counted below, and
    # they are not rare. So subtracting years does not measure how long
    # anything has gone unincorporated --- and commencement dates are not in
    # this metadata, so that duration cannot be computed from this collection
    # at all.
    #
    # What can be said exactly: the affecting instrument dates from year Y, and
    # the effect is still unapplied as at the date the analysis is run against.
    # That date is a parameter whose value is recorded, rather than today's
    # date read silently, so the same files and the same --as-of always give
    # the same answer.
    ages = Counter()
    for e in all_effects:
        y = e.get("AffectingYear")
        if y and y.isdigit():
            ages[int(y)] += 1
    backwards = sum(
        1 for a in got for e in live_effects(a)
        if e.get("AffectingYear", "").isdigit()
        and int(e["AffectingYear"]) < a["_year"])

    per_act = sorted((len(live_effects(a)), a["id"], a.get("title") or "")
                     for a in affected)[::-1]
    total = sum(n for n, _, _ in per_act)
    top10 = sum(n for n, _, _ in per_act[:10])

    results = {
        "coverage": {
            "years": [min(years), max(years)] if years else None,
            "acts_listed": len(acts),
            "acts_retrieved": len(got),
            "recovered_on_second_attempt": len(recovered),
            "acts_never_retrieved": len(lost),
            "never_retrieved_ids": [a["id"] for a in lost],
        },
        "unincorporated": {
            "acts_affected": len(affected),
            "acts_affected_share": round(len(affected) / len(got), 4) if got else None,
            "effects_requiring_application": len(all_effects),
            "effects_in_block_total": len(every_effect),
            "difference_between_the_two_measures":
                len(every_effect) - len(all_effects),
            "distinct_affected_provisions": len(provisions),
            "top_10_acts_share_of_effects":
                round(top10 / total, 4) if total else None,
        },
        "by_type": dict(Counter(e.get("Type", "?") for e in all_effects)
                        .most_common(15)),
        "affecting_instrument_year": dict(sorted(ages.items())),
        "effects_whose_affecting_instrument_predates_the_act": backwards,
        "oldest_affecting_instrument": (
            {"year": min(ages),
             "years_since": as_of.year - min(ages),
             "count": ages[min(ages)],
             "note": "years since the affecting instrument was passed, NOT the "
                     "time the amendment has gone unincorporated --- "
                     "commencement dates are not in this metadata"}
            if ages else None),
        "as_of": as_of.isoformat(),
        "most_affected_acts": [
            {"effects": n, "id": i, "title": t} for n, i, t in per_act[:15]],
    }
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    c, u = results["coverage"], results["unincorporated"]
    print(f"years {c['years'][0]}-{c['years'][1]}   "
          f"Acts listed {c['acts_listed']}, retrieved {c['acts_retrieved']} "
          f"({c['recovered_on_second_attempt']} on a second attempt), "
          f"never retrieved {c['acts_never_retrieved']}")
    print(f"\nActs displaying text the service says is out of date: "
          f"{u['acts_affected']}/{c['acts_retrieved']} "
          f"({u['acts_affected_share']*100:.1f}%)")
    print(f"  amendments enacted but not incorporated: "
          f"{u['effects_requiring_application']:,}")
    print(f"  across {u['distinct_affected_provisions']:,} distinct provisions")
    print(f"  the whole effects block holds {u['effects_in_block_total']:,}; "
          f"reporting that number instead would overstate by "
          f"{u['difference_between_the_two_measures']:,}")
    print(f"  ten most affected Acts hold "
          f"{u['top_10_acts_share_of_effects']*100:.1f}% of all of them")
    if results["oldest_affecting_instrument"]:
        o = results["oldest_affecting_instrument"]
        print(f"\noldest affecting instrument still unapplied: {o['year']}, "
              f"{o['years_since']} years before {as_of.isoformat()} "
              f"({o['count']} effect(s))")
        print("  that is the age of the amending instrument, not how long the "
              "amendment has gone\n  unincorporated --- commencement dates "
              "are not published in this metadata")
    print(f"  effects whose affecting instrument predates the Act it amends: "
          f"{results['effects_whose_affecting_instrument_predates_the_act']}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
