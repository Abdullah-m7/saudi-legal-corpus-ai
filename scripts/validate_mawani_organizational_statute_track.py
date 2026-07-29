#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Organizational Statute of the General Authority
for Ports (Mawani) track (20 records, all اصلية; flat structure -- NO
أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/mawani_organizational_statute/law/official_source/
mawani_organizational_statute_official_source.json's verification_methodology_
note for the full account: TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE.
laws.boe.gov.sa (HTTP 503 / TLS reset on 3 attempts), the Wayback Machine
(confirmed blocked via WebFetch tool refusal and egress policy), and
mawani.gov.sa (HTTP 405 WAF block) were all confirmed unreachable this pass.
The statute's own article text rests on ONE full-text source (nezams.com),
cross-checked only at the metadata level (decree number/date, name change,
board composition, scope) against independent sources. This validator does
not attempt to re-adjudicate any of this; it only checks internal
self-consistency of the text this track actually ingests, and that every
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
SRC = os.path.join(ROOT, "sources", "mawani_organizational_statute", "law", "official_source",
                   "mawani_organizational_statute_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "mawani_organizational_statute", "law", "verified",
                       "mawani_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "mawani_organizational_statute", "law", "verified",
                       "mawani_organizational_statute_verified_summary.json")
LLM = os.path.join(ROOT, "data", "mawani_organizational_statute_arabic_legal_llm",
                   "mawani_organizational_statute_legal_llm_001_020.json")
N = 20
BASE_ARTICLE_COUNT = 20
KEY_RE = r"mawani_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-20

STATUS_UNCHANGED = ("NEZAMS_COM_SINGLE_FULLTEXT_SOURCE_BOE_LIVE_TLS_RESET_WAYBACK_MACHINE_EGRESS_"
                    "AND_TOOL_BLOCKED_MAWANI_GOV_SA_WAF_405_BLOCKED_QANOONSA_NO_DEDICATED_PAGE_"
                    "FOUND_INDEPENDENT_METADATA_ONLY_CROSSCHECK_TIER_4_SINGLE_SOURCE")
EXPECTED_STATUS_BY_KEY = {}
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "mawani_single_fulltext_source_no_second_mirror_found",
    "mawani_boe_and_wayback_confirmed_unreachable_this_pass",
    "mawani_gov_sa_own_site_waf_blocked",
    "mawani_uqn_gazette_issue_not_located",
    "mawani_no_amendments_single_source_negative_finding",
    "mawani_predecessor_repeal_clause_confirmed",
    "mawani_article8_item15_after_closing_sentence",
    "mawani_article5_item_zay_plural_role_word",
    "mawani_article1_decorative_tatweel_normalized",
    "mawani_qanoonsa_and_mohamah_no_dedicated_page_found",
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
    """Yield (lo, hi) for every leaf range in chapter_structure. This Law has
    no أبواب/فصول nesting -- every top-level entry IS a leaf (no 'sections'
    key), so this is a flat single-level walk over the 20 articles."""
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
        e.append("[1c] expected %d top-level chapter_structure entries (flat law, "
                  "no أبواب/فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one leaf range" % n)
            covered.add(n)
    if covered != set(range(1, BASE_ARTICLE_COUNT + 1)):
        missing = sorted(set(range(1, BASE_ARTICLE_COUNT + 1)) - covered)
        extra = sorted(covered - set(range(1, BASE_ARTICLE_COUNT + 1)))
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
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source supplies no "
                      "inline per-article titles for this law -- see "
                      "known_unresolved_discrepancies)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "‌" in a["text"] or "‍" in a["text"]:
            e.append("[2f] %s: residual zero-width joiner/non-joiner artifact detected" % k)
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
        e.append("[2k] missing amendment_history (must record base decree 299)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        if "299" not in decrees:
            e.append("[2k] amendment_history must reference 299")

    # spot-checks anchoring key facts established this pass
    art19 = arts.get("mawani_organizational_statute_art_019", {})
    if "يحل التنظيم محل نظام المؤسسة العامة للموانئ" not in art19.get("text", ""):
        e.append("[2j] Article 19 missing expected predecessor repeal clause")
    if "م/13" not in art19.get("text", "") or "1397" not in art19.get("text", ""):
        e.append("[2j] Article 19 missing expected predecessor decree citation (M/13, 1397H)")
    art5 = arts.get("mawani_organizational_statute_art_005", {})
    if "وزير النقل رئيساً" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected board chair clause")
    if "ثلاثة من القطاع الخاص من غير المستثمرين في قطاع الموانئ" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected private-sector board seats clause")
    art1 = arts.get("mawani_organizational_statute_art_001", {})
    if "المملكة: المملكة العربية السعودية" not in art1.get("text", "").replace("\n", " "):
        e.append("[2j] Article 1 missing expected المملكة definition (tatweel-normalization check)")
    if "ـ" in art1.get("text", "").replace("هـ", ""):
        e.append("[2j] Article 1 unexpectedly retains decorative tatweel after normalization")
    art7 = arts.get("mawani_organizational_statute_art_007", {})
    if "م/42" not in art7.get("text", "") or "هـ" not in art7.get("text", ""):
        e.append("[2j] Article 7 missing expected fees-system cross-reference with intact هـ abbreviation")
    if src.get("decree") != "قرار مجلس الوزراء رقم (299)" or src.get("decree_date_hijri") != "11/6/1439":
        e.append("[2j] decree/decree_date_hijri mismatch with verified 299, 11/6/1439H")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law should be False -- no amendments located this pass")

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
        print("FAIL: %d error(s) in Mawani Organizational Statute track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Organizational Statute of the General Authority for Ports (Mawani)")
    print("  - 20 records, all اصلية (original) -- no amendments located this pass")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-20); no inline")
    print("    per-article titles in the source (no title_ar key used)")
    print("  - VERIFICATION TIER: TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE. laws.boe.gov.sa")
    print("    (HTTP 503 / TLS reset x3), the Wayback Machine (tool refusal + egress block),")
    print("    and mawani.gov.sa (HTTP 405 WAF) all confirmed unreachable this pass. Article")
    print("    text rests on ONE full-text source (nezams.com); metadata-only corroboration")
    print("    via ar.wikipedia.org, saudipedia.com, my.gov.sa")
    print("  - Council of Ministers Resolution 299 (11/6/1439H); GENUINE PREDECESSOR REPEAL")
    print("    CONFIRMED in Article 19 (Royal Decree M/13, 7/4/1397H, Public Ports Corporation)")
    print("  - Several structural oddities preserved literally and flagged (Article 8 item 15")
    print("    placement, Article 5 item ز plural role-word, Article 1 decorative tatweel)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
