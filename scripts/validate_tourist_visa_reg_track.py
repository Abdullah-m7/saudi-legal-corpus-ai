#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Regulation of the Tourist Visit Visa track
(لائحة تأشيرة الزيارة لغرض السياحة).

13 records: flat statute (المادة الأولى .. الثالثة عشرة), NO chapters,
NO appendix. All 13 اصلية.

VERIFICATION TIER: TIER_2 -- unlike three sibling tracks in this batch,
the official PDF does NOT embed a scanned signed-decision-letter page;
the decision number/date is printed only on the cover page. See the
generator docstring and the official_source JSON's
verification_methodology_note. This validator only checks internal
self-consistency of the ingested text and that every discrepancy is
disclosed.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "tourist_visa",
                   "official_source",
                   "tourist_visa_reg_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "tourist_visa",
                       "verified",
                       "tourist_visa_reg_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "tourist_visa",
                       "verified",
                       "tourist_visa_reg_verified_summary.json")
LLM = os.path.join(ROOT, "data",
                   "tourist_visa_reg_arabic_legal_llm",
                   "tourist_visa_reg_legal_llm_001_013.json")

N_ARTICLES = 13
N_RECORDS = 13
ART_RE = r"tourist_visa_reg_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 13, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

FLAGGED_DISCREPANCY_KEYS = {
    "tourist_visa_reg_argaam_batch_confirmed",
    "tourist_visa_reg_no_signed_letter_page",
    "tourist_visa_reg_gazette_date_unconfirmed",
}
AR = "ء-ي"
TASHKEEL = re.compile("[ً-ٰٟ]")  # excludes Arabic-Indic digits U+0660-0669


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
    if len(arts) != N_RECORDS:
        e.append("[1] %d records != %d" % (len(arts), N_RECORDS))
    if src.get("article_count") != N_ARTICLES:
        e.append("[1] article_count field != %d" % N_ARTICLES)
    if src.get("appendix_count") != 0:
        e.append("[1] appendix_count field must be 0 (flat statute, no appendix)")
    if src.get("record_count") != N_RECORDS:
        e.append("[1] record_count field != %d" % N_RECORDS)

    art_nums = []
    for k, a in arts.items():
        ma = re.match(ART_RE, k)
        if ma:
            art_nums.append(int(ma.group(1)))
            if a.get("is_appendix") is not False:
                e.append("[1] %s: article key must have is_appendix False" % k)
        else:
            e.append("[1] %s: does not match article key pattern" % k)
    if sorted(art_nums) != list(range(1, N_ARTICLES + 1)):
        e.append("[1] article numbers not 1..%d: %s" % (N_ARTICLES, sorted(art_nums)))

    # [1c] FLAT statute: chapter_structure MUST be empty (no chapters/فصول)
    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1c] this statute is flat (no chapters); chapter_structure must be [] but is %r" % chs)

    # [2] per-record content + status
    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != "MATCHES_PDF":
            e.append("[2] %s: expected status MATCHES_PDF, got %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: structure_status divergence" % k)
        if ls != "اصلية":
            e.append("[2] %s: all records must be اصلية, got %r" % (k, ls))
        if a.get("history"):
            e.append("[2] %s: article-level history must be empty" % k)
        t = a.get("text", "")
        if not t.strip():
            e.append("[2] %s: empty text" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if TASHKEEL.search(t):
            e.append("[2] %s: residual tashkeel (should be stripped uniformly)" % k)
        if _bad_tatweel(t):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "\xa0" in t:
            e.append("[2f] %s: residual non-breaking-space artifact" % k)
        if "​" in t or "‏" in t or "‎" in t:
            e.append("[2f] %s: residual zero-width/bidi artifact" % k)
        if "“" in t or "”" in t:
            e.append("[2f] %s: residual curly-quote artifact" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st, 0), want))

    # [2d] methodology + discrepancies
    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    # [2j] anchor facts
    if src.get("decree") != "القرار الوزاري رقم (2344)" \
            or src.get("decree_date_hijri") != "19/5/1444":
        e.append("[2j] decree/decree_date_hijri mismatch with verified 2344, 19/5/1444H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("base_law_track") != "tourism_law":
        e.append("[2j] base_law_track must be 'tourism_law'")
    if "م/18" not in src.get("legal_basis_ar", "") and "م\\/18" not in src.get("legal_basis_ar", ""):
        e.append("[2j] legal_basis_ar must cite the founding Royal Decree M/18")

    art9 = arts.get("tourist_visa_reg_art_009", {})
    if "300" not in art9.get("text", ""):
        e.append("[2j] Article 9 must state the 300-riyal visa fee")

    # [4] verified records
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_RECORDS:
        e.append("[4] %d verified records != %d" % (len(ver), N_RECORDS))
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
    if summary.get("record_count") != N_RECORDS:
        e.append("[4b] summary record_count != %d" % N_RECORDS)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")

    # [5] LLM layer
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_RECORDS or len(recs) != N_RECORDS:
        e.append("[5] llm count != %d" % N_RECORDS)
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
        if r.get("text_summarized_or_paraphrased") is not False:
            e.append("[5] %s: text_summarized_or_paraphrased must be False" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Regulation of the Tourist Visit Visa track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Regulation of the Tourist Visit Visa")
    print("  - 13 records: flat statute, NO chapters, NO appendix; all 13 اصلية")
    print("  - Founding: Ministerial Decision (2344), 19/5/1444H, printed on cover page")
    print("    (no signed decision letter embedded, unlike three sibling tracks)")
    print("  - VERIFICATION TIER: TIER_2 — official PDF, but no primary signed-document")
    print("    capture; founding Royal Decree citation (M/18, 26/1/1444H) matches this")
    print("    corpus's own tourism_law track")
    return 0


if __name__ == "__main__":
    sys.exit(main())
