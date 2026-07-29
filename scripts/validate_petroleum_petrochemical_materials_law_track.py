#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Petroleum and Petrochemical Materials Law track
(نظام المواد البترولية والبتروكيماوية, Royal Decree M/139, 12/7/1446H -- the
currently in-force law regulating petroleum and petrochemical operations).

22 records: 22 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (a brand-new 2025 law -- no
evidence of any amendment was found this pass). NO chapter/فصل structure -- a
short law, directly numbered from Article 1 to Article 22 with no
sub-division.

SUPERSESSION -- confirmed INSIDE the Law's own Article 21: "يحل النظام محل
نظام التجارة بالمنتجات البترولية، الصادر بالمرسوم الملكي رقم (م / 18) وتاريخ
28 / 1 / 1439هـ، ويلغي ما يتعارض معه من أحكام."

VERIFICATION TIER -- TIER_2. See the generator docstring and the source
artifact's verification_methodology_note: a single web.archive.org snapshot
of the official laws.boe.gov.sa portal (2026-01-17) was reached and matches
the qanoonsa.com text used for storage nearly word-for-word (4 disclosed
immaterial variances only); the live BOE portal itself is unreachable this
pass (connection reset). This validator does not re-adjudicate provenance; it
only checks internal self-consistency of the ingested text and that every
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
SRC = os.path.join(ROOT, "sources", "petroleum_petrochemical_materials_law", "law", "official_source",
                   "petroleum_petrochemical_materials_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "petroleum_petrochemical_materials_law", "law", "verified",
                       "petroleum_petrochemical_materials_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "petroleum_petrochemical_materials_law", "law", "verified",
                       "petroleum_petrochemical_materials_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "petroleum_petrochemical_materials_law_arabic_legal_llm",
                   "petroleum_petrochemical_materials_law_legal_llm_001_022.json")
N = 22
KEY_RE = r"petroleum_petrochemical_materials_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 22, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 0  # no فصول in this law

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
    "petroleum_petrochemical_materials_law_boe_live_unreachable_single_wayback_snapshot_used",
    "petroleum_petrochemical_materials_law_four_immaterial_boe_qanoonsa_variances_disclosed",
    "petroleum_petrochemical_materials_law_explicit_repeal_confirmed_article_21",
    "petroleum_petrochemical_materials_law_transitional_license_exception_outside_articles",
    "petroleum_petrochemical_materials_law_gazette_hijri_date_not_located",
    "petroleum_petrochemical_materials_law_no_chapter_structure",
    "petroleum_petrochemical_materials_law_implementing_regulation_not_ingested",
    "petroleum_petrochemical_materials_law_com_resolution_clauses_3_to_6_outside_articles",
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
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits, "
                     "except the disclosed Arabic percent sign ٪)" % k)
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)
        if "‏" in a["text"] or "‎" in a["text"]:
            e.append("[2m] %s: residual RLM/LRM directional-mark artifact present" % k)

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
        e.append("[2k] missing amendment_history (must record the founding M/139 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/139" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/139")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/139)" \
            or src.get("decree_date_hijri") != "12/7/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/139, 12/7/1446H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendments found this pass)")
    sup = src.get("supersedes_ar", "")
    if not sup or "م/18" not in sup or "المادة الحادية والعشرون" not in sup:
        e.append("[2j] supersedes_ar must name the repealed instrument (م/18) and anchor the "
                 "repeal to Article 21 of this Law's own text")
    if not src.get("preamble_ar") or "12/7/1446" not in src.get("preamble_ar", "") \
            or "نظام المواد البترولية والبتروكيماوية" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "12/7/1446H decree date and نظام المواد البترولية والبتروكيماوية")
    if not src.get("com_resolution_ar") or "473" not in src.get("com_resolution_ar", ""):
        e.append("[2j] com_resolution_ar must be present and reference CoM Resolution 473")

    art1 = arts.get("petroleum_petrochemical_materials_law_art_001", {})
    if "الوزارة: وزارة الطاقة" not in art1.get("text", "") \
            or "الترخيص" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الوزارة / الترخيص)")
    art5 = arts.get("petroleum_petrochemical_materials_law_art_005", {})
    if "لا يجوز" not in art5.get("text", "") or "الترخيص" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected licensing-requirement clause")
    art20 = arts.get("petroleum_petrochemical_materials_law_art_020", {})
    if "اللوائح" not in art20.get("text", "") or "تسعين" not in art20.get("text", ""):
        e.append("[2j] Article 20 missing expected implementing-regulation mandate (اللوائح/تسعين)")
    art21 = arts.get("petroleum_petrochemical_materials_law_art_021", {})
    if "يحل النظام محل" not in art21.get("text", "") or "18" not in art21.get("text", ""):
        e.append("[2j] Article 21 missing expected supersession clause referencing م/18")
    art21_label = art21.get("number_label_ar")
    if art21_label != "المادة الحادية والعشرون":
        e.append("[2j] Article 21 number_label_ar must be 'المادة الحادية والعشرون', got %r"
                 % art21_label)
    art22 = arts.get("petroleum_petrochemical_materials_law_art_022", {})
    if "الجريدة الرسمية" not in art22.get("text", "") or "تسعين" not in art22.get("text", ""):
        e.append("[2j] Article 22 missing expected entry-into-force clause (تسعين يوما)")

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
        print("FAIL: %d error(s) in Petroleum and Petrochemical Materials Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Petroleum and Petrochemical Materials Law (نظام المواد البترولية والبتروكيماوية)")
    print("  - 22 records: 22 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (a brand-new 2025 law; no amendment")
    print("    found this pass)")
    print("  - NO chapter (فصول) structure -- a short, flat, directly-numbered 22-article law")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/139, 12/7/1446H (CoM Resolution 473,")
    print("    7/7/1446H; Shura Resolution 80/8, 2/5/1446H). Brand-new base-law track, not")
    print("    previously in this corpus. Published Umm Al-Qura Gazette issue 5066, 24 Jan 2025.")
    print("  - SUPERSESSION confirmed INSIDE Article 21 of the Law's own text: replaces the prior")
    print("    Petroleum Products Trading Law (M/18, 28/1/1439H); a partial transitional license")
    print("    exception (outside the 22 articles, in the enacting decree/CoM resolution) is")
    print("    disclosed, not silently folded into the repeal.")
    print("  - VERIFICATION TIER: TIER_2 -- one official primary source (laws.boe.gov.sa) reached")
    print("    via a SINGLE web.archive.org snapshot (2026-01-17; live portal unreachable this")
    print("    pass), matching the qanoonsa.com storage text nearly word-for-word (4 disclosed")
    print("    immaterial variances only), plus nezams.com and argaam.com corroboration.")
    print("    Re-verify against a live/second BOE snapshot when reachable.")
    print("  - Implementing Regulation (Article 20 mandate) referenced via qanoonsa.com/p/514706")
    print("    but NOT ingested this pass -- flagged as a follow-up candidate")
    print("    (petroleum_petrochemical_materials_regulation).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
