#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Energy Supplies System track (نظام إمدادات
الطاقة, Royal Decree M/80, 4/6/1444H -- the CURRENTLY IN-FORCE law regulating
energy allocation across ten named consumption sectors, which by its own
Article 12 repealed/replaced the older Gas Supply and Pricing System
(نظام إمدادات الغاز وتسعيره, M/36, 25/6/1424H)).

12 records: 12 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (the Law has had no
amendments); NO chapter/فصل structure.

VERIFICATION TIER -- TIER_2. See the generator docstring and the source
artifact's verification_methodology_note for the full account: the exact
laws.boe.gov.sa URL supplied for this task was checked FIRST (per standard
methodology) but its live portal is unreachable this pass (connection reset
via curl; HTTP 503 via WebFetch); a SINGLE web.archive.org snapshot
(2025-10-17) was reached directly and matches the nezams.com text (fetched
live) word-for-word in legal content, with only disclosed immaterial
formatting/decorative variances (kashida placement, one missing comma, and
inconsistent thousands-separator glyphs in Article 8's penalty figure). This
validator does not re-adjudicate provenance; it only checks internal
self-consistency of the ingested text and that every discrepancy is still
recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "energy_supplies_system", "law", "official_source",
                   "energy_supplies_system_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "energy_supplies_system", "law", "verified",
                       "energy_supplies_system_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "energy_supplies_system", "law", "verified",
                       "energy_supplies_system_verified_summary.json")
LLM = os.path.join(ROOT, "data", "energy_supplies_system_arabic_legal_llm",
                   "energy_supplies_system_legal_llm_001_012.json")
N = 12
KEY_RE = r"energy_supplies_system_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 12, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

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
    "energy_supplies_system_boe_live_unreachable_single_wayback_snapshot_used",
    "energy_supplies_system_immaterial_boe_nezams_formatting_variances_disclosed",
    "energy_supplies_system_explicit_repeal_confirmed_article_12",
    "energy_supplies_system_transitional_provisions_outside_articles",
    "energy_supplies_system_gazette_issue_number_not_located",
    "energy_supplies_system_akhbaar24_two_year_regulation_deadline_conflated_resolved",
    "energy_supplies_system_no_chapter_structure",
    "energy_supplies_system_uqn_spa_not_ingested",
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
    if chs:
        e.append("[1c] chapter_structure must be empty (no فصل divisions in this law), got %d entries" % len(chs))

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
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
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
        # residual tashkeel guard (harakat/shadda/sukun/tanwin/superscript-alef must be
        # stripped from article bodies; NOTE the range deliberately excludes U+066C
        # ARABIC THOUSANDS SEPARATOR, which is a legitimate disclosed source glyph in
        # Article 8 -- see known_unresolved_discrepancies)
        if re.search(r"[ً-ْٰ]", a["text"]):
            e.append("[2g] %s: residual tashkeel/diacritics not stripped" % k)
        # non-standard Arabic-block letters (Farsi yeh/keheh) must not leak into article text
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
        e.append("[2k] missing amendment_history (must record the founding M/80 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/80" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/80")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/80)" \
            or src.get("decree_date_hijri") != "4/6/1444":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/80, 4/6/1444H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (the Law has no amendments)")
    if not src.get("supersedes_ar") or "م/36" not in src.get("supersedes_ar", ""):
        e.append("[2j] supersedes_ar must record that this Law replaced the older M/36 (1424H) Law")
    if not src.get("preamble_ar") or "م/80" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference M/80")
    if not src.get("com_resolution_ar") or "374" not in src.get("com_resolution_ar", ""):
        e.append("[2j] com_resolution_ar must be present and reference CoM Resolution 374")
    art1 = arts.get("energy_supplies_system_art_001", {})
    if "الوزارة: وزارة الطاقة" not in art1.get("text", "") \
            or "الطاقة: كل ما يندرج ضمن منتجات الطاقة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الوزارة / الطاقة)")
    art2 = arts.get("energy_supplies_system_art_002", {})
    art2_txt = art2.get("text", "")
    for sector in ("إنتاج الكهرباء", "تكرير الزيت الخام", "إنتاج البتروكيماويات",
                   "تحلية المياه", "الصناعة", "التعدين", "الزراعة", "الإنشاءات",
                   "الاتصالات", "النقل"):
        if sector not in art2_txt:
            e.append("[2j] Article 2 missing expected named sector: %s" % sector)
    art3 = arts.get("energy_supplies_system_art_003", {})
    if "لجنة تخصيص الطاقة" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected Energy Allocation Committee content")
    art8 = arts.get("energy_supplies_system_art_008", {})
    if "20" not in art8.get("text", "") or "عشرين مليون ريال" not in art8.get("text", ""):
        e.append("[2j] Article 8 missing expected SAR-20-million penalty ceiling")
    art11 = arts.get("energy_supplies_system_art_011", {})
    if "ستين" not in art11.get("text", ""):
        e.append("[2j] Article 11 missing expected 60-day regulation-issuance deadline")
    art12 = arts.get("energy_supplies_system_art_012", {})
    art12_txt = art12.get("text", "")
    if "يحل" not in art12_txt or "محل" not in art12_txt or "36" not in art12_txt or "1424" not in art12_txt:
        e.append("[2j] Article 12 must contain the named repeal/replace clause for the M/36 "
                 "(1424H) Law (يحل ... محل ... رقم (م/36) ... 1424هـ)")
    art12_label = art12.get("number_label_ar")
    if art12_label != "المادة الثانية عشرة":
        e.append("[2j] Article 12 number_label_ar must be 'المادة الثانية عشرة', got %r" % art12_label)

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
        if r.get("law_component") != "law":
            e.append("[4] %s: law_component must be 'law'" % r["article_key"])
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
        if r.get("law_component") != "law":
            e.append("[5] %s: law_component must be 'law'" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Energy Supplies System track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Energy Supplies System (نظام إمدادات الطاقة)")
    print("  - 12 records: 12 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (the Law has had no amendments)")
    print("  - NO chapter/فصل structure (flat, directly-numbered 12-article law)")
    print("  - CURRENT VERSION CONFIRMED: Royal Decree M/80, 4/6/1444H -- the in-force")
    print("    Energy Supplies System, which by its own Article 12 repealed/replaced the older")
    print("    Gas Supply and Pricing System (M/36, 25/6/1424H) (named repeal-and-replace clause).")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa checked first but its live portal is")
    print("    unreachable this pass (connection reset / HTTP 503); a single web.archive.org")
    print("    snapshot (2025-10-17) of the exact supplied BOE URL was reached and matches the")
    print("    nezams.com text word-for-word in legal content (disclosed immaterial formatting")
    print("    variances only), with additional partial corroboration from akhbaar24.com.")
    print("    Re-verification vs a live/second BOE snapshot recommended.")
    print("  - TRANSITIONAL PROVISIONS (outside the 12 numbered articles, in the enacting Decree")
    print("    and CoM Resolution 374 only): Article 3 (Energy Allocation Committee) takes")
    print("    effect immediately from the Decree's issuance date; licenses under the repealed")
    print("    M/36 law remain valid for up to 2 years (extendable by the Minister up to 6 more)")
    print("    while licensees correct their status.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
