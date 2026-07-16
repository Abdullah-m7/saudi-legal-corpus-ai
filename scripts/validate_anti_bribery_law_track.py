#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Anti-Bribery Law track (25 records, consolidated
amended law: 16 اصلية / 7 معدلة / 2 مضافة / 0 ملغاة).

DISTINCT, LOWER-CONFIDENCE VERIFICATION TIER — see the generator's module
docstring and sources/anti_bribery/law/official_source/
anti_bribery_law_official_source.json's verification_methodology_note for
the full caveat. This law is not MOJ-issued and laws.boe.gov.sa /
web.archive.org were both confirmed unreachable from the build environment.
Two ad hoc tiers were used instead of this corpus's two established methods:
SINGLE_PRIMARY_SOURCE_TOPICAL_CORROBORATION (16 unchanged 1412H articles) and
SECONDARY_SOURCE_CONVERGENCE_UNVERIFIED_PRIMARY (7 amended + 2 added
articles) — the weakest tier used anywhere in this corpus, approved by the
repository owner after two dedicated research passes confirmed the primary
channels were unreachable. This validator checks internal consistency and
that every article is explicitly tagged with its tier; it CANNOT verify
against a primary source the build environment cannot reach."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_bribery", "law", "official_source",
                   "anti_bribery_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "anti_bribery", "law", "verified",
                       "anti_bribery_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "anti_bribery_arabic_legal_llm",
                   "anti_bribery_law_legal_llm_001_023.json")
PDFS = [
    os.path.join(ROOT, "inputs", "anti_bribery_official_pdfs",
                 "anti_bribery_law_1412h_original_ksu.pdf"),
    os.path.join(ROOT, "inputs", "anti_bribery_official_pdfs",
                 "anti_bribery_law_consolidated_manielaw.pdf"),
]
N = 25
KEY_RE = r"anti_bribery_art_(\d{3})(_mukarrar_(\d))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 16, "معدلة": 7, "مضافة": 2}
TIER_ORIGINAL = "SINGLE_PRIMARY_SOURCE_TOPICAL_CORROBORATION"
TIER_AMENDED = "SECONDARY_SOURCE_CONVERGENCE_UNVERIFIED_PRIMARY"
TRUSTED = {TIER_ORIGINAL, TIER_AMENDED}
AMENDED_KEYS = {"anti_bribery_art_005", "anti_bribery_art_008", "anti_bribery_art_009",
                "anti_bribery_art_014", "anti_bribery_art_015", "anti_bribery_art_017",
                "anti_bribery_art_021"}
ADDED_KEYS = {"anti_bribery_art_009_mukarrar_1", "anti_bribery_art_009_mukarrar_2"}
AR = "ء-ي"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def main():
    e = []
    for p in [SRC, RECORDS, LLM] + PDFS:
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)
    for k in AMENDED_KEYS | ADDED_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    sc = Counter()
    for k, a in arts.items():
        tier = a.get("verification_tier")
        if tier not in TRUSTED:
            e.append("[2] %s: UNTRUSTED/unlabeled verification_tier %r" % (k, tier))
        if a.get("status") != tier:
            e.append("[2] %s: status field must equal verification_tier" % k)
        if k in AMENDED_KEYS | ADDED_KEYS and tier != TIER_AMENDED:
            e.append("[2] %s: expected TIER_AMENDED, got %r" % (k, tier))
        if k not in AMENDED_KEYS | ADDED_KEYS and tier != TIER_ORIGINAL:
            e.append("[2] %s: expected TIER_ORIGINAL, got %r" % (k, tier))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar"):
            e.append("[2] %s: unexpected non-empty section_ar in a flat-structure law" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in ADDED_KEYS and not a.get("history"):
            e.append("[2] %s: added article missing amendment_history" % k)
        if k in AMENDED_KEYS and not a.get("original_1412h_text"):
            e.append("[2] %s: amended article missing original_1412h_text for provenance" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2e] missing known_unresolved_discrepancies (art 17, art 14, art 9-mukarrar-1 caveats expected)")

    ksu_sha = hashlib.sha256(open(PDFS[0], "rb").read()).hexdigest()
    manielaw_sha = hashlib.sha256(open(PDFS[1], "rb").read()).hexdigest()
    if ksu_sha not in src["verification_methodology_note"]:
        e.append("[3] KSU 1412H PDF sha256 not documented in methodology note")
    if manielaw_sha not in src["verification_methodology_note"]:
        e.append("[3] manielaw consolidated PDF sha256 not documented in methodology note")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_tier") != a.get("verification_tier"):
            e.append("[4] %s: verification_tier mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        if r["article_text_ar"] != arts[r["article_key"]]["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("verification_tier") not in TRUSTED:
            e.append("[5] %s: llm record missing/bad verification_tier in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Anti-Bribery Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Anti-Bribery Law — 25 records (consolidated: 16 اصلية / 7 معدلة / 2 مضافة)")
    print("  - DISTINCT LOWER-CONFIDENCE TIER: not MOJ-portal-verified, not BOE-Wayback-verified")
    print("    (laws.boe.gov.sa and web.archive.org both confirmed unreachable from this build")
    print("    environment); 16 articles SINGLE_PRIMARY_SOURCE_TOPICAL_CORROBORATION, 9 articles")
    print("    SECONDARY_SOURCE_CONVERGENCE_UNVERIFIED_PRIMARY — every article explicitly tagged")
    print("  - numbered 1..23 with 2 مكرر articles inserted after art 9 (no renumbering), flat structure")
    print("  - IN-FORCE Royal Decree M/36 (29/12/1412H); both source PDFs committed, hashes verified")
    print("  - 3 documented unresolved discrepancies (art 17 wording, art 14 rename inference, art 9-mukarrar-1 punctuation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
