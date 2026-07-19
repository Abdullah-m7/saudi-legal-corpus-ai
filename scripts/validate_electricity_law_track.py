#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Electricity Law track (نظام الكهرباء,
Royal Decree M/44, 16/5/1442H -- the CURRENTLY IN-FORCE Electricity Law, which
by its own Article 23 repealed/replaced the older M/56 (20/10/1426H) Law).

23 records: 23 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (the Law has had no amendments);
9 chapters.

VERIFICATION TIER -- TIER_3. See the generator docstring and the source artifact's
verification_methodology_note for the full account: laws.boe.gov.sa was checked
FIRST (per standard methodology) but is unreachable this pass (connection reset /
HTTP 503) and Wayback is egress-blocked (not circumvented); the verbatim text of
all 23 articles was extracted from nezams.com (a single clean born-digital HTML
aggregator -- no scan/OCR/ligature defects), with every governing metadata fact
cross-verified against multiple independent sources. This validator does not
re-adjudicate provenance; it only checks internal self-consistency of the ingested
text and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "electricity", "law", "official_source",
                   "electricity_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "electricity", "law", "verified",
                       "electricity_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "electricity", "law", "verified",
                       "electricity_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "electricity_arabic_legal_llm",
                   "electricity_law_legal_llm_001_023.json")
N = 23
KEY_RE = r"electricity_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 9

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
    "electricity_law_current_version_confirmed_m44_supersedes_m56",
    "electricity_law_boe_unreachable_fulltext_from_single_aggregator",
    "electricity_law_art4_art18_concatenated_subitems_preserved",
    "electricity_law_gregorian_dates_secondary_only",
    "electricity_law_implementing_regulations_companion_candidates",
    "electricity_law_regulator_renamed_to_sera",
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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
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
        # residual tashkeel guard (all harakat/shadda/tanwin/superscript-alef must be stripped)
        if re.search(r"[ً-ٰٟ]", a["text"]):
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
        e.append("[2k] missing amendment_history (must record the founding M/44 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/44" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/44")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/44)" \
            or src.get("decree_date_hijri") != "16/5/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/44, 16/5/1442H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (the Law has no amendments)")
    if not src.get("supersedes_ar") or "م/56" not in src.get("supersedes_ar", ""):
        e.append("[2j] supersedes_ar must record that this Law replaced the older M/56 (1426H) Law")
    if not src.get("preamble_ar") or "م/44" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference M/44")
    art1 = arts.get("electricity_law_art_001", {})
    if "الوزارة: وزارة الطاقة" not in art1.get("text", "") \
            or "هيئة تنظيم المياه والكهرباء" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الوزارة / الهيئة)")
    art8 = arts.get("electricity_law_art_008", {})
    if "مصدر احتياطي للطاقة الكهربائية" not in art8.get("text", ""):
        e.append("[2j] Article 8 missing expected backup-power-source content")
    art22 = arts.get("electricity_law_art_022", {})
    if "اللائحة التنفيذية" not in art22.get("text", ""):
        e.append("[2j] Article 22 missing expected implementing-regulation mandate")
    art23 = arts.get("electricity_law_art_023", {})
    art23_txt = art23.get("text", "")
    if "يحل النظام محل" not in art23_txt or "56" not in art23_txt or "1426" not in art23_txt:
        e.append("[2j] Article 23 must contain the named repeal/replace clause for the M/56 "
                 "(1426H) Law (يحل النظام محل ... رقم (م / 56) ... 1426هـ)")
    art23_label = art23.get("number_label_ar")
    if art23_label != "المادة الثالثة والعشرون":
        e.append("[2j] Article 23 number_label_ar must be 'المادة الثالثة والعشرون', got %r" % art23_label)

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
        print("FAIL: %d error(s) in Electricity Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Electricity Law (نظام الكهرباء)")
    print("  - 23 records: 23 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (the Law has had no amendments)")
    print("  - 9 chapters (الفصل الأول..التاسع)")
    print("  - CURRENT VERSION CONFIRMED: Royal Decree M/44, 16/5/1442H -- the in-force")
    print("    Electricity Law, which by its own Article 23 repealed/replaced the older")
    print("    M/56 (20/10/1426H) Electricity Law (named repeal-and-replace clause).")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa checked first but unreachable this")
    print("    pass (connection reset / HTTP 503), Wayback egress-blocked (not circumvented);")
    print("    full verbatim text from nezams.com (single clean born-digital HTML aggregator,")
    print("    no scan/OCR/ligature defects), all governing metadata cross-verified against")
    print("    multiple independent sources (BOE/Umm Al-Qura via WebSearch, Lexis Middle East,")
    print("    SERA's own site, qanoonsa.com). Re-verification vs laws.boe.gov.sa recommended.")
    print("  - OLDER M/56 LAW: superseded/replaced by M/44 (Article 23) but retains a separate")
    print("    historical BOE lawId; its Article-13 committee continues transitionally (per")
    print("    Decree M/44 clause 6) only for cases filed before the new Law took effect.")
    print("  - Implementing Regulations (Article 22: Minister's + Council's, plus the")
    print("    violation-enforcement regulation) exist and are flagged as companion candidates,")
    print("    NOT ingested this pass (one-instrument-per-pass).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
