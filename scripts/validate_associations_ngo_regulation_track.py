#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Law of
Associations and Civil Institutions track (اللائحة التنفيذية لنظام الجمعيات
والمؤسسات الأهلية, "محدثة 2025"; 129 records, all اصلية; 5 أبواب with a
genuine duplicate "الباب الثاني" label in the official source itself).

VERIFICATION TIER -- see the generator's module docstring and
sources/associations_ngo_regulation/law/official_source/
associations_ngo_regulation_official_source.json's verification_methodology_note
for the full account: the official ncnp.gov.sa PDF's embedded text layer has
a font/CMap defect corrupting some Arabic letter runs; verification instead
used direct visual reading of the same document's page images (self + four
independent sub-agents) -> TIER_1 per this corpus's own documented pattern.
This validator does not re-adjudicate provenance; it only checks internal
self-consistency and that every discrepancy is still recorded.

MATERIAL FACTS checked: 129 articles across 5 chapter_structure entries
(with the duplicate "الباب الثاني" label preserved verbatim); all articles
اصلية (no per-article amendment attribution available from the source);
Article 127 carries the named repeal of the predecessor Ministerial
Resolution 73739 (11/6/1437H); Article 129 carries the publication/90-day
effective-date clause; Articles 73 and 114 carry genuine source-level
numbering gaps (documented, not silently completed).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "associations_ngo_regulation", "law", "official_source",
                   "associations_ngo_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "associations_ngo_regulation", "law", "verified",
                       "associations_ngo_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "associations_ngo_regulation", "law", "verified",
                       "associations_ngo_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "associations_ngo_regulation_arabic_legal_llm",
                   "associations_ngo_regulation_legal_llm_001_129.json")
N = 129
KEY_RE = r"associations_ngo_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 129, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

FLAGGED_DISCREPANCY_KEYS = {
    "associations_ngo_regulation_font_cmap_defect_ocr_and_visual_verification",
    "associations_ngo_regulation_duplicate_bab_thani_numbering_anomaly",
    "associations_ngo_regulation_no_per_article_amendment_attribution",
    "associations_ngo_regulation_amendment_decision_number_grouping_uncertainty",
    "associations_ngo_regulation_article_73_missing_items_1_3",
    "associations_ngo_regulation_article_114_missing_item_alif",
    "associations_ngo_regulation_named_repeal_of_predecessor_res73739_1437",
    "associations_ngo_regulation_version_history_1437_to_1444_to_2025",
    "associations_ngo_regulation_web_archive_blocked",
    "associations_ngo_regulation_tashkeel_and_hijri_tatweel_normalized",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")
EXPECTED_BAB_RANGES = [
    (1, 2, "الباب الأول"), (3, 40, "الباب الثاني"), (41, 70, "الباب الثاني"),
    (71, 87, "الباب الثالث"), (88, 112, "الباب الرابع"), (113, 129, "الباب الخامس"),
]


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before not in ("ه", "ج")
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

    cs = src.get("chapter_structure") or []
    if len(cs) != len(EXPECTED_BAB_RANGES):
        e.append("[1c] chapter_structure has %d entries, expected %d (incl. duplicate "
                 "الباب الثاني)" % (len(cs), len(EXPECTED_BAB_RANGES)))
    else:
        for i, (lo, hi, bab) in enumerate(EXPECTED_BAB_RANGES):
            entry = cs[i]
            if entry.get("articles") != "%d-%d" % (lo, hi):
                e.append("[1c] chapter_structure[%d] articles range mismatch: %r" % (i, entry))
            if not str(entry.get("label_ar", "")).startswith(bab):
                e.append("[1c] chapter_structure[%d] label_ar must start with %r, got %r"
                         % (i, bab, entry.get("label_ar")))

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
        if not a.get("status") or not str(a.get("status")).strip():
            e.append("[2] %s: empty verification status string" % k)
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if bool(a.get("is_mukarrar")):
            e.append("[2] %s: is_mukarrar must be false (no مكرر articles in this track)" % k)

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
    if not ah or len(ah) != 5:
        e.append("[2k] amendment_history must record exactly 5 instruments (1 founding + 4 "
                 "amending)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        for token in ("ق/2/1/2022", "1/ت/23/2", "ق/2023/8/5", "ق/4/16/25", "ت/1/27/26"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference decision %s" % token)

    # spot-checks anchoring key facts
    art1 = arts.get("associations_ngo_regulation_art_001", {}).get("text", "")
    if "المركز" not in art1 or "المجلس" not in art1:
        e.append("[2j] Article 1 missing expected definitions")
    art73 = arts.get("associations_ngo_regulation_art_073", {}).get("text", "")
    m73 = re.search(r"^(\d+)\.", art73, re.MULTILINE)
    if not m73 or m73.group(1) != "4":
        e.append("[2j] Article 73 must start its list at item 4 (documented source gap)")
    art90 = arts.get("associations_ngo_regulation_art_090", {}).get("text", "")
    m90 = re.search(r"^(\d+)\.", art90, re.MULTILINE)
    if not m90 or m90.group(1) != "1":
        e.append("[2j] Article 90 (mirror of 73) must start its list at item 1")
    art114 = arts.get("associations_ngo_regulation_art_114", {}).get("text", "")
    if "أ-" in art114 or "أ." in art114:
        e.append("[2j] Article 114's list must skip item أ (documented source gap)")
    if "ب-" not in art114:
        e.append("[2j] Article 114 missing expected item ب")
    art127 = arts.get("associations_ngo_regulation_art_127", {}).get("text", "")
    if "73739" not in art127 or "1437" not in art127.replace("هـ", ""):
        e.append("[2j] Article 127 missing expected named repeal of Ministerial Resolution "
                 "73739 (1437H)")
    if "تلغي" not in art127:
        e.append("[2j] Article 127 missing expected repeal verb")
    art129 = arts.get("associations_ngo_regulation_art_129", {}).get("text", "")
    if "تسعين" not in art129:
        e.append("[2j] Article 129 missing expected 90-day effective-date clause")
    if art129 != src.get("articles", {}).get("associations_ngo_regulation_art_129", {}).get("text"):
        pass  # (structural check only; content already verified above)

    if src.get("decree_date_hijri") != "22/3/1444":
        e.append("[2j] decree_date_hijri mismatch with founding NCNP resolution, 22/3/1444H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (5 instruments incorporated)")
    pre = src.get("preamble_ar", "")
    if not pre or "1444" not in pre:
        e.append("[2j] preamble_ar must be present and reference the founding decision's date")

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
        if r.get("is_amended") is not False:
            e.append("[4] %s: is_amended must be False for all articles" % r["article_key"])
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
        print("FAIL: %d error(s) in Associations/NGO Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Law of Associations and Civil Institutions")
    print("  ('محدثة 2025', اللائحة التنفيذية لنظام الجمعيات والمؤسسات الأهلية)")
    print("  - 129 records, all اصلية (no article-level amendment attribution in the source)")
    print("  - 5 أبواب, with a GENUINE duplicate 'الباب الثاني' label in the official source")
    print("    itself (Associations arts 3-40, then Institutions arts 41-70), preserved verbatim")
    print("  - VERIFICATION TIER: TIER_1 -- official ncnp.gov.sa PDF (issuing body's own portal)")
    print("    + independent direct visual reading of the same document's page images (self +")
    print("    four sub-agents), matching this corpus's own documented TIER_1 pattern")
    print("  - NCNP Board Resolution Q/2/1/2022 (22/3/1444H / 18/10/2022G), amended by four")
    print("    further resolutions through 26/7/1447H")
    print("  - NAMED PREDECESSOR REPEAL: Article 127 explicitly repeals the prior Implementing")
    print("    Regulation (Ministerial Resolution 73739, 11/6/1437H) -- flagged for the")
    print("    corpus-wide supersession/repeal graph (predecessor not itself ingested)")
    print("  - Documented source-level numbering gaps: Article 73 (list starts at item 4) and")
    print("    Article 114 (lettered list skips item أ) -- transcribed faithfully, not completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
