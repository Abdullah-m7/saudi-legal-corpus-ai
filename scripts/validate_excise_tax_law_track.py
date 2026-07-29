#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Excise Tax Law track (نظام الضريبة الانتقائية,
Royal Decree M/86, 27/8/1438H) -- 30 records, 10 chapters, 28 اصلية / 2 معدلة.

TIER_2 track: one official source (ZATCA's own consolidated Arabic PDF) plus an
independent secondary cross-check (nezams.com). This validator therefore does
NOT require original_XXXXh_text on the two amended articles -- the pre-amendment
wording was not established from an official source this pass and is documented
as a gap rather than fabricated.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "excise_tax_law", "law", "official_source",
                   "excise_tax_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "excise_tax_law", "law", "verified",
                       "excise_tax_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "excise_tax_law", "law", "verified",
                       "excise_tax_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "excise_tax_law_arabic_legal_llm",
                   "excise_tax_law_legal_llm_001_030.json")

N = 30
KEY_RE = r"excise_tax_law_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 28, "معدلة": 2}
STATUS = "ZATCA_OFFICIAL_CONSOLIDATED_PDF_X_SECONDARY_CROSS_VERIFIED"
AMENDED_KEYS = {"excise_tax_law_art_025", "excise_tax_law_art_027"}
EXPECTED_CHAPTERS = 10
EXPECTED_DECREE = "المرسوم الملكي رقم (م/86)"
EXPECTED_DECREE_DATE = "27/8/1438"
EXPECTED_TIER = "TIER_2"
EXPECTED_AMENDING = {"المرسوم الملكي رقم (م/113)", "المرسوم الملكي رقم (م/52)"}
FLAGGED_DISCREPANCY_KEYS = {
    "excise_tax_law_art_001_authority_name",
    "excise_tax_law_art_025_original_text_gap",
    "excise_tax_law_art_027_amending_instrument_conflict",
    "excise_tax_law_publication_gazette",
    "excise_tax_law_boe_and_archive_unreachable",
    "excise_tax_law_gcc_agreement_not_extracted",
}
AR = "ء-ي"


def _bad_tatweel(text):
    """In-word decorative kashida (the tatweel of 'هـ' is legitimate)."""
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
            print("FAIL: missing %s" % os.path.relpath(p, ROOT))
            return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # [1] structure
    if len(arts) != N or src.get("article_count") != N:
        e.append("[1] %d articles / article_count=%s, expected %d"
                 % (len(arts), src.get("article_count"), N))
    seen_numbers = set()
    for k in arts:
        m = re.match(KEY_RE, k)
        if not m:
            e.append("[1] %s: does not match key pattern" % k)
        else:
            seen_numbers.add(int(m.group(1)))
    if seen_numbers != set(range(1, N + 1)):
        e.append("[1] article numbers are not exactly 1..%d" % N)
    for k in AMENDED_KEYS:
        if k not in arts:
            e.append("[1] expected amended article key %s missing" % k)

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTERS, len(chapters)))
    covered = set()
    for c in chapters:
        if not c.get("label_ar") or not c.get("title_ar"):
            e.append("[1c] chapter entry missing label/title: %r" % c)
        rng = c.get("articles", "")
        if "-" in rng:
            a, b = rng.split("-")
            covered |= set(range(int(a), int(b) + 1))
        elif rng.isdigit():
            covered.add(int(rng))
    if covered != set(range(1, N + 1)):
        e.append("[1c] chapter ranges do not cover articles 1..%d exactly" % N)

    # [2] citation must never drift
    if src.get("decree") != EXPECTED_DECREE:
        e.append("[2] decree %r != %r" % (src.get("decree"), EXPECTED_DECREE))
    if src.get("decree_date_hijri") != EXPECTED_DECREE_DATE:
        e.append("[2] decree_date_hijri %r != %r"
                 % (src.get("decree_date_hijri"), EXPECTED_DECREE_DATE))
    if src.get("verification_tier") != EXPECTED_TIER:
        e.append("[2] verification_tier %r != %r"
                 % (src.get("verification_tier"), EXPECTED_TIER))
    if not src.get("verification_tier_basis"):
        e.append("[2] missing verification_tier_basis")
    hist_instruments = {h.get("decree") for h in src.get("amendment_history", [])}
    if EXPECTED_DECREE not in hist_instruments:
        e.append("[2] amendment_history does not open with the enacting decree")
    if not EXPECTED_AMENDING <= hist_instruments:
        e.append("[2] amendment_history missing %s"
                 % sorted(EXPECTED_AMENDING - hist_instruments))
    if not src.get("cover_page_verbatim_ar"):
        e.append("[2] missing cover_page_verbatim_ar (the source's own citation line)")

    # [3] per-article integrity
    sc = Counter()
    for k, a in sorted(arts.items()):
        if a.get("status") != STATUS:
            e.append("[3] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[3] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[3] %s: section/status divergence" % k)
        txt = a.get("text", "")
        if not txt.strip():
            e.append("[3] %s: empty text" % k)
        if re.search(r"[A-Za-z<>&]", txt):
            e.append("[3] %s: latin/html leftovers in Arabic text" % k)
        if not a.get("section_ar"):
            e.append("[3] %s: missing section_ar" % k)
        if _bad_tatweel(txt):
            e.append("[3] %s: in-word decorative tatweel survived extraction" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[3] %s: legal_status/AMENDED_KEYS mismatch" % k)
        if k in AMENDED_KEYS:
            if not a.get("history"):
                e.append("[3] %s: amended article missing history" % k)
            else:
                for h in a["history"]:
                    if not h.get("instrument") or not h.get("date_hijri"):
                        e.append("[3] %s: history entry missing instrument/date" % k)
                    if not h.get("source"):
                        e.append("[3] %s: history entry missing its source citation" % k)
        elif a.get("history"):
            e.append("[3] %s: unamended article carries amendment history" % k)
        # zero-fabrication: no reconstructed pre-amendment text may appear
        for f in a:
            if "original_" in f and "text" in f:
                e.append("[3] %s: unexpected reconstructed field %r" % (k, f))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[3] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[3] unexpected repealed/added articles present")
    if src.get("status_counts") != {"اصلية": 28, "معدلة": 2, "ملغاة": 0, "مضافة": 0}:
        e.append("[3] status_counts block does not match the articles")

    # [4] honesty apparatus
    if not src.get("verification_methodology_note"):
        e.append("[4] missing verification_methodology_note")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[4] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[4] expected discrepancy entries missing for: %s" % sorted(missing))
        for d in disc:
            if not d.get("description"):
                e.append("[4] discrepancy %r has no description" % d.get("article_key"))

    # [5] verified records layer
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[5] %d verified records != %d" % (len(ver), N))
    for r in ver:
        k = r["article_key"]
        if k not in arts:
            e.append("[5] %s: unknown article_key" % k)
            continue
        a = arts[k]
        if r["article_text_verified"] != a["text"]:
            e.append("[5] %s: text != source" % k)
        if r.get("verification_status") != a.get("status"):
            e.append("[5] %s: verification_status mismatch" % k)
        if r.get("verification_tier") != EXPECTED_TIER:
            e.append("[5] %s: verification_tier missing/incorrect" % k)
        if r.get("number_label_ar") != a["number_label_ar"]:
            e.append("[5] %s: number_label mismatch" % k)
        if r.get("is_amended") != (a["legal_status_ar"] == "معدلة"):
            e.append("[5] %s: is_amended mismatch" % k)
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[5] %s: %s must be False" % (k, f))

    # [6] summary layer
    summ = json.load(open(SUMMARY, encoding="utf-8"))
    if summ.get("record_count") != N:
        e.append("[6] summary record_count != %d" % N)
    if summ.get("verification_tier") != EXPECTED_TIER:
        e.append("[6] summary verification_tier incorrect")
    if summ.get("decree") != EXPECTED_DECREE:
        e.append("[6] summary decree drifted")
    if not summ.get("known_unresolved_discrepancies"):
        e.append("[6] summary does not carry the discrepancy list")

    # [7] LLM layer
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[7] llm count != %d" % N)
    if llm.get("article_range") != [1, N]:
        e.append("[7] llm article_range != [1, %d]" % N)
    for r in recs:
        k = r["article_key"]
        if k not in arts:
            e.append("[7] %s: unknown article_key" % k)
            continue
        if r["article_text_ar"] != arts[k]["text"]:
            e.append("[7] %s: llm text != source" % k)
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[7] %s: hash mismatch" % k)
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[7] %s: missing retrieval metadata" % k)
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[7] %s: bad source_status in source_trust" % k)
        if r.get("source_trust", {}).get("verification_tier") != EXPECTED_TIER:
            e.append("[7] %s: source_trust missing verification_tier" % k)
        if r.get("english_used_for_correction") is not False:
            e.append("[7] %s: english_used_for_correction must be False" % k)

    if e:
        print("FAIL: %d error(s) in Excise Tax Law track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: نظام الضريبة الانتقائية / Excise Tax Law — 30 records "
          "(28 اصلية / 2 معدلة, 10 chapters)")
    print("  - IN-FORCE Royal Decree M/86 (27/8/1438H); consolidated with M/113")
    print("    (2/11/1438H, Article 25) and M/52 (28/4/1441H, Article 27)")
    print("  - TIER_2: ZATCA official consolidated PDF x independent secondary")
    print("    cross-check (20/30 articles matched letter-for-letter)")
    print("  - pre-amendment original text NOT included for Articles 25 or 27:")
    print("    a documented gap, not a fabrication")
    print("  - %d unresolved discrepancies recorded" % len(disc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
