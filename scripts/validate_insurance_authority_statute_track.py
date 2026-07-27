#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Statute of the Insurance Authority track
(15 records, all اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; flat structure -- NO
أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/insurance_authority_statute/law/official_source/
insurance_authority_statute_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa's live
portal was unreachable this pass (TLS connection reset, consistent with a
prior HTTP 503 finding), and this environment additionally resets every TLS
connection to web.archive.org itself, so the Wayback Machine could not be
used either even though an archived snapshot is known (via a separate,
reachable archive.org availability-API host) to exist. The GOVERNING PRIMARY
source used instead is uqn.gov.sa -- the official Umm Al-Qura Gazette portal
itself -- live-fetched this pass, cross-verified at byte level against
qanoonsa.com and at quote level against argaam.com. This validator does not
attempt to re-adjudicate any of this; it only checks internal
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
SRC = os.path.join(ROOT, "sources", "insurance_authority_statute", "law", "official_source",
                   "insurance_authority_statute_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "insurance_authority_statute", "law", "verified",
                       "insurance_authority_statute_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "insurance_authority_statute", "law", "verified",
                       "insurance_authority_statute_verified_summary.json")
LLM = os.path.join(ROOT, "data", "insurance_authority_statute_arabic_legal_llm",
                   "insurance_authority_statute_legal_llm_001_015.json")
N = 15
KEY_RE = r"insurance_authority_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-15

STATUS_UNCHANGED = ("UQN_OFFICIAL_GAZETTE_LIVE_FETCH_PRIMARY_X_QANOONSA_COM_BYTE_LEVEL_"
                     "CROSSCHECK_X_ARGAAM_COM_QUOTE_CROSSCHECK_LIVE_BOE_UNREACHABLE")
EXPECTED_STATUS_BY_KEY = {}
AMENDED_KEYS = set(EXPECTED_STATUS_BY_KEY)
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "insurance_authority_boe_live_and_wayback_unreachable",
    "insurance_authority_uqn_primary_source_used",
    "insurance_authority_qanoonsa_byte_level_crosscheck",
    "insurance_authority_argaam_quote_crosscheck",
    "insurance_authority_qanoonsa_resolution_date_typo_resolved",
    "insurance_authority_ia_own_site_no_full_text",
    "insurance_authority_no_bab_fasl_structure",
    "insurance_authority_no_inline_article_titles",
    "insurance_authority_no_repeal_clause_in_statute_itself",
    "insurance_authority_health_insurance_2024_transfer_not_a_textual_amendment",
    "insurance_authority_no_amendments_found_this_pass",
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
    key), so this is a flat single-level walk."""
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
                      "inline per-article titles for this law -- see "
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
        e.append("[2k] missing amendment_history (must record 85)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        if "85" not in decrees:
            e.append("[2k] amendment_history must reference 85")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("insurance_authority_statute_art_001", {})
    if "هيئة التأمين" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected الهيئة definition")
    art2 = arts.get("insurance_authority_statute_art_002", {})
    if "الشخصية الاعتبارية العامة" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected legal-personality wording")
    art5 = arts.get("insurance_authority_statute_art_005", {})
    if "بأمر ملكي" not in art5.get("text", "") or "مجلس إدارة" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected royal-order board chair appointment wording")
    art6 = arts.get("insurance_authority_statute_art_006", {})
    if "تحديد المقابل المالي للخدمات والأعمال التي تقدمها الهيئة" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected paragraph (12) fee-setting power referenced "
                 "by the companion resolution's item ثامناً")
    art10 = arts.get("insurance_authority_statute_art_010", {})
    if "السنة المالية للهيئة هي السنة المالية للدولة" not in art10.get("text", ""):
        e.append("[2j] Article 10 missing expected paragraph (2) fiscal-year wording referenced "
                 "by the companion resolution's item سابعاً")
    art15 = arts.get("insurance_authority_statute_art_015", {})
    if "الجريدة الرسمية" not in art15.get("text", ""):
        e.append("[2j] Article 15 missing expected official-gazette publication clause")
    if src.get("decree") != "قرار مجلس الوزراء رقم (85)" or src.get("decree_date_hijri") != "28/1/1445":
        e.append("[2j] decree/decree_date_hijri mismatch with verified 85, 28/1/1445H")

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
        print("FAIL: %d error(s) in Insurance Authority Statute track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Statute of the Insurance Authority")
    print("  - 15 records: all اصلية, 0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-15); no")
    print("    inline per-article titles in the source (no title_ar key used)")
    print("  - VERIFICATION TIER: uqn.gov.sa (official Umm Al-Qura Gazette portal),")
    print("    live-fetched, PRIMARY x qanoonsa.com byte-level crosscheck x argaam.com")
    print("    quote crosscheck; live BOE and web.archive.org unreachable this pass")
    print("  - Council of Ministers Resolution 85 (28/1/1445H); companion resolution's")
    print("    own numbered decisions (not this statute's articles) transfer insurance")
    print("    competencies from SAMA and the Council of Cooperative Health Insurance --")
    print("    NOT ingested here (see known_unresolved_discrepancies)")
    print("  - This statute's own 15 articles contain NO repeal/predecessor clause,")
    print("    unlike this corpus's tvtc_organizational_statute track")
    return 0


if __name__ == "__main__":
    sys.exit(main())
