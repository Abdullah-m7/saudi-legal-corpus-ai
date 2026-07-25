#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Commercial
Register Law track (اللائحة التنفيذية لنظام السجل التجاري; 21 records, ALL
اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; flat structure -- no chapters).

VERIFICATION TIER -- see the generator's module docstring and
sources/commercial_register_regulation/law/official_source/
commercial_register_regulation_official_source.json's verification_methodology_note
for the full account: PRIMARY-ish source is qanoonsa.com/p/507902/ (a legal
aggregator reproducing the Umm al-Qura Gazette text, stating Decision No. (288)
and gazette issue 5079 explicitly) cross-checked against aleqt.com (Al-Eqtisadiah,
independent Saudi financial daily) -> TIER_2. laws.boe.gov.sa was checked first
per standard methodology but has NO dedicated lawId page for this Implementing
Regulation (the lawId surfaced by web search is the BASE LAW's page, confirmed
by direct inspection of two independent-date Wayback Machine snapshots). This
validator does not re-adjudicate provenance; it only checks internal
self-consistency and that every discrepancy is still recorded.

DISAMBIGUATION FROM THE JOINT MOC DECISION 288 (checked explicitly): the same
Decision jointly approves three further entirely separate instruments (Trade
Names Regulation, a subsidiary-register correction mechanism, and pre-existing
trade-name controls) -- this validator checks that the disambiguation and the
correction-mechanism out-of-scope decision are both disclosed in
known_unresolved_discrepancies.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "commercial_register_regulation", "law", "official_source",
                   "commercial_register_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "commercial_register_regulation", "law", "verified",
                       "commercial_register_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "commercial_register_regulation", "law", "verified",
                       "commercial_register_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "commercial_register_regulation_arabic_legal_llm",
                   "commercial_register_regulation_legal_llm_001_021.json")
N = 21
KEY_RE = r"commercial_register_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 21, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "commercial_register_regulation_joint_decision_cleanly_disambiguated",
    "commercial_register_regulation_correction_mechanism_out_of_scope",
    "commercial_register_regulation_boe_shares_base_law_page",
    "commercial_register_regulation_mc_uqn_unreachable_direct",
    "commercial_register_regulation_art_019_mismatched_parentheses",
    "commercial_register_regulation_annex1_typo_preserved",
    "commercial_register_regulation_no_chapters_flat_structure",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        # legitimate uses: the alphabetic list-marker "هـ-"/"هـ " and the
        # Hijri-date suffix "هـ" both have "ه" immediately before the run.
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

    # continuous 1..21, no gaps/dupes, no مكرر
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))
    if any(k.endswith(tuple("_mukarrar%d" % i for i in range(10))) or "_mukarrar" in k
           for k in arts):
        e.append("[1b] unexpected مكرر keys (this regulation has none)")

    # flat structure: no chapter_structure field, every section_ar empty
    if src.get("chapter_structure"):
        e.append("[1c] unexpected chapter_structure present (this regulation is flat, no فصول)")

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a.get("status") or not str(a.get("status")).strip():
            e.append("[2] %s: empty verification status string" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar"):
            e.append("[2] %s: section_ar must be empty (flat structure, no فصول)" % k)
        if not a.get("article_title_ar"):
            e.append("[2] %s: missing article_title_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if a.get("history"):
            e.append("[2i] %s: no article in this unamended regulation should carry history[]" % k)
        if "‏" in a["text"]:
            e.append("[2f] %s: residual RIGHT-TO-LEFT MARK (U+200F) artifact detected" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)

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

    ah = src.get("amendment_history")
    if not ah:
        e.append("[2k] missing amendment_history (must record founding decision 288)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "288" not in decrees:
            e.append("[2k] amendment_history must reference founding Decision (288)")

    # annex must be preserved verbatim, referenced by Article 18, with its
    # documented typo retained (flag-don't-correct)
    annex = src.get("annex_ar")
    if not annex or not annex.get("text"):
        e.append("[2n] missing annex_ar (financial fees table) verbatim preservation")
    else:
        if "المقابل المالي" not in annex.get("title_ar", ""):
            e.append("[2n] annex_ar missing expected title")
        if annex.get("referenced_by_article") != "commercial_register_regulation_art_018":
            e.append("[2n] annex_ar must record it is referenced by Article 18")
        if "السجل تجاري" not in annex["text"]:
            e.append("[2n] annex_ar must RETAIN the documented typo 'السجل تجاري' verbatim")

    # preamble (issuance decision) must be present and name the issuing Minister
    pre = src.get("preamble_ar") or ""
    if not pre:
        e.append("[2p] preamble_ar (issuance decision) should be present and verbatim")
    else:
        if "القصبي" not in pre:
            e.append("[2p] preamble_ar must name the issuing Minister (القصبي)")
        if "الثامنة والعشرين" not in pre:
            e.append("[2p] preamble_ar must cite enabling Article 28 of the Commercial Register Law")
        if "اللائحة التنفيذية لنظام الأسماء التجارية" not in pre:
            e.append("[2p] preamble_ar must show the joint approval of the sibling Trade Names "
                     "Regulation (disambiguation evidence)")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("commercial_register_regulation_art_001", {}).get("text", "")
    if "م / ٨٣" not in art1 and "م/83" not in art1 and "٨٣" not in art1:
        e.append("[2j] Article 1 missing expected reference to the base Law (Royal Decree M/83)")
    art6 = arts.get("commercial_register_regulation_art_006", {}).get("text", "")
    if "يقيد التاجر في السجل التجاري مرة واحدة" not in art6:
        e.append("[2j] Article 6 missing expected single-registration rule (cross-verified via aleqt.com)")
    art13 = arts.get("commercial_register_regulation_art_013", {}).get("text", "")
    if "ستين" not in art13 or "مائة وثمانين" not in art13:
        e.append("[2j] Article 13 missing expected 60/180-day heir periods (cross-verified via aleqt.com)")
    art19 = arts.get("commercial_register_regulation_art_019", {}).get("text", "")
    if "الثالثة والعشرين" not in art19 or ")٥٠٠)" not in art19:
        e.append("[2j] Article 19 missing expected committee cross-reference or the documented "
                 "mismatched-parenthesis anomaly (رقم 500)")
    art21 = arts.get("commercial_register_regulation_art_021", {}).get("text", "")
    if "تنشر اللائحة في الجريدة الرسمية" not in art21:
        e.append("[2j] Article 21 (final) missing expected publication/effect clause")

    if src.get("decree") != "قرار وزير التجارة رقم (288)" \
            or src.get("decree_date_hijri") != "20/9/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with verified MoC Decision 288, 20/9/1446H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (fresh full issuance, no amendments)")

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
        if r.get("legal_status_ar") != a.get("legal_status_ar"):
            e.append("[4] %s: legal_status_ar mismatch" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("consolidated_amended_law") is not False:
        e.append("[4b] summary consolidated_amended_law must be False")
    if not summary.get("known_unresolved_discrepancies"):
        e.append("[4b] summary missing known_unresolved_discrepancies")
    if not summary.get("annex_ar"):
        e.append("[4b] summary missing annex_ar")

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
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Commercial Register Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Commercial Register Law")
    print("  (اللائحة التنفيذية لنظام السجل التجاري)")
    print("  - 21 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- fresh full issuance")
    print("  - Flat structure, no chapters; plus Annex (1) financial-fees table (not per-article)")
    print("  - VERIFICATION TIER: TIER_2 -- qanoonsa.com (Umm al-Qura Gazette reproduction, Decision")
    print("    288, issue 5079/30-Mar-2025) cross-checked against aleqt.com (Al-Eqtisadiah, independent")
    print("    secondary source); laws.boe.gov.sa checked first but shares the base Law's lawId page")
    print("    (confirmed by direct Wayback inspection), no dedicated page for this Regulation")
    print("  - Ministry of Commerce Decision No. (288), 20 Ramadan 1446H (20 March 2025G), issued under")
    print("    Article 28 of the Commercial Register Law (Royal Decree M/83, 19/3/1446H)")
    print("  - JOINT-DECISION DISAMBIGUATION: MoC Decision 288 also approves three further separate")
    print("    instruments (Trade Names Regulation, subsidiary-register correction mechanism, and")
    print("    pre-existing trade-name controls) -- cleanly disambiguated from the Decision's own text;")
    print("    none of their content is included in this track")
    print("  - Documented source anomalies preserved verbatim: Article 19's mismatched parentheses")
    print("    (rows 2-4), Annex 1's 'السجل تجاري' typo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
