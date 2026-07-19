#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Arabian VAT
Law track (82 records: 37 اصلية, 42 معدلة, 3 مضافة, 0 ملغاة; 12 chapters; three
"mukarrar" articles added by later amendments -- 32-mukarrar, 36-mukarrar,
36-mukarrar-2).

VERIFICATION TIER -- see the generator's module docstring and
sources/vat/regulation/official_source/vat_regulation_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa was checked
first (per this corpus's standard methodology) but has no dedicated lawId page
for this Implementing Regulation at all. The PRIMARY source is zatca.gov.sa (the
issuing Authority's own official consolidated PDF, the "Tenth Edition" of April
2025, a born-digital file), whose current consolidated text was extracted via
two independent pipelines (PyMuPDF character-geometric reconstruction +
Tesseract Arabic OCR of 300dpi renders) reconciled together. This validator does
not re-adjudicate provenance; it only checks internal self-consistency of the
text this track ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "vat", "regulation", "official_source",
                   "vat_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "vat", "regulation", "verified",
                       "vat_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "vat", "regulation", "verified",
                       "vat_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "vat_regulation_arabic_legal_llm",
                   "vat_regulation_legal_llm_001_082.json")
N = 82
BASE_MAX = 79
KEY_RE = r"vat_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 37, "معدلة": 42, "ملغاة": 0, "مضافة": 3}
EXPECTED_TOP_LEVEL_CHAPTERS = 12
VERIF_CONST = "ZATCA_OFFICIAL_PDF_TENTH_EDITION_OCR_X_EMBEDDED_RECONCILED"
MUKARRAR_KEYS = {"vat_regulation_art_032_mukarrar",
                 "vat_regulation_art_036_mukarrar",
                 "vat_regulation_art_036_mukarrar2"}
FLAGGED_DISCREPANCY_KEYS = {
    "vat_regulation_decree_date_gregorian_anomaly",
    "vat_regulation_boe_no_dedicated_page",
    "vat_regulation_text_extraction_residual_artifacts",
    "vat_regulation_per_article_amendment_attribution",
    "vat_regulation_edition_currency_boundary",
    "vat_regulation_no_preamble_extracted",
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


def _base_num(key):
    return int(re.match(KEY_RE, key).group(1))


def _iter_chapter_ranges(chs):
    for ch in chs:
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        yield (lo, hi)


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

    # mukarrar keys exactly
    got_muk = {k for k in arts if "_mukarrar" in k}
    if got_muk != MUKARRAR_KEYS:
        e.append("[1m] mukarrar key set mismatch: %s" % sorted(got_muk))

    chs = src.get("chapter_structure") or []
    if len(chs) != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, len(chs)))
    # base article numbers 1..79 covered exactly once by chapter ranges
    covered = []
    for lo, hi in _iter_chapter_ranges(chs):
        covered.extend(range(lo, hi + 1))
    cc = Counter(covered)
    dupes = [n for n, c in cc.items() if c > 1]
    if dupes:
        e.append("[1c] base article(s) in more than one chapter range: %s" % dupes[:20])
    if set(cc) != set(range(1, BASE_MAX + 1)):
        miss = sorted(set(range(1, BASE_MAX + 1)) - set(cc))
        extra = sorted(set(cc) - set(range(1, BASE_MAX + 1)))
        if miss:
            e.append("[1c] chapter_structure missing base article(s): %s" % miss[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])
    # every article (incl. mukarrar) must have a section_ar naming a real chapter
    chap_titles = {c["title_ar"] for c in chs}
    for k, a in arts.items():
        sec = a.get("section_ar") or ""
        if not any(t in sec for t in chap_titles):
            e.append("[1s] %s: section_ar does not name a known chapter" % k)

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: structure/section status divergence" % k)
        if a.get("status") != VERIF_CONST:
            e.append("[2] %s: verification status %r != %r" % (k, a.get("status"), VERIF_CONST))
        t = a.get("text", "")
        if not t.strip() or re.search(r"[A-Za-z<>&]", t):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if _bad_tatweel(t):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if re.search(r"[ؐ-ًؚ-ٰٟ]", t):
            e.append("[2] %s: residual tashkeel present (should be stripped)" % k)
        if "\xa0" in t:
            e.append("[2f] %s: residual non-breaking-space artifact" % k)
        if "“" in t or "”" in t:
            e.append("[2f] %s: residual curly-quote artifact" % k)
        if "  " in t:
            e.append("[2f] %s: residual double-space artifact" % k)
        # amendment/added <-> history <-> mukarrar consistency
        is_amended = (ls == "معدلة")
        is_added = (ls == "مضافة")
        if (is_amended or is_added) and not a.get("history"):
            e.append("[2] %s: amended/added article missing history" % k)
        if not (is_amended or is_added) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if (k in MUKARRAR_KEYS) and ls != "مضافة":
            e.append("[2] %s: mukarrar article must be legal_status مضافة" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    if src.get("status_counts") != EXPECTED_COUNTS:
        e.append("[2] top-level status_counts != expected")

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
        # the date anomaly entry must record both the wrong printed date and the corrected one
        da = next((d["description"] for d in disc
                   if d["article_key"] == "vat_regulation_decree_date_gregorian_anomaly"), "")
        if "نوفمبر 2016" not in da or "5 سبتمبر 2017" not in da:
            e.append("[2e] date-anomaly discrepancy must cite both the printed '14 نوفمبر 2016م' "
                     "error and the corrected '5 سبتمبر 2017م'")

    # amendment_history: founding + 11 amendments = 12 entries, referencing key decrees
    ah = src.get("amendment_history") or []
    if len(ah) != 12:
        e.append("[2k] amendment_history must have 12 entries (founding + 11 amendments), got %d"
                 % len(ah))
    decrees = " ".join(str(h.get("decree", "")) for h in ah)
    if "3839" not in decrees:
        e.append("[2k] amendment_history must reference founding decree 3839")
    if "01-06-24" not in decrees and "24-06-01" not in decrees:
        e.append("[2k] amendment_history must reference the latest amendment (2024)")

    if src.get("decree") != "قرار مجلس إدارة الهيئة العامة للزكاة والدخل رقم (3839)" \
            or src.get("decree_date_hijri") != "14/12/1438":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Resolution 3839, 14/12/1438")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True")
    if "preamble_ar" in src:
        e.append("[2j] preamble_ar should be ABSENT (not recovered; see "
                 "known_unresolved_discrepancies) rather than a fabricated placeholder")

    # spot-checks anchoring key facts established this pass
    a1 = arts.get("vat_regulation_art_001", {})
    if "الاتفاقية" not in a1.get("text", "") or "المعاني" not in a1.get("text", ""):
        e.append("[2j] Article 1 (التعريفات) missing expected definitional wording")
    a32m = arts.get("vat_regulation_art_032_mukarrar", {})
    if "تعليق الضريبة" not in a32m.get("text", ""):
        e.append("[2j] Article 32-mukarrar missing expected 'تعليق الضريبة' content")
    if arts.get("vat_regulation_art_032_mukarrar", {}).get("legal_status_ar") != "مضافة":
        e.append("[2j] Article 32-mukarrar must be مضافة")

    # verified records
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        exp = {"معدلة": "AMENDED", "مضافة": "ADDED"}.get(a["legal_status_ar"], "UNCHANGED")
        if r.get("official_text_status") != exp:
            e.append("[4] %s: official_text_status %r != %r" % (r["article_key"],
                     r.get("official_text_status"), exp))
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
            e.append("[5] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm source_status mismatch" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in VAT Regulation track:" % len(e))
        for x in e[:50]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Arabian VAT Law")
    print("  - 82 records: 37 اصلية, 42 معدلة, 3 مضافة, 0 ملغاة (79 numbered articles + 3 mukarrar)")
    print("  - 12 chapters; base articles 1-79 covered exactly once")
    print("  - VERIFICATION TIER: laws.boe.gov.sa checked first but has NO dedicated lawId page for")
    print("    this Implementing Regulation; PRIMARY source is zatca.gov.sa (issuing Authority's")
    print("    own consolidated 'Tenth Edition', April 2025), extracted via two independent")
    print("    pipelines (PyMuPDF character-geometric reconstruction + Tesseract Arabic OCR)")
    print("    reconciled -- see verification_methodology_note for disclosed residual artifacts")
    print("  - Resolution (3839), 14 Dhul-Hijjah 1438H = 5 Sep 2017G (ZATCA's own PDF misprints")
    print("    the Gregorian as '14 نوفمبر 2016م' -- resolved and disclosed, not silently corrected)")
    print("  - Consolidates founding Resolution 3839 + 11 amending Board resolutions through")
    print("    Resolution (01-06-24), 19 Nov 2024G (all 12 in amendment_history)")
    print("  - 3 مضافة articles are the mukarrar articles (32-mukarrar, 36-mukarrar, 36-mukarrar-2);")
    print("    42 معدلة derived from the source's own inline amendment footnotes + its 'ما طرأ على")
    print("    اللائحة' section (article-level, with disclosed attribution uncertainty)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
