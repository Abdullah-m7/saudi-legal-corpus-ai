#!/usr/bin/env python3
"""The evidentiary basis of a digital legal corpus (paper 5).

Papers 1--4 measured what a legal system contains, how it connects, whether it
agrees with itself, and how it changes. All four rest on an assumption that
nobody states: that the official text was reachable and stable when the corpus
was built. This one tests that assumption against the record the corpus kept
while being built.

Every verified article carries a provenance string naming the sources consulted
and how they were reconciled, and every track carries a hand-assigned
verification tier. Those strings are free text written during the build, not a
controlled vocabulary, so the script classifies each distinct string by an
explicit rule and publishes the whole mapping for audit rather than asserting
the counts. Strings that turn out not to be provenance statements at all --- an
amendment status that leaked into the field --- are excluded and reported.

Read-only and deterministic over `sources/` and `data/`. Run from the
repository root:

    python3 docs/research/provenance_paper/provenance_analysis.py
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = REPO_ROOT / "data" / "corpus_registry" / "corpus_registry.json"
TIERS = (REPO_ROOT / "data" / "corpus_verification_tiers"
         / "corpus_verification_tiers.json")
FRESHNESS = (REPO_ROOT / "data" / "corpus_freshness_manifest"
             / "corpus_freshness_manifest.json")
OUT = Path(__file__).resolve().parent / "provenance_analysis_results.json"

# A string counts as a provenance statement when it names a source, an artefact
# or a retrieval route. Everything else --- a bare lifecycle or amendment
# status that leaked into the same field --- is excluded from every measure
# below and reported separately.
SOURCE_TOKENS = {
    "BOE", "MOJ", "UQN", "HRSD", "ZATCA", "SAMA", "CMA", "MOF", "MOH", "MOI",
    "MOE", "SFDA", "SASO", "SDAIA", "NCA", "REGA", "MISA", "SOCPA", "GACA",
    "MOMAH", "MCIT", "CST", "NEZAMS", "QANOONSA", "QANONIAH", "QISTAS", "KSU",
    "WIPO", "WIPOLEX", "FAOLEX", "ISLAMPORT", "MOHAMAH", "RAKADVOCATE",
    "AUNKLAW", "SPA", "ARGAAM", "ALRIYADH", "OKAZ", "SABQ", "GSTC", "NCNP",
    "QADHA", "SAUDIENG", "MAWANI", "BAYANCB", "NCOSH", "SAUDIPEDIA", "WHO",
    "EMRO", "UNODC", "CYRILLA", "LEXISMIDDLEEAST", "PDF", "PORTAL", "GAZETTE",
    "WAYBACK", "ARCHIVE", "API", "OCR", "SCAN", "HTML", "SNAPSHOT", "MIRROR",
    "SOURCE", "TRANSLATION", "CHANGELOG", "POPUP", "RULEBOOK", "JINA",
    "TESSERACT", "PDFTOTEXT", "PDFPLUMBER", "PDFMINER", "POPPLER",
}

# Each measure is a set of tokens; a string counts once for a measure if any
# token appears. The measures overlap by design --- an instrument reached only
# through an archive because the live portal was down scores on both.
MEASURES = {
    "official_source_unreachable": {
        "UNREACHABLE", "UNRESOLVED", "RESET", "CONNRESET", "503", "405",
        "BLOCKED", "UNOBTAINED", "PAYWALLED", "404",
    },
    "reached_through_a_web_archive": {"WAYBACK", "ARCHIVE", "ARCHIVED"},
    "single_source_only": {"SINGLE", "SOLE", "ONLY"},
    "required_optical_or_visual_reconstruction": {
        "OCR", "TESSERACT", "VISUAL", "VISUALLY", "TRANSCRIPTION",
        "TRANSCRIBED", "RECONSTRUCTED", "RECON", "REEXTRACTION",
        "REEXTRACTED", "IMAGE",
    },
    "defect_in_the_official_source": {
        "TYPO", "LIGATURE", "SCRAMBLED", "CONTRADICTION", "ANOMALY", "STALE",
        "DEFECT", "TRANSPOSITION", "REMEDIATED", "CORRECTED", "INCOMPLETE",
        "TRUNCATED",
    },
    "multi_source_cross_verification": {
        "DUAL", "TRIPLE", "MULTI", "CROSS", "CROSSCHECK", "CROSSCHECKED",
        "XVERIFIED", "CORROBORATED",
    },
}


def tokens(text):
    return {t for t in re.split(r"[^A-Za-z0-9]+", (text or "").upper()) if t}


def is_provenance(text):
    return bool(tokens(text) & SOURCE_TOKENS)


def track_resolver():
    """Map a verified-records path to its registry track_id.

    The directory under sources/ is not the track_id --- `patent` holds
    `patent_law` --- so resolve by the registry's own declared paths first and
    fall back to the directory name only when it is itself a track_id. Keying
    on the directory alone silently orphaned four fifths of the corpus from its
    verification tier in an earlier run of this script.
    """
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    track_ids = {t["track_id"] for t in registry["tracks"]}
    by_path = {}
    for t in registry["tracks"]:
        for key in ("data_paths", "manifest_paths", "report_paths"):
            for path in (t.get(key) or []):
                by_path[path] = t["track_id"]

    def resolve(path):
        rel = str(path.relative_to(REPO_ROOT))
        if rel in by_path:
            return by_path[rel]
        segment = path.parts[len(REPO_ROOT.parts) + 1]
        if segment in track_ids:
            return segment
        # sources/<dir>/... where <dir> prefixes exactly one track_id
        candidates = [t for t in track_ids if t.startswith(segment + "_")]
        return candidates[0] if len(candidates) == 1 else None

    return resolve


def load_articles():
    """Every verified article record and the provenance string it carries.

    `official_text_status` is preferred because it is populated for every
    record; `verification_status` fills in where it is not.
    """
    resolve = track_resolver()
    rows, unresolved = [], set()
    for path in sorted(REPO_ROOT.glob(
            "sources/**/verified/*verified_records.jsonl")):
        track = resolve(path)
        if track is None:
            unresolved.add(str(path.relative_to(REPO_ROOT)))
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                status = (rec.get("official_text_status")
                          or rec.get("verification_status"))
                if status is None:
                    continue
                rows.append({"track": track,
                             "article": rec.get("article_number"),
                             "status": " ".join(str(status).split())})
    if unresolved:
        raise SystemExit("unresolved verified-record files: "
                         + ", ".join(sorted(unresolved)[:5]))
    return rows


def classify_strings(rows):
    """Every distinct provenance string, with its classification and weight.

    Published in full so that a reader can disagree with any single
    assignment rather than having to trust the totals.
    """
    per_string = Counter(r["status"] for r in rows)
    table = []
    for text, count in per_string.most_common():
        provenance = is_provenance(text)
        tk = tokens(text)
        table.append({
            "string": text,
            "articles": count,
            "is_provenance_statement": provenance,
            "measures": sorted(name for name, keys in MEASURES.items()
                               if tk & keys) if provenance else [],
        })
    return table


def measure(rows, table):
    by_string = {t["string"]: t for t in table}
    provenance_rows = [r for r in rows
                       if by_string[r["status"]]["is_provenance_statement"]]
    excluded = [r for r in rows
                if not by_string[r["status"]]["is_provenance_statement"]]

    article_hits = Counter()
    track_hits = defaultdict(set)
    for r in provenance_rows:
        for name in by_string[r["status"]]["measures"]:
            article_hits[name] += 1
            track_hits[name].add(r["track"])

    tracks_with_provenance = {r["track"] for r in provenance_rows}
    n_articles = len(provenance_rows)
    n_tracks = len(tracks_with_provenance)

    out = {
        "articles_with_a_status_field": len(rows),
        "distinct_status_strings": len(by_string),
        "articles_whose_status_is_a_provenance_statement": n_articles,
        "articles_excluded_not_a_provenance_statement": len(excluded),
        "excluded_strings": sorted(
            {r["status"] for r in excluded},
            key=lambda s: -Counter(x["status"] for x in excluded)[s])[:12],
        "note": "The status field mixes provenance statements with lifecycle "
                "values such as UNCHANGED. Only the former are measured; the "
                "mixture is itself reported in the paper as a finding about "
                "uncontrolled provenance vocabularies.",
        "tracks_with_a_provenance_statement": n_tracks,
        "measures": {},
    }
    for name in MEASURES:
        out["measures"][name] = {
            "articles": article_hits[name],
            "article_share": round(article_hits[name] / n_articles, 4)
            if n_articles else 0.0,
            "tracks": len(track_hits[name]),
            "track_share": round(len(track_hits[name]) / n_tracks, 4)
            if n_tracks else 0.0,
        }
    return out, provenance_rows


def unavailability_and_archive_overlap(rows, table):
    """How often the archive stood in for an unreachable official source.

    Two similar marginals do not establish that they describe the same
    instruments. The claim needs the joint distribution, so it is computed.
    """
    by_string = {t["string"]: t for t in table}
    prov = [r for r in rows if by_string[r["status"]]["is_provenance_statement"]]
    unreachable = archive = both = 0
    for r in prov:
        m = set(by_string[r["status"]]["measures"])
        u = "official_source_unreachable" in m
        a = "reached_through_a_web_archive" in m
        unreachable += u
        archive += a
        both += u and a
    total = len(prov)
    return {
        "articles": total,
        "unreachable": unreachable,
        "archive": archive,
        "both": both,
        "share_of_unreachable_that_also_used_an_archive":
            round(both / unreachable, 4) if unreachable else 0.0,
        "share_of_archive_use_that_was_also_unreachable":
            round(both / archive, 4) if archive else 0.0,
        "archive_without_recorded_unavailability": archive - both,
        "unavailability_without_archive_recovery": unreachable - both,
        "reading": "The archive standing in for an unreachable official page "
                   "is the dominant pattern but not the only one: about two "
                   "thirds of each set overlaps, and each retains a "
                   "substantial remainder.",
    }


def tier_analysis(provenance_rows):
    """The hand-assigned tiers, weighted by article as well as by track.

    A single-source track of five articles and one of three hundred are not
    the same exposure, and a track count cannot tell them apart.
    """
    tiers = json.loads(TIERS.read_text(encoding="utf-8"))
    by_track = {t["track_id"]: t for t in tiers["tracks"]}
    articles_per_track = Counter(r["track"] for r in provenance_rows)

    by_tier_articles = Counter()
    by_tier_tracks = Counter()
    unmatched = 0
    for track, n in articles_per_track.items():
        entry = by_track.get(track)
        if entry is None:
            unmatched += n
            continue
        by_tier_articles[entry["tier"]] += n
        by_tier_tracks[entry["tier"]] += 1

    total_articles = sum(by_tier_articles.values())
    order = tiers["tier_order"]
    weak = [t for t in order if t.startswith(("TIER_3", "TIER_4"))]

    # The article-level sample does not cover every track, and the tracks it
    # misses are not a random draw: the weakest-evidence tiers are the least
    # likely to have article-level verified records at all. Quantify the gap
    # so the direction of the bias is stated rather than assumed.
    registry_wide = tiers["summary_by_tier"]
    coverage = {t: {
        "tracks_registry_wide": registry_wide.get(t, 0),
        "tracks_in_the_article_sample": by_tier_tracks[t],
        "coverage": round(by_tier_tracks[t] / registry_wide[t], 4)
        if registry_wide.get(t) else None,
    } for t in order}
    return {
        "taxonomy": {k: " ".join(str(v).split())[:200]
                     for k, v in tiers["taxonomy"].items()},
        "tracks_by_tier_registry_wide": tiers["summary_by_tier"],
        "tracks_with_per_article_variation": tiers[
            "tracks_with_per_article_variation"],
        "articles_by_tier": {t: by_tier_articles[t] for t in order},
        "article_share_by_tier": {
            t: round(by_tier_articles[t] / total_articles, 4)
            for t in order} if total_articles else {},
        "tracks_by_tier_in_this_sample": {t: by_tier_tracks[t] for t in order},
        "articles_in_a_track_with_no_tier_record": unmatched,
        "articles_without_a_cross_verified_official_primary":
            sum(by_tier_articles[t] for t in weak),
        "share_without_a_cross_verified_official_primary":
            round(sum(by_tier_articles[t] for t in weak) / total_articles, 4)
        if total_articles else 0.0,
        "sample_coverage_by_tier": coverage,
        "sample_bias": "Coverage is uneven and not monotonic: 87% of tier-1 "
                       "tracks have article-level records against 59% of "
                       "tier-2, 28% of tier-3 and 73% of tier-4. The "
                       "under-representation of tier 3 --- the tracks whose "
                       "official source could not be reached at all --- means "
                       "the share without a cross-verified official primary "
                       "is more likely understated than overstated.",
    }


def self_contradiction_cases(rows, table):
    """Where the official record disagrees with itself.

    The sharpest evidence in the corpus: an official portal whose displayed
    text and whose own change log do not match, or whose article contradicts
    another part of the same portal.
    """
    def contradicts_itself(tk):
        # Either the record says so outright, or the portal's own change log
        # disagrees with the article the same portal displays.
        if {"CONTRADICTION", "ANOMALY"} & tk:
            return True
        return "CHANGELOG" in tk and bool(
            {"STALE", "MISMATCH", "OMITS", "UNRESOLVED"} & tk)

    cases = []
    seen = set()
    for r in rows:
        tk = tokens(r["status"])
        if not contradicts_itself(tk) or not is_provenance(r["status"]):
            continue
        if r["status"] in seen:
            continue
        seen.add(r["status"])
        cases.append({"track": r["track"], "article": r["article"],
                      "status": r["status"]})
    # A provenance string is attached to every article of its track, so the
    # number of articles carrying it is the scope of the VERIFICATION ROUTE,
    # not the scope of the contradiction. The Environmental Law's string rides
    # on 49 articles while its registry note records that 48 of them matched
    # verbatim across three sources and one definition in article 1 did not.
    # The articles actually implicated are therefore read from each track's own
    # note and recorded here, with the string count kept as the upper bound it
    # is.
    DIRECTLY_IMPLICATED = {
        "environmental_law": {
            "articles": [1],
            "what": "BOE's own per-article amendment log gives a current "
                    "wording for the definition of `the competent authority' "
                    "that differs from BOE's own main running text. The other "
                    "48 articles matched verbatim across all three sources.",
        },
        "press_law": {
            "articles": [5, 9, 36, 37, 38, 40],
            "what": "BOE's page carries a changed-article marker and a fully "
                    "quoted amendment log for each of these articles while its "
                    "main displayed body still shows the pre-amendment text.",
        },
        "engineering_practice_law": {
            "articles": [1],
            "what": "BOE's change log quotes Council of Ministers Resolution "
                    "250 (7/4/1444H) substituting a ministry name, while BOE's "
                    "main body has shown a third, different wording at every "
                    "snapshot checked since 2019 --- predating the resolution.",
        },
        "travel_documents_law": {
            "articles": [6],
            "what": "BOE's own amendment log for the article omits any decree "
                    "citation for its 1439H amendment; the citation was "
                    "recovered from a secondary source.",
        },
    }

    per_string = Counter(r["status"] for r in rows)
    stale = [r for r in rows
             if "STALE" in tokens(r["status"]) and is_provenance(r["status"])
             and not contradicts_itself(tokens(r["status"]))]
    return {
        "measure": "The official record contradicting itself --- a portal "
                   "whose displayed article and whose own change log differ, "
                   "or which contradicts another part of itself. Reported "
                   "separately from mere staleness against an independent "
                   "source, which is a weaker claim.",
        "separately_stale_against_another_source": {
            "articles": len(stale),
            "tracks": len({r["track"] for r in stale}),
        },
        "distinct_strings": len(cases),
        "articles_directly_implicated": sum(
            len(v["articles"]) for v in DIRECTLY_IMPLICATED.values()),
        "directly_implicated": DIRECTLY_IMPLICATED,
        "articles_carrying_one_of_these_strings_upper_bound": sum(
            per_string[c["status"]] for c in cases),
        "tracks_affected": len({
            r["track"] for r in rows
            if contradicts_itself(tokens(r["status"]))
            and is_provenance(r["status"])}),
        "cases": sorted(cases, key=lambda c: -per_string[c["status"]])[:20],
    }


def freshness():
    manifest = json.loads(FRESHNESS.read_text(encoding="utf-8"))
    return {
        "total_tracks": manifest["total_tracks"],
        "known_source_staleness_risk_count":
            manifest["known_source_staleness_risk_count"],
        "tracks_without_a_resolvable_official_source_file":
            len(manifest["tracks_without_resolvable_official_source_file"]),
        "methodology": " ".join(
            manifest["known_source_staleness_risk_methodology"].split())[:300],
    }


def main():
    rows = load_articles()
    table = classify_strings(rows)
    measures, provenance_rows = measure(rows, table)
    results = {
        "provenance_layer": measures,
        "verification_tiers": tier_analysis(provenance_rows),
        "unavailability_and_archive_overlap":
            unavailability_and_archive_overlap(rows, table),
        "official_record_disagrees_with_itself":
            self_contradiction_cases(rows, table),
        "freshness": freshness(),
        "string_classification_table": table,
    }
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"wrote {OUT}")
    p = results["provenance_layer"]
    print(f"  {p['articles_with_a_status_field']:,} articles carry a status "
          f"field; {p['distinct_status_strings']} distinct strings")
    print(f"  {p['articles_whose_status_is_a_provenance_statement']:,} are "
          f"provenance statements "
          f"({p['articles_excluded_not_a_provenance_statement']:,} excluded)")
    for name, m in p["measures"].items():
        print(f"    {name:44} {m['article_share']:6.1%} of articles, "
              f"{m['track_share']:6.1%} of instruments")
    t = results["verification_tiers"]
    print(f"  {t['share_without_a_cross_verified_official_primary']:.1%} of "
          "articles sit in a track with no cross-verified official primary")
    o = results["unavailability_and_archive_overlap"]
    print(f"  archive stood in for an unreachable source in "
          f"{o['share_of_unreachable_that_also_used_an_archive']:.1%} of the "
          "unreachable cases")
    c = results["official_record_disagrees_with_itself"]
    print(f"  official record disagrees with itself: {c['tracks_affected']} "
          f"instruments, {c['articles_directly_implicated']} articles "
          "directly implicated")


if __name__ == "__main__":
    main()
