#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Implementing Regulation of the Protection
from Abuse Law track (اللائحة التنفيذية لنظام الحماية من الإيذاء) -- the
CURRENT (2024G) version published by HRSD, NOT the original ~1435H version.

14 records, all اصلية within this instrument, 0 معدلة / ملغاة / مضافة; FLAT
regulation -- no chapters/فصول.

VERIFICATION TIER -- see the generator's module docstring and
sources/protection_from_abuse_regulation/law/official_source/
protection_from_abuse_regulation_official_source.json's
verification_methodology_note for the full account: primary source fetched
directly (HTTP 200) from hrsd.gov.sa (Arabic + English official PDFs);
laws.boe.gov.sa has no dedicated page found for this Regulation this pass;
Wayback Machine's content-serving path and r.jina.ai reader-proxy were both
blocked/refused this pass (CDX metadata API worked); qanoniah.com is a
JS-rendered SPA (title-only corroboration of a distinct "1440" predecessor
file) -> TIER_2. This validator does not re-adjudicate provenance; it only
checks internal self-consistency and that every discrepancy is still
recorded.

MATERIAL FACTS checked: flat structure (chapter_structure == []); no
self-stated decree number (self_citation_status ==
NOT_STATED_IN_DOCUMENT, decree_date_hijri is None); Article 13 explicitly
names the predecessor it replaces (Ministerial Resolution 76048, 20/4/1440H);
Article 1 defines "الوزارة" as the modern HRSD name confirming this is the
current-era text; the three-version lineage (1435H original -> 1440H
Resolution 76048 -> current 2024G) is recorded in amendment_history.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "protection_from_abuse_regulation", "law", "official_source",
                    "protection_from_abuse_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "protection_from_abuse_regulation", "law", "verified",
                        "protection_from_abuse_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "protection_from_abuse_regulation", "law", "verified",
                        "protection_from_abuse_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "protection_from_abuse_regulation_arabic_legal_llm",
                    "protection_from_abuse_regulation_legal_llm_001_014.json")
N = 14
KEY_RE = r"protection_from_abuse_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 14, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "protection_from_abuse_regulation_current_decree_number_not_self_stated",
    "protection_from_abuse_regulation_no_preamble",
    "protection_from_abuse_regulation_version_lineage",
    "protection_from_abuse_regulation_adlm_stale",
    "protection_from_abuse_regulation_boe_no_dedicated_page_found",
    "protection_from_abuse_regulation_wayback_content_path_blocked",
    "protection_from_abuse_regulation_jina_reader_blocked",
    "protection_from_abuse_regulation_qanoniah_js_rendered_no_fulltext",
    "protection_from_abuse_regulation_istitlaa_draft_stage_unreachable",
    "protection_from_abuse_regulation_pdf_font_ligature_lam_hamza",
    "protection_from_abuse_regulation_source_typo_alma_missing_hamza",
    "protection_from_abuse_regulation_source_duplicate_definition_term",
    "protection_from_abuse_regulation_hamza_inconsistency_art7",
    "protection_from_abuse_regulation_repeals_1440_version_confirmed",
    "protection_from_abuse_regulation_hrsd_naming_confirms_current_version",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ٰٟۖ-ۭ]")


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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1c] this regulation is flat (no chapters); chapter_structure must be [] but is %r"
                  % (chs,))

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
        if a.get("section_ar") != "":
            e.append("[2] %s: section_ar must be empty for this flat regulation" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if a.get("history"):
            e.append("[2i] %s: no article in this track carries amendment history (full "
                     "replacement instrument, not per-article amendment); history must be []"
                     % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # reversed bidi-mirrored parens must have been fixed already: no ")X(" pattern left
        if re.search(r"\)[^()\n]{1,80}\(", a["text"]):
            e.append("[2n] %s: unresolved reversed-parenthesis (bidi mirror) artifact" % k)

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
    if not ah or len(ah) < 3:
        e.append("[2k] amendment_history must record the full 3-version lineage "
                 "(1435H original -> 1440H Resolution 76048 -> current 2024G)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "43047" not in decrees:
            e.append("[2k] amendment_history must reference the original Resolution 43047 (1435H)")
        if "76048" not in decrees:
            e.append("[2k] amendment_history must reference the superseded Resolution 76048 (1440H)")

    # this track's CURRENT version deliberately has NO self-stated decree number
    if src.get("self_citation_status") != "NOT_STATED_IN_DOCUMENT":
        e.append("[2l] self_citation_status must honestly record NOT_STATED_IN_DOCUMENT "
                 "(no ministerial resolution number/date is self-cited in the current PDF)")
    if src.get("decree_date_hijri") is not None:
        e.append("[2l] decree_date_hijri must be None (no self-stated issuance date exists; "
                 "do not fabricate one)")
    dfm = src.get("document_file_metadata") or {}
    if not dfm.get("arabic_pdf_creation_utc") or not dfm.get("english_pdf_creation_utc"):
        e.append("[2l] document_file_metadata must record both PDF file-creation timestamps")

    # spot-checks anchoring key facts
    art1 = arts.get("protection_from_abuse_regulation_art_001", {}).get("text", "")
    if "الموارد البشرية والتنمية الاجتماعية" not in art1:
        e.append("[2j] Article 1 must define الوزارة as the modern HRSD name "
                 "(confirms this is the CURRENT-era version)")
    if "الإيذاء" not in art1:
        e.append("[2j] Article 1 missing expected abuse terminology")
    art13 = arts.get("protection_from_abuse_regulation_art_013", {}).get("text", "")
    for token in ("76048", "1440", "تحل هذه اللائحة محل"):
        if token not in art13:
            e.append("[2j] Article 13 (repeal clause) missing expected token %r" % token)
    art14 = arts.get("protection_from_abuse_regulation_art_014", {}).get("text", "")
    if "يصدر الوزير" not in art14:
        e.append("[2j] Article 14 missing expected minister-delegation clause")

    # no OTHER repeal/predecessor should be named besides the 1440H one in Article 13
    for k, a in arts.items():
        if k == "protection_from_abuse_regulation_art_013":
            continue
        if re.search(r"يلغى|يُلغى|يلغي|تحل .* محل", a["text"]):
            e.append("[2j] %s: unexpected repeal/replacement clause outside Article 13" % k)

    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (full-replacement instrument, "
                 "no per-article amendment layering within this track)")

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
        if (r.get("is_amended")) != (r["article_key"] in AMENDED_KEYS):
            e.append("[4] %s: is_amended flag mismatch" % r["article_key"])
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
    if summary.get("self_citation_status") != "NOT_STATED_IN_DOCUMENT":
        e.append("[4b] summary self_citation_status must be NOT_STATED_IN_DOCUMENT")

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

    if e:
        print("FAIL: %d error(s) in Protection from Abuse Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Implementing Regulation of the Protection from Abuse Law (CURRENT, 2024G)")
    print("  - 14 records, all اصلية within this instrument, 0 معدلة/ملغاة/مضافة")
    print("  - FLAT regulation: continuous 1-14, NO chapters/فصول (chapter_structure == [],")
    print("    section_ar empty by design)")
    print("  - VERIFICATION TIER: TIER_2 -- hrsd.gov.sa official PDFs (Arabic+English) fetched")
    print("    directly (HTTP 200); laws.boe.gov.sa has no dedicated page found this pass;")
    print("    Wayback content path and r.jina.ai both blocked/refused; qanoniah.com JS-rendered")
    print("    (title-only corroboration)")
    print("  - NO self-stated ministerial decision number/date for the current version (honestly")
    print("    disclosed, not fabricated); Article 13 replaces Ministerial Resolution 76048,")
    print("    20/4/1440H (27/12/2018G)")
    print("  - Full version lineage: Resolution 43047 (8/5/1435H, original) -> Resolution 76048")
    print("    (20/4/1440H, superseded) -> current (2024G, this track)")
    print("  - adlm.moj.gov.sa confirmed STALE (still hosts only the 1435H original)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
