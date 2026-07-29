#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the NCA "Rules Organizing the Reporting of
Cybersecurity Violations" track (قواعد تنظيم الإبلاغ عن مخالفات الأمن
السيبراني; 8 records, all اصلية; flat structure -- NO أبواب/فصول grouping
at all, just 8 numbered مادة articles).

VERIFICATION TIER -- see the generator's module docstring and
sources/nca_cybersecurity_violations_reporting_rules/law/official_source/
nca_cybersecurity_violations_reporting_rules_official_source.json's
verification_methodology_note for the full account. Summary: TIER_2.
A single official/primary source (an NCA cdn.nca.gov.sa PDF) was reached and
internally cross-checked by two independent methods (clean pdftotext -layout
extraction + direct visual read of rendered page images, in full agreement),
plus topical-only secondary corroboration from two independent news outlets
-- NOT TIER_1, because (a) no second independent OFFICIAL source carrying
this specific instrument's full text was reached this pass (no dedicated
uqn.gov.sa gazette page could be located for this instrument, unlike its
companion investigation-rules instrument which does have one), and (b) the
NCA Board of Directors decision number/date approving THIS specific
instrument could not be independently confirmed -- a direct fetch of the
companion instrument's own uqn.gov.sa gazette page affirmatively confirmed
the number suggested in this track's commissioning brief (ع26/1/1/1ت,
22/08/1447H) belongs to that OTHER, companion instrument, not this one. This
validator does not re-adjudicate any of this; it only checks internal
self-consistency of the text this track actually ingests, and that every
discrepancy remains recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "nca_cybersecurity_violations_reporting_rules", "law",
                   "official_source",
                   "nca_cybersecurity_violations_reporting_rules_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "nca_cybersecurity_violations_reporting_rules", "law",
                       "verified", "nca_cybersecurity_violations_reporting_rules_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "nca_cybersecurity_violations_reporting_rules", "law",
                       "verified", "nca_cybersecurity_violations_reporting_rules_verified_summary.json")
LLM = os.path.join(ROOT, "data", "nca_cybersecurity_violations_reporting_rules_arabic_legal_llm",
                   "nca_cybersecurity_violations_reporting_rules_legal_llm_001_008.json")
N = 8
KEY_RE = r"nca_cybersecurity_violations_reporting_rules_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 8, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = ("NCA_OFFICIAL_PDF_PRIMARY_TEXTLAYER_X_VISUAL_RENDER_CROSSCHECK_X_NEWS_TOPICAL_"
          "SECONDARY_TIER2_DECISION_NUMBER_UNCONFIRMED_CITED_NUMBER_BELONGS_TO_COMPANION")
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat instrument -- no أبواب/فصول, single leaf range 1-8
EXPECTED_LABELS = {
    1: "المادة الأولى", 2: "المادة الثانية", 3: "المادة الثالثة", 4: "المادة الرابعة",
    5: "المادة الخامسة", 6: "المادة السادسة", 7: "المادة السابعة", 8: "المادة الثامنة",
}
FLAGGED_DISCREPANCY_KEYS = {
    "nca_reporting_rules_decision_number_belongs_to_companion_not_this_instrument",
    "nca_reporting_rules_no_dedicated_uqn_gazette_page_located",
    "nca_reporting_rules_istitlaa_platform_unreachable",
    "nca_reporting_rules_no_baab_fasl_flat_8_madda_structure",
    "nca_reporting_rules_numeral_conventions_and_decree_date_order_preserved",
    "nca_reporting_rules_legal_status_basis_disclosed",
    "nca_reporting_rules_secondary_corroboration_topical_only",
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
        secs = ch.get("sections")
        if not secs:
            lo, hi = (int(x) for x in ch["articles"].split("-"))
            yield (lo, hi)
            continue
        for sec in secs:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            yield (slo, shi)


def main():
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1

    e = []
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field %r != %d" % (src.get("article_count"), N))
    seen = set()
    for k in arts:
        m = re.match(KEY_RE, k)
        if not m:
            e.append("[1] %s: does not match key pattern" % k)
        else:
            seen.add(int(m.group(1)))
    if seen != set(range(1, N + 1)):
        e.append("[1] article numbers not a clean 1..%d run: %s" % (N, sorted(seen)))

    chs = src.get("chapter_structure") or []
    if len(chs) != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapter_structure entries (flat instrument, no "
                  "أبواب/فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, len(chs)))
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
            e.append("[1c] chapter_structure missing article(s): %s" % missing)
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra)

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track")
    if src.get("law_component") != "regulation":
        e.append("[1d] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "نافذ":
        e.append("[1d] legal_status_ar must be نافذ")

    # honest-citation-disclosure checks (this is the whole point of this track's tier)
    decree = src.get("decree") or ""
    if "غير مؤكَّد" not in decree and "غير مؤكد" not in decree:
        e.append("[1f] decree field must explicitly disclose the citation is unconfirmed "
                 "for this specific instrument")
    if "ع26" not in decree and "26/1/1/1" not in decree:
        e.append("[1f] decree field must mention the companion's decision number "
                 "(ع26/1/1/1ت) to disclose it does NOT apply to this instrument")
    if src.get("decree_date_hijri") != "غير مؤكد لهذا الصك تحديداً":
        e.append("[1f] decree_date_hijri must explicitly read 'غير مؤكد لهذا الصك تحديداً' "
                 "(not silently copied from the companion instrument)")

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or unexpected latin/html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: section_ar must be non-empty" % k)
        if a.get("article_title_ar") is None:
            e.append("[2] %s: article_title_ar must be present (empty string allowed)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "\xa0" in a["text"]:
            e.append("[2] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2] %s: residual curly-quote artifact detected" % k)
        if re.search(r"[‎‏‪-‮⁦-⁩]", a["text"]):
            e.append("[2] %s: residual bidi control character not stripped" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if a.get("number_label_ar") != EXPECTED_LABELS.get(n):
            e.append("[2i] %s: expected number_label_ar %r, got %r"
                     % (k, EXPECTED_LABELS.get(n), a.get("number_label_ar")))
        if ls != "اصلية":
            e.append("[3] %s: article %d expected اصلية (single confirmed edition), "
                     "got %r" % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: article %d must have empty history (اصلية-only track)" % (k, n))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    declared = src.get("status_counts") or {}
    for st in ALLOWED_STATUS:
        if declared.get(st, 0) != sc.get(st, 0):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

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

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("nca_cybersecurity_violations_reporting_rules_art_001", {})
    if "الممكنات النظامية" not in art1.get("text", "") or "م/١١٧" not in art1.get("text", ""):
        e.append("[2j] المادة الأولى missing expected reference to الممكنات النظامية (م/117)")
    art4 = arts.get("nca_cybersecurity_violations_reporting_rules_art_004", {})
    if "الدرجة الرابعة" not in art4.get("text", ""):
        e.append("[2j] المادة الرابعة missing expected 4th-degree-relative exclusion clause")
    art6 = arts.get("nca_cybersecurity_violations_reporting_rules_art_006", {})
    if "٥٠٬٠٠٠" not in art6.get("text", "") and "50" not in art6.get("text", ""):
        e.append("[2j] المادة السادسة missing expected 50,000 SAR reward cap")
    if "١٪" not in art6.get("text", "") and "1%" not in art6.get("text", ""):
        e.append("[2j] المادة السادسة missing expected 1%% collected-fine alternative")
    art8 = arts.get("nca_cybersecurity_violations_reporting_rules_art_008", {})
    if "تلغي كل ما" not in art8.get("text", ""):
        e.append("[2j] المادة الثامنة missing expected generic repeal clause")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"]); continue
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
        if "article_number" not in r:
            e.append("[4] %s: missing article_number field" % r["article_key"])
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("is_amended") is not False or r.get("is_repealed") is not False or r.get("is_added") is not False:
            e.append("[4] %s: expected all status flags False (اصلية-only track)" % r["article_key"])
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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in NCA Cybersecurity Violations Reporting Rules track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Rules Organizing the Reporting of Cybersecurity Violations (النطاق: قواعد")
    print("  تنظيم الإبلاغ عن مخالفات الأمن السيبراني)")
    print("  - 8 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة); flat structure, no أبواب/فصول")
    print("  - VERIFICATION TIER: TIER_2 -- primary source is an official PDF on the National")
    print("    Cybersecurity Authority's own site (cdn.nca.gov.sa), internally cross-checked via")
    print("    a clean text-layer extraction AND an independent visual read of rendered page")
    print("    images (full agreement), plus topical secondary corroboration from two")
    print("    independent news outlets")
    print("  - CITATION: the NCA Board decision number/date approving THIS specific instrument")
    print("    is explicitly UNCONFIRMED -- a direct fetch of the companion investigation-rules")
    print("    instrument's own uqn.gov.sa gazette page confirmed the number suggested in this")
    print("    track's commissioning brief (ع26/1/1/1ت, 22/08/1447H) belongs to that OTHER,")
    print("    companion instrument, not this one -- this is why the tier is TIER_2, not higher")
    return 0


if __name__ == "__main__":
    sys.exit(main())
