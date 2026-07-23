#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation for Environmental
Inspection & Audit track (10 records: 8 articles + Table (1) penalty schedule +
Appendix (1) audit-study template; all اصلية relative to the in-force 2024
replacement text).

VERIFICATION TIER -- see the generator's module docstring and
sources/environmental_inspection_audit/official_source/
environmental_inspection_audit_reg_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa was checked
FIRST (standard methodology) but is unreachable this pass (HTTP 503) and has no
dedicated lawId page for this Regulation (only for the base Environmental Law).
The current in-force text was issued by Ministerial Decision (15116190), 12
Jumada al-Ula 1446H (14 Nov 2024, Umm Al-Qura issue 5057), which WHOLLY REPLACED
the original Decision (393691/1/1442), 13/7/1442H. PRIMARY reachable full-text
source: qanoonsa.com, with the citation cross-verified against the replacing
decision's own recital, qistas.com, and the MEWA/SPA announcement. This
validator does not re-adjudicate provenance; it only checks internal self-
consistency of the ingested text and that every disclosed discrepancy is
recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_inspection_audit",
                   "official_source",
                   "environmental_inspection_audit_reg_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "environmental_inspection_audit", "verified",
                       "environmental_inspection_audit_reg_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "environmental_inspection_audit", "verified",
                       "environmental_inspection_audit_reg_verified_summary.json")
LLM = os.path.join(ROOT, "data", "environmental_inspection_audit_arabic_legal_llm",
                   "environmental_inspection_audit_reg_legal_llm_001_010.json")

N_ARTICLES = 8
N_ANNEX = 2
N_TOTAL = 10
ART_RE = r"environmental_inspection_audit_reg_art_(\d{3})$"
ANNEX_KEYS = {"environmental_inspection_audit_reg_jadwal_001",
              "environmental_inspection_audit_reg_mulhaq_001"}
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 8, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
FLAGGED_DISCREPANCY_KEYS = {
    "environmental_inspection_audit_reg_boe_unreachable_no_dedicated_page",
    "environmental_inspection_audit_reg_fulltext_single_reachable_source",
    "environmental_inspection_audit_reg_wholesale_replacement_not_article_diff",
    "environmental_inspection_audit_reg_citation_number_refinement",
    "environmental_inspection_audit_reg_appendix_title_tahqiq_typo",
    "environmental_inspection_audit_reg_penalty_table_column_ambiguity",
    "environmental_inspection_audit_reg_source_rendering_artifact_alshab",
    "environmental_inspection_audit_reg_arabic_indic_digits_preserved",
    "environmental_inspection_audit_reg_gregorian_date_founding_not_pinned",
    "environmental_inspection_audit_reg_definitions_terms_changed_2024",
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

    # [1] structure counts
    art_keys = [k for k in arts if re.match(ART_RE, k)]
    annex_keys = [k for k in arts if k in ANNEX_KEYS]
    if len(art_keys) != N_ARTICLES:
        e.append("[1] %d article records != %d" % (len(art_keys), N_ARTICLES))
    if len(annex_keys) != N_ANNEX:
        e.append("[1] %d annex records != %d" % (len(annex_keys), N_ANNEX))
    if len(arts) != N_TOTAL:
        e.append("[1] %d total records != %d" % (len(arts), N_TOTAL))
    if src.get("article_count") != N_ARTICLES:
        e.append("[1] article_count field != %d" % N_ARTICLES)
    if src.get("annex_count") != N_ANNEX:
        e.append("[1] annex_count field != %d" % N_ANNEX)
    # article numbers 1..8 contiguous
    nums = sorted(int(re.match(ART_RE, k).group(1)) for k in art_keys)
    if nums != list(range(1, N_ARTICLES + 1)):
        e.append("[1] article numbers not contiguous 1..8: %s" % nums)

    sc = Counter()  # article-level legal-status breakdown (annexes tallied separately)
    for k, a in arts.items():
        if a.get("status") != "UNCHANGED":
            e.append("[2] %s: expected status UNCHANGED, got %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        if re.match(ART_RE, k):
            sc[ls] += 1
        if ls != "اصلية":
            e.append("[2] %s: expected اصلية (wholesale-replacement instrument), got %r" % (k, ls))
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        # Latin allowed ONLY for the appendix's 'MSDS' term; flag any other Latin.
        latin = re.findall(r"[A-Za-z]+", a["text"])
        if latin and set(latin) - {"MSDS"}:
            e.append("[2] %s: unexpected latin tokens %r" % (k, sorted(set(latin))))
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("history"):
            e.append("[2i] %s: unchanged record must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact" % k)
        if "الش عب" in a["text"]:
            e.append("[2g] %s: uncorrected 'الش عب' split-word artifact" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    # [2d] provenance / disclosure blocks
    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    if not src.get("preamble_ar") or "يقرر ما يلي" not in src.get("preamble_ar", ""):
        e.append("[2d] preamble_ar missing/incomplete (must include the issuing recital)")
    if not src.get("supersession_finding_ar") or "تحل" not in src.get("supersession_finding_ar", ""):
        e.append("[2d] supersession_finding_ar missing the replace-clause finding")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing: %s" % sorted(missing))

    # [2k] amendment_history must record BOTH the founding and the replacing decisions
    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "393691/1/1442" not in decrees:
            e.append("[2k] amendment_history must reference founding decree 393691/1/1442")
        if "15116190" not in decrees:
            e.append("[2k] amendment_history must reference replacing decree 15116190")

    # [2j] anchor key facts established this pass
    if src.get("decree") != "القرار الوزاري رقم (393691/1/1442)" \
            or src.get("decree_date_hijri") != "13/7/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with founding Decision 393691/1/1442")
    if src.get("current_text_decree") != "قرار وزير البيئة والمياه والزراعة رقم (15116190)":
        e.append("[2j] current_text_decree mismatch with replacing Decision 15116190")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (current text = 2024 replacement)")
    art1 = arts.get("environmental_inspection_audit_reg_art_001", {})
    if "ميثاق السرية" not in art1.get("text", "") or "المركز الوطني للرقابة على الالتزام البيئي" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected 2024-version definitions "
                 "(ميثاق السرية / المركز الوطني للرقابة على الالتزام البيئي)")
    art2 = arts.get("environmental_inspection_audit_reg_art_002", {})
    if "تسري أحكام هذه اللائحة على جميع الأشخاص ضمن إقليم المملكة" not in art2.get("text", ""):
        e.append("[2j] Article 2 (scope) text mismatch")
    art7 = arts.get("environmental_inspection_audit_reg_art_007", {})
    if "المحظورات" not in art7.get("title_ar", "") or "العبث بأجهزة الرصد" not in art7.get("text", ""):
        e.append("[2j] Article 7 (prohibitions) missing expected content")
    jadwal = arts.get("environmental_inspection_audit_reg_jadwal_001", {})
    if "يطبق مبدأ الإنذار" not in jadwal.get("text", "") or "١٠٠,٠٠٠" not in jadwal.get("text", ""):
        e.append("[2j] Table (1) missing expected penalty rows (warning-principle / 100,000)")
    mulhaq = arts.get("environmental_inspection_audit_reg_mulhaq_001", {})
    if "دراسة التحقيق البيئي" not in mulhaq.get("title_ar", ""):
        e.append("[2j] Appendix (1) title must preserve the source's own 'التحقيق' typo verbatim")
    if "MSDS" not in mulhaq.get("text", ""):
        e.append("[2j] Appendix (1) missing expected MSDS reference")

    # [4] verified records
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_TOTAL:
        e.append("[4] %d verified records != %d" % (len(ver), N_TOTAL))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N_TOTAL:
        e.append("[4b] summary record_count != %d" % N_TOTAL)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if not summary.get("preamble_ar"):
        e.append("[4b] summary missing preamble_ar")

    # [5] LLM records
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_TOTAL or len(recs) != N_TOTAL:
        e.append("[5] llm count != %d" % N_TOTAL)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != "UNCHANGED":
            e.append("[5] %s: llm record bad source_status" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Environmental Inspection & Audit Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation for Environmental Inspection and Audit")
    print("  - 10 records: 8 articles + Table (1) penalty schedule + Appendix (1) "
          "audit-study template; all اصلية")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa checked first but unreachable")
    print("    this pass and confirmed to have no dedicated lawId page for this Regulation;")
    print("    PRIMARY reachable full-text source is qanoonsa.com (reproducing Umm Al-Qura")
    print("    issue 5057), citation cross-verified against the replacing decision's own")
    print("    recital, qistas.com, and the MEWA/SPA announcement")
    print("  - CURRENT text: Ministerial Decision (15116190), 12 Jumada al-Ula 1446H")
    print("    (14 Nov 2024), which WHOLLY REPLACED the original Decision (393691/1/1442),")
    print("    13/7/1442H -- a repeal-and-replace supersession, documented as such")
    print("  - Issued under Article 48 of the Environmental Law (Royal Decree M/165,")
    print("    19/11/1441H); the base law is already ingested as the environmental_law track")
    print("  - Disclosed: single reachable full-text source; penalty-table column ambiguity;")
    print("    preserved appendix-title typo (التحقيق vs التدقيق); Arabic-Indic digits kept")
    return 0


if __name__ == "__main__":
    sys.exit(main())
