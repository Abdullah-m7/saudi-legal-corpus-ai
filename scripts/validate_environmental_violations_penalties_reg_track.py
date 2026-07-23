#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation for Recording Violations
and Imposing Penalties under the (General) Environmental Law track
(اللائحة التنفيذية لضبط المخالفات وإيقاع العقوبات لنظام البيئة).

10 records: 8 numbered articles (المادة الأولى .. الثامنة) + 2 appendix form
templates (الملحق (١) نموذج محضر ضبط، الملحق (٢) نموذج محضر تحقيق). All 10 are
اصلية (the amending decision 15101619 re-issued the regulation WHOLESALE and did
not designate any article as معدلة/مضافة/ملغاة). Track-level:
consolidated_amended_law=true, legal_status ساري, with the self-supersession of
the original 312186/1/1442 version documented.

VERIFICATION TIER (TIER_2) -- see the generator docstring and the official_source
JSON's verification_methodology_note: laws.boe.gov.sa checked FIRST but has NO
dedicated lawId page for this Implementing Regulation; PRIMARY full text is
qanoonsa.com/p/505504 (server-rendered, consolidated in-force text), with the
appendix corroborated on qistas.com and the amending decision on
qanoonsa.com/p/505503, and the citation cross-verified across mewa.gov.sa,
uqn.gov.sa and istitlaa.ncc.gov.sa. This validator only checks internal
self-consistency of the ingested text and that every discrepancy is disclosed.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_violations_penalties",
                   "official_source",
                   "environmental_violations_penalties_reg_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "environmental_violations_penalties",
                       "verified",
                       "environmental_violations_penalties_reg_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "environmental_violations_penalties",
                       "verified",
                       "environmental_violations_penalties_reg_verified_summary.json")
LLM = os.path.join(ROOT, "data",
                   "environmental_violations_penalties_arabic_legal_llm",
                   "environmental_violations_penalties_reg_legal_llm_001_010.json")

N_ARTICLES = 8
N_APPENDICES = 2
N_RECORDS = 10
ART_RE = r"environmental_violations_penalties_reg_art_(\d{3})$"
APP_RE = r"environmental_violations_penalties_reg_appendix_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 10, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

FLAGGED_DISCREPANCY_KEYS = {
    "environmental_violations_penalties_reg_gap_map_candidate_confirmed",
    "environmental_violations_penalties_reg_boe_no_dedicated_page",
    "environmental_violations_penalties_reg_wholesale_reissuance_not_itemized",
    "environmental_violations_penalties_reg_original_1442_text_not_diffable",
    "environmental_violations_penalties_reg_gregorian_original_date_not_pinpointed",
    "environmental_violations_penalties_reg_appendices_are_form_templates",
    "environmental_violations_penalties_reg_source_spacing_artifact_fixed",
    "environmental_violations_penalties_reg_primary_gov_fulltext_not_directly_fetchable",
}
AR = "ء-ي"
# tashkeel/harakat only (U+064B-0652 marks, U+0653-0658 madda/hamza marks,
# U+065F, U+0670 superscript alef); deliberately EXCLUDES Arabic-Indic digits
# U+0660-0669 so they are not mistaken for diacritics.
TASHKEEL = re.compile("[ً-ْٓ-ٰٟ٘]")


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

    # [1] structure counts
    if len(arts) != N_RECORDS:
        e.append("[1] %d records != %d" % (len(arts), N_RECORDS))
    if src.get("article_count") != N_ARTICLES:
        e.append("[1] article_count field != %d" % N_ARTICLES)
    if src.get("appendix_count") != N_APPENDICES:
        e.append("[1] appendix_count field != %d" % N_APPENDICES)
    if src.get("record_count") != N_RECORDS:
        e.append("[1] record_count field != %d" % N_RECORDS)

    art_nums, app_nums = [], []
    for k, a in arts.items():
        ma, mp = re.match(ART_RE, k), re.match(APP_RE, k)
        if ma:
            art_nums.append(int(ma.group(1)))
            if a.get("is_appendix") is not False:
                e.append("[1] %s: article key must have is_appendix False" % k)
        elif mp:
            app_nums.append(int(mp.group(1)))
            if a.get("is_appendix") is not True:
                e.append("[1] %s: appendix key must have is_appendix True" % k)
        else:
            e.append("[1] %s: does not match article/appendix key pattern" % k)
    if sorted(art_nums) != list(range(1, N_ARTICLES + 1)):
        e.append("[1] article numbers not 1..%d: %s" % (N_ARTICLES, sorted(art_nums)))
    if sorted(app_nums) != list(range(1, N_APPENDICES + 1)):
        e.append("[1] appendix numbers not 1..%d: %s" % (N_APPENDICES, sorted(app_nums)))

    # [2] per-record content + status
    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != "UNCHANGED":
            e.append("[2] %s: expected status UNCHANGED, got %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: structure_status divergence" % k)
        if ls != "اصلية":
            e.append("[2] %s: all records must be اصلية (wholesale re-issuance, no "
                     "per-article amendment designation), got %r" % (k, ls))
        if a.get("history"):
            e.append("[2] %s: article-level history must be empty (amendment is "
                     "track-level wholesale re-issuance)" % k)
        t = a.get("text", "")
        if not t.strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[A-Za-z<>&]", t):
            e.append("[2] %s: latin/html leftovers" % k)
        if not a.get("title_ar"):
            e.append("[2] %s: missing title_ar" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if TASHKEEL.search(t):
            e.append("[2] %s: residual tashkeel (should be stripped uniformly)" % k)
        if _bad_tatweel(t):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "\xa0" in t:
            e.append("[2f] %s: residual non-breaking-space artifact" % k)
        if "​" in t or "‏" in t or "‎" in t:
            e.append("[2f] %s: residual zero-width/bidi artifact" % k)
        if "“" in t or "”" in t:
            e.append("[2f] %s: residual curly-quote artifact" % k)
        if "  " in t:
            e.append("[2f] %s: residual double-space artifact" % k)
        if "الش عب" in t:
            e.append("[2g] %s: unresolved 'الش عب' spacing artifact" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st, 0), want))

    # [2c] chapter_structure coverage (articles 1-8, appendices 1-2)
    chs = src.get("chapter_structure") or []
    art_cov, app_cov = set(), set()
    for ch in chs:
        if "articles" in ch:
            lo, hi = (int(x) for x in ch["articles"].split("-"))
            art_cov |= set(range(lo, hi + 1))
        if "appendices" in ch:
            lo, hi = (int(x) for x in ch["appendices"].split("-"))
            app_cov |= set(range(lo, hi + 1))
    if art_cov != set(range(1, N_ARTICLES + 1)):
        e.append("[2c] chapter_structure article coverage != 1..%d: %s" % (N_ARTICLES, sorted(art_cov)))
    if app_cov != set(range(1, N_APPENDICES + 1)):
        e.append("[2c] chapter_structure appendix coverage != 1..%d: %s" % (N_APPENDICES, sorted(app_cov)))

    # [2d] methodology + discrepancies
    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    # [2k] amendment history + supersession
    ah = src.get("amendment_history")
    if not ah:
        e.append("[2k] missing amendment_history")
    else:
        decrees = " ".join(str(h.get("decree", "")) + str(h.get("decree_ar_indic", "")) for h in ah)
        if "312186/1/1442" not in decrees:
            e.append("[2k] amendment_history must reference founding decree 312186/1/1442")
        if "15101619" not in decrees:
            e.append("[2k] amendment_history must reference amending decree 15101619")
    sup = src.get("supersession")
    if not sup or sup.get("supersedes_named_predecessor") is not True:
        e.append("[2k] missing/incorrect supersession block (self-supersession of the "
                 "312186/1/1442 version by 15101619)")
    elif "312186/1/1442" not in str(sup.get("predecessor_decree", "")):
        e.append("[2k] supersession predecessor_decree must be 312186/1/1442")

    # [2j] anchor facts
    if src.get("decree") != "قرار وزير البيئة والمياه والزراعة رقم (312186/1/1442)" \
            or src.get("decree_date_hijri") != "4/6/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with verified 312186/1/1442, 4/6/1442H")
    if src.get("amending_decree_date_hijri") != "26/4/1446":
        e.append("[2j] amending_decree_date_hijri must be 26/4/1446")
    if src.get("gazette_ar", "").find("5055") < 0:
        e.append("[2j] gazette_ar must reference Umm Al-Qura issue 5055")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True")
    if src.get("base_law_track") != "environmental":
        e.append("[2j] base_law_track must be 'environmental'")
    if "الثامنة والأربع" not in src.get("legal_basis_ar", ""):
        e.append("[2j] legal_basis_ar must cite Article 48 (الثامنة والأربعون) of the Environmental Law")
    art1 = arts.get("environmental_violations_penalties_reg_art_001", {})
    if "المؤسسة العامة للمحافظة على الشعب المرجانية" not in art1.get("text", ""):
        e.append("[2j] Article 1 must contain the post-1445H reference to المؤسسة العامة "
                 "للمحافظة على الشعب المرجانية (evidence Art.1 changed in the amendment)")
    art4 = arts.get("environmental_violations_penalties_reg_art_004", {})
    if "100" not in art4.get("text", "") and "١٠٠" not in art4.get("text", ""):
        e.append("[2j] Article 4 must contain the 100,000-riyal competent-authority threshold")
    app1 = arts.get("environmental_violations_penalties_reg_appendix_001", {})
    if "نموذج محضر ضبط" not in app1.get("text", "") or "م / ١٦٥" not in app1.get("text", ""):
        e.append("[2j] Appendix 1 must preserve the محضر ضبط form referencing Royal Decree م/165")

    # [4] verified records
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_RECORDS:
        e.append("[4] %d verified records != %d" % (len(ver), N_RECORDS))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N_RECORDS:
        e.append("[4b] summary record_count != %d" % N_RECORDS)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if not summary.get("supersession"):
        e.append("[4b] summary missing supersession block")

    # [5] LLM layer
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_RECORDS or len(recs) != N_RECORDS:
        e.append("[5] llm count != %d" % N_RECORDS)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != "unchanged":
            e.append("[5] %s: llm source_trust.source_status must be 'unchanged'" % r["article_key"])
        if r.get("text_summarized_or_paraphrased") is not False:
            e.append("[5] %s: text_summarized_or_paraphrased must be False" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Environmental Violations & Penalties Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation for Recording Violations and Imposing Penalties "
          "under the Environmental Law")
    print("  - 10 records: 8 numbered articles + 2 appendix form templates; all 10 اصلية")
    print("  - Founding: Ministerial Decision (312186/1/1442), 4/6/1442H, under Article 48")
    print("    of the Environmental Law (Royal Decree M/165, 19/11/1441H)")
    print("  - Wholly re-issued/amended by Ministerial Decision (15101619), 26/4/1446H")
    print("    (30 Oct 2024, Umm Al-Qura issue 5055) — its clause (ثانيا) states the")
    print("    re-issued regulation 'تحل محل' (replaces) the original 312186/1/1442 version")
    print("    (self-supersession documented; no external named-predecessor repealed)")
    print("  - VERIFICATION TIER: TIER_2 — laws.boe.gov.sa checked first, NO dedicated lawId")
    print("    page for this Implementing Regulation; PRIMARY full text qanoonsa.com/p/505504")
    print("    (server-rendered consolidated in-force text), appendix corroborated on")
    print("    qistas.com, amending decision on qanoonsa.com/p/505503, citation cross-verified")
    print("    across mewa.gov.sa, uqn.gov.sa (Umm Al-Qura 5055) and istitlaa.ncc.gov.sa")
    print("  - LEGAL STATUS: all اصلية — the 1446H amendment re-issued the regulation")
    print("    WHOLESALE without itemising per-article changes; consolidated_amended_law=true")
    print("    at track level. Positive evidence Article 1 changed (now references المؤسسة")
    print("    العامة للمحافظة على الشعب المرجانية, created by CoM 406, 14/5/1445H); a precise")
    print("    per-article diff vs the 1442H original could not be performed (disclosed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
