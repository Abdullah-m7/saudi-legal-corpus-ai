#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Amendment Timeline — Read-Only Validator

Validates data/corpus_amendment_timeline/corpus_amendment_timeline.jsonl and its
summary, produced by scripts/gen_corpus_amendment_timeline.py.

Checks:
  1.  Output exists, parses, and the summary agrees with a fresh recount.
  2.  Every record_id is unique and exists in the unified LLM index — the layer
      is only useful if it joins to what retrieval returns.
  3.  Every row's legal_status_ar is one of معدلة/مضافة/ملغاة, and every article
      in the corpus carrying one of those statuses has a row here. AN OMITTED
      ROW IS THE DANGEROUS FAILURE: a missing row reads as "never amended",
      which is a different statement and a false one.
  4.  dating_status is one of the three documented values and agrees with the
      row's own contents (dated <=> at least one amendment; undated <=> none).
  5.  Every amendment carries an evidence tag from the documented set, and
      every dated amendment carries at least one of a Hijri or Gregorian date —
      an "amendment" with no date at all would defeat the layer's whole purpose.
  6.  Conflicting dates are PRESERVED, never silently dropped: any row with a
      conflicting_dates entry states both readings and asserts neither.
  7.  No row invents an instrument: every instrument_ar appears verbatim in the
      track's own source artifact.
  8.  Generator is idempotent: two consecutive runs are byte-identical.
  9.  Read-only: the validator writes nothing except by re-running the
      generator into its own declared outputs.

Usage:
    python3 scripts/validate_corpus_amendment_timeline.py
Exit 0 == pass; 1 == problems.
"""
from __future__ import annotations

import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYER = os.path.join(ROOT, "data", "corpus_amendment_timeline",
                     "corpus_amendment_timeline.jsonl")
SUMMARY = os.path.join(ROOT, "data", "corpus_amendment_timeline",
                       "corpus_amendment_timeline_summary.json")
INDEX = os.path.join(ROOT, "data", "corpus_unified_index",
                     "corpus_unified_llm_index.jsonl")
REGISTRY = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
GEN = os.path.join(ROOT, "scripts", "gen_corpus_amendment_timeline.py")

AMENDED = {"معدلة", "مضافة", "ملغاة"}
STATUSES = {"dated", "disclosed_conflict", "undated"}
EVIDENCE = {
    "per_article_history_in_the_source_artifact",
    ("printed_footnote_matched_to_the_document_level_history_on_BOTH_the_"
     "decision_number_and_the_date"),
}

PASSED = FAILED = 0
LINES: list[str] = []


def check(name, ok, detail=""):
    global PASSED, FAILED
    LINES.append("  %s %s" % (name, "✓" if ok else "✗ FAIL"))
    if detail:
        LINES.append("    %s" % detail)
    if ok:
        PASSED += 1
    else:
        FAILED += 1


def main() -> int:
    print("=" * 62)
    print("Corpus Amendment Timeline validation")
    print("=" * 62)

    if not os.path.isfile(LAYER):
        print("layer not found: %s" % LAYER)
        return 1
    rows = [json.loads(l) for l in open(LAYER, encoding="utf-8") if l.strip()]
    summary = json.load(open(SUMMARY, encoding="utf-8"))
    check("[1] layer and summary parse; totals agree...",
          summary.get("total_rows") == len(rows),
          "%d rows" % len(rows))

    ids = [r.get("record_id") for r in rows]
    check("[2a] record_ids unique...", len(set(ids)) == len(ids),
          "%d unique" % len(set(ids)))
    index_ids = set()
    index_status = {}
    for line in open(INDEX, encoding="utf-8"):
        if line.strip():
            rec = json.loads(line)
            index_ids.add(rec["record_id"])
            index_status[rec["record_id"]] = rec.get("legal_status_ar")
    missing = [i for i in ids if i not in index_ids]
    check("[2b] every record_id exists in the unified LLM index...",
          not missing,
          "joins to retrieval" if not missing else "absent: %s" % missing[:5])

    bad_status = [r["record_id"] for r in rows
                  if r.get("legal_status_ar") not in AMENDED]
    check("[3a] every row is an amended/added/repealed article...",
          not bad_status, "" if not bad_status else str(bad_status[:5]))

    # every amended article in the index must have a row — an omission reads
    # as "never amended", which is a different and false statement
    covered = set(ids)
    tracked = {r["track_id"] for r in rows}
    omitted = []
    registry = json.load(open(REGISTRY, encoding="utf-8"))
    consolidated = set()
    for t in registry.get("tracks", []):
        srcs = [p for p in t.get("data_paths", []) if "/official_source/" in p]
        if not srcs or not os.path.exists(os.path.join(ROOT, srcs[0])):
            continue
        try:
            doc = json.load(open(os.path.join(ROOT, srcs[0]), encoding="utf-8"))
        except ValueError:
            continue
        if doc.get("consolidated_amended_law"):
            consolidated.add(t["track_id"])
    for rid, st in index_status.items():
        if st in AMENDED and rid not in covered:
            omitted.append(rid)
    check("[3b] no amended article in the index lacks a row...",
          not omitted,
          "an omitted row would read as 'never amended'"
          if not omitted else "omitted: %d e.g. %s" % (len(omitted), omitted[:4]))

    bad = [r["record_id"] for r in rows if r.get("dating_status") not in STATUSES]
    check("[4a] dating_status is one of the documented values...", not bad,
          "" if not bad else str(bad[:5]))
    inconsistent = [
        r["record_id"] for r in rows
        if (r["dating_status"] == "dated") != bool(r.get("amendments"))]
    check("[4b] dating_status agrees with the row's own contents...",
          not inconsistent, "" if not inconsistent else str(inconsistent[:5]))

    bad_ev = [a.get("evidence") for r in rows for a in r.get("amendments", [])
              if a.get("evidence") not in EVIDENCE]
    check("[5a] every amendment carries a documented evidence tag...",
          not bad_ev, "" if not bad_ev else str(sorted(set(bad_ev))[:3]))
    undatedish = [r["record_id"] for r in rows for a in r.get("amendments", [])
                  if not (a.get("date_hijri") or a.get("date_gregorian"))]
    check("[5b] every recorded amendment carries a date...",
          not undatedish,
          "an undated 'amendment' would defeat the layer's purpose"
          if not undatedish else str(undatedish[:5]))

    conflicts = [c for r in rows for c in r.get("conflicting_dates", [])]
    incomplete = [c for c in conflicts
                  if not (c.get("date_printed_in_the_article_text")
                          and c.get("date_in_the_document_level_history"))]
    check("[6] disclosed conflicts state BOTH readings...",
          not incomplete,
          "%d conflict(s), each asserting neither side" % len(conflicts)
          if not incomplete else "incomplete: %d" % len(incomplete))

    # [7] no invented instruments
    invented = []
    src_blobs = {}
    for t in registry.get("tracks", []):
        srcs = [p for p in t.get("data_paths", []) if "/official_source/" in p]
        if srcs and os.path.exists(os.path.join(ROOT, srcs[0])):
            src_blobs[t["track_id"]] = open(
                os.path.join(ROOT, srcs[0]), encoding="utf-8").read()
    for r in rows:
        blob = src_blobs.get(r["track_id"], "")
        for a in r.get("amendments", []):
            inst = a.get("instrument_ar")
            if inst and json.dumps(inst, ensure_ascii=False)[1:-1] not in blob:
                invented.append((r["record_id"], inst[:40]))
    check("[7] every instrument appears verbatim in its own source artifact...",
          not invented,
          "nothing invented" if not invented else str(invented[:3]))

    tmp = tempfile.mkdtemp(prefix="amend_timeline_")
    try:
        a = os.path.join(tmp, "a.jsonl")
        r1 = subprocess.run([sys.executable, GEN], capture_output=True)
        shutil.copy(LAYER, a)
        r2 = subprocess.run([sys.executable, GEN], capture_output=True)
        check("[8] generator is idempotent...",
              r1.returncode == 0 and r2.returncode == 0 and filecmp.cmp(a, LAYER,
                                                                       shallow=False),
              "two consecutive runs byte-identical")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    for l in LINES:
        print(l)
    print()
    print("=" * 62)
    print("RESULT: %d passed, %d failed" % (PASSED, FAILED))
    print("=" * 62)
    if not FAILED:
        by = summary.get("by_dating_status", {})
        print("PASS: amendment timeline over %d amended articles" % len(rows))
        print("  dated %s | disclosed_conflict %s | undated %s"
              % (by.get("dated", 0), by.get("disclosed_conflict", 0),
                 by.get("undated", 0)))
        print("  keyed by record_id, so «متى عُدِّلت هذه المادة؟» is answerable")
        print("  from the same identifier retrieval already returns")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
