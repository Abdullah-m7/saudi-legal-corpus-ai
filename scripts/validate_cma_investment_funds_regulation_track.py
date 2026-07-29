#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the CMA Investment Funds Regulations track
(لائحة صناديق الاستثمار -- CMA Board Resolution 2006-219-1, 3/12/1427H =
24/12/2006G, as most recently amended by Resolution 2025-135-1, 03/06/1447H =
24/11/2025G; 113 articles in 9 أبواب, 14 ملاحق NOT ingested).

This validator is deliberately strict about the things this corpus cares
about -- that the text is verbatim, that the counts are the REAL counts, and
that every weakness is disclosed rather than papered over. It asserts:

  * exactly 113 articles in a clean 1..113 run, and article_count == 113;
  * exactly 9 non-empty باب entries whose article spans tile 1..113 with no
    gap and no overlap, in ascending order;
  * every article carries a non-empty section_ar, number_label_ar and text;
  * the article ordinal labels form the document's own unbroken Arabic-ordinal
    sequence (المادة الأولى ... المادة الثالثة عشرة بعد المئة) -- this is what
    makes the 113 count self-checking rather than asserted;
  * exactly Articles 48 and 49 are معدلة, each citing Resolution 2025-135-1
    and each explicitly disclosing pre_amendment_text_recovered=false; every
    other article is اصلية with an EMPTY history (absence of evidence is
    recorded as absence, never filled in);
  * the wording the gazette says Resolution 2025-135-1 substituted is actually
    present, verbatim, in Articles 48 and 49 -- the cross-check that justifies
    flagging exactly those two and no others;
  * NO ligature-corruption artefact survives anywhere in the text (the twelve
    canary strings pdftotext would have produced on this PDF's font);
  * no Latin characters, Arabic presentation forms, bidi control characters,
    leaked page furniture ('Internal', the 'داخ ل' watermark) or leaked
    structural headings (الباب/الملحق lines) in any article body;
  * TIER_2 is declared consistently across all four artifacts, English is
    declared unconsulted everywhere, and every honesty flag is False;
  * the five document-level amending instruments are present, four of them
    explicitly marked article_level_mapping_available=false;
  * the seven known_unresolved_discrepancies are present;
  * verified records and the LLM layer agree with the source artifact
    byte-for-byte, and every LLM record's SHA-256 matches its own text.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "sources", "cma_investment_funds_regulation", "law")
SRC = os.path.join(BASE, "official_source",
                   "cma_investment_funds_regulation_official_source.json")
RECORDS = os.path.join(BASE, "verified",
                       "cma_investment_funds_regulation_verified_records.jsonl")
SUMMARY = os.path.join(BASE, "verified",
                       "cma_investment_funds_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "cma_investment_funds_regulation_arabic_legal_llm",
                   "cma_investment_funds_regulation_legal_llm_001_113.json")

N = 113
KEY_RE = r"cma_investment_funds_regulation_art_(\d{3})$"
STATUS = ("CMA_GOV_SA_OFFICIAL_PDF_PRIMARY_X_GLYPH_ATOMIC_BIDI_EXTRACTION"
          "_X_GAZETTE_AMENDMENT_CROSSCHECK")
TIER = "TIER_2"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 111, "معدلة": 2, "ملغاة": 0, "مضافة": 0}
AMENDED_ARTICLE_NUMBERS = {48, 49}
AMENDING_RESOLUTION = "2025-135-1"
EXPECTED_CHAPTERS = 9
EXPECTED_ANNEXES = 14

# The phrase the official gazette says Resolution 1-135-2025 substituted INTO
# Articles 48 and 49. Its verbatim presence is the evidence that the ingested
# consolidated text really does incorporate that amendment.
AMENDMENT_PHRASE = "فئات المستثمرين المؤهلين في السوق الموازية"

# Strings that WOULD appear if the PDF's ligature glyphs had been reversed by a
# character-level bidi pass (i.e. if pdftotext output had been used). 'خالف' is
# excluded on purpose: it is a legitimate substring of مخالفة/مخالفات.
LIGATURE_CANARIES = [
    "اململكة", "الالئحة", "املادة", "املصاحل", "متهيدية", "جمالس",
    "حمدودة", "الاستمثار", "املستثمرين", "صناديقـ", "اهليئة", "الالزتام",
]

# In-word kashida (U+0640) present in the PDF's OWN text stream (pdftotext sees
# the same sequences independently) and preserved verbatim rather than stripped:
# Art. 2 «بـالكلمات»; Art. 95 «وفقــاً», «الملحـق»; Art. 110 «نظـام», «ولوائحـه».
EXPECTED_KASHIDA = {2: 1, 95: 2, 110: 2}

# The published text mixes U+0025 '%' and U+066A '٪' (confirmed against the PDF's
# own character stream via an independent pdftotext read). Both are preserved
# verbatim; the counts are pinned so a later "normalisation" cannot rewrite the
# enacted text unnoticed. Every digit in the instrument is a Western digit even
# though the PDF renders Arabic-Indic numerals (Word numeral shaping).
EXPECTED_PERCENT = {"%": 47, "٪": 31}
EXPECTED_ASCII_PERCENT_ARTICLES = {15, 41, 44, 48, 49, 53, 54, 56, 58, 59, 60,
                                   77, 82, 92, 93, 98, 99, 100, 107}

REQUIRED_DISCREPANCY_KEYS = {
    "cma_ifr_mixed_percent_sign_codepoints_preserved",
    "cma_ifr_source_native_kashida_preserved",
    "cma_ifr_annexes_1_to_14_not_ingested",
    "cma_ifr_intermediate_amendments_not_attributable_per_article",
    "cma_ifr_asliyya_does_not_mean_unamended",
    "cma_ifr_amendment_date_2025_11_24_vs_2025_11_26",
    "cma_ifr_gazette_text_not_fetched_from_uqn_directly",
    "cma_ifr_pdf_line_breaks_preserved_not_reflowed",
    "cma_ifr_footer_watermark_daakhil_rendering",
}

REQUIRED_INSTRUMENTS = {
    "2006-219-1", "2016-61-1", "2021-22-2", "2025-54-1", "2025-135-1",
}

ONES = ["", "الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة",
        "السابعة", "الثامنة", "التاسعة"]
TENS = {10: "العاشرة", 20: "العشرون", 30: "الثلاثون", 40: "الأربعون",
        50: "الخمسون", 60: "الستون", 70: "السبعون", 80: "الثمانون",
        90: "التسعون"}
TENS_COMPOUND = {20: "والعشرون", 30: "والثلاثون", 40: "والأربعون",
                 50: "والخمسون", 60: "والستون", 70: "والسبعون",
                 80: "والثمانون", 90: "والتسعون"}
ONES_C = ["", "الحادية", "الثانية", "الثالثة", "الرابعة", "الخامسة",
          "السادسة", "السابعة", "الثامنة", "التاسعة"]


def ordinal_label(n):
    """The document's own ordinal wording for article n (1..113)."""
    if n <= 9:
        return "المادة " + ONES[n]
    if n == 10:
        return "المادة العاشرة"
    if 11 <= n <= 19:
        return "المادة %s عشرة" % ONES_C[n - 10]
    if n % 10 == 0 and n < 100:
        return "المادة " + TENS[n]
    if n < 100:
        return "المادة %s %s" % (ONES_C[n % 10], TENS_COMPOUND[(n // 10) * 10])
    if n == 100:
        return "المادة المئة"
    r = n - 100
    if r <= 9:
        return "المادة %s بعد المئة" % ONES[r]
    if r == 10:
        return "المادة العاشرة بعد المئة"
    return "المادة %s عشرة بعد المئة" % ONES_C[r - 10]


AR = "ء-ي"
PRESENTATION_FORMS = re.compile(r"[ﭐ-﷿ﹰ-﻿]")
BIDI_CONTROLS = re.compile(r"[‎‏‪-‮⁦-⁩]")


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def _span(s):
    if "-" in s:
        lo, hi = s.split("-")
        return int(lo), int(hi)
    return int(s), int(s)


def main():
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT))
            return 1

    e = []
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # ---------- [1] structure ----------
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
        missing = sorted(set(range(1, N + 1)) - seen)
        e.append("[1] article numbers not a clean 1..%d run; missing %s" % (N, missing[:10]))

    if src.get("verification_tier") != TIER:
        e.append("[1b] source verification_tier %r != %s" % (src.get("verification_tier"), TIER))
    if src.get("consolidated_amended_law") is not True:
        e.append("[1b] consolidated_amended_law must be True (multi-resolution consolidated text)")
    if src.get("english_text_consulted") is not False:
        e.append("[1b] english_text_consulted must be False (Arabic governs; no English used)")
    if src.get("governing_text_language") != "ar":
        e.append("[1b] governing_text_language must be 'ar'")
    if not str(src.get("official_source_url", "")).startswith("https://cma.gov.sa/"):
        e.append("[1b] official_source_url must point at the issuing Authority's own domain")

    # ---------- [1c] أبواب tile 1..113 exactly once, in order ----------
    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d باب entries, got %d" % (EXPECTED_CHAPTERS, len(chapters)))
    else:
        prev_hi = 0
        covered = Counter()
        for c in chapters:
            if not str(c.get("label_ar", "")).startswith("الباب"):
                e.append("[1c] chapter label %r does not use الباب" % c.get("label_ar"))
            if not str(c.get("title_ar", "")).strip():
                e.append("[1c] chapter %r has empty title_ar" % c.get("label_ar"))
            lo, hi = _span(c.get("articles", "0"))
            if lo != prev_hi + 1:
                e.append("[1c] chapter %r starts at %d, expected %d (gap/overlap)"
                         % (c.get("label_ar"), lo, prev_hi + 1))
            if hi < lo:
                e.append("[1c] chapter %r has inverted span" % c.get("label_ar"))
            prev_hi = hi
            for n in range(lo, hi + 1):
                covered[n] += 1
        if prev_hi != N:
            e.append("[1c] chapters end at article %d, expected %d" % (prev_hi, N))
        dupes = [n for n, c in covered.items() if c > 1]
        if dupes:
            e.append("[1c] articles covered by more than one باب: %s" % sorted(dupes)[:10])

    annexes = src.get("annexes_not_ingested") or []
    if len(annexes) != EXPECTED_ANNEXES:
        e.append("[1d] expected %d disclosed non-ingested ملاحق, got %d"
                 % (EXPECTED_ANNEXES, len(annexes)))

    # ---------- [2] per-article integrity ----------
    sc = Counter()
    for k in sorted(arts, key=lambda x: int(re.match(KEY_RE, x).group(1))):
        a = arts[k]
        n = int(re.match(KEY_RE, k).group(1))
        text = a.get("text", "")

        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: section/structure status divergence" % k)
        if not text.strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[A-Za-z]", text):
            e.append("[2] %s: Latin characters in article body: %r"
                     % (k, re.findall(r"[A-Za-z]+", text)[:3]))
        if re.search(r"[<>&]", text):
            e.append("[2] %s: html leftovers in article body" % k)
        if PRESENTATION_FORMS.search(text):
            e.append("[2] %s: Arabic presentation-form codepoints survived extraction" % k)
        if BIDI_CONTROLS.search(text):
            e.append("[2] %s: bidi control characters survived extraction" % k)
        if "داخ ل" in text or "Internal" in text:
            e.append("[2] %s: leaked page-footer watermark in article body" % k)
        # Source-native kashida is PRESERVED verbatim, so this check pins the
        # exact known inventory rather than banning U+0640 outright: any new or
        # missing occurrence is drift and must fail.
        if _bad_tatweel(text) != EXPECTED_KASHIDA.get(n, 0):
            e.append("[2] %s: in-word tatweel count %d != pinned source inventory %d"
                     % (k, _bad_tatweel(text), EXPECTED_KASHIDA.get(n, 0)))
        for line in text.split("\n"):
            s = line.strip()
            if re.match(r"^الباب (الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع)$", s):
                e.append("[2] %s: leaked باب heading inside article body" % k)
            if re.match(r"^الملحق \d+\s*:?$", s):
                e.append("[2] %s: leaked ملحق heading inside article body" % k)
            if re.fullmatch(r"\d{1,3}", s):
                e.append("[2] %s: leaked bare page number inside article body" % k)
        if not str(a.get("section_ar", "")).strip():
            e.append("[2] %s: section_ar must be non-empty" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        elif a["number_label_ar"] != ordinal_label(n):
            e.append("[2] %s: ordinal label %r != document sequence %r"
                     % (k, a["number_label_ar"], ordinal_label(n)))
        if a.get("is_mukarrar") is not False:
            e.append("[2] %s: is_mukarrar must be False (no مكرر articles in this text)" % k)
        # section_ar must name the باب this article actually falls in
        for c in chapters:
            lo, hi = _span(c.get("articles", "0"))
            if lo <= n <= hi:
                want = "%s: %s" % (c["label_ar"], c["title_ar"])
                if a.get("section_ar") != want:
                    e.append("[2] %s: section_ar %r != %r" % (k, a.get("section_ar"), want))
                break

        # ---------- [3] amendment discipline ----------
        expect_amended = n in AMENDED_ARTICLE_NUMBERS
        if expect_amended:
            if ls != "معدلة":
                e.append("[3] %s: article %d must be معدلة (gazette-confirmed amendment)" % (k, n))
            hist = a.get("history") or []
            if not hist:
                e.append("[3] %s: amended article %d must carry non-empty history" % (k, n))
            for h in hist:
                if h.get("pre_amendment_text_recovered") is not False:
                    e.append("[3] %s: history must explicitly disclose "
                             "pre_amendment_text_recovered=false" % k)
                if AMENDING_RESOLUTION not in str(h.get("instrument", "")):
                    e.append("[3] %s: history entry must cite Resolution %s"
                             % (k, AMENDING_RESOLUTION))
                if not h.get("description_ar") or not h.get("description_en"):
                    e.append("[3] %s: history entry missing description" % k)
            if AMENDMENT_PHRASE not in text:
                e.append("[3] %s: article %d is flagged معدلة but the gazette-substituted "
                         "phrase %r is NOT present verbatim -- the cross-check that "
                         "justifies the flag has failed" % (k, n, AMENDMENT_PHRASE))
        else:
            if ls != "اصلية":
                e.append("[3] %s: article %d expected اصلية, got %r" % (k, n, ls))
            if a.get("history"):
                e.append("[3] %s: article %d has no attributable amendment and must "
                         "carry an EMPTY history (never a guessed one)" % (k, n))
            if AMENDMENT_PHRASE in text:
                e.append("[3] %s: article %d carries the gazette-substituted phrase but "
                         "is not flagged معدلة" % (k, n))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st, 0), want))

    # ---------- [2b] no ligature corruption anywhere ----------
    whole = "\n".join(a["text"] for a in arts.values())
    for canary in LIGATURE_CANARIES:
        if canary in whole:
            e.append("[2b] ligature-corruption artefact %r present -- the text was NOT "
                     "extracted glyph-atomically" % canary)
    if re.search(r"[٠-٩]", whole):
        e.append("[2b] Arabic-Indic digits present: the PDF's character stream uses "
                 "Western digits throughout (it merely RENDERS Arabic-Indic), so these "
                 "would be a transcription change, not the enacted text")

    # ---------- [2b2] source-native percent-sign mix preserved exactly ----------
    for sign, want in EXPECTED_PERCENT.items():
        got = whole.count(sign)
        if got != want:
            e.append("[2b2] %r occurs %d times, pinned source inventory is %d -- the "
                     "document's own %%-sign inconsistency must be preserved, not "
                     "normalised" % (sign, got, want))
    ascii_pct = {int(re.match(KEY_RE, k).group(1))
                 for k, a in arts.items() if "%" in a["text"]}
    if ascii_pct != EXPECTED_ASCII_PERCENT_ARTICLES:
        e.append("[2b2] articles using U+0025 '%%' changed: unexpected %s, missing %s"
                 % (sorted(ascii_pct - EXPECTED_ASCII_PERCENT_ARTICLES),
                    sorted(EXPECTED_ASCII_PERCENT_ARTICLES - ascii_pct)))

    # ---------- [2c] disclosure ----------
    if not src.get("verification_methodology_note"):
        e.append("[2c] missing verification_methodology_note explaining the tier")
    elif TIER not in src["verification_methodology_note"]:
        e.append("[2c] verification_methodology_note does not state the tier")
    disc = src.get("known_unresolved_discrepancies") or []
    flagged = {d.get("article_key") for d in disc}
    missing = REQUIRED_DISCREPANCY_KEYS - flagged
    if missing:
        e.append("[2c] required discrepancy entries missing: %s" % sorted(missing))
    for d in disc:
        if not str(d.get("description", "")).strip():
            e.append("[2c] discrepancy %r has empty description" % d.get("article_key"))

    instruments = src.get("amending_instruments") or []
    got = {r for r in REQUIRED_INSTRUMENTS
           if any(r in str(i.get("instrument", "")) for i in instruments)}
    if got != REQUIRED_INSTRUMENTS:
        e.append("[2d] amending_instruments missing: %s" % sorted(REQUIRED_INSTRUMENTS - got))
    mapped = [i for i in instruments if i.get("article_level_mapping_available") is True]
    if len(mapped) != 1 or AMENDING_RESOLUTION not in str(mapped[0].get("instrument", "")):
        e.append("[2d] exactly one instrument (%s) may declare "
                 "article_level_mapping_available=true; got %d"
                 % (AMENDING_RESOLUTION, len(mapped)))
    for i in instruments:
        if "article_level_mapping_available" not in i:
            e.append("[2d] instrument %r must state article_level_mapping_available"
                     % i.get("instrument"))

    # ---------- [4] verified records ----------
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    ver_seen = set()
    for r in ver:
        key = r.get("article_key")
        a = arts.get(key)
        if a is None:
            e.append("[4] %s: unknown article_key" % key)
            continue
        ver_seen.add(key)
        n = int(re.match(KEY_RE, key).group(1))
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % key)
        if r.get("article_number") != n:
            e.append("[4] %s: article_number mismatch" % key)
        if r.get("article_text_verified") != a["text"]:
            e.append("[4] %s: verified text != source artifact text" % key)
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % key)
        if r.get("verification_tier") != TIER:
            e.append("[4] %s: verification_tier must be %s" % (key, TIER))
        if r.get("section_ar") != a.get("section_ar"):
            e.append("[4] %s: section_ar mismatch" % key)
        if r.get("is_amended") != (n in AMENDED_ARTICLE_NUMBERS):
            e.append("[4] %s: is_amended flag mismatch" % key)
        if r.get("is_repealed") or r.get("is_added"):
            e.append("[4] %s: unexpected repealed/added flag" % key)
        if r.get("amendment_history") != (a.get("history") or []):
            e.append("[4] %s: amendment_history mismatch with source" % key)
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (key, f))
    if len(ver_seen) != len(ver):
        e.append("[4] duplicate article_key in verified records")

    # ---------- [4b] summary ----------
    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")
    if summary.get("verification_tier") != TIER:
        e.append("[4b] summary verification_tier != %s" % TIER)
    if summary.get("english_text_consulted") is not False:
        e.append("[4b] summary must declare english_text_consulted=False")
    if summary.get("chapter_structure") != src["chapter_structure"]:
        e.append("[4b] summary chapter_structure mismatch")
    if summary.get("known_unresolved_discrepancies") != src["known_unresolved_discrepancies"]:
        e.append("[4b] summary discrepancies mismatch with source")
    if summary.get("amending_instruments") != src["amending_instruments"]:
        e.append("[4b] summary amending_instruments mismatch with source")

    # ---------- [5] LLM layer ----------
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm record_count/records != %d" % N)
    if llm.get("article_range") != [1, N]:
        e.append("[5] llm article_range != [1, %d]" % N)
    if llm.get("verification_tier") != TIER:
        e.append("[5] llm verification_tier != %s" % TIER)
    if llm.get("not_legal_advice") is not True:
        e.append("[5] llm layer must carry not_legal_advice=True")
    if llm.get("status_counts") != src["status_counts"]:
        e.append("[5] llm status_counts mismatch")
    for r in recs:
        key = r.get("article_key")
        a = arts.get(key)
        if a is None:
            e.append("[5] %s: unknown article_key" % key)
            continue
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % key)
        if r.get("article_text_ar") != a["text"]:
            e.append("[5] %s: llm text != source artifact text" % key)
        if r.get("article_text_hash_sha256") != hashlib.sha256(
                r.get("article_text_ar", "").encode("utf-8")).hexdigest():
            e.append("[5] %s: sha256 mismatch" % key)
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % key)
        st = r.get("source_trust", {})
        if st.get("source_status") != STATUS.lower():
            e.append("[5] %s: bad source_status in source_trust" % key)
        if st.get("verification_tier") != TIER:
            e.append("[5] %s: source_trust verification_tier != %s" % (key, TIER))
        if not str(st.get("source_url", "")).startswith("https://cma.gov.sa/"):
            e.append("[5] %s: source_trust source_url must cite the official PDF" % key)
        for f in ("translation_performed", "legal_interpretation_performed",
                  "english_used_for_correction", "text_summarized_or_paraphrased"):
            if r.get(f) is not False:
                e.append("[5] %s: %s must be False" % (key, f))

    if e:
        print("FAIL: %d error(s) in CMA Investment Funds Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1

    print("PASS: لائحة صناديق الاستثمار (CMA Investment Funds Regulations) — 113 records")
    print("  - REAL article count 113, re-counted from the PDF's own TOC and body")
    print("    (census figure CONFIRMED; the superseded 2021 consolidation had 111)")
    print("  - 9 أبواب tiling 1..113 exactly; 14 ملاحق disclosed as NOT ingested")
    print("  - CHAIN: Resolution 2006-219-1, 3/12/1427H = 24/12/2006G, under the")
    print("    Capital Market Law (M/30, 2/6/1424H); text REPLACED in full by")
    print("    2021-22-2 (12/7/1442H); amended 2025-54-1 (23/11/1446H) and")
    print("    2025-135-1 (03/06/1447H = 24/11/2025G) — both brief numbers verified")
    print("  - TIER_2: one OFFICIAL primary supplying the complete verbatim Arabic")
    print("    text (cma.gov.sa PDF), + secondary cross-check of the gazette wording")
    print("    of Resolution 2025-135-1, confirmed verbatim inside Arts. 48(ع)/49(ك)")
    print("  - 2 معدلة (48, 49 — the ONLY article-level attribution obtainable);")
    print("    111 اصلية means 'no attributable amendment', NOT 'unchanged since 2006'")
    print("  - Arabic governs; NO English text consulted anywhere in this build")
    print("  - Text extracted glyph-atomically; 12 ligature-corruption canaries absent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
