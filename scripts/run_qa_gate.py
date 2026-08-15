#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strict repository QA gate — one command, everything must pass.

Three phases, all mandatory:

  [1] VALIDATORS — runs EVERY ``scripts/validate_*.py`` in the repository.
      Coverage is strict by construction: validators are discovered from the
      filesystem, so a newly added validator automatically joins the gate.
      A validator may only be skipped by listing it in ``EXCLUDED`` with a
      written reason; anything else that fails, fails the gate.

  [2] IDEMPOTENCE — re-runs EVERY ``scripts/gen_*.py`` and then requires the git
      working tree to be byte-identical to before (tracked files). This catches
      "generator edited but outputs not regenerated" and any non-deterministic
      generator drift. Like phase 1, coverage is strict by construction: the
      generators are discovered from the filesystem, and one may be skipped only
      by appearing in ``EXCLUDED_GENERATORS`` with a written reason. The order in
      which the corpus-wide derived layers run cannot be discovered, so it is
      declared in ``DERIVED_LAYER_ORDER`` — and a layer missing from it fails the
      phase rather than running wherever the alphabet puts it.

  [3] TESTS — the full pytest suite (skippable with --no-tests when the caller
      already runs pytest separately, e.g. as its own CI step).

Exit 0 only if every phase passes. Output is a per-step PASS/FAIL table plus a
final verdict line. Read-only over corpus data except for the regeneration in
phase 2, which must produce zero diffs to pass.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import glob
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Validators intentionally excluded from the gate. Empty today — keep it that
# way unless a validator genuinely cannot run headless; every entry MUST carry
# a reason string.
EXCLUDED: dict[str, str] = {}

# Phase 2 discovers its generators the way phase 1 discovers its validators.
#
# It did not always. Until now the list below was written by hand, and a hand-
# written list of a growing thing is a promise that quietly stops being kept: it
# named 392 of the 814 generators on disk. The gate printed "IDEMPOTENCE — 392
# deterministic generators ... clean (zero drift)" and a reader took that for
# coverage. It was 48%.
#
# What the uncovered half was hiding, measured by running all 423 of them: every
# one exits 0 and none touches the network, so nothing about them justified the
# exclusion — and 21 produced output that differed from what is committed. Ten
# tracks were MISSING a currency warning their own generator emits, one carried a
# warning its own rule no longer supports, and nine carried a superseded wording
# of it. Two of the eleven corpus-wide derived layers — the caveat layer and the
# amendment timeline — were outside the phase entirely.
#
# So the list is gone. Everything matching scripts/gen_*.py runs, and a generator
# may be skipped only by appearing in EXCLUDED_GENERATORS with a written reason.
EXCLUDED_GENERATORS: dict[str, str] = {
    "scripts/gen_corpus_export_primary_arabic.py":
        "stamps its own generation date into the export manifest, so it is "
        "non-idempotent BY DESIGN. The export is a versioned cut, re-made "
        "deliberately, not on every gate run.",
}

# The corpus-wide derived layers read what the track generators write, so they run
# LAST, and among themselves in dependency order: the unified index before the
# registry that embeds a snapshot of it, both before the layers that join to them.
#
# This is the one list phase 2 still keeps by hand, because an ORDER cannot be
# discovered. So it is checked instead: every scripts/gen_corpus_*.py on disk must
# appear here or in EXCLUDED_GENERATORS, and the phase FAILS if one does not. A new
# derived layer therefore cannot join the corpus without someone deciding where in
# the order it belongs — which is exactly the decision that was silently skipped
# twice before.
DERIVED_LAYER_ORDER = [
    "scripts/gen_corpus_unified_llm_index.py",
    "scripts/gen_corpus_registry.py",
    "scripts/gen_corpus_verification_tiers.py",
    "scripts/gen_corpus_supersession_graph.py",
    "scripts/gen_corpus_cross_reference_graph.py",
    "scripts/gen_corpus_glossary.py",
    "scripts/gen_corpus_chunking_layer.py",
    "scripts/gen_corpus_freshness_manifest.py",
    "scripts/gen_corpus_caveat_layer.py",
    "scripts/gen_corpus_amendment_timeline.py",
    "scripts/gen_corpus_schema_manifest.py",
]

# Deterministic non-generator producers, run after the layers they read.
TAIL_GENERATORS = [
    "scripts/run_corpus_retrieval_eval.py",
]


def discover_generators():
    """(ordered generators, corpus layers missing from DERIVED_LAYER_ORDER)."""
    found = sorted(os.path.relpath(p, ROOT).replace(os.sep, "/")
                   for p in glob.glob(os.path.join(ROOT, "scripts", "gen_*.py")))
    unplaced = [g for g in found
                if g.startswith("scripts/gen_corpus_")
                and g not in DERIVED_LAYER_ORDER and g not in EXCLUDED_GENERATORS]
    tracks = [g for g in found
              if not g.startswith("scripts/gen_corpus_") and g not in EXCLUDED_GENERATORS]
    layers = [g for g in DERIVED_LAYER_ORDER if g not in EXCLUDED_GENERATORS]
    return tracks + layers + TAIL_GENERATORS, unplaced

# Raised from 900s on 2026-08-01. The retrieval-eval pass is O(queries x index
# records) and the corpus has grown to 437 tracks / 20,162 indexed records /
# 811 gold queries, so a single scoring pass now takes ~17 minutes and its
# validator runs one twice (committed-vs-fresh reproduction). At 900s the gate
# reported a TIMEOUT that looked like a validator failure but was purely the
# clock; the same validator passes standalone.
VALIDATOR_TIMEOUT = 3600
WORKERS = 4


def _run(cmd, timeout):
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        return r.returncode, time.time() - t0, (r.stdout + r.stderr)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", time.time() - t0, ""


def _tracked_state():
    r = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                       text=True, cwd=ROOT)
    return r.stdout


def phase_validators():
    scripts = sorted(os.path.relpath(p, ROOT).replace(os.sep, "/")
                     for p in glob.glob(os.path.join(ROOT, "scripts", "validate_*.py")))
    to_run = [s for s in scripts if s not in EXCLUDED]
    print("[1] VALIDATORS — %d discovered, %d excluded (%s)"
          % (len(scripts), len(EXCLUDED), "none" if not EXCLUDED else "; ".join(
              "%s: %s" % kv for kv in EXCLUDED.items())))
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(_run, [sys.executable, s], VALIDATOR_TIMEOUT): s for s in to_run}
        for fut in concurrent.futures.as_completed(futs):
            s = futs[fut]
            code, dt, out = fut.result()
            if code != 0:
                failures.append((s, code, out))
    for s, code, out in sorted(failures):
        print("    FAIL (%s) %s" % (code, s))
        tail = [ln for ln in out.strip().split("\n") if ln.strip()][-5:]
        for ln in tail:
            print("      | %s" % ln)
    print("    -> %d/%d passed" % (len(to_run) - len(failures), len(to_run)))
    return not failures


def phase_idempotence():
    generators, unplaced = discover_generators()
    print("[2] IDEMPOTENCE — %d generators discovered, %d excluded (%s)"
          % (len(generators), len(EXCLUDED_GENERATORS),
             "none" if not EXCLUDED_GENERATORS else "; ".join(
                 "%s: %s" % (os.path.basename(k), v.split(".")[0])
                 for k, v in EXCLUDED_GENERATORS.items())))
    before = _tracked_state()
    failures = []
    if unplaced:
        failures.append(
            "corpus-wide layer(s) with no position in DERIVED_LAYER_ORDER: %s — a derived "
            "layer must be placed in the regeneration order deliberately, not by "
            "alphabetical accident" % unplaced)
    for g in generators:
        code, dt, out = _run([sys.executable, g], VALIDATOR_TIMEOUT)
        if code != 0:
            failures.append("%s exited %s" % (g, code))
    after = _tracked_state()
    if after != before:
        changed = sorted(set(after.split("\n")) ^ set(before.split("\n")))
        failures.append("working tree changed after regeneration: %s"
                        % [c.strip() for c in changed if c.strip()][:8])
    for f in failures:
        print("    FAIL %s" % f)
    print("    -> %s" % ("clean (zero drift)" if not failures else "%d failure(s)" % len(failures)))
    return not failures


def phase_tests():
    print("[3] TESTS — full pytest suite")
    code, dt, out = _run([sys.executable, "-m", "pytest", "-q"], 1800)
    tail = [ln for ln in out.strip().split("\n") if ln.strip()][-1:]
    print("    -> %s (exit %s, %.0fs)" % (tail[0] if tail else "?", code, dt))
    return code == 0


def main():
    ap = argparse.ArgumentParser(description="Strict repository QA gate.")
    ap.add_argument("--no-tests", action="store_true",
                    help="skip phase 3 (pytest) when the caller runs it separately")
    args = ap.parse_args()

    print("=" * 64)
    print("STRICT QA GATE — saudi-legal-corpus-ai")
    print("=" * 64)
    t0 = time.time()
    ok1 = phase_validators()
    ok2 = phase_idempotence()
    ok3 = True if args.no_tests else phase_tests()
    print("=" * 64)
    verdict = ok1 and ok2 and ok3
    tests_label = "SKIPPED" if args.no_tests else ("PASS" if ok3 else "FAIL")
    print("QA GATE: %s  (validators=%s, idempotence=%s, tests=%s, %.0fs)"
          % ("PASS" if verdict else "FAIL",
             "PASS" if ok1 else "FAIL",
             "PASS" if ok2 else "FAIL",
             tests_label,
             time.time() - t0))
    print("=" * 64)
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
