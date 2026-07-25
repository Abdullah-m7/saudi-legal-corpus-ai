#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Privatization Law
track (اللائحة التنفيذية لنظام التخصيص; 169 records: 140 اصلية, 19 معدلة,
10 مضافة, 0 ملغاة; two-level باب/فصل structure -- Book 7 has no فصول).

VERIFICATION TIER -- see the generator's module docstring and sources/
privatization_regulation/law/official_source/privatization_regulation_
official_source.json's verification_methodology_note for the full account:
governing text fetched directly and live from the Official Gazette itself
(uqn.gov.sa/details?p=24451, HTTP 200) -> TIER_1 for the current text's
source. A SEPARATE, more important reservation is disclosed about amendment-
diff completeness (privatization_regulation_amendment_diff_partial): the 10
ADDED and 19 AMENDED articles below are directly confirmed via old-vs-new
content comparison; the remaining 140 "اصلية" articles reflect "not
identified as changed in the checks performed", not an exhaustive
word-for-word guarantee. This validator does not re-adjudicate provenance;
it only checks internal self-consistency of the text this track ingests, and
that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "privatization_regulation", "law", "official_source",
                   "privatization_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "privatization_regulation", "law", "verified",
                       "privatization_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "privatization_regulation", "law", "verified",
                       "privatization_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "privatization_regulation_arabic_legal_llm",
                   "privatization_regulation_legal_llm_001_169.json")
N = 169
KEY_RE = r"privatization_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 140, "معدلة": 19, "ملغاة": 0, "مضافة": 10}
EXPECTED_TOP_LEVEL_BOOKS = 8
SECTIONLESS_BOOK_LABEL = "الباب السابع"  # العروض التلقائية -- no فصول

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
STATUS_ADDED_DATED = "ADDED_DATED"

AMENDED_KEYS = {
    "privatization_regulation_art_%03d" % n for n in
    (15, 23, 30, 32, 33, 34, 49, 64, 67, 71, 75, 76, 79, 84, 85, 86, 87, 88, 135)
}
ADDED_KEYS = {
    "privatization_regulation_art_%03d" % n for n in
    (66, 72, 80, 81, 82, 89, 104, 141, 155, 158)
}
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()

FLAGGED_DISCREPANCY_KEYS = {
    "privatization_regulation_boe_unreachable",
    "privatization_regulation_wayback_blocked",
    "privatization_regulation_jina_reader_blocked",
    "privatization_regulation_original_pdf_letter_reversal",
    "privatization_regulation_amendment_diff_partial",
    "privatization_regulation_article_165_missing_colon",
    "privatization_regulation_original_gregorian_date_not_pinpointed",
    "privatization_regulation_argaam_attribution_discrepancy",
    "privatization_regulation_disambiguation_from_organizing_rules_and_ncp_statute",
    "privatization_regulation_superseded_internal_guides_out_of_scope",
    "privatization_regulation_page_footer_last_modified_not_new_amendment",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")

# Deterministic 2021->2024 renumbering: for a non-added article numbered X, its
# 2021 (159-article) predecessor number = X minus the count of ADDED articles
# whose (current) number is <= X. Verified against every confirmed insertion
# point (structural book/chapter deltas cross-checked with direct content
# comparison -- see the source artifact's verification_methodology_note).
ADDED_NUMS = sorted(int(k.rsplit("_", 1)[1]) for k in ADDED_KEYS)


def _expected_renumbered_from(n):
    if n in ADDED_NUMS:
        return None
    shift = sum(1 for a in ADDED_NUMS if a <= n)
    old = n - shift
    return None if old == n else old


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

    books = src.get("chapter_structure") or []
    if len(books) != EXPECTED_TOP_LEVEL_BOOKS:
        e.append("[1c] expected %d أبواب, got %d" % (EXPECTED_TOP_LEVEL_BOOKS, len(books)))

    covered = set()
    for b in books:
        lo, hi = (int(x) for x in b["articles"].split("-")) if "-" in b["articles"] else (int(b["articles"]),) * 2
        chapters = b.get("chapters") or []
        if not chapters and b["label_ar"] != SECTIONLESS_BOOK_LABEL:
            e.append("[1c] %s: has no فصول but is not the designated sectionless book (%s)"
                     % (b["label_ar"], SECTIONLESS_BOOK_LABEL))
        if chapters and b["label_ar"] == SECTIONLESS_BOOK_LABEL:
            e.append("[1c] %s: designated sectionless book unexpectedly has فصول" % b["label_ar"])
        chap_covered = set()
        for c in chapters:
            clo, chi = (int(x) for x in c["articles"].split("-")) if "-" in c["articles"] else (int(c["articles"]),) * 2
            for nn in range(clo, chi + 1):
                if nn in chap_covered:
                    e.append("[1c] %s/%s: article %d covered by more than one فصل" % (b["label_ar"], c["label_ar"], nn))
                chap_covered.add(nn)
        if chapters and chap_covered != set(range(lo, hi + 1)):
            missing = sorted(set(range(lo, hi + 1)) - chap_covered)
            extra = sorted(chap_covered - set(range(lo, hi + 1)))
            if missing:
                e.append("[1c] %s: فصول missing article(s) %s" % (b["label_ar"], missing[:20]))
            if extra:
                e.append("[1c] %s: فصول cover out-of-book article(s) %s" % (b["label_ar"], extra[:20]))
        for nn in range(lo, hi + 1):
            if nn in covered:
                e.append("[1c] article %d covered by more than one باب" % nn)
            covered.add(nn)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in ADDED_KEYS and not a.get("history"):
            e.append("[2] %s: added article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in AMENDED_KEYS and k not in ADDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended/non-added article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        expected_rf = _expected_renumbered_from(n)
        if a.get("renumbered_from_2021_article") != expected_rf:
            e.append("[2r] %s: renumbered_from_2021_article expected %r, got %r"
                     % (k, expected_rf, a.get("renumbered_from_2021_article")))
        if n not in ADDED_NUMS and not a.get("book_title_ar"):
            e.append("[2] %s: missing book_title_ar" % k)

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

    if not src.get("amendment_history") or len(src["amendment_history"]) < 2:
        e.append("[2k] amendment_history must record both the original (Q-9/2021) and "
                 "amending (1/4/2023) decisions")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "ق-9/2021" not in decrees:
            e.append("[2k] amendment_history must reference founding decision ق-9/2021")
        if "1/4/2023" not in decrees:
            e.append("[2k] amendment_history must reference amending decision 1/4/2023")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("privatization_regulation_art_001", {})
    t1 = art1.get("text", "")
    if "القواعد المنظمة" not in t1 or "اللائحة التنفيذية للنظام" not in t1:
        e.append("[2j] Article 1 missing expected cross-reference to القواعد المنظمة "
                 "(disambiguation from the separate Organizing Rules instrument)")
    art3 = arts.get("privatization_regulation_art_003", {})
    if "50.000.000" not in art3.get("text", "") and "50،000،000" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected 50-million minimum threshold clause")
    art66 = arts.get("privatization_regulation_art_066", {})
    if art66.get("legal_status_ar") != "مضافة":
        e.append("[2j] Article 66 must be مضافة (confirmed new article, no 2021 predecessor)")
    art169 = arts.get("privatization_regulation_art_169", {})
    if "نافذة" not in art169.get("text", ""):
        e.append("[2j] Article 169 missing expected entry-into-force clause")
    art165 = arts.get("privatization_regulation_art_165")
    if art165 is None:
        e.append("[2j] Article 165 missing entirely (known source-header colon quirk must still "
                 "yield a parsed article)")

    if src.get("decree") != "قرار مجلس إدارة المركز الوطني للتخصيص رقم (1/4/2023)":
        e.append("[2j] decree field must record the current governing (amending) decision")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this text IS the amended/"
                 "consolidated 169-article version)")
    pre = src.get("preamble_ar", "")
    if not pre or "1445" not in pre or "التخصيص" not in pre:
        e.append("[2j] preamble_ar must be present and reference the amending decision context")
    base_ref = src.get("base_law_reference", "")
    if "م/63" not in base_ref or "44" not in base_ref and "الرابعة والأربعون" not in base_ref:
        e.append("[2j] base_law_reference must cite the Privatization Law (M/63) Article 44 mandate")

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
        if r.get("renumbered_from_2021_article") != a.get("renumbered_from_2021_article"):
            e.append("[4] %s: renumbered_from_2021_article mismatch" % r["article_key"])
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
        n = int(re.match(KEY_RE, r["article_key"]).group(1))
        expected_status = (STATUS_AMENDED_DATED if r["article_key"] in AMENDED_KEYS else
                           STATUS_ADDED_DATED if r["article_key"] in ADDED_KEYS else
                           STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Privatization Regulation track:" % len(e))
        for x in e[:60]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Privatization Law (اللائحة التنفيذية لنظام التخصيص)")
    print("  - 169 records: 140 اصلية, 19 معدلة, 10 مضافة, 0 ملغاة")
    print("  - 8 أبواب; 7 divided into فصول, Book 7 (العروض التلقائية) has none (direct articles "
          "142-148); no مكرر articles")
    print("  - VERIFICATION TIER: TIER_1 for governing text -- fetched directly and live from the")
    print("    Official Gazette itself (uqn.gov.sa/details?p=24451, HTTP 200), no secondary")
    print("    aggregator, no OCR. SEPARATE reservation disclosed: amendment-diff is NOT")
    print("    exhaustive across all 169 articles (see privatization_regulation_amendment_diff_partial)")
    print("  - NCP Board Decision 1/4/2023 (18/6/1445H = 31 Dec 2023G), gazette-published")
    print("    21/7/1445H = 2 Feb 2024G, amending the original NCP Board Decision Q-9/2021")
    print("    (23/4/1443H, 159 articles); issued under Article 44 of the Privatization Law (M/63)")
    print("  - 10 articles confirmed ADDED: 66, 72, 80, 81, 82, 89, 104, 141, 155, 158")
    print("  - 19 articles confirmed AMENDED: 15, 23, 30, 32, 33, 34, 49, 64, 67, 71, 75, 76, 79,")
    print("    84, 85, 86, 87, 88, 135 (see each article's history[] for specifics)")
    print("  - DISTINCT from the Privatization Law itself, the separate 'Organizing Rules'")
    print("    (القواعد المنظمة للتخصيص, CoM Resolution 114), and the NCP's own organizational")
    print("    statute -- none of those are built in this track")
    return 0


if __name__ == "__main__":
    sys.exit(main())
