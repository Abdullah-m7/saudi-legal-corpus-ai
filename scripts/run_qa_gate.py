#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strict repository QA gate — one command, everything must pass.

Three phases, all mandatory:

  [1] VALIDATORS — runs EVERY ``scripts/validate_*.py`` in the repository.
      Coverage is strict by construction: validators are discovered from the
      filesystem, so a newly added validator automatically joins the gate.
      A validator may only be skipped by listing it in ``EXCLUDED`` with a
      written reason; anything else that fails, fails the gate.

  [2] IDEMPOTENCE — re-runs the registered deterministic generators and then
      requires the git working tree to be byte-identical to before (tracked
      files). This catches "generator edited but outputs not regenerated" and
      any non-deterministic generator drift.

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

# Deterministic generators re-run in phase 2. Each must be idempotent: running
# it on a clean tree must produce zero tracked-file changes.
IDEMPOTENT_GENERATORS = [
    "scripts/gen_pdpl_arabic_law_verified.py",
    "scripts/gen_pdpl_arabic_law_legal_llm.py",
    "scripts/gen_pdpl_implementing_regulation_arabic_cleaned.py",
    "scripts/gen_pdpl_implementing_regulation_arabic_verified.py",
    "scripts/gen_pdpl_implementing_regulation_arabic_legal_llm.py",
    "scripts/gen_investment_law_verified.py",
    "scripts/gen_investment_law_legal_llm.py",
    "scripts/gen_investment_regulation_verified.py",
    "scripts/gen_investment_regulation_legal_llm.py",
    "scripts/gen_civil_transactions_law_verified.py",
    "scripts/gen_civil_transactions_law_legal_llm.py",
    "scripts/gen_gtpl_law_track.py",
    "scripts/gen_gtpl_regulation_track.py",
    "scripts/gen_labor_law_track.py",
    "scripts/gen_labor_regulation_track.py",
    "scripts/gen_labor_annex1_track.py",
    "scripts/gen_labor_annex34_tracks.py",
    "scripts/gen_labor_annex2_track.py",
    "scripts/gen_labor_annex5_track.py",
    "scripts/gen_evidence_law_track.py",
    "scripts/gen_evidence_companions_tracks.py",
    "scripts/gen_personal_status_tracks.py",
    "scripts/gen_sharia_procedure_law_track.py",
    "scripts/gen_sharia_procedure_regulation_track.py",
    "scripts/gen_criminal_procedure_law_track.py",
    "scripts/gen_criminal_procedure_regulation_track.py",
    "scripts/gen_enforcement_law_track.py",
    "scripts/gen_enforcement_regulation_track.py",
    "scripts/gen_judiciary_law_track.py",
    "scripts/gen_board_of_grievances_law_track.py",
    "scripts/gen_law_practice_law_track.py",
    "scripts/gen_law_practice_regulation_track.py",
    "scripts/gen_commercial_courts_law_track.py",
    "scripts/gen_commercial_courts_regulation_track.py",
    "scripts/gen_bankruptcy_law_track.py",
    "scripts/gen_bankruptcy_regulation_track.py",
    "scripts/gen_bankruptcy_case_rules_track.py",
    "scripts/gen_judicial_costs_law_track.py",
    "scripts/gen_judicial_costs_regulation_track.py",
    "scripts/gen_arbitration_law_track.py",
    "scripts/gen_arbitration_regulation_track.py",
    "scripts/gen_commercial_papers_law_track.py",
    "scripts/gen_commercial_register_law_track.py",
    "scripts/gen_trade_names_law_track.py",
    "scripts/gen_commercial_agencies_law_track.py",
    "scripts/gen_chambers_of_commerce_law_track.py",
    "scripts/gen_commercial_books_law_track.py",
    "scripts/gen_aml_law_track.py",
    "scripts/gen_tawtheeq_law_track.py",
    "scripts/gen_tawtheeq_regulation_track.py",
    "scripts/gen_real_estate_registration_law_track.py",
    "scripts/gen_real_estate_registration_regulation_track.py",
    "scripts/gen_real_estate_mortgage_law_track.py",
    "scripts/gen_real_estate_finance_law_track.py",
    "scripts/gen_real_estate_units_law_track.py",
    "scripts/gen_real_estate_units_regulation_track.py",
    "scripts/gen_foreign_ownership_law_track.py",
    "scripts/gen_municipal_realestate_law_track.py",
    "scripts/gen_municipal_realestate_regulation_track.py",
    "scripts/gen_gcc_ownership_law_track.py",
    "scripts/gen_terrorism_law_track.py",
    "scripts/gen_terrorism_regulation_track.py",
    "scripts/gen_juveniles_law_track.py",
    "scripts/gen_juveniles_regulation_track.py",
    "scripts/gen_whistleblower_law_track.py",
    "scripts/gen_judicial_inspection_regulation_track.py",
    "scripts/gen_qismah_regulation_track.py",
    "scripts/gen_sulook_regulation_track.py",
    "scripts/gen_aawan_regulation_track.py",
    "scripts/gen_muslaha_regulation_track.py",
    "scripts/gen_iflas_hudud_regulation_track.py",
    "scripts/gen_judicial_documents_regulation_track.py",
    "scripts/gen_bankruptcy_fees_regulation_track.py",
    "scripts/gen_enforcement_providers_regulation_track.py",
    "scripts/gen_alimony_fund_regulation_track.py",
    "scripts/gen_judiciary_bog_mechanism_track.py",
    "scripts/gen_documentation_settlement_regulation_track.py",
    "scripts/gen_mosalaha_center_regulation_track.py",
    "scripts/gen_corpus_unified_llm_index.py",
    "scripts/gen_corpus_registry.py",
    "scripts/run_corpus_retrieval_eval.py",
]

VALIDATOR_TIMEOUT = 300
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
    print("[2] IDEMPOTENCE — %d deterministic generators" % len(IDEMPOTENT_GENERATORS))
    before = _tracked_state()
    failures = []
    for g in IDEMPOTENT_GENERATORS:
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
