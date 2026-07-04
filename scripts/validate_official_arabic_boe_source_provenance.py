#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the official Arabic BOE source-provenance/status correction (provenance only).

Confirms the repository posture now documents the owner-provided Bureau of Experts Arabic text +
scanned PDF packet as the controlling official source packet, with OCR artifacts as supporting
evidence only — while nothing was verified, promoted, or text-changed. Source-provenance
confidence is separated from article-by-article automated verification (which is NOT performed).

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT = os.path.join(ROOT, "reports", "official_arabic_verification")
CORRECTION = os.path.join(RPT, "boe_official_source_provenance_correction.json")
PROV_DOC = os.path.join(ROOT, "docs", "official_arabic_text",
                        "BOE_OFFICIAL_SOURCE_PROVENANCE_AR.md")
INGEST = os.path.join(ROOT, "data", "official_arabic", "ingestion_status.json")
PROVENANCE = os.path.join(ROOT, "data", "metadata", "source_provenance.json")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")
QUEUE = os.path.join(RPT, "manual_review_queue.json")

TARGET = 281
AUTHORITY_AR = "هيئة الخبراء بمجلس الوزراء"
AUTHORITY_EN = "Bureau of Experts"


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _agg_hash(cand):
    blob = "".join(a["official_text_ar"] for a in cand["articles"])
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main() -> int:
    problems = []

    for p, label in ((CORRECTION, "boe_official_source_provenance_correction.json"),
                     (PROV_DOC, "BOE_OFFICIAL_SOURCE_PROVENANCE_AR.md")):
        if not os.path.exists(p):
            problems.append("missing: %s" % label)

    corr = _read(CORRECTION) if os.path.exists(CORRECTION) else None
    if corr is not None:
        # required posture on the correction record
        want = {
            "source_authority": "Bureau of Experts at the Council of Ministers",
            "source_authority_ar": AUTHORITY_AR,
            "text_source_status": "owner_provided_from_official_boe_source",
            "pdf_source_status": "owner_provided_from_official_boe_source",
            "controlling_source_packet": "owner_provided_boe_text_plus_pdf_packet",
            "ocr_role": "supporting_artifact_only_not_controlling_gate",
            "direct_automated_capture_status": "blocked_or_unsuitable",
            "article_count": TARGET,
            "candidate_text_changed": False,
            "no_legal_text_changed": True,
            "no_article_promoted_by_ocr": True,
        }
        for k, v in want.items():
            if corr.get(k) != v:
                problems.append("correction.%s must be %r (got %r)" % (k, v, corr.get(k)))
        if corr.get("verified_by_ocr", False) is not False:
            problems.append("correction.verified_by_ocr must be false")
        if corr.get("verified_against_official_gazette", False) is not False:
            problems.append("correction.verified_against_official_gazette must be false")
        blob = json.dumps(corr, ensure_ascii=False)
        if AUTHORITY_AR not in blob or AUTHORITY_EN not in blob:
            problems.append("correction must name the Bureau of Experts authority (AR + EN)")

    # provenance document mentions the authority + separation of axes
    if os.path.exists(PROV_DOC):
        doc = open(PROV_DOC, encoding="utf-8").read()
        for needle in (AUTHORITY_AR, AUTHORITY_EN, "supporting", "281"):
            if needle not in doc:
                problems.append("provenance doc missing expected content: %r" % needle)

    # ingestion_status: BOE block present + correct; ingestion/verification axis unchanged
    st = _read(INGEST) if os.path.exists(INGEST) else None
    if st is None:
        problems.append("ingestion_status.json missing")
    else:
        boe = st.get("boe_source_provenance")
        if not isinstance(boe, dict):
            problems.append("ingestion_status.json missing boe_source_provenance block")
        else:
            checks = {
                "source_authority_ar": AUTHORITY_AR,
                "text_source_status": "owner_provided_from_official_boe_source",
                "pdf_source_status": "owner_provided_from_official_boe_source",
                "controlling_source_packet": "owner_provided_boe_text_plus_pdf_packet",
                "ocr_role": "supporting_artifact_only_not_controlling_gate",
                "direct_automated_capture_status": "blocked_or_unsuitable",
                "article_count": TARGET,
                "candidate_text_changed": False,
                "no_legal_text_changed": True,
                "no_article_promoted_by_ocr": True,
                "verified_by_ocr": False,
                "article_by_article_verified": False,
                "articles_verified": 0,
            }
            for k, v in checks.items():
                if boe.get(k) != v:
                    problems.append("ingestion_status.boe_source_provenance.%s must be %r (got %r)"
                                    % (k, v, boe.get(k)))
            if AUTHORITY_EN not in json.dumps(boe, ensure_ascii=False):
                problems.append("boe_source_provenance must name the Bureau of Experts (EN)")
            if boe.get("manual_review_queue_is_controlling_gate", True) is not False:
                problems.append("boe_source_provenance: manual_review_queue must NOT be the "
                                "controlling source-confidence gate")
        # authority wording corrected (no generic 'user_provided_text_claimed_official' anymore)
        if "user_provided_text_claimed_official" in str(st.get("source_authority", "")):
            problems.append("ingestion_status.json source_authority still uses generic-unverified "
                            "wording; must state owner-provided official BOE source")
        if AUTHORITY_EN not in str(st.get("source_authority", "")):
            problems.append("ingestion_status.json source_authority must name Bureau of Experts")
        # retained ingestion/verification-axis enum fields (accurate; must remain)
        if st.get("official_arabic_text_status") != "user_provided_source_ingested":
            problems.append("ingestion_status.official_arabic_text_status axis field changed")
        if st.get("verification_status") != "ingested_unverified":
            problems.append("ingestion_status.verification_status axis field changed")
        if st.get("article_by_article_verified") is not False:
            problems.append("ingestion_status.article_by_article_verified must remain false")
        if st.get("articles_verified") != 0:
            problems.append("ingestion_status.articles_verified must remain 0")
        if st.get("articles_ingested") != TARGET:
            problems.append("ingestion_status.articles_ingested must remain 281")

    # source_provenance metadata: BOE block present under official_arabic_foundation
    prov = _read(PROVENANCE) if os.path.exists(PROVENANCE) else None
    if prov is None:
        problems.append("source_provenance.json missing")
    else:
        oaf = prov.get("official_arabic_foundation", {})
        pboe = oaf.get("boe_source_provenance")
        if not isinstance(pboe, dict):
            problems.append("source_provenance.official_arabic_foundation missing "
                            "boe_source_provenance block")
        else:
            if pboe.get("source_authority_ar") != AUTHORITY_AR:
                problems.append("source_provenance boe_source_provenance.source_authority_ar wrong")
            if pboe.get("ocr_role") != "supporting_artifact_only_not_controlling_gate":
                problems.append("source_provenance boe_source_provenance.ocr_role must be "
                                "supporting only")
            if pboe.get("article_by_article_verified") is not False:
                problems.append("source_provenance boe: article_by_article_verified must be false")
        # provenance must keep source non-official-summaries + not-yet-gazette-checked posture
        if prov.get("official_text_status", {}).get("checked_against_official_gazette") is not False:
            problems.append("source_provenance: checked_against_official_gazette must remain false")

    # candidate untouched: 281, ingested_unverified, nothing verified, official_text_ar unchanged
    if os.path.exists(CAND):
        c = _read(CAND)
        if len(c.get("articles", [])) != TARGET:
            problems.append("candidate must still have 281 records")
        if c.get("verification_status") != "ingested_unverified":
            problems.append("candidate verification_status must remain ingested_unverified")
        if c.get("article_by_article_verified") is not False:
            problems.append("candidate article_by_article_verified must remain false")
        if c.get("articles_verified", 0) not in (0, None):
            problems.append("candidate articles_verified must remain 0")
        for a in c.get("articles", []):
            if a.get("verification_status") in ("verified_against_official_gazette",
                                                "verified_by_ocr"):
                problems.append("candidate art %s marked verified" % a.get("article_number"))
        # official_text_ar unchanged (aggregate hash matches the recorded snapshot)
        if corr is not None:
            recorded = corr.get("candidate_integrity", {}).get(
                "aggregate_official_text_ar_sha256")
            actual = _agg_hash(c)
            if recorded != actual:
                problems.append("candidate official_text_ar changed: aggregate hash %s != "
                                "recorded %s" % (actual, recorded))
    else:
        problems.append("candidate file missing")

    # manual_review_queue still present (but not the controlling gate)
    if not os.path.exists(QUEUE):
        problems.append("manual_review_queue.json must remain present")
    else:
        q = _read(QUEUE)
        if len(q.get("entries", [])) != TARGET:
            problems.append("manual_review_queue must still have 281 entries")

    # protected derived layers unchanged in shape
    en = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    if len(en) != 8 or sum(len(_read(x)["records"]) for x in en) != 87:
        problems.append("English Legal LLM must remain 8 files / 87 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("Chinese Legal LLM must remain 5 files / 23 records")
    for x in glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json")):
        b = open(x, encoding="utf-8").read().lower()
        if "official_text_ar" in b or "verified_against_official_gazette" in b:
            problems.append("Arabic Legal LLM must not be relabeled official: %s"
                            % os.path.basename(x))
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58)))):
        pth = os.path.join(ref, fname)
        if os.path.exists(pth) and [x["article_number"] for x in _read(pth)["records"]] != exp:
            problems.append("official English reference changed: %s" % fname)
    for fname in ("book1_articles_001_034.json", "book2_articles_035_050.json",
                  "book3_articles_051_057.json"):
        if not os.path.exists(os.path.join(ROOT, "data", "articles", fname)):
            problems.append("existing data/articles file missing: %s" % fname)
    if not os.path.exists(os.path.join(ROOT, "schemas", "official_arabic_article.schema.json")):
        problems.append("existing schema missing: official_arabic_article.schema.json")

    print("=" * 60)
    print("Official Arabic BOE source-provenance/status correction validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] BOE owner-provided text + PDF packet documented as controlling source packet; "
          "OCR = supporting artifact only (not the gate); source_authority = Bureau of Experts / "
          "هيئة الخبراء بمجلس الوزراء; article_count=281; candidate official_text_ar unchanged "
          "(aggregate hash matches); article_by_article_verified=false; articles_verified=0; "
          "nothing verified/promoted by OCR; derived layers unchanged.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
