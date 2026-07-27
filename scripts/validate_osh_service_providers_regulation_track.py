#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the OSH Service Providers Licensing/Accreditation
Regulation track (لائحة ترخيص واعتماد مزاولي ومقدمي خدمات السلامة والصحة
المهنية, Ministerial Decision No. 64764, dated 13/5/1447H = 4/11/2025G; 38
records, all اصلية; 6 chapters/الفصول, every one of which carries at least
one numbered article -- unlike some other tracks in this corpus, there is no
chapter with unnumbered closing text here).

VERIFICATION TIER -- see the generator's module docstring and
sources/osh_service_providers_regulation/law/official_source/
osh_service_providers_regulation_official_source.json's
verification_methodology_note for the full account. This validator asserts:
exactly 38 articles in a clean 1..38 run; exactly 6 chapter_structure entries
(الفصل, not الباب) tiling articles 1-38 with no gap/overlap; every article
carries an explicit source_tier ("primary" for 1-29, matching uqn.gov.sa's
own reachable page this pass, or "secondary_only" for 30-38, where only
qanoonsa.com was reachable) and a status string consistent with that tier;
all 38 articles are اصلية with empty amendment history (single, first-and-
only-confirmed edition); no ملغاة/معدلة/مضافة articles this pass; and that
every discrepancy this build's own methodology note flags as a named,
non-obvious judgment call is present in known_unresolved_discrepancies.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "osh_service_providers_regulation", "law", "official_source",
                   "osh_service_providers_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "osh_service_providers_regulation", "law", "verified",
                       "osh_service_providers_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "osh_service_providers_regulation", "law", "verified",
                       "osh_service_providers_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "osh_service_providers_regulation_arabic_legal_llm",
                   "osh_service_providers_regulation_legal_llm_001_038.json")
N = 38
KEY_RE = r"osh_service_providers_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 38, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
PRIMARY_STATUS = "UQN_GAZETTE_OFFICIAL_PRIMARY_TEXT_AR_CROSS_VERIFIED_AJEL_QANOONSA"
SECONDARY_STATUS = "QANOONSA_SECONDARY_TEXT_UQN_PRIMARY_PAGE_TRUNCATED_STRUCTURALLY_XVERIFIED_LEXIS"
STATUS_BY_TIER = {"primary": PRIMARY_STATUS, "secondary_only": SECONDARY_STATUS}
PRIMARY_ARTICLE_RANGE = set(range(1, 30))
SECONDARY_ARTICLE_RANGE = set(range(30, 39))
EXPECTED_CHAPTERS = 6
EXPECTED_SPANS = {"1-1", "2-3", "4-14", "15-26", "27-34", "35-38"}
FLAGGED_DISCREPANCY_KEYS = {
    "osh_service_providers_regulation_uqn_primary_page_truncated_after_art29",
    "osh_service_providers_regulation_articles_30_38_secondary_only",
    "osh_service_providers_regulation_qanoonsa_diacritics_normalized",
    "osh_service_providers_regulation_article18_duplicate_table_excluded",
    "osh_service_providers_regulation_article19_last_row_gap",
    "osh_service_providers_regulation_argaam_undercounted",
    "osh_service_providers_regulation_istitlaa_unreachable",
    "osh_service_providers_regulation_lexis_404_direct",
    "osh_service_providers_regulation_gregorian_decree_date_calculated",
    "osh_service_providers_regulation_no_boe_lawid_checked",
    "osh_service_providers_regulation_sibling_high_risk_professions_not_touched",
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

    chapters = src.get("chapter_structure")
    if not chapters or len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d الفصل entries in chapter_structure, got %r"
                 % (EXPECTED_CHAPTERS, chapters))
    else:
        for c in chapters:
            if not c.get("label_ar", "").startswith("الفصل"):
                e.append("[1c] chapter label %r does not use الفصل" % c.get("label_ar"))
            if not c.get("articles"):
                e.append("[1c] chapter %r must carry a numbered article range (no chapter "
                         "in this regulation is closing-text-only)" % c.get("label_ar"))
        got_spans = {c.get("articles") for c in chapters}
        if got_spans != EXPECTED_SPANS:
            e.append("[1c] chapter_structure article spans %r != expected %r"
                     % (got_spans, EXPECTED_SPANS))
        covered = set()
        for c in chapters:
            lo, hi = (int(x) for x in c["articles"].split("-"))
            for n in range(lo, hi + 1):
                if n in covered:
                    e.append("[1c] article %d covered by more than one الفصل range" % n)
                covered.add(n)
        if covered != set(range(1, N + 1)):
            e.append("[1c] chapters do not exactly tile articles 1..%d: got %s"
                     % (N, sorted(covered)))

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track")
    if src.get("law_component") != "regulation":
        e.append("[1d] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "نافذ":
        e.append("[1d] legal_status_ar must be نافذ")

    tier_counts = Counter()
    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        tier = a.get("source_tier")
        if tier not in ("primary", "secondary_only"):
            e.append("[2] %s: missing/invalid source_tier %r" % (k, tier))
        else:
            tier_counts[tier] += 1
            if n in PRIMARY_ARTICLE_RANGE and tier != "primary":
                e.append("[2] %s: article %d expected source_tier 'primary' (1-29), got %r"
                         % (k, n, tier))
            if n in SECONDARY_ARTICLE_RANGE and tier != "secondary_only":
                e.append("[2] %s: article %d expected source_tier 'secondary_only' (30-38), "
                         "got %r" % (k, n, tier))
            expected_status = STATUS_BY_TIER[tier]
            if a.get("status") != expected_status:
                e.append("[2] %s: expected status %r for tier %r, got %r"
                         % (k, expected_status, tier, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: section_ar must be non-empty (chapter this article belongs to)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2] %s: residual Eastern-Arabic-Indic digit (must be normalized)" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if "<TABLE_" in a["text"] or "<CELL>" in a["text"] or "<ROW>" in a["text"]:
            e.append("[2] %s: unconverted table markup leftover in text" % k)

        if ls != "اصلية":
            e.append("[3] %s: article %d expected اصلية (no amendment confirmed this pass), "
                     "got %r" % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: article %d must have empty history (اصلية-only track)" % (k, n))

    if tier_counts.get("primary", 0) != 29:
        e.append("[2g] expected 29 primary-tier articles, got %d" % tier_counts.get("primary", 0))
    if tier_counts.get("secondary_only", 0) != 9:
        e.append("[2g] expected 9 secondary_only-tier articles, got %d"
                 % tier_counts.get("secondary_only", 0))
    declared_tiers = src.get("source_tier_counts") or {}
    if declared_tiers.get("primary") != tier_counts.get("primary", 0):
        e.append("[2g] declared source_tier_counts.primary does not match actual per-article count")
    if declared_tiers.get("secondary_only") != tier_counts.get("secondary_only", 0):
        e.append("[2g] declared source_tier_counts.secondary_only does not match actual per-article count")

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    declared = src.get("status_counts") or {}
    for st in ALLOWED_STATUS:
        if declared.get(st, 0) != sc.get(st, 0):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    if not (src.get("preamble_ar") or "").strip():
        e.append("[2d] missing preamble_ar")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[4] %s: missing article_number field" % r["article_key"])
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("source_tier") != a.get("source_tier"):
            e.append("[4] %s: source_tier mismatch" % r["article_key"])
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
        e.append("[4b] summary status_counts mismatch with source")
    if summary.get("source_tier_counts") != src.get("source_tier_counts"):
        e.append("[4b] summary source_tier_counts mismatch with source")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[5] %s: missing article_number field" % r["article_key"])
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_tier") != a.get("source_tier"):
            e.append("[5] %s: llm record source_trust.source_tier mismatch" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in OSH Service Providers Regulation track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: OSH Service Providers Licensing/Accreditation Regulation — 38 records "
          "(38 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 6 فصول)")
    print("  - TIER: MIXED/PER-ARTICLE -- Articles 1-29 primary (uqn.gov.sa, Umm Al-Qura "
          "Official Gazette, cross-verified against ajel.sa + qanoonsa.com, zero substantive "
          "divergence); Articles 30-38 secondary-only (qanoonsa.com; uqn.gov.sa's own page did "
          "not reach this far this pass; structurally cross-verified via Lexis Middle East)")
    print("  - IN-FORCE Ministerial Decision No. 64764 (13/5/1447H = 4/11/2025G), published Umm "
          "Al-Qura Issue 5138 (20/7/1447H = 9/1/2026G), effective 180 days after publication")
    print("  - Article 18's duplicate orphan table excluded; Article 19's genuine last-row gap "
          "preserved as-is; see known_unresolved_discrepancies for full detail")
    print("  - Sibling regulation (High-Risk Professions, Decision No. 64762, same date) NOT "
          "touched -- tracked independently elsewhere in this corpus")
    return 0


if __name__ == "__main__":
    sys.exit(main())
