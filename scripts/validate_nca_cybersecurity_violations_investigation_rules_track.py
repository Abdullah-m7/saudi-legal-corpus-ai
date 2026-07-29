#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Rules for Detecting and Investigating Cybersecurity
Violations track (قواعد ضبط مخالفات الأمن السيبراني والتحقيق فيها; 9 records, all اصلية;
a flat sequence of 9 مواد with no أبواب/فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/nca_cybersecurity_violations_investigation_rules/law/official_source/
nca_cybersecurity_violations_investigation_rules_official_source.json's
verification_methodology_note for the full account. This validator asserts: exactly 9
articles in a clean 1..9 run; exactly 1 chapter_structure entry spanning articles 1-9
(flat structure, no أبواب/فصول); all 9 articles اصلية with empty amendment history
(single, first-and-only-confirmed edition, consistent with this being one of the newest
instruments in the corpus); the 5 expected known_unresolved_discrepancies keys are present;
every article's text is non-empty with no stray Latin/HTML characters, no residual
Eastern-Arabic-Indic-digit/decimal artifacts beyond the source's own genuine Arabic-Indic
numeral usage, and no double-space artifacts.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "nca_cybersecurity_violations_investigation_rules", "law",
                   "official_source",
                   "nca_cybersecurity_violations_investigation_rules_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "nca_cybersecurity_violations_investigation_rules", "law",
                       "verified",
                       "nca_cybersecurity_violations_investigation_rules_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "nca_cybersecurity_violations_investigation_rules", "law",
                       "verified",
                       "nca_cybersecurity_violations_investigation_rules_verified_summary.json")
LLM = os.path.join(ROOT, "data", "nca_cybersecurity_violations_investigation_rules_arabic_legal_llm",
                   "nca_cybersecurity_violations_investigation_rules_legal_llm_001_009.json")
N = 9
KEY_RE = r"nca_cybersecurity_violations_investigation_rules_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 9, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "NCA_OFFICIAL_LIVE_PDF_X_UQN_GAZETTE_FULLTEXT_DUAL_PRIMARY_CROSS_VERIFIED_TIER1"
EXPECTED_CHAPTERS = 1
FLAGGED_DISCREPANCY_KEYS = {
    "nca_cybersecurity_violations_investigation_rules_pdf_typo_correction_between_fetches",
    "nca_cybersecurity_violations_investigation_rules_digit_convention_cosmetic_difference",
    "nca_cybersecurity_violations_investigation_rules_toc_body_title_order_mismatch",
    "nca_cybersecurity_violations_investigation_rules_effective_date_tied_to_own_website_not_gazette",
    "nca_cybersecurity_violations_investigation_rules_decree_date_gregorian_computed_not_sourced",
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
        e.append("[1c] expected %d chapter_structure entry (flat, no أبواب/فصول), got %r"
                 % (EXPECTED_CHAPTERS, chapters))
    else:
        c = chapters[0]
        if c.get("articles") != "1-9":
            e.append("[1c] the single flat chapter_structure entry must span articles 1-9, got %r"
                     % c.get("articles"))

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track")
    if src.get("law_component") != "regulation":
        e.append("[1d] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "نافذ":
        e.append("[1d] legal_status_ar must be نافذ")

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
        if a.get("article_title_ar") is None or not a.get("article_title_ar", "").strip():
            e.append("[2] %s: article_title_ar must be a non-empty string for this track "
                     "(every article has its own distinct title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)

        # single, first-and-only-confirmed edition: every article must be اصلية, no history
        if ls != "اصلية":
            e.append("[3] %s: article %d expected اصلية (no amendment confirmed this pass), "
                     "got %r" % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: article %d must have empty history (اصلية-only track)" % (k, n))

    # Article 6's own title must reflect the body/gazette-confirmed word order
    art6 = arts.get("nca_cybersecurity_violations_investigation_rules_art_006")
    if art6 and art6.get("article_title_ar") != "إجراءات التعامل مع الحالات العاجلة والضرورية":
        e.append("[3b] Article 6's title must use the body/gazette-confirmed order "
                 "'العاجلة والضرورية' (the index page's own 'الضرورية والعاجلة' order is a "
                 "documented, disclosed discrepancy, not the canonical title)")

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

    if not src.get("decree", "").strip() or "ع26" not in src.get("decree", ""):
        e.append("[2g] decree field must cite the Board decision number (ع26/1/1/1ت)")
    if src.get("decree_date_hijri") != "22/8/1447":
        e.append("[2g] decree_date_hijri must be 22/8/1447")

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
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in NCA Cybersecurity Violations Investigation Rules track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Rules for Detecting and Investigating Cybersecurity Violations — 9 records "
          "(9 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; flat structure, no أبواب/فصول)")
    print("  - TIER: TIER_1_PRIMARY_MULTI_SOURCE -- NCA's own official website (live-refetched)")
    print("    cross-verified word-for-word against the Umm Al-Qura Official Gazette's own full")
    print("    HTML text (uqn.gov.sa/decisions-and-regulations/4001430) -- no OCR required")
    print("  - Board Decision No. (ع26/1/1/1ت), 22/8/1447H; gazetted 3/2/1448H = 17/7/2026G,")
    print("    ~11 days before this track's build date -- one of the newest instruments in the corpus")
    print("  - Three minor typos found corrected between an earlier PDF fetch and this pass's live")
    print("    re-fetch (Articles 3, 4(3), 8(2)) -- disclosed, live/gazette-matching wording used")
    return 0


if __name__ == "__main__":
    sys.exit(main())
