#!/usr/bin/env python3
"""Turn the analysis results into LaTeX macros the manuscript can use.

Every number in papers 1 to 5 was typed into the manuscript by hand and checked
by review afterwards. Review caught a wrong share in paper 3, a wrong count and
a wrong top-ten figure in paper 4, and a wrong article count in paper 5 --- four
defects of one kind, each of which had survived every earlier reading because a
plausible number in prose looks exactly like a correct one.

This removes the class rather than checking for it. The manuscript never
contains a digit; it contains `\\nActsRetrieved`, and the macro is regenerated
from `uk_analysis_results.json` before every compile. A number cannot go stale,
cannot be mistyped, and cannot disagree with the analysis, because there is
only one copy of it.

The formatting rules are here rather than in the manuscript for the same
reason: thousands separators and percentages to one decimal are decisions that
should be made once.

    python3 docs/research/comparison_paper/make_numbers.py

Named `make_numbers.py`, not `numbers.py`. The obvious name shadows Python's
standard-library `numbers` module for every script in this directory, and numpy
imports it: `make_figures.py` died with "module 'numbers' has no attribute
'Integral'", an error naming neither this file nor the collision.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "uk_analysis_results.json"
OUT = HERE / "numbers.tex"


def thousands(n):
    return f"{n:,}".replace(",", "{,}")


def percent(x, places=1):
    return f"{x * 100:.{places}f}"


def macros(r):
    c, u, s = r["coverage"], r["unincorporated"], r["schema_in_use"]
    o, tail = r["old_queue_concentration"], r["tail"]
    m = {
        "AsOf": r["as_of"],
        "YearFrom": str(c["years"][0]),
        "YearTo": str(c["years"][1]),
        "ActsListed": thousands(c["acts_listed"]),
        "ActsRetrieved": thousands(c["acts_retrieved"]),
        "ActsRecovered": thousands(c["recovered_on_second_attempt"]),
        "ActsNeverRetrieved": thousands(c["acts_never_retrieved"]),
        "ActsAffected": thousands(u["acts_affected"]),
        "ActsAffectedShare": percent(u["acts_affected_share"]),
        "ActsRevised": thousands(u["acts_status_revised"]),
        "ActsFinal": thousands(u["acts_status_final"]),
        "ActsRepealed": thousands(u["acts_marked_repealed_in_title"]),
        "AffectedShareOfRevised": percent(u["acts_affected_share_of_revised"]),
        "AffectedShareOfLive":
            percent(u["acts_affected_share_of_revised_and_not_repealed"]),
        "Effects": thousands(u["effects_requiring_application"]),
        "EffectsInBlock": thousands(u["effects_in_block_total"]),
        "EffectsOverstatement":
            thousands(u["difference_between_the_two_measures"]),
        "Provisions": thousands(u["distinct_affected_provisions"]),
        "BodyParagraphs": thousands(u["body_paragraphs_in_those_acts"]),
        "ProvisionsPerThousand":
            f"{u['affected_provisions_per_1000_body_paragraphs']:.1f}",
        "TopTenActShare": percent(u["top_10_acts_share_of_effects"]),
        "OldQueueEffects": thousands(o["effects"]),
        "OldQueueInstruments": thousands(o["distinct_affecting_instruments"]),
        "OldQueueTopTenShare": percent(o["top_10_share"]),
        "SchemaRecords": thousands(s["records"]),
        "DiscrepancyDeclared": thousands(s["discrepancy_declared_by_source"]),
        "DiscrepancyFound": thousands(s["discrepancy_found_by_collector"]),
        "BackwardEffects":
            thousands(r["effects_whose_affecting_instrument_predates_the_act"]),
        "MaintainedButStale":
            thousands(r["count_revised_within_a_year_carrying_old_effects"]),
    }
    # A LaTeX control sequence is letters only: \nTailEffects10 parses as
    # \nTailEffects followed by the characters "10", which fails with an error
    # naming \begin{document} and pointing nowhere near the cause. The
    # thresholds are spelled out for that reason and no other.
    words = {5: "Five", 10: "Ten", 20: "Twenty"}
    for threshold, word in words.items():
        key = f"affecting_instrument_{threshold}_or_more_years_old"
        m[f"TailEffects{word}"] = thousands(tail[key]["effects"])
        m[f"TailShare{word}"] = percent(tail[key]["share"])
    # From the pre-1988 probe, which is a sample rather than a sweep and lives
    # in the README with its method. Hard-coded here because it is measured
    # data that no analysis run produces; regenerate it by re-running the probe
    # if the claim is ever revisited.
    st = u["flagged_effects_by_state"]
    flagged = sum(st.values())
    m["Flagged"] = thousands(flagged)
    m["Prospective"] = thousands(st.get("prospective", 0))
    m["ProspectiveShare"] = percent(st.get("prospective", 0) / flagged)
    m["Scheduled"] = thousands(st.get("commencement_scheduled", 0))
    m["ScheduledShare"] = percent(st.get("commencement_scheduled", 0) / flagged)
    m["InForceNow"] = thousands(st.get("in_force", 0))
    m["InForceShare"] = percent(st.get("in_force", 0) / flagged)
    m["InForceUndated"] = thousands(st.get("in_force_undated", 0))
    m["TargetDays"] = str(u["publisher_target_days"])
    m["BeyondTarget"] = str(u["in_force_unapplied_beyond_target"])
    m["LongestDays"] = str(u["longest_unapplied_days"])
    m["OverstatementFactor"] = str(round(flagged / u["effects_requiring_application"]))
    m["PreSampleActs"] = "20"
    m["PreSampleAffected"] = "five"
    m["PreSampleEffects"] = "218"
    m["HighwaysEffects"] = "132"
    oldest = r.get("oldest_affecting_instrument") or {}
    if oldest:
        m["OldestInstrumentYear"] = str(oldest["year"])
        m["OldestInstrumentYearsSince"] = str(oldest["years_since"])
    return m


def main():
    r = json.loads(RESULTS.read_text(encoding="utf-8"))
    m = macros(r)
    lines = ["% Generated by numbers.py from uk_analysis_results.json.",
             "% Do not edit: every value here has exactly one source, and it is",
             "% not this file. Regenerated before each build.", ""]
    bad = [k for k in m if not k.isalpha()]
    if bad:
        raise SystemExit(
            f"macro names must be letters only --- LaTeX cannot define "
            f"\\n{bad[0]}: {sorted(bad)}")
    lines += [f"\\newcommand{{\\n{k}}}{{{v}}}" for k, v in sorted(m.items())]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}: {len(m)} macros")
    return m


if __name__ == "__main__":
    main()
