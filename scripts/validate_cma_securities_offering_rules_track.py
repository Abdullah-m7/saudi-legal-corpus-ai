#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the CMA Rules on the Offer of Securities and
Continuing Obligations track (قواعد طرح الأوراق المالية والالتزامات المستمرة,
CMA Board Resolution 2017-123-3, 9/4/1439H, consolidated as amended by
Resolution 2026-6-3, 30/07/1447H).

VERIFICATION TIER: TIER_1 (CMA's own official Arabic PDF + the Umm Al-Qura
official gazette, two independent official publishers). See the generator's
module docstring and the source artifact's verification_methodology_note.

This validator asserts:
  * exactly 112 articles in a clean 1..112 run, no مكرر;
  * exactly 12 article-bearing Parts (أبواب) whose ranges tile 1..112 with no
    gap and no overlap, every label starting الباب, and the Chapter (فصل)
    ranges inside each Part tiling that Part;
  * every article carries a non-empty section_ar and number_label_ar, and the
    number_label_ar is the exact Arabic ordinal this instrument uses for that
    article number (recomputed here, not copied);
  * every article is اصلية with empty history -- because neither official
    source attributes the 2026 amendment to individual articles, this track
    flags none, and that refusal must not silently drift;
  * consolidated_amended_law is true and both amending_instruments entries are
    present, so "no article flagged معدلة" can never be mistaken for "never
    amended";
  * no article text is empty, contains Latin/HTML leftovers, contains a page
    footer artefact, or contains in-word decorative tatweel;
  * every disclosed discrepancy key is still present, including the ones
    recording the seven CMA-PDF-vs-gazette textual divergences, and the article
    texts still contain the exact divergent readings that were disclosed (so a
    later silent "correction" of CMA's typos fails this validator);
  * the verified JSONL, the summary and the LLM layer all agree with the source
    artifact character-for-character, and every hash matches.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = "cma_securities_offering_rules"
SRC = os.path.join(ROOT, "sources", KEY, "law", "official_source",
                   KEY + "_official_source.json")
RECORDS = os.path.join(ROOT, "sources", KEY, "law", "verified",
                       KEY + "_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", KEY, "law", "verified",
                       KEY + "_verified_summary.json")
LLM = os.path.join(ROOT, "data", KEY + "_arabic_legal_llm",
                   KEY + "_legal_llm_001_112.json")

N = 112
KEY_RE = KEY + r"_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 112, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = ("CMA_GOV_SA_OFFICIAL_PDF_PRIMARY_X_UMM_AL_QURA_OFFICIAL_GAZETTE_"
          "CROSSCHECK_X_GLYPH_LEVEL_LIGATURE_RECONSTRUCTION")
EXPECTED_PARTS = 12
DECREE = "قرار مجلس هيئة السوق المالية رقم (2017-123-3)"
DECREE_DATE_HIJRI = "9/4/1439"
AMENDING_INSTRUMENT = "قرار مجلس هيئة السوق المالية رقم (2026-6-3)"

FLAGGED_DISCREPANCY_KEYS = {
    "cma_sec_offer_no_per_article_amendment_footnotes",
    "cma_sec_offer_art_006_adawt_typo_in_cma_pdf",
    "cma_sec_offer_art_026_ashara_sanawat",
    "cma_sec_offer_art_053_malam_and_juz",
    "cma_sec_offer_art_062_missing_waw",
    "cma_sec_offer_art_065_ijraa_and_missing_space",
    "cma_sec_offer_art_034_uqn_heading_typo",
    "cma_sec_offer_art_002_date_digit_group_order",
    "cma_sec_offer_tashkeel_tounicode_imprecision",
    "cma_sec_offer_arabic_indic_numeral_shaping",
    "cma_sec_offer_annexes_not_ingested",
    "cma_sec_offer_line_breaks_are_the_pdf_own",
}

# The exact readings that this track deliberately preserves from CMA's own PDF
# instead of adopting the gazette's wording. If any of these disappears, a
# silent editorial "fix" has been made and the honesty guarantee is broken.
DISCLOSED_VERBATIM_READINGS = {
    6: "أدوت الدين",
    26: "عشرة سنوات",
    53: "مالم تكن",
    62: "السابعة والستين الثامنة والستين",
    65: "أي جراء من إجراءات",
}

ORD = {1: "الأولى", 2: "الثانية", 3: "الثالثة", 4: "الرابعة", 5: "الخامسة",
       6: "السادسة", 7: "السابعة", 8: "الثامنة", 9: "التاسعة", 10: "العاشرة",
       11: "الحادية عشرة", 12: "الثانية عشرة", 13: "الثالثة عشرة",
       14: "الرابعة عشرة", 15: "الخامسة عشرة", 16: "السادسة عشرة",
       17: "السابعة عشرة", 18: "الثامنة عشرة", 19: "التاسعة عشرة"}
UNITS = {1: "الحادية", 2: "الثانية", 3: "الثالثة", 4: "الرابعة", 5: "الخامسة",
         6: "السادسة", 7: "السابعة", 8: "الثامنة", 9: "التاسعة"}
TENS = {20: "العشرون", 30: "الثلاثون", 40: "الأربعون", 50: "الخمسون",
        60: "الستون", 70: "السبعون", 80: "الثمانون", 90: "التسعون"}
AR = "ء-ي"


def expected_label(n):
    if n <= 19:
        return "المادة " + ORD[n]
    if n < 100:
        if n % 10 == 0:
            return "المادة " + TENS[n]
        return "المادة %s و%s" % (UNITS[n % 10], TENS[n - n % 10])
    if n == 100:
        return "المادة المائة"
    return "المادة %s بعد المائة" % ORD[n - 100]


def _span(s):
    if "-" in s:
        lo, hi = s.split("-")
        return set(range(int(lo), int(hi) + 1))
    return {int(s)} if s else set()


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
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT))
            return 1

    e = []
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # ---- [1] shape ---------------------------------------------------------
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field %r != %d" % (src.get("article_count"), N))
    seen = set()
    for k in arts:
        m = re.match(KEY_RE, k)
        if not m:
            e.append("[1] %s: does not match key pattern" % k)
        else:
            seen.add(int(m.group(1)))
    if seen != set(range(1, N + 1)):
        e.append("[1] article numbers not a clean 1..%d run (missing %s)"
                 % (N, sorted(set(range(1, N + 1)) - seen)))

    # ---- [1b] citation -----------------------------------------------------
    if src.get("decree") != DECREE:
        e.append("[1b] decree %r != %r" % (src.get("decree"), DECREE))
    if src.get("decree_date_hijri") != DECREE_DATE_HIJRI:
        e.append("[1b] decree_date_hijri %r != %r"
                 % (src.get("decree_date_hijri"), DECREE_DATE_HIJRI))
    if src.get("consolidated_amended_law") is not True:
        e.append("[1b] consolidated_amended_law must be True (the ingested text is "
                 "the consolidated text as amended by Resolution 2026-6-3)")
    ai = src.get("amending_instruments") or []
    if len(ai) != 2:
        e.append("[1b] expected 2 amending_instruments entries, got %d" % len(ai))
    elif ai[1].get("instrument") != AMENDING_INSTRUMENT:
        e.append("[1b] second amending instrument %r != %r"
                 % (ai[1].get("instrument"), AMENDING_INSTRUMENT))

    # ---- [1c] Part / Chapter structure -------------------------------------
    parts = src.get("chapter_structure")
    if not parts or len(parts) != EXPECTED_PARTS:
        e.append("[1c] expected %d article-bearing Parts (أبواب), got %r"
                 % (EXPECTED_PARTS, len(parts) if parts else parts))
    else:
        covered = set()
        for c in parts:
            if not c.get("label_ar", "").startswith("الباب"):
                e.append("[1c] Part label %r does not start with الباب" % c.get("label_ar"))
            if not c.get("title_ar", "").strip():
                e.append("[1c] Part %r has empty title" % c.get("label_ar"))
            span = _span(c.get("articles", ""))
            if covered & span:
                e.append("[1c] Part %r overlaps an earlier Part" % c.get("label_ar"))
            covered |= span
            fasl = c.get("fasl") or []
            if fasl:
                fcov = set()
                for f in fasl:
                    if not f.get("label_ar", "").startswith("الفصل"):
                        e.append("[1c] Chapter label %r does not start with الفصل"
                                 % f.get("label_ar"))
                    fcov |= _span(f.get("articles", ""))
                if fcov != span:
                    e.append("[1c] Part %r: chapters cover %s but the Part spans %s"
                             % (c.get("label_ar"), sorted(fcov), sorted(span)))
        if covered != set(range(1, N + 1)):
            e.append("[1c] Parts do not tile 1..%d (missing %s)"
                     % (N, sorted(set(range(1, N + 1)) - covered)))

    if not src.get("annexes_not_ingested"):
        e.append("[1d] missing annexes_not_ingested disclosure (Part 13 is not ingested)")

    # ---- [2] per-article integrity -----------------------------------------
    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        text = a.get("text", "")
        if not text.strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[A-Za-z<>&]", text):
            e.append("[2] %s: latin/html leftovers in article text" % k)
        if "Internal" in text or re.search(r"^\s*\d{1,3}\s*$", text, re.M):
            e.append("[2] %s: page header/footer artefact leaked into article text" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: section_ar must be non-empty" % k)
        if _bad_tatweel(text):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("number_label_ar") != expected_label(n):
            e.append("[2] %s: number_label_ar %r != expected %r"
                     % (k, a.get("number_label_ar"), expected_label(n)))
        if a.get("is_mukarrar") is not False:
            e.append("[2] %s: this instrument has no مكرر article" % k)
        if not a.get("article_title_ar", "").strip():
            e.append("[2] %s: article_title_ar must be non-empty (every article of "
                     "this instrument is titled)" % k)
        # [3] no article may claim an amendment this track cannot evidence
        if ls != "اصلية":
            e.append("[3] %s: article %d must be اصلية -- neither official source "
                     "attributes the 2026 amendment to individual articles" % (k, n))
        if a.get("history"):
            e.append("[3] %s: article %d must carry empty history" % (k, n))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    if src.get("status_counts") != EXPECTED_COUNTS:
        e.append("[2] status_counts %r != %r" % (src.get("status_counts"), EXPECTED_COUNTS))

    # ---- [2d] disclosure -----------------------------------------------------
    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    elif "TIER 1" not in src["verification_methodology_note"]:
        e.append("[2d] verification_methodology_note must state the tier explicitly")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))
        for d in disc:
            if not d.get("description", "").strip():
                e.append("[2e] discrepancy %r has empty description" % d.get("article_key"))

    # ---- [2f] the disclosed verbatim readings must still be there ------------
    for n, needle in DISCLOSED_VERBATIM_READINGS.items():
        k = "%s_art_%03d" % (KEY, n)
        a = arts.get(k)
        if a is None:
            continue
        flat = re.sub(r"\s+", " ", a["text"])
        if needle not in flat:
            e.append("[2f] article %d no longer contains the disclosed verbatim CMA "
                     "reading %r -- a silent editorial correction has been made" % (n, needle))

    # ---- [4] verified records ----------------------------------------------
    ver = [json.loads(line) for line in open(RECORDS, encoding="utf-8") if line.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: unknown article_key" % r["article_key"])
            continue
        if r.get("law_component") != "rules":
            e.append("[4] %s: law_component must be 'rules', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[4] %s: missing article_number field" % r["article_key"])
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("is_amended") or r.get("is_repealed") or r.get("is_added"):
            e.append("[4] %s: unexpected amended/repealed/added flag" % r["article_key"])
        if not r.get("governing_source_note"):
            e.append("[4] %s: missing governing_source_note" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")
    if summary.get("verification_tier") != "TIER_1":
        e.append("[4b] summary must declare verification_tier TIER_1")
    if summary.get("known_unresolved_discrepancies") != src["known_unresolved_discrepancies"]:
        e.append("[4b] summary discrepancy list drifted from the source artifact")

    # ---- [5] LLM layer ------------------------------------------------------
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("article_range") != [1, N]:
        e.append("[5] llm article_range != [1, %d]" % N)
    if llm.get("verification_tier") != "TIER_1":
        e.append("[5] llm layer must declare verification_tier TIER_1")
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: unknown article_key" % r["article_key"])
            continue
        if r.get("law_component") != "rules":
            e.append("[5] %s: law_component must be 'rules', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[5] %s: missing article_number field" % r["article_key"])
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust"
                     % r["article_key"])
        if r.get("governing_text_language") != "ar":
            e.append("[5] %s: governing_text_language must be 'ar'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in CMA Securities Offering Rules track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: قواعد طرح الأوراق المالية والالتزامات المستمرة — 112 records "
          "(112 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 12 أبواب tiling 1..112)")
    print("  - TIER_1: CMA's own official Arabic PDF (cma.gov.sa) + the Umm Al-Qura")
    print("    official gazette (uqn.gov.sa) — two independent official publishers;")
    print("    105/112 articles word-identical between them after normalisation")
    print("  - CITATION: CMA Board Resolution 2017-123-3, 9/4/1439H (27/12/2017G),")
    print("    under the Capital Market Law (M/30, 2/6/1424H); consolidated as")
    print("    amended by Resolution 2026-6-3, 30/07/1447H (19/01/2026G)")
    print("  - ARTICLE COUNT 112 verified from the document itself (TOC + body")
    print("    headings + gazette), not assumed from the census")
    print("  - NO article flagged معدلة: neither official source attributes the 2026")
    print("    amendment to individual articles, and this track refuses to guess")
    print("  - 7 CMA-PDF-vs-gazette textual divergences preserved verbatim and")
    print("    disclosed; 38 annexes (Part 13, pages 99-296) NOT ingested")
    return 0


if __name__ == "__main__":
    sys.exit(main())
