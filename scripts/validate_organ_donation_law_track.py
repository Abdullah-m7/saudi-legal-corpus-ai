#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Human Organ Donation Law track (نظام
التبرع بالأعضاء البشرية, Royal Decree M/70, 19/8/1442H -- the currently in-force
Human Organ Donation Law).

27 records: 27 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (the Law has had no amendments per
nezams.com: "لم يجرى عليه تعديل"). NO chapters/فصول -- confirmed independently by a
zero-hit search for the word "الفصل" across the entire source page; the Law is a
single flat sequence of Articles 1-27 (unlike waste_management_law's 11 chapters).

SUPERSESSION -- UNLIKE waste_management_law (named predecessor inside its own
Article 37), this Law's Article 27(2) carries only a GENERIC unnamed repeal
clause: "يلغي النظام كل ما يتعارض معه من أحكام." No specific predecessor law is
named anywhere in the text.

VERIFICATION TIER -- TIER_3. See the generator docstring and the source
artifact's verification_methodology_note: laws.boe.gov.sa was checked FIRST but
is unreachable this pass (TLS "Connection reset by peer" on repeated direct
curl attempts, including a probe of the bare portal homepage); web.archive.org
was explicitly attempted this pass via TWO different tools (a direct curl to a
confirmed-existing snapshot, and the WebFetch tool) and BOTH independently
confirmed the archive is blocked this session -- not circumvented further. The
verbatim text of all 27 articles was extracted from nezams.com (a single clean
born-digital HTML aggregator), with governing metadata and content cross-checked
for identity -- including near-verbatim textual overlap for Article 3 and the
Article 21 penalty amounts, not merely metadata -- against saudipedia.com and
ar.wikipedia.org (for SCOT's identity as a Saudi Health Council affiliate). This
validator does not re-adjudicate provenance; it only checks internal
self-consistency of the ingested text and that every discrepancy is still
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
SRC = os.path.join(ROOT, "sources", "organ_donation_law", "law", "official_source",
                   "organ_donation_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "organ_donation_law", "law", "verified",
                       "organ_donation_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "organ_donation_law", "law", "verified",
                       "organ_donation_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "organ_donation_law_arabic_legal_llm",
                   "organ_donation_law_legal_llm_001_027.json")
N = 27
KEY_RE = r"organ_donation_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 27, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 0  # no فصول -- flat article sequence, confirmed

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "organ_donation_law_boe_and_wayback_unreachable_single_aggregator",
    "organ_donation_law_implementing_regulation_not_ingested",
    "organ_donation_law_shura_resolution_215_54_source_typo",
    "organ_donation_law_no_named_predecessor_general_repeal_only",
    "organ_donation_law_gregorian_dates_secondary_only",
    "organ_donation_law_no_chapter_structure_confirmed_flat",
    "organ_donation_law_farsi_yeh_glyph_normalized",
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

    chs = src.get("chapter_structure")
    if chs is None or len(chs) != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected chapter_structure to be an empty list (no فصول), got %r" % chs)

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
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
        if a.get("section_ar") not in ("", None):
            e.append("[2] %s: expected empty section_ar (no chapters in this Law)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if k in (AMENDED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/added article missing amendment_history" % k)
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
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits only)" % k)
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)

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
        e.append("[2k] missing amendment_history (must record the founding M/70 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/70" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/70")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/70)" \
            or src.get("decree_date_hijri") != "19/8/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/70, 19/8/1442H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (the Law has no amendments)")
    sup = src.get("supersedes_ar", "")
    if not sup or "يلغي النظام كل ما يتعارض معه" not in sup:
        e.append("[2j] supersedes_ar must disclose the Law's own generic (unnamed) repeal clause")

    if not src.get("preamble_ar") or "19 / 8 / 1442" not in src.get("preamble_ar", "") \
            or "نظام التبرع بالأعضاء البشرية" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "decree date and نظام التبرع بالأعضاء البشرية")
    if not src.get("com_resolution_ar") or "قرار مجلس الوزراء" not in src.get("com_resolution_ar", "") \
            or "468" not in src.get("com_resolution_ar", ""):
        e.append("[2j] com_resolution_ar (CoM Resolution 468 full text) must be present")

    art1 = arts.get("organ_donation_law_art_001", {})
    if "المركز: المركز السعودي لزراعة الأعضاء" not in art1.get("text", "") \
            or "المجلس: المجلس الصحي السعودي" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (المركز / المجلس)")
    art26 = arts.get("organ_donation_law_art_026", {})
    if "اللائحة" not in art26.get("text", "") or "تسعين" not in art26.get("text", ""):
        e.append("[2j] Article 26 missing expected implementing-regulation mandate (اللائحة/تسعين)")
    art27 = arts.get("organ_donation_law_art_027", {})
    if "يعمل بالنظام" not in art27.get("text", "") or "تسعين" not in art27.get("text", ""):
        e.append("[2j] Article 27 missing expected entry-into-force clause (تسعين يوما)")
    if "يلغي النظام كل ما يتعارض معه من أحكام" not in art27.get("text", ""):
        e.append("[2j] Article 27 missing expected generic repeal clause")
    art27_label = art27.get("number_label_ar")
    if art27_label != "المادة السابعة والعشرون":
        e.append("[2j] Article 27 number_label_ar must be 'المادة السابعة والعشرون', got %r"
                 % art27_label)

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
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Human Organ Donation Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Human Organ Donation Law (نظام التبرع بالأعضاء البشرية)")
    print("  - 27 records: 27 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (the Law has had no amendments)")
    print("  - NO chapters (فصول) -- confirmed independently via a zero-hit search for 'الفصل'")
    print("    across the source page; a single flat sequence of Articles 1-27")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/70, 19/8/1442H (CoM Resolution 468,")
    print("    17/8/1442H / 30 March 2021G; Shura Resolutions 215/54 and 24/4). Brand-new")
    print("    base-law track, not previously in this corpus.")
    print("  - SUPERSESSION: Article 27(2) is a GENERIC unnamed repeal clause only -- no")
    print("    specific predecessor law is named (unlike waste_management_law's Article 37).")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa checked first but unreachable this")
    print("    pass (TLS connection reset, including the bare portal homepage); web.archive.org")
    print("    explicitly attempted via TWO different tools (curl + WebFetch) and BOTH")
    print("    confirmed blocked this session. Full verbatim text from nezams.com (single")
    print("    clean born-digital HTML aggregator, no scan/OCR/ligature defects); governing")
    print("    metadata + content cross-checked for identity -- including near-verbatim")
    print("    textual overlap, not merely metadata -- against saudipedia.com and")
    print("    ar.wikipedia.org. Re-verify verbatim text vs laws.boe.gov.sa when reachable.")
    print("  - Implementing Regulation (Article 26 mandate) confirmed to EXIST via multiple")
    print("    independent secondary references (lexismiddleeast.com, uqn.gov.sa, qanoniah.com,")
    print("    moh.gov.sa/istitlaa.ncc.gov.sa draft pages), but its full text was NOT")
    print("    retrieved/ingested this pass -- flagged as a follow-up candidate track.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
