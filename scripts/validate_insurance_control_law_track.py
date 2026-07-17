#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Cooperative Insurance Companies Control Law
track (25 records, consolidated amended law: 17 اصلية / 8 معدلة, flat
structure with no chapters).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/insurance_control/law/official_source/
insurance_control_law_official_source.json's verification_methodology_note
for the full caveat. laws.boe.gov.sa and the Wayback Machine were both
unreachable this research pass. This track instead rests on misa.gov.sa's
official bilingual PDF cross-verified against nezams.com. IMPORTANT: this
validator does NOT require original_XXXXh_text on amended articles (unlike
most other consolidated-amended-law tracks) — the research pass explicitly
did not recover/transcribe pre-amendment original text for any of the 8
amended articles this pass, a documented gap rather than a fabricated
field."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "insurance_control", "law", "official_source",
                   "insurance_control_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "insurance_control", "law", "verified",
                       "insurance_control_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "insurance_control_arabic_legal_llm",
                   "insurance_control_law_legal_llm_001_025.json")
N = 25
KEY_RE = r"insurance_control_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 17, "معدلة": 8}
STATUS = "MISA_OFFICIAL_PDF_X_NEZAMS_CROSS_VERIFIED_BOE_UNREACHABLE"
AMENDED_KEYS = {"insurance_control_art_%03d" % n for n in (2, 3, 6, 18, 19, 20, 21, 22)}
FLAGGED_DISCREPANCY_KEYS = {"insurance_control_institutional_name_divergence",
                            "insurance_control_art_021", "insurance_control_art_022",
                            "insurance_control_original_text_not_retained",
                            "insurance_control_nezams_art21_22_render_bug",
                            "insurance_control_mof_stale_reproduction",
                            "insurance_control_administering_authority_transfer"}
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
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)
    for k in AMENDED_KEYS:
        if k not in arts:
            e.append("[1] expected amended article key %s missing" % k)

    if src.get("chapter_structure"):
        e.append("[1c] expected empty chapter_structure for this flat-structure law")

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
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
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
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
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Insurance Control Law track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Cooperative Insurance Companies Control Law — 25 records (17 اصلية / 8 معدلة)")
    print("  - DISTINCT TIER: misa.gov.sa official bilingual PDF x nezams.com cross-verified,")
    print("    laws.boe.gov.sa and the Wayback Machine both unreachable this research pass")
    print("  - numbered 1..25, flat structure, no chapters")
    print("  - IN-FORCE Royal Decree M/32 (2/6/1424H); amended by M/30 (1434H) and M/12 (1443H)")
    print("  - pre-amendment original text NOT included for any of the 8 amended articles this")
    print("    pass, a documented gap not a fabrication; institutional-name divergence flagged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
