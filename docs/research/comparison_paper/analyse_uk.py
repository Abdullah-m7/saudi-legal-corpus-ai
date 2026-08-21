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


def schema_record(act, effects):
    """The five-field provenance record as paper 5 defines it, assembled whole.

    The collector writes four of the five fields directly. The fifth,
    `discrepancy`, it writes only for a failed retrieval --- and that leaves out
    the defect this whole study is about, because an Act whose text omits
    enacted amendments was retrieved perfectly: official-primary, live, no
    transformation, nothing to report. Under the schema as written, the record
    with 222 unapplied effects and the record with none are indistinguishable.

    They should not be, and the schema does not actually require them to be.
    Its purpose line for `discrepancy` is "is there a known problem with this
    record?", and an Act the publisher itself flags as not reflecting the law in
    force is exactly that. What paper 5's field *values* leave out is that a
    discrepancy can be **declared by the source** rather than **found by the
    collector**, and the two are not interchangeable:

      found by the collector --- cost two or more sources and a comparison, so
      a null means "we did not find one", which may only mean we did not look
      hard enough;
      declared by the source --- costs nothing to record, and a null means "the
      publisher did not say", which is not evidence of absence either, but of a
      completely different kind.

    A single null field standing for both is the same collapse paper 5 objects
    to when a confidence score stands for availability and consistency at once.
    So `discrepancy` carries who declared it. That is the refinement this
    jurisdiction produced, and it is recorded here rather than asserted: the
    UK's 222-effect Act is the case that makes it unavoidable.

    Assembled in the analysis rather than the collector only because the sweep
    was already running. The information was in the collector's hands at the
    moment of retrieval --- it arrived in the same response --- so the schema's
    cost claim is untouched; where the value is serialised is not an epistemic
    question. The collector is to write it directly on the next full run.
    """
    record = dict(act.get("provenance") or {})
    if effects:
        record["discrepancy"] = {
            "kind": "source-declares-text-not-current",
            "declared_by": "source",
            "effects_not_incorporated": len(effects),
            "oldest_affecting_instrument_year": min(
                (int(e["AffectingYear"]) for e in effects
                 if e.get("AffectingYear", "").isdigit()), default=None),
        }
    elif record.get("discrepancy"):
        record["discrepancy"]["declared_by"] = "collector"
    return record

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

    # The service marks each Act `revised` --- maintained in amended form --- or
    # `final`. A `final` Act is served as enacted, so it has no revised text for
    # an amendment to be missing from, and an absence of unapplied effects on it
    # says nothing about whether it reflects the law in force. Left in the
    # denominator it would look clean and pull the headline share down. Both
    # shares are reported rather than one chosen quietly. What is observed is
    # reported as observed: `final` Acts carrying an unapplied effect are
    # counted, not assumed away.
    revised = [a for a in got if a.get("document_status") == "revised"]
    final = [a for a in got if a.get("document_status") != "revised"]
    affected = [a for a in got if live_effects(a)]
    affected_final = [a for a in final if live_effects(a)]
    all_effects = [e for a in got for e in live_effects(a)]
    every_effect = [e for a in got for e in a.get("effects", [])]

    # Provisions, not effects: several effects can name the same provision, and
    # counting effects would overstate how much text is involved.
    def distinct_provisions(acts):
        seen = set()
        for a in acts:
            for e in live_effects(a):
                p = e.get("AffectedProvisions")
                if p:
                    seen.add((e.get("AffectedURI", a["id"]), p))
        return seen

    provisions = distinct_provisions(got)

    # The denominator for the per-provision figure. legislation.gov.uk counts
    # body paragraphs separately from schedule paragraphs; a Saudi article is a
    # numbered provision in the body of an instrument, so `body_paragraphs` is
    # the closer analogue, but affected provisions do sit in schedules too.
    # Both totals are reported and neither is presented as the answer.
    #
    # The ratio is computed over the Acts that publish a paragraph count and
    # nothing else. Taking provisions from every Act and paragraphs from only
    # those that publish a count would put a numerator and a denominator drawn
    # from different sets into the same fraction --- which is what the first
    # version of this did, silently, and it inflated the rate.
    counted = [a for a in got if a.get("body_paragraphs") is not None]
    body = sum(a["body_paragraphs"] for a in counted)
    total_paras = sum(a.get("total_paragraphs") or 0 for a in counted)
    missing_stats = len(got) - len(counted)
    provisions_in_counted = distinct_provisions(counted)

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

    # The service commits to incorporating amendments within three months of
    # their coming into force, so a non-zero backlog is the design and its
    # existence is not a finding. What can be a finding is the tail. These
    # thresholds are on the age of the *affecting instrument*, which is the
    # only date published: an effect whose amending Act is twenty years old is
    # not proof of a twenty-year breach, because commencement can lag enactment
    # by decades, but the distribution is what the publisher gives a user to
    # reason with, and that is the point.
    tail = {}
    for threshold in (5, 10, 20):
        n = sum(c for y, c in ages.items() if as_of.year - y >= threshold)
        tail[f"affecting_instrument_{threshold}_or_more_years_old"] = {
            "effects": n,
            "share": round(n / len(all_effects), 4) if all_effects else None,
        }

    # An Act the service revised recently, still carrying effects from an old
    # instrument, separates a standing backlog from a record nobody has touched.
    # If the record were simply stale, its last-modified date would be stale
    # too.
    recently_revised_with_old_effects = []
    for a in affected:
        modified = a.get("last_modified") or ""
        if not modified[:4].isdigit():
            continue
        if as_of.year - int(modified[:4]) > 1:
            continue
        old_effects = [e for e in live_effects(a)
                       if e.get("AffectingYear", "").isdigit()
                       and as_of.year - int(e["AffectingYear"]) >= 10]
        if old_effects:
            recently_revised_with_old_effects.append({
                "id": a["id"], "title": a.get("title"),
                "last_modified": modified,
                "effects_from_instruments_10_years_or_older": len(old_effects),
                "oldest_affecting_instrument_year":
                    min(int(e["AffectingYear"]) for e in old_effects),
            })
    recently_revised_with_old_effects.sort(
        key=lambda r: -r["effects_from_instruments_10_years_or_older"])

    schema = [schema_record(a, live_effects(a)) for a in got]
    declared = sum(1 for r in schema
                   if (r.get("discrepancy") or {}).get("declared_by") == "source")
    collector_found = sum(
        1 for r in schema
        if (r.get("discrepancy") or {}).get("declared_by") == "collector")
    constant_fields = {
        field: len({r.get(field) for r in schema})
        for field in ("source_class", "retrieval_route", "corroboration",
                      "transformation")
    }

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
            "acts_status_revised": len(revised),
            "acts_status_final": len(final),
            "acts_affected_share_of_revised":
                round(len(affected) / len(revised), 4) if revised else None,
            "final_acts_carrying_an_unapplied_effect": len(affected_final),
            "acts_with_paragraph_statistics": len(counted),
            "acts_without_paragraph_statistics": missing_stats,
            "affected_provisions_in_those_acts": len(provisions_in_counted),
            "body_paragraphs_in_those_acts": body,
            "total_paragraphs_in_those_acts": total_paras,
            "affected_provisions_per_1000_body_paragraphs":
                round(len(provisions_in_counted) / body * 1000, 2)
                if body else None,
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
        "schema_in_use": {
            "records": len(schema),
            "distinct_values_per_field": constant_fields,
            "discrepancy_declared_by_source": declared,
            "discrepancy_found_by_collector": collector_found,
        },
        "publisher_target": "amendments incorporated within three months of "
                            "coming into force (legislation.gov.uk); "
                            "compliance is not computable from this metadata "
                            "because commencement dates are not published",
        "tail": tail,
        "revised_within_a_year_but_carrying_effects_10_years_or_older":
            recently_revised_with_old_effects[:15],
        "count_revised_within_a_year_carrying_old_effects":
            len(recently_revised_with_old_effects),
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
    if u["acts_status_revised"]:
        print(f"\nof the {u['acts_status_revised']} Acts the service maintains in "
              f"revised form, {u['acts_affected_share_of_revised']*100:.1f}% are "
              f"affected")
        print(f"  {u['acts_status_final']} are marked final --- served as enacted, "
              f"with no revised text\n  for an amendment to be missing from; "
              f"{u['final_acts_carrying_an_unapplied_effect']} of those carry an "
              f"unapplied effect anyway")
    if u["body_paragraphs_in_those_acts"]:
        print(f"\n{u['affected_provisions_in_those_acts']:,} affected provisions "
              f"against {u['body_paragraphs_in_those_acts']:,} body paragraphs"
              f"\n  = {u['affected_provisions_per_1000_body_paragraphs']} per "
              f"1,000 ({u['total_paragraphs_in_those_acts']:,} paragraphs "
              f"including schedules)")
        print(f"  over the {u['acts_with_paragraph_statistics']} Acts that publish "
              f"a paragraph count; {u['acts_without_paragraph_statistics']} do not "
              f"and are\n  excluded from both sides of that ratio")
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
    print("\nthe service aims to incorporate amendments within three months of "
          "their coming\n  into force, so some backlog is the design --- the "
          "tail is the question:")
    for key, v in results["tail"].items():
        years = key.split("_")[2]
        print(f"    affecting instrument {years}+ years old: {v['effects']:,} "
              f"effects ({v['share']*100:.1f}%)")
    n = results["count_revised_within_a_year_carrying_old_effects"]
    print(f"\n{n} Acts were revised within the last year and still carry an "
          f"effect from an\n  instrument 10+ years old --- a standing queue, "
          f"not an untouched record")
    for r in results[
            "revised_within_a_year_but_carrying_effects_10_years_or_older"][:5]:
        print(f"    {r['effects_from_instruments_10_years_or_older']:>4} effects, "
              f"oldest {r['oldest_affecting_instrument_year']}, "
              f"revised {r['last_modified']}  {(r['title'] or '')[:44]}")
    s = results["schema_in_use"]
    print(f"\nthe five-field schema over {s['records']} records: "
          f"distinct values per field")
    for field, n in s["distinct_values_per_field"].items():
        print(f"    {field:16s} {n}")
    print(f"    discrepancy      declared by the source {s['discrepancy_declared_by_source']}, "
          f"found by the collector {s['discrepancy_found_by_collector']}")
    print("  four fields near-constant is the schema behaving correctly on a "
          "well-run API;\n  it is the discrepancy field that carries this "
          "jurisdiction, and only once it\n  records who declared the problem")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
