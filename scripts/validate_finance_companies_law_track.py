#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Finance Companies Control Law track (41
records, consolidated amended law: 28 اصلية / 12 معدلة / 1 مضافة; فصل
تمهيدي + 8 فصول, no أبواب).

VERIFICATION TIER -- see the generator's module docstring and
sources/finance_companies/law/official_source/
finance_companies_law_official_source.json's verification_methodology_note
for the full caveat: laws.boe.gov.sa's LIVE portal was unreachable this
pass (HTTP 503), but a Wayback Machine archive of the exact law page WAS
reachable and is treated as the primary source, cross-verified against
bfc.gov.sa's official PDF (OCR'd) and nezams.com. IMPORTANT: this
validator does NOT require original_text on the article amended only by
M/21 in a way whose full pre-amendment content is irrecoverable -- see
known_unresolved_discrepancies (Article 5 DOES carry an
original_1440h_text field reflecting its state immediately before the
2024 amendment, itself already a post-M/21 state; the true 1433H content
of the bend M/21 deleted is not recoverable from any source and is not
fabricated)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "finance_companies", "law", "official_source",
                   "finance_companies_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "finance_companies", "law", "verified",
                       "finance_companies_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "finance_companies_arabic_legal_llm",
                   "finance_companies_law_legal_llm_001_041.json")
N = 41
KEY_RE = r"finance_companies_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 28, "معدلة": 12, "مضافة": 1}
STATUS = "BOE_WAYBACK_ARCHIVE_X_BFC_GOV_PDF_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_503"
EXPECTED_CHAPTERS = 9  # فصل تمهيدي + 8 فصول
AMENDED_KEYS = {"finance_companies_art_%03d" % n for n in
                (1, 5, 11, 12, 16, 17, 18, 19, 20, 21, 29, 35)}
MUKARRAR_KEYS = {"finance_companies_art_036_mukarrar"}
FLAGGED_DISCREPANCY_KEYS = {
    "finance_companies_art_005_original_khamisan_bend_unrecoverable",
    "finance_companies_art_005_1440h_amendment_arithmetic_unresolved",
    "finance_companies_art_035_amending_instrument_dual_citation",
    "finance_companies_boe_art035_numeral_corruption_not_adopted",
    "finance_companies_institutional_name_divergence",
    "finance_companies_implementing_regulation_not_ingested_this_pass",
}
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
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)
    for k in AMENDED_KEYS | MUKARRAR_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    n_ch = len(src.get("chapter_structure") or [])
    if n_ch != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d فصل divisions, got %d" % (EXPECTED_CHAPTERS, n_ch))

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
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a فصل path)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in MUKARRAR_KEYS):
            e.append("[2] %s: legal_status_ar/MUKARRAR_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar flag mismatch" % k)
        original = a.get("original_1433h_text") or a.get("original_1440h_text")
        if original and original == a["text"]:
            e.append("[2] %s: original text identical to current text (no-op amendment?)" % k)
        # residual bidi paren-before-digit / doubled-tanwin artifacts
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")

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
        expected_original = a.get("original_1433h_text") or a.get("original_1440h_text")
        if r.get("original_text") != expected_original:
            e.append("[4] %s: original_text not propagated" % r["article_key"])
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
        print("FAIL: %d error(s) in Finance Companies Control Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Finance Companies Control Law — 41 records (28 اصلية / 12 معدلة / 1 مضافة)")
    print("  - فصل تمهيدي + 8 فصول (تعريفات؛ أحكام عامة؛ أحكام الترخيص؛ نشاط شركات التمويل؛")
    print("    إدارة شركات التمويل؛ الإشراف [عُدّل عنوانه من 'الإشراف على شركات التمويل']؛")
    print("    المخالفات والمنازعات؛ العقوبات؛ أحكام ختامية)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine archive (primary, live BOE HTTP 503)")
    print("    x bfc.gov.sa official OCR'd PDF x nezams.com HTML transcription (zero substantive")
    print("    discrepancies across all 40 original articles); 2024 amendment text from")
    print("    qanoonsa.com's verbatim decree reproduction x nezams.com footnotes")
    print("  - IN-FORCE Royal Decree M/51 (13/8/1433H); amended by M/21 (1440H, Art. 5 only),")
    print("    M/24 (1443H, Art. 35 only), M/272 (1445H/2024, Arts. 1,5,11,12,16-21,29 + new Art.")
    print("    36 مكرر)")
    print("  - pre-1440H original content of Article 5's deleted بند (خامساً) NOT recoverable")
    print("    from any source this pass, a documented gap not a fabrication; companion")
    print("    Implementing Regulation identified but NOT ingested this pass (38 scanned pages,")
    print("    independent multi-wave amendment history -- candidate for follow-up)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
