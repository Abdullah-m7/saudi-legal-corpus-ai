#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Finance
Companies Control Law track (106 records, all اصلية as currently-governing
text; 22 أبواب, one -- الباب الحادي عشر -- subdivided into 3 فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/finance_companies_regulation/law/official_source/
finance_companies_regulation_official_source.json's verification_methodology_note
for the full account: full text fetched directly (HTTP 200) from bfc.gov.sa;
the PDF is a pure image scan with no text layer, transcribed by directly
reading rendered page images. The PDF's own creation-date metadata (22 Dec
2025) and its first page (a SAMA circular) confirm this is the Dec-2025
consolidated re-issuance (Governor's Decision 179/M SH T), cross-verified
against five independent secondary sources. consolidated_amended_law=True:
no prior text was available this pass for an article-level amendment diff,
so no individual article is tagged معدلة/مضافة -- a disclosed constraint,
not a fabricated negative. This validator does not re-adjudicate any of
this; it only checks internal self-consistency of the text this track
ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "finance_companies_regulation", "law", "official_source",
                   "finance_companies_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "finance_companies_regulation", "law", "verified",
                       "finance_companies_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "finance_companies_regulation", "law", "verified",
                       "finance_companies_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "finance_companies_regulation_arabic_legal_llm",
                   "finance_companies_regulation_legal_llm_001_106.json")
N = 106
KEY_RE = r"finance_companies_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 106, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_PARTS = 22  # 22 أبواب

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {}
FLAGGED_DISCREPANCY_KEYS = {
    "finance_companies_regulation_no_prior_version_for_article_level_diff",
    "finance_companies_regulation_decision_number_179_confirmed_via_secondary_sources",
    "finance_companies_regulation_sama_own_pdf_and_rulebook_unreachable_this_pass",
    "finance_companies_regulation_annual_percentage_rate_formula_transcription",
    "finance_companies_regulation_roman_numeral_sub_items_article_60",
    "finance_companies_regulation_repealed_companion_rules_not_ingested",
    "finance_companies_regulation_no_boe_cross_check_this_pass",
}
# Article 60 §6 genuinely prints lowercase Roman-numeral sub-items ("i.", "ii.")
# in the source PDF (confirmed by direct visual inspection of the rendered
# page image); Article 85 genuinely prints a mathematical APR formula whose
# variable names are Latin letters (Cd, Sd, Bp, tp, X, m, n, d, p -- see
# known_unresolved_discrepancies for the transcription-fidelity caveat on the
# formula's exact visual layout). These are the only legitimate exceptions to
# the "no Latin characters in article body" check below.
LATIN_ALLOWED_CHARS_BY_KEY = {
    "finance_companies_regulation_art_060": set("i"),
    "finance_companies_regulation_art_085": set("BCSXdmnpst"),
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def _iter_part_ranges(chs):
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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_PARTS:
        e.append("[1c] expected %d parts (أبواب), got %d" % (EXPECTED_TOP_LEVEL_PARTS, n_top))

    covered = set()
    for lo, hi in _iter_part_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one part range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    titles = [c.get("title_ar") for c in chs]
    if len(set(titles)) != len(titles):
        e.append("[1d] unexpected duplicate part title(s): %s"
                 % [t for t in titles if titles.count(t) > 1])

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
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        latin_hits = re.findall(r"[A-Za-z<>&]", a["text"])
        if latin_hits:
            allowed = LATIN_ALLOWED_CHARS_BY_KEY.get(k)
            if allowed is None:
                e.append("[2] %s: latin/html leftovers" % k)
            elif set(latin_hits) - allowed:
                e.append("[2] %s: unexpected latin/html leftovers beyond the known "
                         "allowed characters for this article" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (this law's source supplies no "
                     "inline per-article titles -- section_ar carries the part/chapter title)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected (should be normalized "
                     "to straight quotes)" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

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
        e.append("[2k] missing amendment_history (must record founding decision + latest amendment)")
    elif len(src["amendment_history"]) < 2:
        e.append("[2k] amendment_history must record both the 1434H founding decision and the "
                 "179/M SH T (2025) amendment")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("finance_companies_regulation_art_001", {})
    if "شركة الدفع الآجل" not in art1.get("text", "") or "التمويل الجماعي بالدين" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected Dec-2025-era definitions (شركة الدفع الآجل / "
                 "التمويل الجماعي بالدين) confirming the consolidated post-amendment text")
    art8 = arts.get("finance_companies_regulation_art_008", {})
    if "٢٠٠,٠٠٠,٠٠٠" not in art8.get("text", ""):
        e.append("[2j] Article 8 missing expected minimum-capital figures")
    art9 = arts.get("finance_companies_regulation_art_009", {})
    if "التمويل الاستهلاكي المصغر" not in art9.get("text", ""):
        e.append("[2j] Article 9 missing expected micro consumer finance activity rules")
    art60 = arts.get("finance_companies_regulation_art_060", {})
    if "طرفاً ذا علاقة" not in art60.get("text", "") and "ذا علاقة" not in art60.get("text", ""):
        e.append("[2j] Article 60 missing expected related-party definition")
    art85 = arts.get("finance_companies_regulation_art_085", {})
    if "معدل النسبة السنوي" not in art85.get("text", ""):
        e.append("[2j] Article 85 missing expected APR-calculation content")
    art106 = arts.get("finance_companies_regulation_art_106", {})
    if "الجريدة الرسمية" not in art106.get("text", ""):
        e.append("[2j] Article 106 missing expected official-gazette publication clause")

    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this is a confirmed Dec-2025 "
                 "post-amendment consolidated re-issuance)")

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
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation' not %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[4] %s: missing article_number field" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("consolidated_amended_law") is not True:
        e.append("[4b] summary consolidated_amended_law must be True")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("law_component") != "regulation":
        e.append("[5] llm-file top-level law_component must be 'regulation' not %r" % llm.get("law_component"))
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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: llm record law_component must be 'regulation' not %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[5] %s: llm record missing article_number field" % r["article_key"])
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Finance Companies Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Finance Companies Control Law")
    print("  - 106 records: 106 اصلية (currently-governing text), 0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - 22 parts (أبواب), continuous 1-106; الباب الحادي عشر subdivided into 3 فصول")
    print("  - VERIFICATION TIER: primary source, direct fetch succeeded (HTTP 200 from")
    print("    bfc.gov.sa). Pure image-scanned PDF; every article transcribed from rendered")
    print("    page images (200dpi), avoiding any OCR guess or character-substitution error")
    print("  - Dec-2025 consolidated re-issuance CONFIRMED via the PDF's own creation-date")
    print("    metadata + its own first-page SAMA circular (472038006, 2/7/1447H), cross-")
    print("    verified against 5 independent secondary sources (Governor's Decision 179/M SH T)")
    print("  - consolidated_amended_law=True: no prior text available this pass for an")
    print("    article-level amendment diff -- disclosed as a limitation, not fabricated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
