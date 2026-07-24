#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Rights of
Persons with Disabilities Law track (اللائحة التنفيذية لنظام حقوق الأشخاص ذوي
الإعاقة; 45 records, ALL اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 12 chapters فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/disability_rights_regulation/law/official_source/
disability_rights_regulation_official_source.json's verification_methodology_note
for the full account: PRIMARY source is the official Umm al-Qura Gazette
portal (uqn.gov.sa) itself -- direct HTML text, not a scanned image --
cross-checked verbatim article-by-article against qanoonsa.com (an
independent secondary aggregator) -> TIER_2. laws.boe.gov.sa shares the base
Law's lawId page rather than hosting a dedicated page for this Regulation,
and was unreachable live this pass (connection reset), not circumvented. A
third source (argaam.com) claims 11 chapters rather than the 12 shown by the
primary uqn.gov.sa text; this is disclosed, not silently resolved. This
validator does not re-adjudicate provenance; it only checks internal
self-consistency and that every discrepancy is still recorded.

MATERIAL FACTS checked: 12-chapter structure (chapter_structure covers
exactly articles 1-45 with no gaps/overlaps); all 45 articles اصلية with
empty history; Article 31 base-law cross-reference; Article 43's reference
to الباب الرابع من النظام (the base law's Violations & Penalties chapter,
articles 21-28) as the origin of its closing-provisions mandate.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "disability_rights_regulation", "law", "official_source",
                   "disability_rights_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "disability_rights_regulation", "law", "verified",
                       "disability_rights_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "disability_rights_regulation", "law", "verified",
                       "disability_rights_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "disability_rights_regulation_arabic_legal_llm",
                   "disability_rights_regulation_legal_llm_001_045.json")
N = 45
KEY_RE = r"disability_rights_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 45, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 12  # 12 فصول

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "disability_rights_regulation_chapter_count_11_vs_12_discrepancy",
    "disability_rights_regulation_resolution_number_26_secondary_source_only",
    "disability_rights_regulation_gazette_issue_number_5033_secondary_source_only",
    "disability_rights_regulation_boe_shares_base_law_lawid_unreachable",
    "disability_rights_regulation_egyptian_law_name_collision_warning",
    "disability_rights_regulation_no_amendments_since_enactment",
    "disability_rights_regulation_annex_1_table_not_modeled",
    "disability_rights_regulation_qanoonsa_minor_typo_variants",
    "disability_rights_regulation_tashkeel_and_tatweel_normalized",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        # legitimate uses: the alphabetic list-marker "هـ-" and the Hijri-date
        # suffix "هـ" both have "ه" immediately before the tatweel run.
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

    # continuous 1..45, no gaps/dupes
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    # 12-chapter structure covers exactly 1..45
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
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (chapter title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if a.get("history"):
            e.append("[2i] %s: no article in this unamended regulation should carry history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # this corpus normalizes enumeration digits to Western glyphs
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2g] %s: residual Eastern-Arabic-Indic digit found (must be normalized "
                     "to Western digits per known discrepancy note)" % k)

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
    if not ah:
        e.append("[2k] missing amendment_history (must record founding resolution)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "26" not in decrees:
            e.append("[2k] amendment_history must reference founding resolution (26)")

    # spot-checks anchoring key facts
    art1 = arts.get("disability_rights_regulation_art_001", {}).get("text", "")
    if "التصميم الشامل" not in art1 or "الترتيبات التيسيرية" not in art1:
        e.append("[2j] Article 1 missing expected definitions (التصميم الشامل / الترتيبات التيسيرية)")
    art3 = arts.get("disability_rights_regulation_art_003", {}).get("text", "")
    if "مشهد الإعاقة" not in art3:
        e.append("[2j] Article 3 missing expected مشهد الإعاقة (disability certification) provision")
    art43 = arts.get("disability_rights_regulation_art_043", {}).get("text", "")
    if "الباب الرابع من النظام" not in art43:
        e.append("[2j] Article 43 missing expected cross-reference to الباب الرابع من النظام "
                 "(base law's Violations & Penalties chapter)")
    art45 = arts.get("disability_rights_regulation_art_045", {}).get("text", "")
    if "الجريدة الرسمية" not in art45:
        e.append("[2j] Article 45 missing expected publication/effective-date clause")

    if src.get("decree") != "قرار مجلس إدارة هيئة رعاية الأشخاص ذوي الإعاقة رقم (26)" \
            or src.get("decree_date_hijri") != "29/10/1445":
        e.append("[2j] decree/decree_date_hijri mismatch with Resolution 26, 29/10/1445H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendments exist for this regulation)")
    if src.get("law_component") != "regulation":
        e.append("[2j] law_component must be 'regulation'")
    pre = src.get("preamble_ar", "")
    if not pre or "شوال" not in pre or "اللائحة التنفيذية لنظام حقوق الأشخاص ذوي الإعاقة" not in pre:
        e.append("[2j] preamble_ar must be present and reference the 29 Shawwal 1445H approval "
                 "and the regulation's name")
    if "الحادية والثلاثين" not in pre or "م/27" not in pre:
        e.append("[2j] preamble_ar must reference Article 31 of the base law (M/27) as legal basis")

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
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("consolidated_amended_law") is not False:
        e.append("[4b] summary consolidated_amended_law must be False")

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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Disability Rights Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Rights of Persons with Disabilities Law")
    print("  (اللائحة التنفيذية لنظام حقوق الأشخاص ذوي الإعاقة)")
    print("  - 45 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- no amendment found since issuance")
    print("  - 12 chapters (فصول): أحكام عامة (1-3), إمكانية الوصول (4-6), إمكانية الوصول والترتيبات")
    print("    التيسيرية في الدعوى الجزائية (7), حق التنقل (8-12), حق التعليم (13-20), حق الصحة (21-28),")
    print("    التوظيف وفرص العمل (29-32), أماكن العبادة ومرافقها (33), الوعي المجتمعي (34), حق الوصول")
    print("    للمحتوى المقروء والمرئي والمسموع (35-37), الدعم الاجتماعي والاقتصادي (38-42), الأحكام")
    print("    الختامية (43-45)")
    print("  - VERIFICATION TIER: TIER_2 -- PRIMARY official Umm al-Qura Gazette portal (uqn.gov.sa,")
    print("    direct HTML text, not scanned) cross-checked verbatim article-by-article against")
    print("    qanoonsa.com (independent secondary aggregator); laws.boe.gov.sa shares the base law's")
    print("    lawId page and was unreachable live this pass (connection reset, not circumvented)")
    print("  - Resolution No. (26) of the Board of Directors of the Authority for the Care of Persons")
    print("    with Disabilities, 29/10/1445H (29 Shawwal, ~8 May 2024G), issued under Article 31 of")
    print("    the base Law (Royal Decree M/27, 11/2/1445H); published Umm al-Qura issue 5033 (per")
    print("    qanoonsa.com secondary source, 24 May 2024G -- not shown explicitly on uqn.gov.sa)")
    print("  - CHAPTER-COUNT DISCREPANCY DISCLOSED: primary source shows 12 chapters; a third source")
    print("    (argaam.com) states 11 -- this track follows the primary uqn.gov.sa 12-chapter text")
    print("  - Annex (1) (assistive-devices table) NOT modeled as an article, matching corpus convention")
    return 0


if __name__ == "__main__":
    sys.exit(main())
