#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Non-Saudi Real
Estate Ownership Law track (اللائحة التنفيذية لنظام تملك غير السعوديين للعقار;
14 articles, ALL اصلية, + 1 penalties-annex-table record, also اصلية).

VERIFICATION TIER -- see the generator's module docstring and
sources/foreign_ownership_regulation/law/official_source/
foreign_ownership_regulation_official_source.json's verification_methodology_note
for the full account: TWO independent PRIMARY Saudi government sources
(uqn.gov.sa, the Official Umm al-Qura Gazette portal; and rega.gov.sa, the
Real Estate General Authority's own legislation portal) were both reached
live and both host the complete text directly as HTML -> TIER_1. This
Regulation is EXTREMELY FRESH; several caveats (unconfirmed decree/gazette-
issue number, an unreachable third source, a conflict with this task's own
prior-research briefing's gazette date) are disclosed in
known_unresolved_discrepancies. This validator does not re-adjudicate
provenance; it only checks internal self-consistency and that every
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
SRC = os.path.join(ROOT, "sources", "foreign_ownership_regulation", "law", "official_source",
                   "foreign_ownership_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "foreign_ownership_regulation", "law", "verified",
                       "foreign_ownership_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "foreign_ownership_regulation", "law", "verified",
                       "foreign_ownership_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "foreign_ownership_regulation_arabic_legal_llm",
                   "foreign_ownership_regulation_legal_llm_001_015.json")
N_ARTICLES = 14
N_RECORDS = 15  # 14 articles + 1 penalties table
KEY_RE = r"foreign_ownership_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 14, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
PENALTIES_KEY = "foreign_ownership_regulation_penalties_table"
EXPECTED_PENALTY_ROWS = 7

FLAGGED_DISCREPANCY_KEYS = {
    "foreign_ownership_regulation_penalty_table_rows_5_6_7_wording_variance",
    "foreign_ownership_regulation_decree_and_gazette_issue_number_unconfirmed",
    "foreign_ownership_regulation_decision_date_vs_publication_date",
    "foreign_ownership_regulation_prior_research_gazette_date_conflict",
    "foreign_ownership_regulation_ncar_boe_unreachable",
    "foreign_ownership_regulation_alweeam_akhbaar24_secondary_access_gaps",
    "foreign_ownership_regulation_no_confirmed_preamble",
    "foreign_ownership_regulation_source_percent_glyph_inconsistency",
    "foreign_ownership_regulation_article9_fee_schedule_currently_four_zones",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")
RLM_LRM = re.compile(r"[‎‏]")


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

    if len(arts) != N_ARTICLES:
        e.append("[1] %d articles != %d" % (len(arts), N_ARTICLES))
    if src.get("article_count") != N_ARTICLES:
        e.append("[1] article_count field != %d" % N_ARTICLES)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N_ARTICLES + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N_ARTICLES, nums))

    sc = Counter()
    for k, a in arts.items():
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
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if RLM_LRM.search(a["text"]):
            e.append("[2h] %s: residual RLM/LRM invisible mark present (must be stripped)" % k)
        if a.get("history"):
            e.append("[2i] %s: no article in this fresh, unamended regulation should carry history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2g] %s: residual Eastern-Arabic-Indic digit found (source uses Western "
                     "digits throughout; must not be introduced)" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    # Article 9 must carry its embedded fee-schedule table (linearized inline)
    art9 = arts.get("foreign_ownership_regulation_art_009", {}).get("text", "")
    if art9.count("قيمة الرسم: 2%") != 4:
        e.append("[2j] Article 9 must contain exactly 4 linearized fee-schedule rows (2%% each)")
    for zone in ("مدينة الرياض", "مدينة مكة المكرمة", "مدينة المدينة المنورة", "محافظة جدة"):
        if zone not in art9:
            e.append("[2j] Article 9 missing expected geographic zone: %s" % zone)

    # Article 12 references the penalties table explicitly (binding, not a courtesy annex)
    art12 = arts.get("foreign_ownership_regulation_art_012", {}).get("text", "")
    if "العقوبات الواردة في الجدول الملحق باللائحة" not in art12:
        e.append("[2j] Article 12 missing expected cross-reference to the binding penalties annex")

    # Article 14 must NOT swallow the annex title (parsing-boundary check)
    art14 = arts.get("foreign_ownership_regulation_art_014", {}).get("text", "")
    if "ملحق" in art14 or "جدول تصنيف" in art14:
        e.append("[2j] Article 14 text must not include the penalties-annex title")
    if "دليلا إجرائيا" not in art14:
        e.append("[2j] Article 14 missing expected procedural-guide clause")

    if src.get("decree_date_hijri") != "18/01/1448":
        e.append("[2j] decree_date_hijri must be 18/01/1448 (Official Gazette display date, "
                 "this track's adopted date of record)")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (fresh issuance, no amendments)")
    if src.get("law_component") != "regulation":
        e.append("[2j] law_component must be 'regulation'")
    if src.get("verification_tier") != "TIER_1_PRIMARY_MULTI_SOURCE":
        e.append("[2j] verification_tier must be TIER_1_PRIMARY_MULTI_SOURCE")

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

    # ---- penalties annex table ----
    pt = src.get("penalties_table")
    if not pt:
        e.append("[3] missing penalties_table")
    else:
        if pt.get("row_count") != EXPECTED_PENALTY_ROWS or len(pt.get("rows", [])) != EXPECTED_PENALTY_ROWS:
            e.append("[3] penalties_table row_count != %d" % EXPECTED_PENALTY_ROWS)
        band_nos = sorted(r["band_no"] for r in pt.get("rows", []))
        if band_nos != list(range(1, EXPECTED_PENALTY_ROWS + 1)):
            e.append("[3] penalties_table band numbers not a clean 1..%d sequence: %s"
                     % (EXPECTED_PENALTY_ROWS, band_nos))
        for r in pt.get("rows", []):
            if not r.get("violation_ar", "").strip():
                e.append("[3] penalties_table row %s: empty violation_ar" % r.get("band_no"))
            if not r.get("penalty_cells"):
                e.append("[3] penalties_table row %s: no penalty_cells" % r.get("band_no"))
            for c in r.get("penalty_cells", []):
                if not c.get("value_ar", "").strip():
                    e.append("[3] penalties_table row %s: empty penalty cell value" % r.get("band_no"))
        row1 = next((r for r in pt.get("rows", []) if r["band_no"] == 1), None)
        if row1 and "10,000,000" not in row1["penalty_cells"][0]["value_ar"]:
            e.append("[3] penalties_table row 1 must reference the (10,000,000) SAR cap")
        if pt.get("legal_status_ar") != "اصلية":
            e.append("[3] penalties_table legal_status_ar must be اصلية")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_RECORDS:
        e.append("[4] %d verified records != %d (14 articles + 1 penalties table)" % (len(ver), N_RECORDS))
    art_recs = [r for r in ver if r["article_key"] != PENALTIES_KEY]
    table_recs = [r for r in ver if r["article_key"] == PENALTIES_KEY]
    if len(table_recs) != 1:
        e.append("[4] expected exactly 1 penalties-table verified record, found %d" % len(table_recs))
    for r in art_recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("legal_status_ar") != a.get("legal_status_ar"):
            e.append("[4] %s: legal_status_ar mismatch" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))
    for r in table_recs:
        if pt and r["article_text_verified"] != "\n".join(
                "البند %d: %s\n%s" % (
                    row["band_no"], row["violation_ar"],
                    " | ".join("%s: %s" % (c["label_ar"], c["value_ar"])
                               for c in row["penalty_cells"] if str(c["value_ar"]).strip()))
                for row in pt["rows"]):
            e.append("[4] penalties-table verified record text does not match a mechanical "
                     "linearization of the source penalties_table rows")

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N_RECORDS:
        e.append("[4b] summary record_count != %d" % N_RECORDS)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("consolidated_amended_law") is not False:
        e.append("[4b] summary consolidated_amended_law must be False")
    if summary.get("verification_tier") != "TIER_1_PRIMARY_MULTI_SOURCE":
        e.append("[4b] summary verification_tier must be TIER_1_PRIMARY_MULTI_SOURCE")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_RECORDS or len(recs) != N_RECORDS:
        e.append("[5] llm count != %d" % N_RECORDS)
    for r in recs:
        if r["article_key"] == PENALTIES_KEY:
            expected_text = table_recs[0]["article_text_verified"] if table_recs else None
            if expected_text is not None and r["article_text_ar"] != expected_text:
                e.append("[5] %s: llm table text != verified record text" % r["article_key"])
        else:
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
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Foreign Ownership Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Non-Saudi Real Estate Ownership Law")
    print("  (اللائحة التنفيذية لنظام تملك غير السعوديين للعقار)")
    print("  - 14 articles, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة) + 1 penalties-annex-table record")
    print("  - No فصول/أبواب: flat sequential 1..14 article structure")
    print("  - VERIFICATION TIER: TIER_1_PRIMARY_MULTI_SOURCE -- two independent PRIMARY Saudi")
    print("    government sources (uqn.gov.sa Official Gazette + rega.gov.sa Real Estate General")
    print("    Authority) both reached live this pass, 8/14 articles byte-identical, remainder only")
    print("    punctuation-level variance; penalties annex differs in 3 one-word labels only")
    print("  - EXTREMELY FRESH DOCUMENT: Gazette date 18 Muharram 1448H (3 July 2026); several")
    print("    caveats disclosed (unconfirmed decree/gazette-issue number, unreachable NCAR/BOE")
    print("    third source, conflict with prior-research briefing's gazette date) -- read")
    print("    known_unresolved_discrepancies before relying on this track for precise citation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
