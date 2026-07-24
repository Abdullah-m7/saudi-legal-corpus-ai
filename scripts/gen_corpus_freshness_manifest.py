#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Freshness Manifest — Derived, Additive Drift-Monitoring Survey Layer

Reads the canonical corpus registry (data/corpus_registry/corpus_registry.json), the
verification-tiers layer (data/corpus_verification_tiers/corpus_verification_tiers.json),
and each of the 178 tracks' own `official_source.json`-equivalent file, and produces a single
survey manifest that lets a human periodically re-check whether a track's SOURCE has drifted
since it was last captured — WITHOUT needing another full research/build pass.

This is a READ-ONLY, PURELY ADDITIVE derived layer, exactly like
scripts/gen_corpus_verification_tiers.py:
  - It does NOT modify the registry, the verification-tiers file, or any of the 178 tracks'
    own files (official_source.json, notes, source_authority, etc.).
  - It does NOT perform any network access. It only reads files already committed to this
    repository. This is what makes it safe to run inside the deterministic QA gate.
  - It does NOT recompute a track's own verification tier or per-article confidence — it only
    cross-references data/corpus_verification_tiers/corpus_verification_tiers.json and points
    back at it.

DETERMINISM / NO FABRICATED TIMESTAMPS
    This generator NEVER calls datetime.now() (or any wall-clock source) to populate a "last
    checked" field. Any date-like information in the output (e.g. a Wayback Machine snapshot
    date, a `fetch_date` field) is extracted verbatim from a track's own already-committed
    files. Where no such date exists in a track's own files, `last_verified_context` says so
    explicitly rather than inventing one. This keeps the generator byte-for-byte idempotent
    across re-runs (verified by scripts/validate_corpus_freshness_manifest.py).

THE SINGLE MOST VALUABLE FIELD: `known_source_staleness_risk`
    Several tracks' own `official_source.json` `known_unresolved_discrepancies` entries
    already document, from the original research pass itself, that the primary government
    portal (usually laws.boe.gov.sa) was confirmed to display STALE / outdated text at build
    time (as opposed to merely being unreachable, or containing a stale INSTITUTIONAL NAME
    baked permanently into the statute's own wording, which is a different, non-monitorable
    concern). Those tracks are the best starting point for a future re-check, so they are
    flagged `known_source_staleness_risk: true` with a one-line pointer back to the exact
    discrepancy entry that documents it. As of this writing that is exactly 4 tracks:
    traffic_law, patent_law, income_tax_law, and environmental_law — independently confirmed
    by the hand-authored RATIONALE_OVERRIDE / PER_ARTICLE_VARIATION_NOTE entries already in
    scripts/gen_corpus_verification_tiers.py for the same four tracks.

    Deliberately EXCLUDED from this flag (spot-checked): civil_service_law (its own
    discrepancy text explicitly says "ليس نصاً قديماً (stale)" — NOT stale, just an
    under-cited amendment metadata gap — and separately flags a stale MINISTRY NAME, a
    different, non-portal-drift concern); allegiance_commission_law (BOE unreachable this
    pass, never confirmed stale); insurance_control_law (a stale mof.gov.sa PDF is
    explicitly "not used as a source for this track"); anti_narcotics_law / ecommerce_law
    (stale institutional/authority NAMEs baked into 1990s/2000s-era statute text, not source
    drift); council_of_ministers_law (secondary references Wikisource/FAOLEX flagged stale,
    not the primary source actually used); judicial_training_center_guide (an internal
    drift within the source document's own text, not a government-portal staleness signal).

NOT PART OF THE LIVE-CHECK FEATURE
    This script has a sibling, scripts/check_corpus_freshness.py, which DOES make live network
    requests to see whether a track's recorded source URL is still reachable / unchanged. That
    tool is explicitly NOT part of this generator and NOT part of the deterministic QA gate
    (see that script's own docstring). This generator makes no network calls whatsoever.

Reads:
    data/corpus_registry/corpus_registry.json
    data/corpus_verification_tiers/corpus_verification_tiers.json
    each track's own official_source.json-equivalent file (resolved heuristically, see
    resolve_official_source_path())
Writes:
    data/corpus_freshness_manifest/corpus_freshness_manifest.json

Usage:
    python3 scripts/gen_corpus_freshness_manifest.py
"""

from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
REGISTRY_PATH = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
TIERS_PATH = os.path.join(ROOT, "data", "corpus_verification_tiers", "corpus_verification_tiers.json")
OUT_DIR = os.path.join(ROOT, "data", "corpus_freshness_manifest")
OUT_PATH = os.path.join(OUT_DIR, "corpus_freshness_manifest.json")

sys.path.insert(0, SCRIPTS_DIR)
from validate_corpus_registry import REQUIRED_TRACK_IDS  # noqa: E402

# ---------------------------------------------------------------------------
# Known government / standards-body authority domains this corpus's tracks cite. Used only to
# recognize a NAMED authority mentioned in a track's own text even where it isn't wrapped in a
# full https:// URL. This list is descriptive (built from a survey of this corpus's own
# sources/**/official_source.json files), not exhaustive of Saudi government domains in
# general.
# ---------------------------------------------------------------------------
KNOWN_AUTHORITY_DOMAINS = [
    "laws.boe.gov.sa", "boe.gov.sa",
    "zatca.gov.sa", "gstc.gov.sa",
    "wipolex.wipo.int", "wipolex-res.wipo.int", "wipo.int",
    "sdaia.gov.sa", "dgp.sdaia.gov.sa",
    "misa.gov.sa",
    "uqn.gov.sa",
    "moj.gov.sa",
    "sama.gov.sa", "rulebook.sama.gov.sa",
    "cma.org.sa",
    "mci.gov.sa",
    "saip.gov.sa",
    "hrsd.gov.sa",
    "spa.gov.sa",
    "mof.gov.sa",
    "green.org.sa",
    "web.archive.org",
    "nezams.com",  # secondary aggregator, still worth recording since many tracks lean on it
    "qadha.org.sa",
    "qanoonsa.com",
]

URL_RE = re.compile(r"https?://[^\s\"'<>\)\]]+")
# Strip trailing ASCII punctuation plus Arabic comma (،), Arabic semicolon (؛), and Arabic
# question mark (؟), which regularly get glued onto a URL at the end of an Arabic sentence.
TRAILING_PUNCT_RE = re.compile(r"[.,;:'\")\]،؛؟]+$")

# --- known_source_staleness_risk detection -----------------------------------------------
# POSITIVE: language that documents the PRIMARY government portal's own displayed/consolidated
# text as confirmed stale/outdated relative to the genuinely current law (as opposed to merely
# "unreachable this pass", which is a reachability caveat, not a confirmed-content problem).
POSITIVE_STALE_RE = re.compile(
    r"confirmed\s+(?:genuinely\s+)?stale"
    r"|genuinely stale"
    r"|own stale (?:main-body|display|text)"
    r"|stale main-body text"
    r"|has not incorporated"
    r"|not incorporated the"
    r"|default.{0,20}body.{0,60}stale"
    r"|confirmed to be genuinely stale",
    re.IGNORECASE,
)
# EXCLUSION: language that uses the word "stale" but is NOT a portal-drift-risk signal — a
# stale INSTITUTIONAL/MINISTRY NAME permanently baked into old statute wording (not something a
# future re-check of the portal will resolve), an explicit negation, a stale SECONDARY source
# not actually used as this track's source, or an internal drift within a training document's
# own text (not a government-portal currency problem).
EXCLUSION_STALE_RE = re.compile(
    r"stale[- ]ministry name"
    r"|stale[- ]authority name"
    r"|stale.{0,20}institutional name"
    r"|stale-authority note"
    r"|ليس نصّ?اً? قديماً?"  # ليس نصاً قديماً (explicit Arabic negation "not stale text")
    r"|not used as a source for this track"
    r"|internal drift within the source document itself",
    re.IGNORECASE,
)

SNAPSHOT_ISO_DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
SNAPSHOT_MONTH_DATE_RE = re.compile(
    r"(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\s+(20\d{2})"
)
MONTHS = {
    "January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06",
    "July": "07", "August": "08", "September": "09", "October": "10", "November": "11",
    "December": "12",
}


def resolve_official_source_path(track_id: str, data_paths: list[str]) -> str | None:
    """Best-effort, heuristic resolution of a track's own official_source.json-equivalent
    file. Most tracks use a `sources/<x>/<component>/official_source/<...>_official_source.json`
    layout registered directly as one of the track's data_paths. A handful of tracks (pdpl_*,
    investment_*, companies_law, implementing_regulations_*) use a differently-named file or a
    sibling directory instead; those are resolved via directory/token heuristics below.
    Returns a repo-relative path, or None if nothing plausible is found (handled gracefully by
    the caller: the resulting manifest entry falls back to registry-only fields)."""
    # 1. Direct hit: one of the track's own registered data_paths IS the official_source file.
    for p in data_paths:
        base = os.path.basename(p).lower()
        if p.endswith(".json") and "official" in base and "source" in base:
            return p

    # 2. Sibling `official_source/` directory, or same-directory match with a differently
    #    named official/source file (e.g. sources/pdpl/verified/*_official_sdaia_source.json).
    candidates: list[str] = []
    for p in data_paths:
        d = os.path.dirname(p)
        parent = os.path.dirname(d)
        sib = os.path.join(parent, "official_source")
        full_sib = os.path.join(ROOT, sib)
        if os.path.isdir(full_sib):
            for fn in sorted(os.listdir(full_sib)):
                if fn.endswith(".json"):
                    candidates.append(os.path.join(sib, fn))
        full_d = os.path.join(ROOT, d)
        if os.path.isdir(full_d):
            for fn in sorted(os.listdir(full_d)):
                fnl = fn.lower()
                if fn.endswith(".json") and "official" in fnl and "source" in fnl:
                    candidates.append(os.path.join(d, fn))
    candidates = sorted(set(candidates))
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        # Disambiguate (e.g. a "law" vs "regulation" track sharing a domain directory) via
        # filename token overlap with the track's own primary data_path.
        query_tokens = set(re.split(r"[_./]", os.path.basename(data_paths[0]).lower()))
        best = max(
            candidates,
            key=lambda c: len(query_tokens & set(re.split(r"[_./]", os.path.basename(c).lower()))),
        )
        return best

    # 3. Special-cased fallbacks for the handful of tracks with no sources/**/official_source
    #    layout at all (the corpus's earliest tracks, predating that convention).
    special = {
        "companies_law": "data/legal_corpus_factory/law_profiles/sa_companies_law_m136_1443.profile.json",
        "implementing_regulations_general": "data/implementing_regulations/general/source_manifest.json",
        "implementing_regulations_listed_joint_stock": "data/implementing_regulations/listed_joint_stock/source_manifest.json",
        "implementing_regulations_arabic_program_closure": data_paths[0] if data_paths else None,
    }
    fallback = special.get(track_id)
    if fallback and os.path.isfile(os.path.join(ROOT, fallback)):
        return fallback
    return None


def load_json_safe(rel_path: str | None) -> dict | None:
    if not rel_path or not rel_path.endswith(".json"):
        return None
    full = os.path.join(ROOT, rel_path)
    if not os.path.isfile(full):
        return None
    try:
        with open(full, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def extract_urls(text: str) -> list[str]:
    urls = set()
    for m in URL_RE.finditer(text):
        url = TRAILING_PUNCT_RE.sub("", m.group(0))
        urls.add(url)
    return sorted(urls)


def extract_named_authorities(text: str) -> list[str]:
    found = set()
    lowered = text.lower()
    for domain in KNOWN_AUTHORITY_DOMAINS:
        if domain.lower() in lowered:
            found.add(domain)
    return sorted(found)


def detect_staleness_risk(source_obj: dict | None) -> tuple[bool, str]:
    if not source_obj:
        return False, ""
    discrepancies = source_obj.get("known_unresolved_discrepancies")
    if not isinstance(discrepancies, list):
        return False, ""
    for item in discrepancies:
        if not isinstance(item, dict):
            continue
        desc = str(item.get("description", ""))
        if POSITIVE_STALE_RE.search(desc) and not EXCLUSION_STALE_RE.search(desc):
            key = item.get("article_key", "unknown_article_key")
            pointer = f"{key}: {desc[:220].strip()}"
            return True, pointer
    return False, ""


def find_snapshot_dates(text: str, source_obj: dict | None) -> list[str]:
    """Extract snapshot/capture dates that are ALREADY recorded in a track's own committed
    files — never derived from wall-clock time. Two sources: (a) structured 14-digit Wayback
    Machine timestamps found anywhere in the JSON structure (e.g. archive_snapshots[].timestamp),
    and (b) free-text dates that appear within ~60 characters of the word "snapshot"/"wayback"
    in the track's own prose (verification_methodology_note, notes, etc.)."""
    dates: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "timestamp" and isinstance(v, str) and re.fullmatch(r"\d{14}", v):
                    dates.add(f"{v[0:4]}-{v[4:6]}-{v[6:8]}")
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)

    if source_obj:
        walk(source_obj)

    for m in SNAPSHOT_ISO_DATE_RE.finditer(text):
        start, end = max(0, m.start() - 60), min(len(text), m.end() + 60)
        window = text[start:end].lower()
        if "snapshot" in window or "wayback" in window:
            dates.add(m.group(1))

    for m in SNAPSHOT_MONTH_DATE_RE.finditer(text):
        start, end = max(0, m.start() - 60), min(len(text), m.end() + 60)
        window = text[start:end].lower()
        if "snapshot" in window or "wayback" in window:
            day, month_name, year = m.groups()
            dates.add(f"{year}-{MONTHS[month_name]}-{int(day):02d}")

    return sorted(dates)


def build_last_verified_context(text: str, source_obj: dict | None, staleness_risk: bool) -> str:
    """Summarize, from information ALREADY present in the track's own files, what is known
    about when/how its source was last captured and whether it was reachable at build time.
    Never calls datetime.now(); if nothing usable is found, says so explicitly."""
    parts: list[str] = []

    fetch_date = None
    if source_obj:
        for key in ("fetch_date", "access_date"):
            v = source_obj.get(key)
            if isinstance(v, str) and v.strip():
                fetch_date = v.strip()
                break
    if fetch_date:
        parts.append(f"track's own recorded capture/fetch date: {fetch_date}")

    snapshot_dates = find_snapshot_dates(text, source_obj)
    if snapshot_dates:
        parts.append(f"Wayback/archive snapshot date(s) recorded in track's own files: {', '.join(snapshot_dates)}")

    unreachable = bool(re.search(r"\bunreachable\b|\b503\b|connection[- ]reset|blocked by sandbox egress", text, re.IGNORECASE))
    if unreachable:
        parts.append("track's own notes record the primary government portal as unreachable at some point during its build")

    if staleness_risk:
        parts.append("track's own discrepancies confirm the primary portal's displayed text as stale/outdated at build time (see known_source_staleness_pointer)")
    elif re.search(r"wayback", text, re.IGNORECASE) and not snapshot_dates:
        parts.append("built via a Wayback Machine archive, but no machine-extractable snapshot date found in track's own text")
    elif re.search(r"cross[- ]verified|cross[- ]checked", text, re.IGNORECASE) and not parts:
        parts.append("cross-verified against multiple sources per track's own verification note")

    if not parts:
        parts.append("no explicit capture-date/reachability signal found in track's own recorded files; see verification_tier and source_authority above")

    return "; ".join(parts)


def build_entry(track: dict, tier_entry: dict | None) -> dict:
    track_id = track["track_id"]
    data_paths = track.get("data_paths", [])
    official_source_path = resolve_official_source_path(track_id, data_paths)
    source_obj = load_json_safe(official_source_path)

    # Text corpus for URL/authority extraction and context-building: the registry's own
    # source_authority/source_url/notes fields, PLUS the resolved official_source file's own
    # scalar/near-top fields (excluding the bulky `articles` array, which is irrelevant to
    # source-authority extraction and would slow this down for no benefit).
    text_chunks = [
        str(track.get("source_authority") or ""),
        str(track.get("source_url") or ""),
        str(track.get("notes") or ""),
    ]
    if source_obj:
        shallow = {k: v for k, v in source_obj.items() if k != "articles"}
        text_chunks.append(json.dumps(shallow, ensure_ascii=False))
    joined_text = "\n".join(text_chunks)

    source_urls = extract_urls(joined_text)
    named_authorities = extract_named_authorities(joined_text)
    staleness_risk, staleness_pointer = detect_staleness_risk(source_obj)
    last_verified_context = build_last_verified_context(joined_text, source_obj, staleness_risk)

    return {
        "track_id": track_id,
        "display_name_en": track.get("display_name_en"),
        "display_name_ar": track.get("display_name_ar"),
        "verification_tier": tier_entry.get("tier") if tier_entry else None,
        "verification_tier_rationale": tier_entry.get("tier_rationale") if tier_entry else None,
        "registry_source_authority": track.get("source_authority") or None,
        "registry_source_url": track.get("source_url") or None,
        "official_source_file": official_source_path,
        "source_urls": source_urls,
        "named_source_authorities": named_authorities,
        "last_verified_context": last_verified_context,
        "known_source_staleness_risk": staleness_risk,
        "known_source_staleness_pointer": staleness_pointer,
    }


def main() -> int:
    if not os.path.isfile(REGISTRY_PATH):
        print(f"ERROR: registry not found at {REGISTRY_PATH}", file=sys.stderr)
        return 1
    if not os.path.isfile(TIERS_PATH):
        print(f"ERROR: verification tiers file not found at {TIERS_PATH}", file=sys.stderr)
        return 1

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    with open(TIERS_PATH, "r", encoding="utf-8") as f:
        tiers = json.load(f)

    tiers_by_id = {t["track_id"]: t for t in tiers.get("tracks", [])}
    tracks_by_id = {t["track_id"]: t for t in registry.get("tracks", [])}

    entries = []
    for track_id in REQUIRED_TRACK_IDS:
        track = tracks_by_id.get(track_id)
        if track is None:
            raise SystemExit(
                f"gen_corpus_freshness_manifest: track '{track_id}' from REQUIRED_TRACK_IDS "
                f"not found in corpus_registry.json."
            )
        entries.append(build_entry(track, tiers_by_id.get(track_id)))

    entries.sort(key=lambda e: e["track_id"])

    staleness_flagged = [e["track_id"] for e in entries if e["known_source_staleness_risk"]]
    no_official_source_file = [e["track_id"] for e in entries if e["official_source_file"] is None]

    out = {
        "schema_version": "1.0",
        "generated_by": "scripts/gen_corpus_freshness_manifest.py",
        "generated_date": registry.get("generated_date"),
        "source_registry": "data/corpus_registry/corpus_registry.json",
        "source_registry_generated_date": registry.get("generated_date"),
        "source_verification_tiers": "data/corpus_verification_tiers/corpus_verification_tiers.json",
        "read_only_derived_layer": True,
        "network_access": False,
        "notes": (
            "Purely additive, read-only survey layer over this corpus's 178 tracks, built "
            "entirely from files already committed to this repository (the corpus registry, "
            "the verification-tiers layer, and each track's own official_source.json-"
            "equivalent file). Makes NO network calls and NEVER calls datetime.now() — every "
            "date-like value here (fetch_date, Wayback snapshot dates, etc.) is extracted "
            "verbatim from a track's own already-committed files, which keeps this generator "
            "deterministic and idempotent. Does not modify the registry, the verification-"
            "tiers file, or any of the 178 tracks' own files. For a LIVE (network-dependent, "
            "non-deterministic, NOT part of the QA gate) reachability/drift check against the "
            "URLs recorded here, run scripts/check_corpus_freshness.py standalone."
        ),
        "known_source_staleness_risk_methodology": (
            "known_source_staleness_risk=true only where a track's OWN "
            "known_unresolved_discrepancies entry documents that the PRIMARY government "
            "portal's displayed/consolidated text was confirmed stale/outdated at build time "
            "(e.g. an amendment the portal has not incorporated, or a portal body that "
            "contradicts its own amendment-history annotation) — not merely 'unreachable this "
            "pass' (a reachability caveat, not a confirmed-content problem), and not a stale "
            "INSTITUTIONAL/MINISTRY NAME permanently baked into old statute wording (a "
            "different, non-monitorable concern; re-checking the portal will not resolve it)."
        ),
        "total_tracks": len(entries),
        "known_source_staleness_risk_count": len(staleness_flagged),
        "known_source_staleness_risk_tracks": staleness_flagged,
        "tracks_without_resolvable_official_source_file": no_official_source_file,
        "tracks": entries,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {OUT_PATH}")
    print(f"Total tracks: {len(entries)}")
    print(f"known_source_staleness_risk=true: {len(staleness_flagged)} -> {staleness_flagged}")
    if no_official_source_file:
        print(f"Tracks with no resolvable official_source file (registry-only fields used): "
              f"{no_official_source_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
