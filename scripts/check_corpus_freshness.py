#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Freshness — Live, Read-Only Drift-Checking CLI Tool

A STANDALONE, human-run operational tool that lets someone periodically re-check whether a
track's recorded SOURCE has drifted since it was last captured, WITHOUT needing another full
research/build pass. It reads data/corpus_freshness_manifest/corpus_freshness_manifest.json
(built by scripts/gen_corpus_freshness_manifest.py) for the URL(s)/authorities on record for a
track, then makes a LIVE network request to see whether that URL is currently reachable and,
if so, whether its content looks different from what this corpus has on record.

*** NOT PART OF THE DETERMINISTIC QA GATE ***
    Unlike scripts/gen_corpus_freshness_manifest.py and scripts/validate_corpus_freshness_manifest.py
    (which are pure, deterministic, network-free, and safe to run in run_qa_gate.py), THIS
    script makes real network requests. Its output depends on live external state (whether a
    government portal happens to be up right now, this sandbox's own egress policy, transient
    timeouts, etc.) and is therefore NON-DETERMINISTIC by design. It is intentionally NOT wired
    into run_qa_gate.py or any other automated gate — it is an operational tool for a human to
    run periodically (e.g. every few months), not a CI check.

*** THIS TOOL IS STRICTLY READ-ONLY ***
    It NEVER writes to, modifies, or "auto-corrects" any track's data, the freshness manifest,
    or any other file in this repository. It only PRINTS a report to stdout. If a URL looks like
    it may have drifted, the tool says "POSSIBLE DRIFT — recommend re-verification" and stops
    there; a human (and a fresh, full research pass) decides what to do next, never this script.

*** NETWORK FAILURE HANDLING ***
    A failed connection, timeout, DNS error, or non-2xx/3xx status is reported as
    "COULD NOT CHECK" (inconclusive), NEVER as "confirmed unreachable" or "confirmed gone" —
    this sandbox's own egress policy may block some domains (e.g. laws.boe.gov.sa,
    web.archive.org have both been observed to time out from this environment), and a network
    failure here says nothing about whether the real-world URL is actually down.

*** NO EGRESS-POLICY-BYPASS WORKAROUNDS, EVER ***
    This corpus has a firm, already-documented rule (see e.g.
    sources/zakat/law/official_source/zakat_law_official_source.json's own provenance notes)
    against bypassing this sandbox's network egress policy — no trailing-dot hostname tricks,
    no alternate proxy chains, no DNS-over-HTTPS workarounds, nothing. This tool makes exactly
    one plain HTTPS request per URL (HEAD, falling back to a small ranged GET if HEAD is
    rejected), through whatever proxy/environment this shell already has configured, and
    reports whatever happens. If a domain is blocked, this tool says so plainly and stops; it
    does not try to route around the block.

WHAT "POSSIBLE DRIFT" MEANS HERE
    Some tracks' own official_source.json records a `sha256` for an archived snapshot of a
    government portal page (see e.g. commercial_agencies_law's `archive_snapshots[].sha256`).
    Where such a recorded hash exists for the URL being checked, this tool fetches the live
    URL, hashes the response body, and compares. A mismatch is reported as
    "POSSIBLE DRIFT — recommend re-verification" (the live content differs from what was
    recorded — could mean the source changed, or could mean the live page differs from the
    archived snapshot for an unrelated reason, e.g. dynamic content). Where NO baseline hash is
    on record for a URL (the common case — most tracks only ever captured the government
    portal's TEXT, not a raw content hash of the fetch itself), this tool cannot determine
    drift and says so explicitly; it just reports the freshly observed status/length/hash for
    the human's own future reference.

Usage:
    python3 scripts/check_corpus_freshness.py --track patent_law
    python3 scripts/check_corpus_freshness.py --track traffic_law --timeout 10
    python3 scripts/check_corpus_freshness.py --all
    python3 scripts/check_corpus_freshness.py --all --only-flagged   # just the tracks already
                                                                       # flagged known_source_staleness_risk
Exit code is always 0 (this is a reporting tool, not a pass/fail gate) unless invoked with bad
arguments or the manifest file is missing/unreadable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT, "data", "corpus_freshness_manifest", "corpus_freshness_manifest.json")

DEFAULT_TIMEOUT_SECONDS = 8
USER_AGENT = "saudi-legal-corpus-ai-freshness-checker/1.0 (read-only drift check; +local repo tool)"


def load_manifest() -> dict:
    if not os.path.isfile(MANIFEST_PATH):
        print(f"ERROR: freshness manifest not found at {MANIFEST_PATH}.", file=sys.stderr)
        print("Run: python3 scripts/gen_corpus_freshness_manifest.py", file=sys.stderr)
        sys.exit(1)
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def find_recorded_hash_for_url(official_source_file: str | None, url: str) -> str | None:
    """Best-effort, read-only lookup of a baseline sha256 hash this corpus already recorded
    for the given URL at build time (e.g. commercial_agencies_law's own
    archive_snapshots[].sha256, keyed by that same archive_snapshots[].url). Returns None if
    no such baseline exists — which is the common case. Never writes anything."""
    if not official_source_file:
        return None
    full = os.path.join(ROOT, official_source_file)
    if not os.path.isfile(full):
        return None
    try:
        with open(full, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    found = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get("url") == url and isinstance(o.get("sha256"), str):
                found["hash"] = o["sha256"]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)

    walk(obj)
    return found.get("hash")


def check_url(url: str, timeout: int) -> dict:
    """Make exactly one plain HTTPS request (HEAD, falling back to GET on HEAD rejection).
    Never retries aggressively, never routes around a block. Returns a result dict describing
    what happened — reachable/blocked/error are all reported plainly, never conflated."""
    result = {
        "url": url,
        "attempted": True,
        "reachable": False,
        "http_status": None,
        "content_length_header": None,
        "fetched_bytes": None,
        "body_sha256": None,
        "method_used": None,
        "error": None,
    }

    req_head = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req_head, timeout=timeout) as resp:
            result["reachable"] = True
            result["http_status"] = resp.status
            result["content_length_header"] = resp.headers.get("Content-Length")
            result["method_used"] = "HEAD"
            return result
    except urllib.error.HTTPError as e:
        if e.code in (405, 501):
            pass  # HEAD not supported by this server; fall through to a GET below.
        else:
            result["reachable"] = True  # server responded, just with an error status
            result["http_status"] = e.code
            result["method_used"] = "HEAD"
            result["error"] = f"HTTP {e.code}"
            return result
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
        result["error"] = f"{type(e).__name__}: {e}"
        result["method_used"] = "HEAD"
        return result

    # Fallback: a single small GET (HEAD was rejected by the server, not the network).
    req_get = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req_get, timeout=timeout) as resp:
            body = resp.read(2_000_000)  # cap at 2MB; this is a freshness check, not a mirror
            result["reachable"] = True
            result["http_status"] = resp.status
            result["content_length_header"] = resp.headers.get("Content-Length")
            result["fetched_bytes"] = len(body)
            result["body_sha256"] = hashlib.sha256(body).hexdigest()
            result["method_used"] = "GET"
    except urllib.error.HTTPError as e:
        result["reachable"] = True
        result["http_status"] = e.code
        result["method_used"] = "GET"
        result["error"] = f"HTTP {e.code}"
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
        result["error"] = f"{type(e).__name__}: {e}"
        result["method_used"] = "GET"

    return result


def report_for_track(entry: dict, timeout: int) -> None:
    track_id = entry["track_id"]
    print("=" * 72)
    print(f"Track: {track_id}  ({entry.get('display_name_en')})")
    print(f"Verification tier: {entry.get('verification_tier')}")
    if entry.get("known_source_staleness_risk"):
        print(f"KNOWN SOURCE STALENESS RISK: {entry.get('known_source_staleness_pointer')}")
    print(f"Named source authorities on record: {entry.get('named_source_authorities') or '(none extracted)'}")

    urls = entry.get("source_urls") or []
    if not urls:
        print("No plain https:// URL is recorded for this track's primary source — only named")
        print("authorities (see above). Nothing to live-fetch; recommend a manual portal check.")
        print()
        return

    for url in urls:
        print(f"\n  Checking: {url}")
        result = check_url(url, timeout)
        if result["error"] and not result["reachable"]:
            print(f"    COULD NOT CHECK — {result['error']}")
            print("    This may be a real outage, a transient network issue, or this sandbox's")
            print("    own egress policy blocking the domain. NOT treated as 'confirmed")
            print("    unreachable' — no bypass workaround was attempted (this corpus's own")
            print("    documented policy forbids that; see this script's docstring).")
            continue

        status = result["http_status"]
        ok = isinstance(status, int) and 200 <= status < 400
        print(f"    Reachable: HTTP {status} via {result['method_used']}"
              + (" (OK)" if ok else " (non-success status)"))
        if result.get("content_length_header"):
            print(f"    Content-Length header: {result['content_length_header']}")

        if result["method_used"] == "GET" and result.get("body_sha256"):
            print(f"    Fetched body: {result['fetched_bytes']} bytes, sha256={result['body_sha256']}")
            baseline = find_recorded_hash_for_url(entry.get("official_source_file"), url)
            if baseline:
                if baseline == result["body_sha256"]:
                    print(f"    Matches recorded baseline sha256 ({baseline[:16]}...) — no drift detected.")
                else:
                    print(f"    ** POSSIBLE DRIFT — recommend re-verification ** "
                          f"(recorded baseline sha256={baseline[:16]}... differs from live "
                          f"fetch sha256={result['body_sha256'][:16]}...)")
            else:
                print("    No baseline hash is on record for this exact URL in this track's own")
                print("    files, so drift cannot be automatically determined. The hash/length")
                print("    above is shown for your own manual future comparison only.")
        elif result["method_used"] == "HEAD":
            print("    (HEAD request only — no body fetched, so no content hash to compare;")
            print("     re-run would need a GET to compute one.)")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Live, read-only freshness/drift check against a track's recorded source URL(s). "
                    "NOT part of the deterministic QA gate (network-dependent). See this script's own "
                    "module docstring for the full read-only / no-bypass guarantees."
    )
    parser.add_argument("--track", help="Single track_id to check (e.g. patent_law).")
    parser.add_argument("--all", action="store_true", help="Check every track in the manifest.")
    parser.add_argument("--only-flagged", action="store_true",
                        help="With --all, restrict to tracks already flagged known_source_staleness_risk=true.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS,
                        help=f"Per-request timeout in seconds (default {DEFAULT_TIMEOUT_SECONDS}).")
    args = parser.parse_args()

    if not args.track and not args.all:
        parser.print_help()
        return 2

    manifest = load_manifest()
    by_id = {t["track_id"]: t for t in manifest.get("tracks", [])}

    if args.track:
        if args.track not in by_id:
            print(f"ERROR: track_id '{args.track}' not found in the freshness manifest.", file=sys.stderr)
            print(f"({len(by_id)} tracks available; see data/corpus_registry/corpus_registry.json "
                  f"for the canonical list of track ids.)", file=sys.stderr)
            return 1
        report_for_track(by_id[args.track], args.timeout)
        return 0

    # --all
    entries = list(by_id.values())
    if args.only_flagged:
        entries = [e for e in entries if e.get("known_source_staleness_risk")]
    print(f"Checking {len(entries)} track(s)"
          + (" (known_source_staleness_risk=true only)" if args.only_flagged else "") + "...\n")
    for entry in entries:
        report_for_track(entry, args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
