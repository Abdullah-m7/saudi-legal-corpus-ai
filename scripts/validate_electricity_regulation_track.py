#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Electricity Law IMPLEMENTING REGULATION(S)
track (اللائحتان التنفيذيتان لنظام الكهرباء) -- ONE combined track holding TWO distinct
instruments issued under Article 22 of the Electricity Law (Royal Decree M/44,
16/5/1442H):

  - Authority's part: Board Decision No. (43/02), 13/04/1443H -- 56 articles, 10 chapters
    (electricity_regulation_art_001..056).
  - Ministry's part: Minister Decision No. (1443/1728/01), 08/03/1443H -- 36 articles, 14
    chapters (electricity_regulation_art_057..092).

92 records total: 92 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (no confirmed amendments this pass).

VERIFICATION TIER -- TIER_3 for both parts. See the generator docstring and the source
artifact's verification_methodology_note for the full account: laws.boe.gov.sa and
sera.gov.sa reset the connection this pass; uqn.gov.sa's legacy permalinks now resolve to
a redesigned homepage shell; Wayback (content path AND CDX API) was egress-blocked and NOT
circumvented. Full verbatim text extracted from qanoonsa.com (one clean born-digital HTML
aggregator per part); the official approval decisions were fetched directly and corroborate
signing dates/gazette issue numbers. This validator does not re-adjudicate provenance; it
only checks internal self-consistency of the ingested text and that every discrepancy is
still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "electricity_regulation", "law", "official_source",
                   "electricity_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "electricity_regulation", "law", "verified",
                       "electricity_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "electricity_regulation", "law", "verified",
                       "electricity_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "electricity_regulation_arabic_legal_llm",
                   "electricity_regulation_legal_llm_001_092.json")
N = 92
N_AUTHORITY = 56
N_MINISTRY = 36
KEY_RE = r"electricity_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 92, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_AUTHORITY_CHAPTERS = 10
EXPECTED_MINISTRY_CHAPTERS = 14

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "electricity_regulation_two_instruments_combined_one_track",
    "electricity_regulation_boe_sera_uqn_live_unreachable_fulltext_from_qanoonsa",
    "electricity_regulation_digit_style_switch_authority_part_art1_6_vs_7_56",
    "electricity_regulation_unverified_2025_amendment_claim_authority_part",
    "electricity_regulation_sera_pdf_unreachable_this_pass",
    "electricity_regulation_signing_vs_publication_order_mismatch",
    "electricity_regulation_gazette_dates_gregorian_only_in_source",
    "electricity_regulation_regulator_renamed_to_sera_confirmed_primary",
}

# True combining Arabic diacritics only (U+064B-065F, U+0670) -- built from explicit
# codepoints, NOT a naive "[ً-ٰ]" contiguous range, because that would wrongly span the
# Arabic-Indic digit block U+0660-0669 that THIS source uses natively for enumeration.
_TASHKEEL_CHARS = ''.join(chr(c) for c in range(0x064B, 0x0660)) + chr(0x0670)
TASHKEEL_RE = re.compile('[' + re.escape(_TASHKEEL_CHARS) + ']')
AR_RANGE = "ء-ي"


def _bad_tatweel(text):
    bad = 0
    heh = chr(0x0647)
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR_RANGE, before) and before != heh
                and re.match("[%s]" % AR_RANGE, after)):
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

    parts = {p["part_key"]: p for p in src.get("parts", [])}
    if set(parts) != {"authority", "ministry"}:
        e.append("[1p] parts must be exactly {authority, ministry}, got %s" % sorted(parts))
    else:
        if parts["authority"]["article_count"] != N_AUTHORITY:
            e.append("[1p] authority part article_count != %d" % N_AUTHORITY)
        if parts["ministry"]["article_count"] != N_MINISTRY:
            e.append("[1p] ministry part article_count != %d" % N_MINISTRY)

        for part_key, n_chapters_expected, n_articles_expected in (
                ("authority", EXPECTED_AUTHORITY_CHAPTERS, N_AUTHORITY),
                ("ministry", EXPECTED_MINISTRY_CHAPTERS, N_MINISTRY)):
            chs = parts[part_key].get("chapter_structure") or []
            if len(chs) != n_chapters_expected:
                e.append("[1c] %s part: expected %d chapters, got %d" %
                         (part_key, n_chapters_expected, len(chs)))
            covered = set()
            for lo, hi in _iter_chapter_ranges(chs):
                for n in range(lo, hi + 1):
                    if n in covered:
                        e.append("[1c] %s part: article %d covered twice" % (part_key, n))
                    covered.add(n)
            if covered != set(range(1, n_articles_expected + 1)):
                missing = sorted(set(range(1, n_articles_expected + 1)) - covered)
                extra = sorted(covered - set(range(1, n_articles_expected + 1)))
                if missing:
                    e.append("[1c] %s part: chapter_structure missing article(s): %s" %
                             (part_key, missing[:20]))
                if extra:
                    e.append("[1c] %s part: chapter_structure covers out-of-range article(s): %s" %
                             (part_key, extra[:20]))

    # per-part native article numbering must be contiguous 1..N within each part, in the
    # SAME relative order as the combined track's own article_number sequence
    for part_key, n_expected in (("authority", N_AUTHORITY), ("ministry", N_MINISTRY)):
        nums = sorted(a["part_article_number"] for k, a in arts.items()
                      if a.get("instrument_part") == part_key)
        if nums != list(range(1, n_expected + 1)):
            e.append("[1n] %s part: part_article_number set is not a contiguous 1..%d run" %
                     (part_key, n_expected))

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if a.get("instrument_part") not in ("authority", "ministry"):
            e.append("[2] %s: bad/missing instrument_part" % k)
        if not a.get("part_number_label_ar"):
            e.append("[2] %s: missing part_number_label_ar" % k)
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
        if k not in (AMENDED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if chr(0x201C) in a["text"] or chr(0x201D) in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if TASHKEEL_RE.search(a["text"]):
            e.append("[2g] %s: residual tashkeel/diacritics not stripped" % k)
        # non-standard Arabic-presentation letters (Farsi yeh/keheh) must not leak in
        if re.search(r"[کیە]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if not src.get("structure_decision_rationale_ar"):
        e.append("[2d] missing structure_decision_rationale_ar (single-vs-two-track reasoning)")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record both founding decisions)")
    else:
        decisions = " ".join(str(h.get("decision", "")) for h in src["amendment_history"])
        if "43/02" not in decisions:
            e.append("[2k] amendment_history must reference the Authority's founding decision 43/02")
        if "1443/1728/01" not in decisions:
            e.append("[2k] amendment_history must reference the Ministry's founding decision 1443/1728/01")

    # spot-checks anchoring key facts established this pass
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no confirmed amendments)")
    if "authority" not in parts or "43/02" not in parts["authority"].get("decision_ar", ""):
        e.append("[2j] authority part decision_ar must reference decision 43/02")
    if "ministry" not in parts or "1443/1728/01" not in parts["ministry"].get("decision_ar", ""):
        e.append("[2j] ministry part decision_ar must reference decision 1443/1728/01")

    art_a1 = arts.get("electricity_regulation_art_001", {})
    if art_a1.get("instrument_part") != "authority" or "تعريفات" not in art_a1.get("text", ""):
        e.append("[2j] article 001 must be the Authority-part's definitions article")
    art_a56 = arts.get("electricity_regulation_art_056", {})
    if art_a56.get("instrument_part") != "authority" or "السريان" not in art_a56.get("text", ""):
        e.append("[2j] article 056 must be the Authority-part's final (السريان) article")
    art_m1 = arts.get("electricity_regulation_art_057", {})
    if art_m1.get("instrument_part") != "ministry" or art_m1.get("part_article_number") != 1:
        e.append("[2j] article 057 must be the Ministry-part's first article")
    art_m36 = arts.get("electricity_regulation_art_092", {})
    if art_m36.get("instrument_part") != "ministry" or art_m36.get("part_article_number") != 36:
        e.append("[2j] article 092 must be the Ministry-part's 36th (final) article")

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
        if r.get("instrument_part") != a.get("instrument_part"):
            e.append("[4] %s: instrument_part mismatch" % r["article_key"])
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
        print("FAIL: %d error(s) in Electricity Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Electricity Law Implementing Regulations")
    print("  (اللائحتان التنفيذيتان لنظام الكهرباء)")
    print("  - 92 records: 92 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (no confirmed amendments)")
    print("  - Authority's part: 56 articles / 10 chapters (Board Decision 43/02, 13/04/1443H)")
    print("  - Ministry's part: 36 articles / 14 chapters (Minister Decision 1443/1728/01, 08/03/1443H)")
    print("  - STRUCTURE: ONE combined track with clear internal sectioning (instrument_part")
    print("    field on every record) -- see structure_decision_rationale_ar for the reasoning.")
    print("  - VERIFICATION TIER: TIER_3 for both parts -- laws.boe.gov.sa/sera.gov.sa reset")
    print("    the connection this pass, uqn.gov.sa legacy permalinks now resolve to a")
    print("    redesigned homepage shell, Wayback (content path AND CDX API) egress-blocked")
    print("    (not circumvented); full verbatim text from qanoonsa.com (clean born-digital")
    print("    HTML, one aggregator per part), with the official approval decisions fetched")
    print("    directly for metadata corroboration. Re-verification vs laws.boe.gov.sa or")
    print("    sera.gov.sa recommended once reachable.")
    print("  - SERA rename (2024) confirmed via its own enabling instrument (Council of")
    print("    Ministers Decision 918, 28 Shawwal 1445H), fetched directly this pass.")
    print("  - An unconfirmed WebSearch claim of 1444H amendments to the Authority's part")
    print("    could NOT be corroborated via qanoonsa.com and was NOT adopted (see")
    print("    known_unresolved_discrepancies).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
