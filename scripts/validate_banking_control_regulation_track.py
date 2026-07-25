#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Banking Control Law IMPLEMENTATION
RULES track (قواعد تطبيق أحكام نظام مراقبة البنوك) -- Ministerial Resolution
No. 2149/3, dated 14/10/1406H, ONE instrument organized into FIVE SECTIONS:

  Section I   (أولاً)   -> Article 16 -- 10 provisions (arts 001-010)
  Section II  (ثانياً)  -> Article 12 -- 4 provisions  (arts 011-014)
  Section III (ثالثاً)  -> Article 17 -- 2 provisions  (arts 015-016)
  Section IV  (رابعاً)  -> Article 18 -- 4 provisions  (arts 017-020)
  Section V   (خامساً)  -> Article 22 -- 11 provisions (arts 021-031)

31 records total: 31 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (no confirmed amendments
this pass).

VERIFICATION TIER -- TIER_2. See the generator docstring and the source
artifact's verification_methodology_note for the full account: fetched
directly from rulebook.sama.gov.sa (live page, marked نافذ/in-force) and
cross-checked against its own linked archival PDF (SAMA_AR_1429_VER1.pdf,
decoded via pdfplumber), both HTTP 200 via direct curl this pass. Two
disclosed textual variances exist between the two sources (regulator-name
terminology; one item's numeral) -- both preserved in
known_unresolved_discrepancies, not silently resolved. This validator does not
re-adjudicate provenance; it only checks internal self-consistency of the
ingested text and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "banking_control_regulation", "law", "official_source",
                   "banking_control_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "banking_control_regulation", "law", "verified",
                       "banking_control_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "banking_control_regulation", "law", "verified",
                       "banking_control_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "banking_control_regulation_arabic_legal_llm",
                   "banking_control_regulation_legal_llm_001_031.json")
N = 31
KEY_RE = r"banking_control_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 31, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_SECTION_COUNTS = {"I": 10, "II": 4, "III": 2, "IV": 4, "V": 11}
EXPECTED_SECTION_BASE_ARTICLE = {"I": 16, "II": 12, "III": 17, "IV": 18, "V": 22}
EXPECTED_SECTION_ORDER = ["I", "II", "III", "IV", "V"]

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
    "banking_control_regulation_circular_not_modern_lauha",
    "banking_control_regulation_sama_domain_reachability",
    "banking_control_regulation_terminology_sama_rename_live_vs_pdf",
    "banking_control_regulation_section_i_item_10_vs_8_numbering",
    "banking_control_regulation_2017_revision_unconfirmed",
    "banking_control_regulation_gazette_not_applicable",
    "banking_control_regulation_item_numbering_intrinsic_continuations",
}

# True combining Arabic diacritics only (U+064B-065F, U+0670) -- built from explicit
# codepoints, NOT a naive "[ً-ٰ]" contiguous range, because that would wrongly span the
# Arabic-Indic digit block U+0660-0669.
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

    sections = {s["section_key"]: s for s in src.get("sections", [])}
    if set(sections) != set(EXPECTED_SECTION_ORDER):
        e.append("[1s] sections must be exactly %s, got %s" %
                 (EXPECTED_SECTION_ORDER, sorted(sections)))
    else:
        for sk, expected_n in EXPECTED_SECTION_COUNTS.items():
            if sections[sk]["provision_count"] != expected_n:
                e.append("[1s] section %s: provision_count != %d" % (sk, expected_n))
            if sections[sk]["base_law_article_number"] != EXPECTED_SECTION_BASE_ARTICLE[sk]:
                e.append("[1s] section %s: base_law_article_number != %d" %
                         (sk, EXPECTED_SECTION_BASE_ARTICLE[sk]))

    # per-section native numbering must be contiguous 1..N within each section
    for sk, n_expected in EXPECTED_SECTION_COUNTS.items():
        nums = sorted(a["section_item_number"] for k, a in arts.items()
                      if a.get("section_key") == sk)
        if nums != list(range(1, n_expected + 1)):
            e.append("[1n] section %s: section_item_number set is not a contiguous 1..%d run" %
                     (sk, n_expected))

    # article_key sequence must group sections in order I,II,III,IV,V with no gaps
    def _sort_key(key):
        m = re.match(KEY_RE, key)
        return int(m.group(1))
    ordered_keys = sorted(arts, key=_sort_key)
    expected_section_at = {}
    running = 1
    for sk in EXPECTED_SECTION_ORDER:
        for _ in range(EXPECTED_SECTION_COUNTS[sk]):
            expected_section_at[running] = sk
            running += 1
    for key in ordered_keys:
        n = _sort_key(key)
        a = arts[key]
        if a.get("section_key") != expected_section_at.get(n):
            e.append("[1o] article %03d: expected section_key %r, got %r" %
                     (n, expected_section_at.get(n), a.get("section_key")))

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
        if a.get("section_key") not in EXPECTED_SECTION_ORDER:
            e.append("[2] %s: bad/missing section_key" % k)
        if not a.get("native_marker_ar"):
            e.append("[2] %s: missing native_marker_ar" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
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
        if TASHKEEL_RE.search(a["text"]):
            e.append("[2g] %s: residual tashkeel/diacritics not stripped" % k)
        if re.search(r"[کیە]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    if not src.get("instrument_type_note_ar"):
        e.append("[2d] missing instrument_type_note_ar (circular-vs-lauha structural note)")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record the founding resolution)")
    else:
        decisions = " ".join(str(h.get("decision", "")) for h in src["amendment_history"])
        if "2149/3" not in decisions:
            e.append("[2k] amendment_history must reference the founding decision 2149/3")

    # spot-checks anchoring key facts established this pass
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no confirmed amendments)")
    if "2149/3" not in src.get("decision_ar", ""):
        e.append("[2j] decision_ar must reference decision 2149/3")
    if not src.get("regulator_rename_footnote_ar"):
        e.append("[2j] missing regulator_rename_footnote_ar")
    if not src.get("pdf_archival_text_variant_note_ar"):
        e.append("[2j] missing pdf_archival_text_variant_note_ar")
    if src.get("gazette_issue_number") is not None:
        e.append("[2j] gazette_issue_number must be null (no gazette publication confirmed)")

    art_1 = arts.get("banking_control_regulation_art_001", {})
    if art_1.get("section_key") != "I" or "حدود القروض" not in art_1.get("text", ""):
        e.append("[2j] article 001 must be Section I's first (lending-limits) provision")
    art_10 = arts.get("banking_control_regulation_art_010", {})
    if art_10.get("section_key") != "I" or art_10.get("native_marker_ar") != "10":
        e.append("[2j] article 010 must be Section I's 10th (final) provision, native marker 10")
    art_11 = arts.get("banking_control_regulation_art_011", {})
    if art_11.get("section_key") != "II" or art_11.get("section_item_number") != 1:
        e.append("[2j] article 011 must be Section II's first provision")
    art_17 = arts.get("banking_control_regulation_art_017", {})
    if art_17.get("section_key") != "IV" or art_17.get("native_marker_ar") != "(1)":
        e.append("[2j] article 017 must be Section IV's first provision, native marker (1)")
    art_31 = arts.get("banking_control_regulation_art_031", {})
    if art_31.get("section_key") != "V" or art_31.get("section_item_number") != 11:
        e.append("[2j] article 031 must be Section V's 11th (final) provision")

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
        if r.get("section_key") != a.get("section_key"):
            e.append("[4] %s: section_key mismatch" % r["article_key"])
        if "article_number" not in r:
            e.append("[4] %s: missing article_number field" % r["article_key"])
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
        if "article_number" not in r:
            e.append("[5] %s: missing article_number field" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation', got %r" %
                     (r["article_key"], r.get("law_component")))
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

    # law_component must be "regulation" (not "law") everywhere -- the specific bug class
    # this track was explicitly asked to avoid, per the sibling-track history.
    for r in ver:
        if r.get("law_component") != "regulation":
            e.append("[6] %s: verified record law_component must be 'regulation', got %r" %
                     (r["article_key"], r.get("law_component")))
    if src.get("law_component") != "regulation":
        e.append("[6] source law_component must be 'regulation'")

    if e:
        print("FAIL: %d error(s) in Banking Control Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Banking Control Law Implementation Rules")
    print("  (قواعد تطبيق أحكام نظام مراقبة البنوك)")
    print("  - 31 records: 31 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (no confirmed amendments)")
    print("  - Section I (Art.16): 10 provisions / Section II (Art.12): 4 / Section III")
    print("    (Art.17): 2 / Section IV (Art.18): 4 / Section V (Art.22): 11")
    print("  - STRUCTURE: ONE instrument (Ministerial Resolution 2149/3, 14/10/1406H),")
    print("    a circular, NOT a modern لائحة تنفيذية -- see instrument_type_note_ar.")
    print("  - VERIFICATION TIER: TIER_2 -- fetched directly from rulebook.sama.gov.sa (live")
    print("    page, marked نافذ) and cross-checked against its own linked archival PDF")
    print("    (SAMA_AR_1429_VER1.pdf, decoded via pdfplumber); both HTTP 200 via direct curl.")
    print("  - Two disclosed textual variances between live page and archival PDF (regulator-")
    print("    name terminology; Section I's final item numbered 10 vs a duplicate 8) --")
    print("    preserved in known_unresolved_discrepancies, not silently resolved.")
    print("  - An unexplained Nov-2017 revision-history boundary on the live page could not")
    print("    be accessed (login-gated) to confirm or rule out as substantive this pass --")
    print("    flagged as an open question, not assumed benign.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
