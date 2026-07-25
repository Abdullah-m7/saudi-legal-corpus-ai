#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the "Regulation on Transfer of Personal Data
Outside the Kingdom" track (لائحة نقل البيانات الشخصية إلى خارج المملكة),
SDAIA President Decision No. (1840), 27/2/1446H (Umm al-Qura Gazette
28/2/1446H / 1 Sept 2024), issued pursuant to Article (29) of the PDPL.

FULL SCOPE = all 9 articles (no chapter subdivisions). See the generator's
docstring and the source artifact's verification_methodology_note for the
full verification-tier writeup: TIER_1_PRIMARY_MULTI_SOURCE -- Umm al-Qura
Official Gazette (uqn.gov.sa) text independently corroborated word-for-word
by SDAIA's own live regulatory portal (dgp.sdaia.gov.sa); laws.boe.gov.sa
unreachable this pass. This validator checks internal self-consistency of the
9 articles and that every disclosed discrepancy (including the unconfirmed
2023-predecessor decree number and the inferred, not directly-read,
supersession) is recorded; it does NOT re-adjudicate provenance.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "pdpl_cross_border_transfer_regulation", "law",
                    "official_source", "pdpl_cross_border_transfer_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "pdpl_cross_border_transfer_regulation", "law",
                        "verified", "pdpl_cross_border_transfer_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "pdpl_cross_border_transfer_regulation", "law",
                        "verified", "pdpl_cross_border_transfer_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "pdpl_cross_border_transfer_regulation_arabic_legal_llm",
                    "pdpl_cross_border_transfer_regulation_legal_llm_001_009.json")
N = 9
KEY_RE = r"pdpl_cross_border_transfer_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 9, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
ALLOWED_VERIFICATION_STATUS = {"SDAIA_DGP_PORTAL_X_UMM_AL_QURA_GAZETTE_DUAL_PRIMARY_SOURCE_CORROBORATED"}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "pdpl_cross_border_transfer_regulation_v1_decree_number_unconfirmed",
    "pdpl_cross_border_transfer_regulation_supersession_inferred_not_explicit",
    "pdpl_cross_border_transfer_regulation_boe_unreachable",
    "pdpl_cross_border_transfer_regulation_sdaia_docs_pdf_waf_blocked",
    "pdpl_cross_border_transfer_regulation_mixed_digit_convention",
    "pdpl_cross_border_transfer_regulation_no_amendment_check_2024_2026",
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
    for p in (SRC, RECORDS, SUMMARY, LLM):
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

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") not in ALLOWED_VERIFICATION_STATUS:
            e.append("[2] %s: unexpected verification status %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("article_title_ar"):
            e.append("[2] %s: missing article_title_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in (AMENDED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "‌" in a["text"] or "‍" in a["text"]:
            e.append("[2f] %s: residual zero-width-joiner/non-joiner artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[ً-ْ]", a["text"]):
            e.append("[2f] %s: residual tashkeel (should be stripped) detected" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record the founding decree 1840)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "1840" not in decrees:
            e.append("[2k] amendment_history must reference founding decree 1840")

    sup = src.get("supersedes_predecessor_v1")
    if not sup:
        e.append("[2s] missing supersedes_predecessor_v1 block (2023 predecessor disclosure)")
    else:
        if sup.get("article_count") != 10 or sup.get("chapter_count") != 4:
            e.append("[2s] supersedes_predecessor_v1 must record 10 articles / 4 chapters")
        if sup.get("explicit_repeal_clause_found") is not False:
            e.append("[2s] explicit_repeal_clause_found must be False (honestly disclosed as "
                     "not directly confirmed, not asserted true)")
        if "UNCONFIRMED" not in str(sup.get("decree_number_and_date", "")):
            e.append("[2s] supersedes_predecessor_v1 must flag its own decree number as unconfirmed")

    basis = src.get("pdpl_delegation_basis")
    if not basis or basis.get("article_key") != "pdpl_law_art_029":
        e.append("[2p] pdpl_delegation_basis must reference pdpl_law_art_029")

    # spot-checks anchoring key facts established this pass
    a1 = arts.get("pdpl_cross_border_transfer_regulation_art_001", {})
    if "الضمانات المناسبة" not in a1.get("text", "") or "م/١٩" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الضمانات المناسبة / م/١٩)")
    a2 = arts.get("pdpl_cross_border_transfer_regulation_art_002", {})
    if "الفقرة الفرعية (د)" not in a2.get("text", "") or "التاسعة والعشرين" not in a2.get("text", ""):
        e.append("[2j] Article 2 missing expected PDPL Art 29(1)(d) cross-reference")
    a5 = arts.get("pdpl_cross_border_transfer_regulation_art_005", {})
    if "اللائحة التنفيذية للنظام" not in a5.get("text", ""):
        e.append("[2j] Article 5 missing expected cross-reference to the PDPL Implementing Regulation")
    a9 = arts.get("pdpl_cross_border_transfer_regulation_art_009", {})
    if "النفاذ" not in a9.get("article_title_ar", ""):
        e.append("[2j] Article 9 must be titled النفاذ (entry into force)")
    if src.get("decree") != "قرار رئيس الهيئة السعودية للبيانات والذكاء الاصطناعي رقم (1840)" \
            or src.get("decree_date_hijri") != "27/2/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Decision 1840, 27/2/1446H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (this is the founding text of v2.0)")
    if "2.0" not in str(src.get("version_label", "")):
        e.append("[2j] version_label must record Version 2.0")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if not summary.get("supersedes_predecessor_v1"):
        e.append("[4b] summary must carry supersedes_predecessor_v1 disclosure")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("english_used_for_correction") is not False:
            e.append("[5] %s: english_used_for_correction must be False" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in PDPL Cross-Border Transfer Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Regulation on Transfer of Personal Data Outside the Kingdom")
    print("  - FULL SCOPE: 9 records (Articles 1-9), all اصلية, no chapter subdivisions")
    print("  - SDAIA President Decision No. (1840), 27/2/1446H; Umm al-Qura Gazette 28/2/1446H")
    print("    (1 Sept 2024); issued pursuant to PDPL Article 29 (1)(d), (2)(b)(c), (4)")
    print("  - VERIFICATION TIER: TIER_1_PRIMARY_MULTI_SOURCE -- Umm al-Qura Gazette (uqn.gov.sa)")
    print("    x SDAIA's own live portal (dgp.sdaia.gov.sa), word-for-word agreement, no")
    print("    reachability gap; structurally cross-checked vs SDAIA's own English PDF")
    print("    ('Version 2.0, August 2024'); laws.boe.gov.sa unreachable this pass")
    print("  - A 2023 predecessor (10 articles/4 chapters) was found; supersession is a strong")
    print("    INFERENCE, not a directly-read repeal clause; its own decree number could NOT")
    print("    be independently confirmed this pass -- both honestly disclosed, not asserted")
    print("  - Distinct from pdpl_law and pdpl_implementing_regulation (already in this corpus);")
    print("    Article 5 cross-references PDPL Implementing Regulation Article 17 directly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
