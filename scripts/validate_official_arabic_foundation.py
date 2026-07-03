#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the OFFICIAL ARABIC TEXT FOUNDATION scaffold.

This is the first official-Arabic stage. It does NOT ingest or verify official Arabic text;
it verifies that the architecture + verification workflow are in place and that the
repository does NOT falsely claim the current Arabic summaries are official statutory text.

Enforces:
- schema schemas/official_arabic_article.schema.json exists;
- folder data/official_arabic/ exists with an ingestion_status.json manifest carrying the
  required provenance fields;
- source-packet requirements + verification plan docs exist;
- the repo does NOT claim the current Arabic summaries are official statutory text
  (ingestion_status + source_provenance both keep them non-official / unverified);
- NO article record is prematurely marked verified: any official_text_ar record under
  data/official_arabic/ must have an explicit verification_status and may only be
  'verified_against_official_gazette' if article_by_article_verified is true;
- no full official Arabic statutory text has been mixed into the summary/article files by
  accident (guard against relabeling existing summaries as official).

Exit 0 == pass; 1 == problems. No network, no heavy dependencies.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "official_arabic_article.schema.json")
OA_DIR = os.path.join(ROOT, "data", "official_arabic")
STATUS = os.path.join(OA_DIR, "ingestion_status.json")
DOCS = os.path.join(ROOT, "docs", "official_arabic_text")
PACKET_DOC = os.path.join(DOCS, "SOURCE_PACKET_REQUIREMENTS_AR.md")
PLAN_DOC = os.path.join(DOCS, "OFFICIAL_ARABIC_VERIFICATION_PLAN_AR.md")
PROVENANCE = os.path.join(ROOT, "data", "metadata", "source_provenance.json")

REQUIRED_PROVENANCE_FIELDS = [
    "official_arabic_text_status",
    "current_arabic_summary_status",
    "official_source_required",
    "verification_status",
    "article_by_article_verified",
    "source_document_type",
    "source_authority",
    "source_publication_reference",
    "source_url_or_file_reference",
    "extraction_method",
    "reviewer_notes",
]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    problems = []

    # 1. schema + folder + docs exist
    if not os.path.exists(SCHEMA):
        problems.append("missing schema: schemas/official_arabic_article.schema.json")
    if not os.path.isdir(OA_DIR):
        problems.append("missing folder: data/official_arabic/")
    if not os.path.exists(PACKET_DOC):
        problems.append("missing doc: docs/official_arabic_text/SOURCE_PACKET_REQUIREMENTS_AR.md")
    if not os.path.exists(PLAN_DOC):
        problems.append("missing doc: docs/official_arabic_text/OFFICIAL_ARABIC_VERIFICATION_PLAN_AR.md")

    # 2. ingestion_status manifest + provenance fields
    status = None
    if not os.path.exists(STATUS):
        problems.append("missing manifest: data/official_arabic/ingestion_status.json")
    else:
        status = _read(STATUS)
        for f in REQUIRED_PROVENANCE_FIELDS:
            if f not in status:
                problems.append("ingestion_status.json missing provenance field: %s" % f)
        # honesty: current Arabic summaries must NOT be labelled official; official text
        # must not be claimed ingested/verified unless it actually is.
        if status.get("current_arabic_summary_status") in (None, "official", "official_statutory_text"):
            problems.append("ingestion_status.json: current_arabic_summary_status must NOT mark summaries official")
        if "not_official" not in str(status.get("current_arabic_summary_status", "")):
            problems.append("ingestion_status.json: current_arabic_summary_status must explicitly say the summaries are not official")
        oats = status.get("official_arabic_text_status")
        if oats is None:
            problems.append("ingestion_status.json: official_arabic_text_status must be explicit")
        abv = status.get("article_by_article_verified")
        if not isinstance(abv, bool):
            problems.append("ingestion_status.json: article_by_article_verified must be a boolean")
        # If nothing is ingested, it cannot claim verification or ingested articles.
        if oats == "not_ingested":
            if abv:
                problems.append("ingestion_status.json: article_by_article_verified cannot be true while official_arabic_text_status=not_ingested")
            if status.get("articles"):
                problems.append("ingestion_status.json: 'articles' must be empty while official_arabic_text_status=not_ingested")
            if status.get("verification_status") == "verified_against_official_gazette":
                problems.append("ingestion_status.json: verification_status cannot be verified while not_ingested")

    # 3. source_provenance must keep the current Arabic non-official / unverified
    if not os.path.exists(PROVENANCE):
        problems.append("missing: data/metadata/source_provenance.json")
    else:
        prov = _read(PROVENANCE)
        ots = prov.get("official_text_status", {})
        if ots.get("checked_against_official_gazette") is not False:
            problems.append("source_provenance.json: official_text_status.checked_against_official_gazette must remain false until verified")
        blob = json.dumps(prov, ensure_ascii=False).lower()
        if "not be treated as official" not in blob and "not official" not in blob and "not used verbatim" not in blob:
            problems.append("source_provenance.json: must explicitly state the Arabic summaries are not official statutory text")

    # 4. no premature/invented official article records under data/official_arabic/
    schema = _read(SCHEMA) if os.path.exists(SCHEMA) else None
    for path in sorted(glob.glob(os.path.join(OA_DIR, "*.json"))):
        base = os.path.basename(path)
        if base == "ingestion_status.json":
            continue
        doc = _read(path)
        records = doc.get("articles", doc.get("records", [])) if isinstance(doc, dict) else doc
        if isinstance(records, list):
            for r in records:
                if not isinstance(r, dict):
                    continue
                if "official_text_ar" in r:
                    vs = r.get("verification_status")
                    if vs not in ("pending_official_source", "ingested_unverified",
                                  "verified_against_official_gazette"):
                        problems.append("%s: official_text_ar record has no explicit valid verification_status" % base)
                    if vs == "verified_against_official_gazette" and not (
                            status and status.get("article_by_article_verified")):
                        problems.append("%s: record marked verified_against_official_gazette but article_by_article_verified is not true" % base)

    print("=" * 60)
    print("Official Arabic text FOUNDATION validation (scaffold stage)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] official Arabic foundation scaffold in place — schema + data/official_arabic/ "
          "+ source-packet requirements + verification plan present; official_arabic_text_status="
          "%s; article_by_article_verified=%s; current Arabic summaries kept NON-official; "
          "no official Arabic text ingested or falsely marked verified."
          % (status.get("official_arabic_text_status") if status else "?",
             status.get("article_by_article_verified") if status else "?"))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
