#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Mental Health Care Law track (نظام
الرعاية الصحية النفسية, Royal Decree M/56, 20/9/1435H -- the currently
in-force Mental Health Care Law).

30 records: 30 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (nezams.com's own metadata
states "لم يجرى عليه تعديل" -- consistent with no verified amended text having
been obtained this pass). No formal division into أبواب/فصول (chapter_
structure carries a SINGLE entry, "بدون تقسيم إلى أبواب أو فصول", mirroring
this corpus's existing health_system_law convention; confirmed by the absence
of any "الباب"/"الفصل" token in the fetched nezams.com page).

VERIFICATION TIER -- TIER_3. See the generator docstring and the source
artifact's verification_methodology_note: laws.boe.gov.sa was checked FIRST
but is unreachable this pass ("Connection reset by peer" on direct curl);
web.archive.org was explicitly attempted this pass and returned a direct HTTP
403 (not retried, per this session's proxy policy). The verbatim text of all
30 articles, the Royal Decree preamble, and the Council of Ministers
Resolution text were extracted from nezams.com (a single clean born-digital
HTML aggregator), with governing metadata and Article 4's wording specifically
cross-checked against saudipedia.com (a second, independent secondary source).
This validator does not re-adjudicate provenance; it only checks internal
self-consistency of the ingested text and that every discrepancy is still
recorded -- including the UNCONFIRMED Al-Riyadh-newspaper-reported Council of
Ministers amendment to Article 4, which this track deliberately does NOT
reflect (no verbatim replacement text could be obtained this pass; see
known_unresolved_discrepancies: mental_health_law_alriyadh_com_amendment_
unconfirmed).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "mental_health_law", "law", "official_source",
                   "mental_health_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "mental_health_law", "law", "verified",
                       "mental_health_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "mental_health_law", "law", "verified",
                       "mental_health_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "mental_health_law_arabic_legal_llm",
                   "mental_health_law_legal_llm_001_030.json")
N = 30
KEY_RE = r"mental_health_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 30, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # no أبواب/فصول -- single "بدون تقسيم" entry

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
    "mental_health_law_boe_unreachable_two_secondary_sources",
    "mental_health_law_alriyadh_com_amendment_unconfirmed",
    "mental_health_law_implementing_regulation_not_ingested_52_pages",
    "mental_health_law_preamble_digit_form_not_normalized",
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
        e.append("[1c] expected %d chapter_structure entr(y/ies), got %d"
                 % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))
    if chs and chs[0].get("label_ar") != "بدون تقسيم إلى أبواب أو فصول":
        e.append("[1c] single chapter_structure entry must be labeled "
                 "'بدون تقسيم إلى أبواب أو فصول'")

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
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
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
        e.append("[2k] missing amendment_history (must record the founding M/56 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/56" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/56")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/56)" \
            or src.get("decree_date_hijri") != "20/9/1435":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/56, 20/9/1435H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no confirmed amendment text was obtained)")
    if not src.get("preamble_ar") or "م/56" not in src.get("preamble_ar", "") \
            or "الرعاية الصحية النفسية" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "م/56 decree and نظام الرعاية الصحية النفسية")
    if not src.get("com_resolution_ar") or "مجلس الوزراء" not in src.get("com_resolution_ar", ""):
        e.append("[2j] com_resolution_ar (CoM Resolution 366 full text) must be present")

    art1 = arts.get("mental_health_law_art_001", {})
    if "المنشأة العلاجية النفسية" not in art1.get("text", "") \
            or "الاضطراب النفسي" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (المنشأة العلاجية النفسية / الاضطراب النفسي)")
    art3 = arts.get("mental_health_law_art_003", {})
    if "مجلس المراقبة العام" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected General Monitoring Council formation clause")
    art4 = arts.get("mental_health_law_art_004", {})
    if "يختص مجلس المراقبة العام" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected General Monitoring Council competencies clause "
                 "(this track deliberately retains the ORIGINAL wording -- see "
                 "known_unresolved_discrepancies: mental_health_law_alriyadh_com_amendment_unconfirmed)")
    art9 = arts.get("mental_health_law_art_009", {})
    if "حقوق المرضى النفسيين" not in art9.get("text", ""):
        e.append("[2j] Article 9 missing expected patient-rights heading")
    art29 = arts.get("mental_health_law_art_029", {})
    if "اللائحة التنفيذية" not in art29.get("text", "") or "تسعين" not in art29.get("text", ""):
        e.append("[2j] Article 29 missing expected implementing-regulation mandate (اللائحة التنفيذية/تسعين)")
    art30 = arts.get("mental_health_law_art_030", {})
    if "يعمل بهذا النظام" not in art30.get("text", "") or "تسعين" not in art30.get("text", ""):
        e.append("[2j] Article 30 missing expected entry-into-force clause (تسعين يوما)")
    art30_label = art30.get("number_label_ar")
    if art30_label != "المادة الثلاثون":
        e.append("[2j] Article 30 number_label_ar must be 'المادة الثلاثون', got %r" % art30_label)

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
        print("FAIL: %d error(s) in Mental Health Care Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Mental Health Care Law (نظام الرعاية الصحية النفسية)")
    print("  - 30 records: 30 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة")
    print("  - No formal division into أبواب/فصول (confirmed: zero occurrences of either token")
    print("    in the fetched nezams.com page); single chapter_structure entry covers 1-30")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/56, 20/9/1435H (CoM Resolution 366, 10/9/1435H;")
    print("    Shura Resolutions 75/61 and 34/18). Brand-new base-law track, not previously in")
    print("    this corpus.")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa checked first but unreachable this")
    print("    pass (connection reset); web.archive.org explicitly attempted and returned HTTP 403")
    print("    (not retried). Full verbatim text from nezams.com (single clean born-digital HTML")
    print("    aggregator); governing metadata + Article 4 wording cross-checked for identity")
    print("    against saudipedia.com (second independent secondary source) and moh.gov.sa (decree")
    print("    identity, third official source). Re-verify verbatim text vs laws.boe.gov.sa when")
    print("    reachable.")
    print("  - UNRESOLVED: Al-Riyadh newspaper (alriyadh.com/1821370) reports a Council of Ministers")
    print("    amendment to Article 4 that could NOT be verified this pass by any available method")
    print("    (curl: broken cert chain on alriyadh.com's own server; WebFetch: HTTP 503 direct and")
    print("    via Wayback; r.jina.ai: HTTP 403). Article 4 is retained with its ORIGINAL wording;")
    print("    NOT marked معدلة. See known_unresolved_discrepancies for the full detail and a")
    print("    high-priority follow-up recommendation.")
    print("  - Implementing Regulation (Article 29 mandate; 3rd edition, 1442H/2021G, 52 pages per")
    print("    moh.gov.sa) exists and is flagged as a follow-up candidate (mental_health_regulation),")
    print("    NOT ingested this pass -- pdftotext showed reversed RTL character order requiring")
    print("    careful correction before any text could be trusted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
