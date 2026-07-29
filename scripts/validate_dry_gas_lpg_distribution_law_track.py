#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Dry Gas / LPG Distribution Law
track (نظام توزيع الغاز الجاف وغاز البترول السائل للأغراض السكنية والتجارية,
originally Royal Decree M/126, 1/12/1438H, substantively amended by Royal
Decree M/112, 9/11/1443H).

21 records: 3 اصلية (Articles 5, 6, 21), 17 معدلة (Articles 1-4, 7, 8, 10-20),
1 ملغاة (Article 9 -- repealed outright, content unrecoverable). No
chapter/باب/فصل subdivision (flat structure of 21 sequential articles).

VERIFICATION TIER -- TIER_1_PRIMARY_MULTI_SOURCE. See the generator docstring
and the source artifact's verification_methodology_note: laws.boe.gov.sa,
moenergy.gov.sa/cdn.moenergy.gov.sa and ecra.gov.sa were all unreachable this
pass, as was web.archive.org (blocked by egress policy). The governing text
is the Ministry of Energy's own consolidated PDF (hosted via misa.gov.sa),
verified via an independent rendered-page-image pass after a systematic
pdftotext ligature-extraction bug was discovered and fixed. This validator
does not re-adjudicate provenance; it only checks internal self-consistency
of the ingested text and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "dry_gas_lpg_distribution_law", "law", "official_source",
                   "dry_gas_lpg_distribution_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "dry_gas_lpg_distribution_law", "law", "verified",
                       "dry_gas_lpg_distribution_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "dry_gas_lpg_distribution_law", "law", "verified",
                       "dry_gas_lpg_distribution_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "dry_gas_lpg_distribution_law_arabic_legal_llm",
                   "dry_gas_lpg_distribution_law_legal_llm_001_021.json")
N = 21
KEY_RE = r"dry_gas_lpg_distribution_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 3, "معدلة": 17, "ملغاة": 1, "مضافة": 0}
AMENDED_KEYS = {"dry_gas_lpg_distribution_law_art_%03d" % n
                for n in (1, 2, 3, 4, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)}
UNCHANGED_KEYS = {"dry_gas_lpg_distribution_law_art_%03d" % n for n in (5, 6, 21)}
REPEALED_KEYS = {"dry_gas_lpg_distribution_law_art_009"}
ADDED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_REPEALED = "REPEALED"

# Articles for which a full, confidently-reconstructed previous_text_ar is
# expected (mechanical single-operation reversal, per the generator docstring
# and known_unresolved_discrepancies). All other amended articles must NOT
# assert a full previous_text_ar this pass.
RECONSTRUCTED_PREVIOUS_TEXT_KEYS = {
    "dry_gas_lpg_distribution_law_art_%03d" % n for n in (2, 10, 11, 14, 15)
}

FLAGGED_DISCREPANCY_KEYS = {
    "dry_gas_lpg_distribution_law_boe_moenergy_ecra_unreachable",
    "dry_gas_lpg_distribution_law_pdf_ligature_extraction_glitch",
    "dry_gas_lpg_distribution_law_footnote29_decree_number_typo",
    "dry_gas_lpg_distribution_law_previous_text_partial_reconstruction",
    "dry_gas_lpg_distribution_law_m126_preamble_unavailable",
    "dry_gas_lpg_distribution_law_original_com_shura_unverified",
    "dry_gas_lpg_distribution_law_executive_regulation_not_ingested",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ٰٟ]")


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

    if "chapter_structure" in src and src.get("chapter_structure"):
        e.append("[1c] this law has no chapters (فصول/أبواب); chapter_structure must be "
                 "absent or empty")

    sc = Counter()
    for k, a in arts.items():
        if k in REPEALED_KEYS:
            expected_status = STATUS_REPEALED
        elif k in AMENDED_KEYS:
            expected_status = STATUS_AMENDED
        else:
            expected_status = STATUS_UNCHANGED
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if k in (AMENDED_KEYS | ADDED_KEYS | REPEALED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/added/repealed article missing amendment_history" % k)
        if k not in (AMENDED_KEYS | ADDED_KEYS | REPEALED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/added/repealed article must have empty history[]" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits only)" % k)
        if "٪" in a["text"]:
            e.append("[2f] %s: residual Arabic percent sign (must be normalized to '%%')" % k)
        if "الالئحة" in a["text"] or "املادة" in a["text"] or "املرخص" in a["text"]:
            e.append("[2f] %s: residual PDF ligature-reversal glitch not normalized "
                     "(الالئحة/املادة/املرخص)" % k)
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)
        for h in a.get("history", []):
            pt = h.get("previous_text_ar", "")
            if pt and ("الالئحة" in pt or "املادة" in pt):
                e.append("[2f] %s: history previous_text_ar has unnormalized ligature glitch" % k)
            if pt and HARAKAT.search(pt):
                e.append("[2h] %s: history previous_text_ar has residual harakat" % k)
        has_previous_text = any(h.get("previous_text_ar") for h in a.get("history", []))
        if k in RECONSTRUCTED_PREVIOUS_TEXT_KEYS and not has_previous_text:
            e.append("[2m] %s: expected a reconstructed previous_text_ar (per generator "
                     "docstring) but none found" % k)
        if k in AMENDED_KEYS and k not in RECONSTRUCTED_PREVIOUS_TEXT_KEYS and has_previous_text:
            e.append("[2m] %s: unexpected previous_text_ar for an article not flagged as "
                     "confidently reconstructable" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

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

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record both M/126 and M/112)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/126" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/126")
        if "م/112" not in decrees:
            e.append("[2k] amendment_history must reference amending decree م/112")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/126)" \
            or src.get("decree_date_hijri") != "1/12/1438":
        e.append("[2j] decree/decree_date_hijri mismatch with verified founding Royal Decree "
                 "M/126, 1/12/1438H")
    if src.get("amendment_decree") != "المرسوم الملكي رقم (م/112)" \
            or src.get("amendment_decree_date_hijri") != "9/11/1443":
        e.append("[2j] amendment_decree/amendment_decree_date_hijri mismatch with verified "
                 "Royal Decree M/112, 9/11/1443H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this is the consolidated "
                 "post-M/112 text)")
    m112_preamble = src.get("amendment_decree_m112_preamble_ar", "")
    if not m112_preamble or "م/112" not in m112_preamble or "1443/11/9" not in m112_preamble:
        e.append("[2j] amendment_decree_m112_preamble_ar must be present and reference the "
                 "decree number (م/112) and date (1443/11/9H)")

    art1 = arts.get("dry_gas_lpg_distribution_law_art_001", {})
    if "وزارة الطاقة" not in art1.get("text", "") or "الغاز الطبيعي البديل" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected current definitions (وزارة الطاقة / "
                 "الغاز الطبيعي البديل)")
    art9 = arts.get("dry_gas_lpg_distribution_law_art_009", {})
    if art9.get("text", "").strip() != "(ملغاة)":
        e.append("[2j] Article 9 (repealed) must have placeholder text '(ملغاة)' matching "
                 "the official source verbatim")
    art16 = arts.get("dry_gas_lpg_distribution_law_art_016", {})
    if "10%" not in art16.get("text", "") or "خمسة ملايين ريال" not in art16.get("text", ""):
        e.append("[2j] Article 16 missing expected post-M/112 penalty provisions (10%% daily "
                 "fine / 5 million riyal cap)")
    art21 = arts.get("dry_gas_lpg_distribution_law_art_021", {})
    if "يعمل بهذا النظام" not in art21.get("text", ""):
        e.append("[2j] Article 21 missing expected entry-into-force clause")
    art21_label = art21.get("number_label_ar")
    if art21_label != "المادة الحادية والعشرون":
        e.append("[2j] Article 21 number_label_ar must be 'المادة الحادية والعشرون', got %r"
                 % art21_label)

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
        if r["article_key"] in REPEALED_KEYS:
            expected_status = STATUS_REPEALED
        elif r["article_key"] in AMENDED_KEYS:
            expected_status = STATUS_AMENDED
        else:
            expected_status = STATUS_UNCHANGED
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])
        if r.get("law_component") != "law":
            e.append("[5] %s: law_component must be 'law'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Dry Gas/LPG Distribution Law track:" % len(e))
        for x in e[:60]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Dry Gas and Liquefied Petroleum Gas Distribution Law")
    print("      (نظام توزيع الغاز الجاف وغاز البترول السائل للأغراض السكنية والتجارية)")
    print("  - 21 records: 3 اصلية (5, 6, 21), 17 معدلة (1-4, 7, 8, 10-20), 1 ملغاة (9)")
    print("  - No chapter/فصل/باب subdivision (flat 21-article structure)")
    print("  - INSTRUMENT CONFIRMED: originally Royal Decree M/126, 1/12/1438H; substantively")
    print("    amended by Royal Decree M/112, 9/11/1443H. Brand-new base-law track, not")
    print("    previously in this corpus.")
    print("  - VERIFICATION TIER: TIER_1_PRIMARY_MULTI_SOURCE -- laws.boe.gov.sa,")
    print("    moenergy.gov.sa/cdn.moenergy.gov.sa, ecra.gov.sa and web.archive.org all")
    print("    unreachable this pass. Governing text is the Ministry of Energy's own")
    print("    consolidated PDF (hosted via misa.gov.sa), verified via an independent")
    print("    rendered-page-image pass after a pdftotext ligature-extraction bug was found.")
    print("  - previous_text_ar included only for 5 of 17 amended articles (2, 10, 11, 14, 15)")
    print("    where full reconstruction was unambiguous; see known_unresolved_discrepancies.")
    print("  - Article 9 repealed outright by M/112; pre-1443H content unrecoverable from any")
    print("    source reached this session.")
    print("  - An Implementing Regulation and multiple Bylaws exist for this Law, NOT ingested")
    print("    this pass -- flagged as follow-up candidates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
