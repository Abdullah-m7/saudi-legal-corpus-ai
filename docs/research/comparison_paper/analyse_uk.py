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


# What each field describes, which is not the same as what it is about.
#
# A value describing the *encounter* --- this collector, this network, this day
# --- cannot be compared against another collection's, because the two
# encounters differ before the records do. A value describing the *record as
# published* can: any reader reproduces it.
#
# Four of paper 5's five fields describe the encounter. That is why the
# availability half of this comparison had to be abandoned (see README): not a
# network accident that a control could have fixed, but the structure of the
# schema. And `discrepancy` is neither, or both --- it depends on who declared
# it, which is the refinement this jurisdiction forced.
FIELD_KIND = {
    "source_class": "record",       # whose copy this is, a fact about the source
    "retrieval_route": "encounter",  # whether the live source answered *us*
    "corroboration": "encounter",    # how many sources *we* found agreeing
    "transformation": "encounter",   # what *we* had to do to the bytes we got
    "discrepancy": "depends on declared_by",
}

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
    def flagged_effects(act):
        return [e for e in act.get("effects", [])
                if e.get("RequiresApplied") == "true"]

    def effect_state(effect):
        """What a flagged effect actually is. Three answers, not two.

        This measure has been wrong twice, each time by reading one field and
        stopping. `RequiresApplied="true"` says only that the effect has not
        been applied; taken as a backlog it overstates by 145 times. Excluding
        `Prospective="true"` fixes most of that and still overstates by ten,
        because an effect can be non-prospective — its commencement date is
        settled — and that date can be in the future. A commencement fixed for
        next March is no more in force than one with no date at all.

        Only `in_force` means the displayed text does not reflect the law.
        """
        if effect.get("InForceProspective") == "true":
            return "prospective"
        raw = (effect.get("InForceDate") or "")[:10]
        try:
            started = date.fromisoformat(raw)
        except ValueError:
            return "in_force_undated"
        return "in_force" if started <= as_of else "commencement_scheduled"

    def live_effects(act):
        return [e for e in flagged_effects(act)
                if effect_state(e) in ("in_force", "in_force_undated")]

    # The service marks each Act `revised` --- maintained in amended form --- or
    # `final`. A `final` Act is served as enacted, so it has no revised text for
    # an amendment to be missing from, and an absence of unapplied effects on it
    # says nothing about whether it reflects the law in force. Left in the
    # denominator it would look clean and pull the headline share down. Both
    # shares are reported rather than one chosen quietly. What is observed is
    # reported as observed: `final` Acts carrying an unapplied effect are
    # counted, not assumed away.
    # A wholly repealed Act has no live text to be out of date, so it belongs in
    # the denominator no more than a `final` one does. The service marks repeal
    # in the title rather than in a metadata field, so this is title-derived and
    # said to be. It matters much less than the status split --- 4 of the
    # affected Acts are repealed and they carry 5 effects out of thousands ---
    # but it is the same argument, and reporting only the denominator that
    # flatters the finding would be the error this analysis is built to avoid.
    def is_repealed(act):
        return "(repealed)" in (act.get("title") or "")

    revised = [a for a in got if a.get("document_status") == "revised"]
    final = [a for a in got if a.get("document_status") != "revised"]
    live = [a for a in revised if not is_repealed(a)]
    repealed = [a for a in got if is_repealed(a)]
    affected = [a for a in got if live_effects(a)]
    affected_final = [a for a in final if live_effects(a)]
    all_effects = [e for a in got for e in live_effects(a)]
    every_effect = [e for a in got for e in a.get("effects", [])]
    states = Counter(effect_state(e) for a in got for e in flagged_effects(a))
    # How long each in-force effect has actually gone unapplied --- the measure
    # the withdrawn version said could not be computed because commencement
    # dates were not published. They are published, in ukm:InForce.
    overdue = []
    for a in got:
        for e in flagged_effects(a):
            if effect_state(e) != "in_force":
                continue
            started = date.fromisoformat(e["InForceDate"][:10])
            overdue.append({"days": (as_of - started).days,
                            "act": a["id"], "title": a.get("title"),
                            "provisions": e.get("AffectedProvisions"),
                            "in_force_since": e["InForceDate"][:10]})
    overdue.sort(key=lambda r: -r["days"])

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

    # Effects grouped by how old the amending instrument is. Bands rather than
    # single years because the reader's question is "how far past any plausible
    # window", not "how many in 2011"; the publisher's target is three months,
    # so the first band is already far outside it.
    bands = [(0, 4, "under 5 years"), (5, 9, "5-9"), (10, 19, "10-19"),
             (20, 29, "20-29"), (30, 999, "30 or more")]
    by_band = {label: 0 for _, _, label in bands}
    for year, count in ages.items():
        age = as_of.year - year
        for lo, hi, label in bands:
            if lo <= age <= hi:
                by_band[label] += count
                break

    # The cross-tabulation behind the backlog-or-neglect claim: when the service
    # last revised an Act against how old the oldest amendment it has still not
    # applied is. A record nobody maintains sits top-left; the finding is the
    # mass at the right-hand end of the recent columns.
    cross = {}
    for a in affected:
        modified = (a.get("last_modified") or "")[:4]
        # Not `years`: that name holds the collection's own year range, and
        # rebinding it here left the coverage line reporting "2026-2026" for a
        # collection spanning 1988 to 2026 --- which would have gone into the
        # manuscript as the period the study covers.
        affecting_years = [int(e["AffectingYear"]) for e in live_effects(a)
                           if e.get("AffectingYear", "").isdigit()]
        if not modified.isdigit() or not affecting_years:
            continue
        decade = (as_of.year - min(affecting_years)) // 10 * 10
        key = f"{modified}|{decade}"
        cross[key] = cross.get(key, 0) + 1

    # Where the old part of the queue comes from. Banding the ages hid this:
    # the pre-2022 tail is not a smooth decay but a set of spikes, and each
    # spike turns out to be dominated by a single amending instrument. That
    # makes the old backlog a small number of identifiable instruments nobody
    # has worked through, rather than diffuse neglect --- a different problem
    # with a different remedy.
    #
    # Reported by URI and not by name. The instrument's title lives in
    # `ukm:AffectingTitle`, a child element rather than an attribute, so the
    # collector's attribute-based parse never captured it. Supplying names from
    # memory instead is exactly the fault that reached the opening paragraph of
    # paper 4 before review caught it.
    old_effects = [e for e in all_effects
                   if e.get("AffectingYear", "").isdigit()
                   and int(e["AffectingYear"]) < as_of.year - 4]
    by_instrument = Counter(e.get("AffectingURI", "?") for e in old_effects)
    old_total = sum(by_instrument.values())
    top_ten = by_instrument.most_common(10)

    per_act = sorted((len(live_effects(a)), a["id"], a.get("title") or "")
                     for a in affected)[::-1]
    total = sum(n for n, _, _ in per_act)
    top10 = sum(n for n, _, _ in per_act[:10])

    if years and len(set(years)) != max(years) - min(years) + 1:
        missing = sorted(set(range(min(years), max(years) + 1)) - set(years))
        print(f"  ! collection has gaps: {missing}")
    results = {
        "coverage": {
            "years": [min(years), max(years)] if years else None,
            "years_collected": len(set(years)),
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
            "flagged_effects_by_state": dict(states),
            "note": "a flagged effect is not necessarily in force. Prospective "
                    "ones have no commencement date; scheduled ones have a "
                    "date still in the future. The service is correct not to "
                    "apply either, and only the in-force remainder means the "
                    "displayed text does not reflect the law",
            "publisher_target_days": 90,
            "in_force_unapplied_beyond_target":
                sum(1 for r in overdue if r["days"] > 90),
            "longest_unapplied_days": overdue[0]["days"] if overdue else None,
            "in_force_unapplied": overdue[:20],
            "difference_between_the_two_measures":
                len(every_effect) - len(all_effects),
            "distinct_affected_provisions": len(provisions),
            "acts_marked_repealed_in_title": len(repealed),
            "acts_revised_and_not_repealed": len(live),
            "acts_affected_share_of_revised_and_not_repealed":
                round(len([a for a in live if live_effects(a)]) / len(live), 4)
                if live else None,
            "affected_acts_that_are_repealed":
                len([a for a in repealed if live_effects(a)]),
            "effects_sitting_on_repealed_acts":
                sum(len(live_effects(a)) for a in repealed),
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
            "what_each_field_describes": FIELD_KIND,
            "distinct_values_per_field": constant_fields,
            "discrepancy_declared_by_source": declared,
            "discrepancy_found_by_collector": collector_found,
        },
        "publisher_target": "amendments incorporated within three months of "
                            "coming into force (legislation.gov.uk); "
                            "compliance is not computable from this metadata "
                            "because commencement dates are not published",
        "tail": tail,
        "old_queue_concentration": {
            "definition": "effects whose affecting instrument is more than "
                          "four years old, i.e. outside any plausible reading "
                          "of the publisher's three-month target",
            "effects": old_total,
            "distinct_affecting_instruments": len(by_instrument),
            "top_10_share": round(sum(n for _, n in top_ten) / old_total, 4)
                            if old_total else None,
            "top_10": [{"affecting_uri": u, "effects": n} for u, n in top_ten],
            "titles": "not recorded --- ukm:AffectingTitle is a child element, "
                      "not an attribute, so the collector did not capture it; "
                      "names must be verified from source before use",
        },
        "effects_by_age_band_of_affecting_instrument": by_band,
        "acts_by_last_revised_year_and_oldest_effect_decade": cross,
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
    print(f"years {c['years'][0]}-{c['years'][1]} "
          f"({c['years_collected']} collected)   "
          f"Acts listed {c['acts_listed']}, retrieved {c['acts_retrieved']} "
          f"({c['recovered_on_second_attempt']} on a second attempt), "
          f"never retrieved {c['acts_never_retrieved']}")
    print(f"\nActs displaying text the service says is out of date: "
          f"{u['acts_affected']}/{c['acts_retrieved']} "
          f"({u['acts_affected_share']*100:.1f}%)")
    print(f"  amendments enacted but not incorporated: "
          f"{u['effects_requiring_application']:,}")
    print(f"  across {u['distinct_affected_provisions']:,} distinct provisions")
    print("\nwhat the flagged effects actually are:")
    total_flagged = sum(u["flagged_effects_by_state"].values())
    labels = {"prospective": "prospective --- no commencement date",
              "commencement_scheduled": "commencement scheduled, still future",
              "in_force": "in force now, and unapplied",
              "in_force_undated": "in force, no date recorded"}
    for key, label in labels.items():
        v = u["flagged_effects_by_state"].get(key, 0)
        print(f"    {v:>7,}  {v / total_flagged * 100:5.1f}%  {label}")
    print(f"\nagainst the publisher's three-month target: "
          f"{u['in_force_unapplied_beyond_target']} effects exceed it")
    if u["longest_unapplied_days"] is not None:
        print(f"  the longest any amendment has been in force and unapplied is "
              f"{u['longest_unapplied_days']} days")
    print(f"  ten most affected Acts hold "
          f"{u['top_10_acts_share_of_effects']*100:.1f}% of all of them")
    print(f"\nthree denominators, none of them the obvious one on its own:")
    print(f"    all {c['acts_retrieved']} retrieved            "
          f"{u['acts_affected_share']*100:5.1f}% affected")
    print(f"    {u['acts_status_revised']:>4} maintained in revised form  "
          f"{u['acts_affected_share_of_revised']*100:5.1f}%")
    print(f"    {u['acts_revised_and_not_repealed']:>4} revised and not repealed   "
          f"{u['acts_affected_share_of_revised_and_not_repealed']*100:5.1f}%")
    print(f"  {u['acts_marked_repealed_in_title']} Acts are marked repealed in "
          f"their title (the service records repeal there,\n  not in a metadata "
          f"field, so this is title-derived); "
          f"{u['affected_acts_that_are_repealed']} of them are affected,\n  "
          f"carrying {u['effects_sitting_on_repealed_acts']} effects")
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
        print(f"    {field:16s} {n}   describes the "
              f"{s['what_each_field_describes'][field]}")
    print(f"    discrepancy      declared by the source {s['discrepancy_declared_by_source']}, "
          f"found by the collector {s['discrepancy_found_by_collector']}")
    print("  four fields near-constant is the schema behaving correctly on a "
          "well-run API;\n  it is the discrepancy field that carries this "
          "jurisdiction, and only once it\n  records who declared the problem")
    o = results["old_queue_concentration"]
    if o["effects"]:
        print(f"\nthe old part of the queue is concentrated, not diffuse:")
        print(f"  {o['effects']:,} effects from instruments more than four "
              f"years old,\n  from {o['distinct_affecting_instruments']} "
              f"distinct instruments --- the ten most prolific hold "
              f"{o['top_10_share']*100:.1f}%")
        for row in o["top_10"][:5]:
            print(f"    {row['effects']:>4}  "
                  f"{row['affecting_uri'].split('/id/')[-1]}")
        print("  (by identifier; titles are not in the collection and must be "
              "verified before use)")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
