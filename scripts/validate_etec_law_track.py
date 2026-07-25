#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Statute (Organizational Regulation) of the
Education and Training Evaluation Commission track (18 records, 16 اصلية /
2 معدلة at the per-article level -- Articles 4 and 7 -- 0 ملغاة, 0 مضافة;
flat structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/etec/law/official_source/etec_law_official_source.json's
verification_methodology_note for the full account: the live laws.boe.gov.sa
portal was unreachable this pass (direct curl: "Connection reset by peer";
WebFetch: HTTP 503) for lawId c7a054a8-6dbc-4323-9405-aa3f00bd5985. This
track instead rests on TWO INDEPENDENT Wayback Machine snapshots of that
SAME official BOE page (19 June 2024 and 12 December 2025), which produced a
FULL LITERAL MATCH across all 18 articles and both embedded amendment-note
popups. Per this corpus's own documented methodology
(reports/verification_tiers/VERIFICATION_TIERS_METHODOLOGY_AR.md section 5),
this exact double-independent-Wayback-snapshot pattern for the official BOE
portal -- with no reliance on any private/secondary source for the primary
text -- is treated as TIER_1_PRIMARY_MULTI_SOURCE. This validator does not
re-adjudicate any of this; it only checks internal self-consistency of the
text this track actually ingests, and that every discrepancy is still
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
SRC = os.path.join(ROOT, "sources", "etec", "law", "official_source",
                   "etec_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "etec", "law", "verified",
                       "etec_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "etec", "law", "verified",
                       "etec_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "etec_arabic_legal_llm",
                   "etec_law_legal_llm_001_018.json")
N = 18
KEY_RE = r"etec_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 16, "معدلة": 2, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat statute -- no أبواب/فصول, single leaf range 1-18

STATUS_UNCHANGED = ("BOE_PORTAL_TWO_INDEPENDENT_WAYBACK_SNAPSHOTS_LITERAL_MATCH_TIER1_"
                     "X_NEZAMS_PARTIAL_CROSSCHECK_LIVE_PORTAL_503")
EXPECTED_STATUS_BY_KEY = {}  # every article shares STATUS_UNCHANGED regardless of amendment
AMENDED_KEYS = {"etec_art_004", "etec_art_007"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "etec_boe_live_portal_unreachable",
    "etec_two_independent_wayback_snapshots_literal_match",
    "etec_structural_caveat_resolved_standard_article_numbering",
    "etec_amendment_631_confirmed_matches_prior_lead",
    "etec_amendment_693_newly_confirmed_not_in_prior_lead",
    "etec_no_named_predecessor_repeal_confirmed_negative",
    "etec_predecessor_bodies_two_distinct_prior_instruments",
    "etec_no_baab_fasl_structure",
    "etec_no_inline_article_titles",
    "etec_main_body_text_not_updated_to_reflect_amendments",
    "etec_nezams_partial_secondary_crosscheck",
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
    statute has no أبواب/فصول nesting -- every top-level entry IS a leaf
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
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level chapter_structure entries (flat statute, "
                  "no أبواب/فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
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
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source supplies no "
                      "inline per-article titles for this statute -- see "
                      "known_unresolved_discrepancies)" % k)
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
        e.append("[2k] missing amendment_history (must record 108, 693, and 631)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("108", "693", "631"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("etec_art_001", {})
    if "هيئة تقويم التعليم والتدريب" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected الهيئة definition")
    art2 = arts.get("etec_art_002", {})
    if "برئيس مجلس الوزراء" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected reporting-line clause")
    # NOTE: the primary source's own main body still shows the PRE-AMENDMENT wording for
    # Articles 4 and 7 in both independent Wayback snapshots (see
    # etec_main_body_text_not_updated_to_reflect_amendments) -- so the spot-checks below
    # anchor on the ORIGINAL as-displayed wording plus the amendment's own declared text
    # inside history, rather than assuming the main body is already consolidated.
    art4 = arts.get("etec_art_004", {})
    if "بناء معايير مناهج التعليم العام بالتنسيق مع وزارة التعليم" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected as-displayed paragraph (5) original text")
    art4_hist = " ".join(json.dumps(h, ensure_ascii=False) for h in art4.get("history", []))
    if "تقويم مناهج التعليم العام بشكل دوري وفق معايير يعتمدها المجلس" not in art4_hist:
        e.append("[2j] Article 4 history missing amended paragraph (5) text (Resolution 631)")
    art7 = arts.get("etec_art_007", {})
    if "وزارة الطاقة والصناعة والثروة المعدنية" not in art7.get("text", ""):
        e.append("[2j] Article 7 missing expected as-displayed original board-seat text")
    art7_hist = " ".join(json.dumps(h, ensure_ascii=False) for h in art7.get("history", []))
    if "693" not in art7_hist or "وزارة الطاقة" not in art7_hist:
        e.append("[2j] Article 7 history missing amended board-seat text (Resolution 693)")
    art18 = arts.get("etec_art_018", {})
    if "ينشر هذا التنظيم في الجريدة الرسمية" not in art18.get("text", ""):
        e.append("[2j] Article 18 missing expected publication/effective-date clause")
    if "يلغي" in art18.get("text", "") or "يحل محل" in art18.get("text", ""):
        e.append("[2j] Article 18 unexpectedly contains repeal language (contradicts the "
                  "confirmed-negative predecessor-repeal finding)")
    if src.get("decree") != "قرار مجلس الوزراء رقم (108)" or src.get("decree_date_hijri") != "14/2/1440":
        e.append("[2j] decree/decree_date_hijri mismatch with verified CoM Resolution 108, 14/2/1440H")

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
        print("FAIL: %d error(s) in ETEC Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Statute (Organizational Regulation) of the Education and Training Evaluation Commission")
    print("  - 18 records: 16 اصلية, 2 معدلة (Articles 4 and 7), 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-18); no")
    print("    inline per-article titles in the source (no title_ar key used)")
    print("  - VERIFICATION TIER: TIER_1 -- primary source is the official laws.boe.gov.sa")
    print("    portal itself, accessed via TWO INDEPENDENT Wayback Machine snapshots")
    print("    (19 June 2024 and 12 December 2025) in full literal agreement across all")
    print("    18 articles and both embedded amendment-note popups, after the live portal")
    print("    returned HTTP 503 / connection-reset this pass. Supplementary partial")
    print("    cross-check from nezams.com (not relied upon for the primary text).")
    print("  - CoM Resolution 108 (14/2/1440H / ~23 Oct 2018G); amended by CoM Resolution")
    print("    693 (2/11/1441H, Article 7 board composition -- newly confirmed this pass,")
    print("    not in the original lead) and CoM Resolution 631 (3/8/1445H, Article 4")
    print("    paragraph 5 -- confirmed identical to the original lead)")
    print("  - CONFIRMED NEGATIVE FINDING: no named predecessor instrument is repealed by")
    print("    this statute -- Article 18 contains no repeal language at all, and the")
    print("    preamble's background reference to CoM Resolution 94 (7/2/1438H) is not an")
    print("    operative repeal clause")
    print("  - A wholly separate, older, NOT-ingested instrument (CoM Resolution 120,")
    print("    22/4/1434H, 'تنظيم هيئة تقويم التعليم العام', different BOE lawId) was found")
    print("    via independent WebSearch and was still listed 'ساري' on BOE's own portal")
    print("    as of a June 2025 Wayback snapshot -- an unresolved status ambiguity for")
    print("    that OTHER instrument, flagged but not resolved here")
    return 0


if __name__ == "__main__":
    sys.exit(main())
