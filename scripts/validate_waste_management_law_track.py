#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Waste Management Law track (نظام إدارة
النفايات, Royal Decree M/3, 5/1/1443H -- the currently in-force Waste Management
Law).

38 records: 38 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (the Law has had no amendments per
nezams.com: "لم يجرى عليه تعديل"). 11 chapters (فصول) confirmed independently
(gray-styled chapter markers embedded at the start of the first article of each
chapter on nezams.com).

SUPERSESSION -- confirmed INSIDE the Law's own Article 37 (not merely the issuing
decree): "يحل هذا النظام محل نظام إدارة النفايات البلدية الصلبة، الصادر بالمرسوم
الملكي رقم (م/48) وتاريخ 17 /9/ 1434هـ."

VERIFICATION TIER -- TIER_3. See the generator docstring and the source
artifact's verification_methodology_note: laws.boe.gov.sa was checked FIRST but
is unreachable this pass (repeated "Connection reset by peer" on direct curl);
web.archive.org was explicitly attempted this pass (unlike some other tracks in
this corpus) and returned the identical connection-reset failure -- not
circumvented further. The verbatim text of all 38 articles was extracted from
nezams.com (a single clean born-digital HTML aggregator), with governing
metadata and the 11-chapter/38-article structure cross-checked for identity
against BOE lawIds (current + repealed), qanoonsa.com, and an mwan.gov.sa
Implementing-Regulation link. This validator does not re-adjudicate provenance;
it only checks internal self-consistency of the ingested text and that every
discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "waste_management_law", "law", "official_source",
                   "waste_management_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "waste_management_law", "law", "verified",
                       "waste_management_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "waste_management_law", "law", "verified",
                       "waste_management_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "waste_management_law_arabic_legal_llm",
                   "waste_management_law_legal_llm_001_038.json")
N = 38
KEY_RE = r"waste_management_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 38, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 11  # 11 فصول

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "waste_management_law_boe_and_wayback_unreachable_single_aggregator",
    "waste_management_law_com_resolution_11_date_conflict",
    "waste_management_law_repeal_confirmed_in_article_37_itself",
    "waste_management_law_implementing_regulation_not_ingested_138_pages",
    "waste_management_law_com_resolution_transitional_clauses_outside_articles",
    "waste_management_law_decree_number_rendering_m3_vs_3",
    "waste_management_law_gregorian_date_secondary_only",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ٰٟ]")


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
        parts = ch["articles"].split("-")
        lo = int(parts[0])
        hi = int(parts[1]) if len(parts) > 1 else lo
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
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one chapter range" % n)
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
        e.append("[1d] unexpected duplicate chapter title(s): %s"
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
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (chapter title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if k in (AMENDED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/added article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in (AMENDED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits only)" % k)
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)

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
        e.append("[2k] missing amendment_history (must record the founding M/3 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/3" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/3")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/3)" \
            or src.get("decree_date_hijri") != "5/1/1443":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/3, 5/1/1443H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (the Law has no amendments)")
    sup = src.get("supersedes_ar", "")
    if not sup or "م/48" not in sup or "المادة السابعة والثلاثون" not in sup:
        e.append("[2j] supersedes_ar must name the repealed instrument (م/48) and anchor the "
                 "repeal to Article 37 of this Law's own text")
    # NOTE: the source's own decree body text renders the decree number as "(3)"
    # without the "م/" prefix (the "م/" prefix appears only in the metadata table on
    # nezams.com) -- disclosed verbatim, see known_unresolved_discrepancies
    # (waste_management_law_decree_number_rendering_m3_vs_3). So this check anchors on
    # the date and the law's own name, not on "م/3" literally appearing in the preamble.
    if not src.get("preamble_ar") or "5/ 1/ 1443" not in src.get("preamble_ar", "") \
            or "نظام إدارة النفايات" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "5/1/1443H decree date and نظام إدارة النفايات")
    if not src.get("com_resolution_ar") or "قرار مجلس الوزراء" not in src.get("com_resolution_ar", ""):
        e.append("[2j] com_resolution_ar (CoM Resolution 11 full text) must be present")

    art1 = arts.get("waste_management_law_art_001", {})
    if "المركز: المركز الوطني لإدارة النفايات" not in art1.get("text", "") \
            or "النفايات الخطرة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (المركز / النفايات الخطرة)")
    art36 = arts.get("waste_management_law_art_036", {})
    if "اللائحة" not in art36.get("text", "") or "ستين" not in art36.get("text", ""):
        e.append("[2j] Article 36 missing expected implementing-regulation mandate (اللائحة/ستين)")
    art37 = arts.get("waste_management_law_art_037", {})
    if "يحل هذا النظام محل" not in art37.get("text", "") or "م/48" not in art37.get("text", ""):
        e.append("[2j] Article 37 missing expected supersession clause referencing م/48")
    art38 = arts.get("waste_management_law_art_038", {})
    if "يعمل بالنظام" not in art38.get("text", "") or "ستين" not in art38.get("text", ""):
        e.append("[2j] Article 38 missing expected entry-into-force clause (ستين يوما)")
    art38_label = art38.get("number_label_ar")
    if art38_label != "المادة الثامنة والثلاثون":
        e.append("[2j] Article 38 number_label_ar must be 'المادة الثامنة والثلاثون', got %r"
                 % art38_label)

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
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Waste Management Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Waste Management Law (نظام إدارة النفايات)")
    print("  - 38 records: 38 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (the Law has had no amendments)")
    print("  - 11 chapters (فصول) confirmed independently from nezams.com's in-body chapter")
    print("    markers; article ranges verified to tile 1-38 exactly once")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/3, 5/1/1443H (CoM Resolution 11 -- date")
    print("    disclosed as conflicting across the source; Shura Resolution 140/26, 14/9/1442H).")
    print("    Brand-new base-law track, not previously in this corpus.")
    print("  - SUPERSESSION confirmed INSIDE Article 37 of the Law's own text: replaces the")
    print("    Municipal Solid Waste Management Law (M/48, 17/9/1434H).")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa checked first but unreachable this")
    print("    pass (connection reset); web.archive.org explicitly attempted and also unreachable")
    print("    (connection reset, not circumvented further). Full verbatim text from nezams.com")
    print("    (single clean born-digital HTML aggregator, no scan/OCR/ligature defects); all")
    print("    governing metadata + 11-chapter/38-article structure cross-checked for identity")
    print("    against BOE lawIds (current + repealed), qanoonsa.com, and mwan.gov.sa. Re-verify")
    print("    verbatim text vs laws.boe.gov.sa when reachable.")
    print("  - Implementing Regulation (Article 36 mandate; ~138 pages per mwan.gov.sa) exists and")
    print("    is flagged as a follow-up candidate (waste_management_regulation), NOT ingested")
    print("    this pass -- mwan.gov.sa itself was unreachable this session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
