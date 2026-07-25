#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Law on
Application of the Saudi Building Code track (30 records: 15 اصلية, 13 معدلة,
0 ملغاة [with a current numbered slot -- two founding articles were repealed
with no surviving slot; see known_unresolved_discrepancies], 2 مضافة; 7
chapters + an implementation-phases appendix).

VERIFICATION TIER -- see the generator's module docstring and
sources/building_code_regulation/law/official_source/
building_code_regulation_official_source.json's verification_methodology_note
for the full account: momah.gov.sa (the administering Ministry's own site)
hosts four directly-fetchable PDFs of this Regulation, compared directly and
found to carry the same decree chain (founding + 56 + 00004 + 304) merely
re-hosted/re-branded -- resolving the "two PDF versions" question. This
track's current (post-Decision-00004) article numbering 1-30 is independently
corroborated against qanoonsa.com. This validator does not re-adjudicate
provenance; it only checks internal self-consistency of the text this track
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
SRC = os.path.join(ROOT, "sources", "building_code_regulation", "law", "official_source",
                   "building_code_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "building_code_regulation", "law", "verified",
                       "building_code_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "building_code_regulation", "law", "verified",
                       "building_code_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "building_code_regulation_arabic_legal_llm",
                   "building_code_regulation_legal_llm_001_030.json")
N = 30
KEY_RE = r"building_code_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 15, "معدلة": 13, "ملغاة": 0, "مضافة": 2}
EXPECTED_TOP_LEVEL_CHAPTERS = 8  # 7 substantive chapters + 1 appendix entry
STATUS_TAG = {
    "اصلية": "MOMAH_OFFICIAL_PDF_X_QANOONSA_CURRENT_TEXT_CROSS_VERIFIED",
    "معدلة": "AMENDED_MOMAH_OFFICIAL_PDF_X_QANOONSA_CURRENT_TEXT_CROSS_VERIFIED",
    "مضافة": "ADDED_MOMAH_OFFICIAL_PDF_X_QANOONSA_CURRENT_TEXT_CROSS_VERIFIED",
}
ADDED_KEYS = {"building_code_regulation_art_011", "building_code_regulation_art_029"}
FLAGGED_DISCREPANCY_KEYS = {
    "building_code_regulation_two_pdf_versions_reconciled",
    "building_code_regulation_renumbering_range_not_fully_reconstructed",
    "building_code_regulation_historic_buildings_exemption_repealed_no_current_slot",
    "building_code_regulation_general_services_release_repealed_no_current_slot",
    "building_code_regulation_possible_unverified_fifth_amendment",
    "building_code_regulation_uqn_gov_sa_and_wayback_inaccessible",
    "building_code_regulation_gazette_issue_not_pinpointed",
    "building_code_regulation_tashkeel_and_normalization",
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


def _iter_chapter_ranges(chs):
    for ch in chs:
        spec = ch["articles"]
        if spec == "appendix":
            continue
        lo, hi = (int(x) for x in spec.split("-"))
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

    # continuous 1..30, no gaps/dupes
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    chs = src.get("chapter_structure") or []
    if len(chs) != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapter_structure entries (7 chapters + appendix), got %d"
                 % (EXPECTED_TOP_LEVEL_CHAPTERS, len(chs)))
    covered = []
    for lo, hi in _iter_chapter_ranges(chs):
        covered.extend(range(lo, hi + 1))
    cc = Counter(covered)
    dupes = [n for n, c in cc.items() if c > 1]
    if dupes:
        e.append("[1c] article(s) in more than one chapter range: %s" % dupes[:20])
    if set(cc) != set(range(1, N + 1)):
        miss = sorted(set(range(1, N + 1)) - set(cc))
        extra = sorted(set(cc) - set(range(1, N + 1)))
        if miss:
            e.append("[1c] chapter_structure missing article(s): %s" % miss[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])
    if not any(c["articles"] == "appendix" for c in chs):
        e.append("[1c] chapter_structure must include the implementation-phases appendix entry")

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
        want_tag = STATUS_TAG.get(ls)
        if want_tag and a.get("status") != want_tag:
            e.append("[2] %s: verification status %r != %r" % (k, a.get("status"), want_tag))
        t = a.get("text", "")
        t_check = t.replace("SBC 201", "")  # legitimate Latin code-designation cited in the Arabic text (art. 16)
        if not t.strip() or re.search(r"[A-Za-z<>&]", t_check):
            e.append("[2] %s: empty text or unexpected latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if _bad_tatweel(t):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(t):
            e.append("[2] %s: residual tashkeel present (should be stripped)" % k)
        if "\xa0" in t:
            e.append("[2f] %s: residual non-breaking-space artifact" % k)
        if "“" in t or "”" in t or "«" in t or "»" in t:
            e.append("[2f] %s: residual curly-quote/guillemet artifact" % k)
        if "  " in t:
            e.append("[2f] %s: residual double-space artifact" % k)
        is_amended = (ls == "معدلة")
        is_added = (ls == "مضافة")
        if (is_amended or is_added) and not a.get("history"):
            e.append("[2] %s: amended/added article missing history" % k)
        if not (is_amended or is_added) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if bool(a.get("is_mukarrar")):
            e.append("[2] %s: no mukarrar articles expected in this track" % k)
        if is_added and k not in ADDED_KEYS:
            e.append("[2] %s: unexpected مضافة status (not in ADDED_KEYS)" % k)
        if (not is_added) and k in ADDED_KEYS:
            e.append("[2] %s: expected مضافة status (in ADDED_KEYS) but got %r" % (k, ls))
        # history integrity for amended/added articles
        if is_amended:
            hist = a.get("history") or []
            types = [h.get("type") for h in hist]
            if "original" not in types:
                e.append("[2m] %s: amended article missing 'original' stage in history" % k)
            cur = next((h for h in hist if h.get("type", "").startswith("amendment_current")), None)
            if cur and cur.get("text") != t:
                e.append("[2m] %s: history's amendment_current text must equal current `text`" % k)
        if is_added:
            hist = a.get("history") or []
            if not any(h.get("type") == "added" for h in hist):
                e.append("[2m] %s: added article missing 'added' stage in history" % k)

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
        # the two repealed-with-no-current-slot founding articles must have their full text preserved
        joined = " ".join(d["description"] for d in disc)
        if "تُستثنى المباني التاريخية" not in joined:
            e.append("[2e] repealed historic-buildings-exemption article text must be preserved verbatim in discrepancies")
        if "لا يسمح بإطلاق الخدمات العامة" not in joined:
            e.append("[2e] repealed general-services-release article text must be preserved verbatim in discrepancies")
        if "47150028" not in joined and "المركز" not in joined:
            e.append("[2e] the possible unverified fifth amendment (اللجنة الوطنية -> المركز) must be disclosed")

    ah = src.get("amendment_history") or []
    if len(ah) != 4:
        e.append("[2k] amendment_history must have 4 entries (founding + 3 amendments), got %d" % len(ah))
    decrees = " ".join(str(h.get("decree", "")) for h in ah)
    for must in ("1213", "56", "00004", "304"):
        if must not in decrees:
            e.append("[2k] amendment_history must reference decree containing %r" % must)

    if src.get("decree") != "القرار الوزاري رقم (1213/ق/أع/39)" or src.get("decree_date_hijri") != "14/10/1439":
        e.append("[2j] decree/decree_date_hijri mismatch with founding Ministerial Decision")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True")
    if not src.get("ministerial_decision_text_ar"):
        e.append("[2j] ministerial_decision_text_ar (founding decision operative text) must be present")

    # spot-checks anchoring key facts established this pass
    a1 = arts.get("building_code_regulation_art_001", {}).get("text", "")
    if "المصمم المعتمد" not in a1 or "جهة التفتيش" not in a1:
        e.append("[2j] Article 1 (current) missing expected amended definitions (المصمم المعتمد / جهة التفتيش)")
    a11 = arts.get("building_code_regulation_art_011", {}).get("text", "")
    if "الهيئة" not in a11 or "المطابقة" not in a11:
        e.append("[2j] Article 11 (added, Standards Authority duties) missing expected content")
    a29 = arts.get("building_code_regulation_art_029", {}).get("text", "")
    if "عشر سنوات" not in a29:
        e.append("[2j] Article 29 (added, ten-year joint liability) missing expected content")
    a30 = arts.get("building_code_regulation_art_030", {}).get("text", "")
    if "تاريخ نشرها" not in a30:
        e.append("[2j] Article 30 (effective date) missing expected wording")

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
        print("FAIL: %d error(s) in Building Code Regulation track:" % len(e))
        for x in e[:50]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Law on Application of the Saudi Building Code")
    print("  - 30 records: 15 اصلية, 13 معدلة, 0 ملغاة (with a current slot), 2 مضافة")
    print("  - 7 chapters + implementation-phases appendix; articles 1-30 covered exactly once")
    print("  - VERIFICATION TIER: PRIMARY source momah.gov.sa (administering Ministry's own site,")
    print("    4 directly-fetchable PDF versions compared and reconciled -- same decree chain,")
    print("    re-hosted/re-branded, NOT a substantive difference); current numbering (1-30, per")
    print("    Ministerial Decision 00004's own renumbering) cross-verified against qanoonsa.com")
    print("  - Founding Ministerial Decision (1213/Q/A/39, 14/10/1439H); amended by Decision (56,")
    print("    3/3/1441H), Decision (00004, 8/1/1443H -- comprehensive renumbering), and Decision")
    print("    (304, 8/7/1444H)")
    print("  - DISCLOSED: two founding articles (historic-buildings exemption; general-services-")
    print("    release) were repealed with no surviving numbered slot in the current sequence --")
    print("    their full text is preserved verbatim in known_unresolved_discrepancies, never deleted")
    print("  - DISCLOSED, NOT INCORPORATED: a likely fifth amendment (اللجنة الوطنية -> المركز,")
    print("    paralleling the parent law's own M/204) could not be confirmed from a primary Umm")
    print("    al-Qura Gazette source this pass (uqn.gov.sa and web.archive.org both inaccessible)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
