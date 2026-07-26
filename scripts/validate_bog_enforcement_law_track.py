#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Law of Enforcement before the Board of
Grievances track (37 records, all اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; five
أبواب: أحكام عامة 1-5, إجراءات التنفيذ 6-24 [split into four فصول: 6-9,
10-15, 16-19, 20-24], منازعات التنفيذ والدعاوى الناشئة عنه 25-29, الجرائم
والعقوبات 30-33, أحكام ختامية 34-37).

VERIFICATION TIER -- see the generator's module docstring and
sources/bog_enforcement_law/law/official_source/
bog_enforcement_law_official_source.json's verification_methodology_note for
the full account: laws.boe.gov.sa's LIVE portal was unreachable this pass
(HTTP 503 twice), and this sandbox's egress policy blocked fetching actual
Wayback Machine snapshot CONTENT (only the metadata-only availability lookup
succeeded, confirming one snapshot exists). This track therefore rests on a
SINGLE secondary aggregator (nezams.com) as primary full text -- a materially
lower tier than this corpus's BOE-Wayback-based tracks -- partially
cross-verified (Article 37 verbatim via independent WebSearch; chapter
structure via BOE's own SearchDetails summary; decree/gazette metadata via
Umm Al-Qura; ~20 of 37 articles spot-checked via muhamapp.com). This
validator does not attempt to re-adjudicate any of this; it only checks
internal self-consistency of the text this track actually ingests, and that
every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "bog_enforcement_law", "law", "official_source",
                   "bog_enforcement_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "bog_enforcement_law", "law", "verified",
                       "bog_enforcement_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "bog_enforcement_law", "law", "verified",
                       "bog_enforcement_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "bog_enforcement_law_arabic_legal_llm",
                   "bog_enforcement_law_legal_llm_001_037.json")
N = 37
KEY_RE = r"bog_tnf_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 37, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 5  # five أبواب; الباب الثاني has four nested فصول

STATUS_SINGLE_AGGREGATOR = ("NEZAMS_FULLTEXT_SINGLE_AGGREGATOR_X_UQN_GAZETTE_DECREE_METADATA_X_"
                             "WEBSEARCH_PARTIAL_VERBATIM_CROSSCHECK_X_MUHAMAPP_STRUCTURAL_PARTIAL_"
                             "LIVE_BOE_UNREACHABLE_WAYBACK_CONTENT_BLOCKED_BY_SANDBOX_EGRESS")
EXPECTED_STATUS_BY_KEY = {}  # every article shares STATUS_SINGLE_AGGREGATOR (all اصلية)
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "bog_enforcement_single_aggregator_tier",
    "bog_enforcement_art035_label_typo_corrected",
    "bog_enforcement_regulation_amended_not_ingested",
    "bog_enforcement_crossref_new_ordinary_enforcement_law_2026",
    "bog_enforcement_distinctness_confirmed_not_duplicate",
}
EXPECTED_CHAPTER_RANGES = {
    "الباب الأول": (1, 5),
    "الباب الثاني": (6, 24),
    "الباب الثالث": (25, 29),
    "الباب الرابع": (30, 33),
    "الباب الخامس": (34, 37),
}
EXPECTED_SECTION_RANGES = {
    "الفصل الأول": (6, 9),
    "الفصل الثاني": (10, 15),
    "الفصل الثالث": (16, 19),
    "الفصل الرابع": (20, 24),
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
    """Yield (lo, hi) for every leaf range in chapter_structure. الباب الثاني
    has four nested فصول (no direct 'articles' range of its own); every other
    باب is itself a leaf range."""
    for ch in chs:
        secs = ch.get("sections")
        if not secs:
            lo, hi = (int(x) for x in ch["articles"].split("-"))
            yield (lo, hi)
            continue
        for sec in secs:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            yield (slo, shi)


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
        e.append("[1c] expected %d top-level chapter_structure entries (five أبواب), "
                  "got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))
    for ch in chs:
        label = ch.get("label_ar")
        want = EXPECTED_CHAPTER_RANGES.get(label)
        if want is None:
            e.append("[1c] unexpected chapter label_ar %r" % label)
            continue
        secs = ch.get("sections")
        if secs:
            los = [int(s["articles"].split("-")[0]) for s in secs]
            his = [int(s["articles"].split("-")[1]) for s in secs]
            got = (min(los), max(his))
            for s in secs:
                slabel = s.get("label_ar")
                swant = EXPECTED_SECTION_RANGES.get(slabel)
                if swant is None:
                    e.append("[1c] unexpected section label_ar %r under %s" % (slabel, label))
                    continue
                slo, shi = (int(x) for x in s["articles"].split("-"))
                if (slo, shi) != swant:
                    e.append("[1c] %s: expected range %s, got %s" % (slabel, swant, (slo, shi)))
        else:
            lo, hi = (int(x) for x in ch["articles"].split("-"))
            got = (lo, hi)
        if got != want:
            e.append("[1c] %s: expected overall range %s, got %s" % (label, want, got))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one leaf range" % n)
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
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_SINGLE_AGGREGATOR)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
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
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)

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
        e.append("[2k] missing amendment_history (must record م/15)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        if "م/15" not in decrees:
            e.append("[2k] amendment_history must reference م/15")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("bog_tnf_art_001", {})
    if "نظام التنفيذ أمام ديوان المظالم" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected النظام definition")
    art4 = arts.get("bog_tnf_art_004", {})
    if "لا يجوز التنفيذ الجبري إلا بسند تنفيذي" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected السند التنفيذي definition")
    art9 = arts.get("bog_tnf_art_009", {})
    if "لا يترتب على عدم قبول طلب التنفيذ" not in art9.get("text", ""):
        e.append("[2j] Article 9 missing expected non-extinction clause")
    art18 = arts.get("bog_tnf_art_018", {})
    if "قاضي التنفيذ الواردة في نظام التنفيذ" not in art18.get("text", ""):
        e.append("[2j] Article 18 missing expected cross-reference to نظام التنفيذ (M/53)")
    art30 = arts.get("bog_tnf_art_030", {})
    if "يعاقب الموظف العام" not in art30.get("text", ""):
        e.append("[2j] Article 30 missing expected penal clause")
    art33 = arts.get("bog_tnf_art_033", {})
    if "من جرائم الفساد" not in art33.get("text", ""):
        e.append("[2j] Article 33 missing expected corruption-crime classification")
    art37 = arts.get("bog_tnf_art_037", {})
    if "ثلاثين" not in art37.get("text", ""):
        e.append("[2j] Article 37 missing expected 30-day regulation-issuance clause")
    if art37.get("number_label_ar") != "المادة السابعة والثلاثون":
        e.append("[2j] Article 37 number_label_ar mismatch")
    art35 = arts.get("bog_tnf_art_035", {})
    if art35.get("number_label_ar") != "المادة الخامسة والثلاثون":
        e.append("[2j] Article 35 number_label_ar must be the corrected "
                 "'المادة الخامسة والثلاثون' (see bog_enforcement_art035_label_typo_corrected)")
    if src.get("decree") != "المرسوم الملكي رقم (م/15)" or src.get("decree_date_hijri") != "27/1/1443":
        e.append("[2j] decree/decree_date_hijri mismatch with verified م/15, 27/1/1443هـ")

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
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_SINGLE_AGGREGATOR)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in BOG Enforcement Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Law of Enforcement before the Board of Grievances")
    print("  - 37 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة)")
    print("  - five أبواب: أحكام عامة (1-5), إجراءات التنفيذ (6-24; أربعة فصول:")
    print("    6-9, 10-15, 16-19, 20-24), منازعات التنفيذ والدعاوى الناشئة عنه (25-29),")
    print("    الجرائم والعقوبات (30-33), أحكام ختامية (34-37)")
    print("  - VERIFICATION TIER: SINGLE-AGGREGATOR (nezams.com full text) --")
    print("    laws.boe.gov.sa live portal unreachable (HTTP 503 x2), Wayback snapshot")
    print("    CONTENT blocked by sandbox egress policy (only availability lookup")
    print("    succeeded, confirming one snapshot at 20260215011202). Partial cross-")
    print("    verification: Art. 37 confirmed verbatim via independent WebSearch;")
    print("    chapter structure via BOE's own SearchDetails; decree/gazette metadata")
    print("    via Umm Al-Qura; ~20/37 articles spot-checked via muhamapp.com.")
    print("  - Royal Decree M/15 (27/1/1443H / ~4 Sep 2021G), CoM Resolution 73")
    print("    (23/1/1443H); effective 4/2/1445H per Administrative Judiciary Council")
    print("    Decision 16/1444/12 (16/12/1444H)")
    print("  - DISTINCTNESS CONFIRMED: genuinely separate from this corpus's")
    print("    already-ingested enforcement_law track (M/53, 98 articles, ordinary")
    print("    judiciary) -- M/15's own enacting decree explicitly carves out an")
    print("    exception from M/53's enacting decree; not a duplicate citation")
    print("  - Article 35 number_label_ar corrected from a disclosed nezams.com")
    print("    heading typo (missing و) -- legal text itself unaffected")
    print("  - Implementing Regulation (لائحة) NOT ingested this pass -- itself")
    print("    amended at least once (Reg. Art. 5/17); flagged as follow-up candidate")
    print("  - SIDE-FINDING flagged (out of scope): a brand-new ordinary نظام التنفيذ")
    print("    (65 articles, CoM Resolution 746) will eventually replace M/53 (the")
    print("    corpus's existing enforcement_law track) once it takes effect ~28 Oct 2026")
    return 0


if __name__ == "__main__":
    sys.exit(main())
