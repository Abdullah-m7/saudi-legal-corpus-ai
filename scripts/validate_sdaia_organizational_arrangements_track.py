#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the "Organizational Arrangements of the Saudi
Data and AI Authority (SDAIA)" track (16 records: 15 اصلية, 1 معدلة at the
per-بند level, 0 ملغاة, 0 مضافة; flat structure -- NO أبواب/فصول grouping,
and NO مادة numbering at all -- sixteen ordinal بند divisions instead).

VERIFICATION TIER -- see the generator's module docstring and
sources/sdaia_organizational_arrangements/law/official_source/
sdaia_organizational_arrangements_official_source.json's
verification_methodology_note for the full account: no laws.boe.gov.sa page
for this exact instrument could be located this pass. The PRIMARY source
actually used is an official PDF hosted on SDAIA's own website
(sdaia.gov.sa), reached via the r.jina.ai reader-proxy since direct
curl/WebFetch to sdaia.gov.sa fail domain-wide in this sandbox. A confirmed
lam-alif-ligature-reversal extraction artifact was corrected via disclosed,
cross-validated word-level reconstruction -- NOT pixel-level OCR, since this
pass could not obtain the PDF's raw bytes. This track is honestly assessed
at TIER_2, not TIER_1. This validator does not attempt to re-adjudicate any
of this; it only checks internal self-consistency of the text this track
actually ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "sdaia_organizational_arrangements", "law", "official_source",
                   "sdaia_organizational_arrangements_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "sdaia_organizational_arrangements", "law", "verified",
                       "sdaia_organizational_arrangements_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "sdaia_organizational_arrangements", "law", "verified",
                       "sdaia_organizational_arrangements_verified_summary.json")
LLM = os.path.join(ROOT, "data", "sdaia_organizational_arrangements_arabic_legal_llm",
                   "sdaia_organizational_arrangements_legal_llm_001_016.json")
N = 16
KEY_RE = r"sdaia_organizational_arrangements_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 15, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat instrument -- no أبواب/فصول, single leaf range 1-16

STATUS_UNCHANGED = ("SDAIA_OFFICIAL_SITE_PDF_PRIMARY_JINA_READER_PROXY_LIGATURE_ARTIFACT_"
                     "RECONSTRUCTED_X_QISTAS_LEXISMIDDLEEAST_SPA_CROSSCHECK_TIER2_BOE_PAGE_"
                     "NOT_LOCATED")
EXPECTED_STATUS_BY_KEY = {}  # every بند shares STATUS_UNCHANGED (status string is unaffected by
                             # legal_status_ar -- only legal_status_ar itself distinguishes اصلية
                             # from معدلة for بند خامساً)
AMENDED_KEYS = {"sdaia_organizational_arrangements_art_005"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "sdaia_organizational_arrangements_lam_alif_ligature_reversal_artifact",
    "sdaia_organizational_arrangements_band_not_madda_structure",
    "sdaia_organizational_arrangements_no_repeal_clause_confirmed_negative",
    "sdaia_organizational_arrangements_predecessor_absorption_confirmed_negative",
    "sdaia_organizational_arrangements_amended_clause_attribution_limited_confidence",
    "sdaia_organizational_arrangements_boe_page_not_located",
    "sdaia_organizational_arrangements_first_fiscal_year_low_confidence_reconstruction",
    "sdaia_organizational_arrangements_qistas_lexis_almirkaz_qanoniah_paywalled_beyond_excerpt",
}
EXPECTED_LABELS = {
    1: "البند أولاً", 2: "البند ثانياً", 3: "البند ثالثاً", 4: "البند رابعاً",
    5: "البند خامساً", 6: "البند سادساً", 7: "البند سابعاً", 8: "البند ثامناً",
    9: "البند تاسعاً", 10: "البند عاشراً", 11: "البند حادي عشر",
    12: "البند ثاني عشر", 13: "البند ثالث عشر", 14: "البند رابع عشر",
    15: "البند خامس عشر", 16: "البند سادس عشر",
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
    """Yield (lo, hi) for every leaf range in chapter_structure. This
    instrument has no أبواب/فصول nesting -- every top-level entry IS a leaf
    (no 'sections' key), so this is a flat single-level walk."""
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
        e.append("[1] %d بنود != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level chapter_structure entries (flat instrument, "
                  "no أبواب/فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] بند %d covered by more than one leaf range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing بند(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range بند(s): %s" % extra[:20])

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended بند missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        m = re.match(KEY_RE, k)
        if m:
            n_num = int(m.group(1))
            if a.get("number_label_ar") != EXPECTED_LABELS.get(n_num):
                e.append("[2i] %s: expected number_label_ar %r, got %r (this instrument uses "
                          "بند labels, not مادة)" % (k, EXPECTED_LABELS.get(n_num),
                                                     a.get("number_label_ar")))
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)
        if re.search(r"^[0-9٠-٩]+[-.\s]", a["text"]):
            e.append("[2h] %s: text begins with a residual list-numeral marker "
                      "(should be omitted per corpus convention)" % k)
        # confirm the disclosed lam-alif-ligature-reversal artifact was actually corrected --
        # these specific corrupted substrings must NOT appear anywhere in the final text
        for bad_substr in ("االعتبار", "اإلعتبار", "باالستقالل", "اآلتية", "التخاذ", "ألحكام",
                            "وحاسبها"):
            if bad_substr in a["text"]:
                e.append("[2h] %s: residual uncorrected lam-alif-ligature artifact %r found"
                          % (k, bad_substr))

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
        e.append("[2k] missing amendment_history (must record 292 and 195)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        if "292" not in decrees:
            e.append("[2k] amendment_history must reference قرار 292")
        if "195" not in decrees:
            e.append("[2k] amendment_history must reference قرار 195 (the amending resolution)")

    # spot-checks anchoring key facts established this pass
    art2 = arts.get("sdaia_organizational_arrangements_art_002", {})
    if "الشخصية الاعتبارية" not in art2.get("text", ""):
        e.append("[2j] بند ثانياً missing expected legal-personality clause")
    if "الاستقلال المالي والإداري" not in art2.get("text", ""):
        e.append("[2j] بند ثانياً missing expected financial/administrative independence clause")
    art3 = arts.get("sdaia_organizational_arrangements_art_003", {})
    if "الجهة المختصة" not in art3.get("text", ""):
        e.append("[2j] بند ثالثاً missing expected competent-authority mandate clause")
    art5 = arts.get("sdaia_organizational_arrangements_art_005", {})
    if "مجلس إدارة" not in art5.get("text", ""):
        e.append("[2j] بند خامساً missing expected board-of-directors clause")
    art10 = arts.get("sdaia_organizational_arrangements_art_010", {})
    if "مكتب إدارة البيانات الوطنية" not in art10.get("text", ""):
        e.append("[2j] بند عاشراً missing expected National Data Management Office clause")
    art16 = arts.get("sdaia_organizational_arrangements_art_016", {})
    if "الجريدة الرسمية" not in art16.get("text", ""):
        e.append("[2j] بند سادس عشر missing expected publication clause")
    if "تلغي" in art16.get("text", "") or "يلغي" in art16.get("text", ""):
        e.append("[2j] بند سادس عشر unexpectedly contains repeal language (confirmed negative "
                  "finding says this instrument has NO repeal clause)")
    if src.get("decree") != "قرار مجلس الوزراء رقم (292)" or src.get("decree_date_hijri") != "27/4/1441":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Resolution 292, 27/4/1441H")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (current text already reflects "
                  "the 195/1444H amendment)")

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
        print("FAIL: %d error(s) in SDAIA Organizational Arrangements track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Organizational Arrangements of the Saudi Data and AI Authority (SDAIA)")
    print("  - 16 records: 15 اصلية, 1 معدلة (بند خامساً) at the per-بند level (0 ملغاة, 0 مضافة)")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-16); NO مادة")
    print("    numbering -- sixteen ordinal بند divisions (أولاً-سادس عشر) instead")
    print("  - VERIFICATION TIER: TIER_2 -- primary source is an official PDF on SDAIA's own")
    print("    site (sdaia.gov.sa), reached via the r.jina.ai reader-proxy (direct fetch fails")
    print("    domain-wide in this sandbox), reconstructed via disclosed, cross-validated")
    print("    correction of a confirmed lam-alif-ligature-reversal extraction artifact (NOT")
    print("    pixel-level OCR), cross-checked against qistas.com, lexismiddleeast.com, and")
    print("    the Saudi Press Agency (for the founding Royal Order A/471); no laws.boe.gov.sa")
    print("    page for this exact instrument could be located this pass")
    print("  - Council of Ministers Resolution 292 (27/4/1441H / 24 Nov 2019G), amended by")
    print("    Resolution 195 (15/3/1444H); founding Royal Order A/471 (29/12/1440H)")
    print("    independently confirmed via the Saudi Press Agency's own verbatim text")
    print("  - CONFIRMED NEGATIVE FINDINGS: no repeal clause and no violations/penalties")
    print("    clause anywhere in this instrument; the pre-existing National Information")
    print("    Center (Royal Order A/293/1438H, CoM Resolution 495/1439H) was organizationally")
    print("    absorbed under SDAIA without either predecessor instrument being repealed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
