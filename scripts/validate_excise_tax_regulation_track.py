#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Excise Tax Implementing Regulation track
(اللائحة التنفيذية للضريبة الانتقائية, ZATCA Board Resolution (9-1-17),
13 Ramadan 1438H) -- 67 records (64 numbered articles + 3 مكرر), 23 chapters,
48 اصلية / 16 معدلة / 3 مضافة.

TIER_2 track: one official source (ZATCA's own consolidated Arabic PDF) plus an
independent secondary cross-check that covers 58 of the 67 records. The nine
records with no secondary counterpart (Articles 9-14 and the three مكرر
articles) rest on the official file alone; the validator asserts that this is
declared rather than hidden.

The validator deliberately asserts the REAL record count (67), which differs
from the corpus census figure (64 = the highest article number), and requires
that divergence to be documented.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "excise_tax_regulation", "law", "official_source",
                   "excise_tax_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "excise_tax_regulation", "law", "verified",
                       "excise_tax_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "excise_tax_regulation", "law", "verified",
                       "excise_tax_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "excise_tax_regulation_arabic_legal_llm",
                   "excise_tax_regulation_legal_llm_001_067.json")

N = 67
HIGHEST = 64
MUKARRAR = {22, 37, 52}
KEY_RE = r"excise_tax_regulation_art_(\d{3})(_mukarrar)?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 48, "معدلة": 16, "مضافة": 3, "ملغاة": 0}
STATUS = "ZATCA_OFFICIAL_CONSOLIDATED_PDF_X_SECONDARY_CROSS_VERIFIED"
EXPECTED_CHAPTERS = 23
EXPECTED_DECREE = "قرار مجلس إدارة الهيئة العامة للزكاة والدخل رقم (9-1-17)"
EXPECTED_DECREE_DATE = "13/9/1438"
EXPECTED_TIER = "TIER_2"
EXPECTED_AMENDING = {
    "قرار مجلس إدارة الهيئة العامة للزكاة والدخل رقم (8-2-19)",
    "قرار مجلس إدارة الهيئة العامة للزكاة والدخل رقم (2-3-19)",
    "قرار مجلس إدارة هيئة الزكاة والضريبة والجمارك رقم (14-6-22)",
    "قرار مجلس إدارة هيئة الزكاة والضريبة والجمارك رقم (13-1-23)",
    "قرار مجلس إدارة هيئة الزكاة والضريبة والجمارك رقم (06-06-25)",
}
FLAGGED_DISCREPANCY_KEYS = {
    "excise_tax_regulation_article_count_vs_census",
    "excise_tax_regulation_decision_number_direction",
    "excise_tax_regulation_pre_2025_amendments_unattributed",
    "excise_tax_regulation_arts_009_014_single_source",
    "excise_tax_regulation_boe_and_archive_unreachable",
    "excise_tax_regulation_gcc_agreement_not_extracted",
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


def _parse(key):
    m = re.match(KEY_RE, key)
    return (int(m.group(1)), bool(m.group(2))) if m else (None, None)


def main():
    e = []
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT))
            return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # [1] structure: 64 numbered + 3 mukarrar, no gaps
    if len(arts) != N or src.get("article_count") != N:
        e.append("[1] %d records / article_count=%s, expected %d"
                 % (len(arts), src.get("article_count"), N))
    if src.get("highest_article_number") != HIGHEST:
        e.append("[1] highest_article_number != %d" % HIGHEST)
    if src.get("mukarrar_count") != len(MUKARRAR):
        e.append("[1] mukarrar_count != %d" % len(MUKARRAR))
    numbered, mukarrar = set(), set()
    for k in arts:
        n, mk = _parse(k)
        if n is None:
            e.append("[1] %s: does not match key pattern" % k)
            continue
        (mukarrar if mk else numbered).add(n)
    if numbered != set(range(1, HIGHEST + 1)):
        e.append("[1] numbered articles are not exactly 1..%d (missing %s)"
                 % (HIGHEST, sorted(set(range(1, HIGHEST + 1)) - numbered)))
    if mukarrar != MUKARRAR:
        e.append("[1] مكرر articles %s != %s" % (sorted(mukarrar), sorted(MUKARRAR)))

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTERS, len(chapters)))
    covered = set()
    for c in chapters:
        if not c.get("label_ar") or not c.get("title_ar"):
            e.append("[1c] chapter entry missing label/title: %r" % c)
        rng = c.get("articles", "")
        if "-" in rng:
            a, b = rng.split("-")
            covered |= set(range(int(a), int(b) + 1))
        elif rng.isdigit():
            covered.add(int(rng))
    if covered != set(range(1, HIGHEST + 1)):
        e.append("[1c] chapter ranges do not cover articles 1..%d exactly" % HIGHEST)

    # [2] citation
    if src.get("decree") != EXPECTED_DECREE:
        e.append("[2] decree %r != %r" % (src.get("decree"), EXPECTED_DECREE))
    if src.get("decree_date_hijri") != EXPECTED_DECREE_DATE:
        e.append("[2] decree_date_hijri %r != %r"
                 % (src.get("decree_date_hijri"), EXPECTED_DECREE_DATE))
    if src.get("verification_tier") != EXPECTED_TIER:
        e.append("[2] verification_tier != %s" % EXPECTED_TIER)
    if not src.get("verification_tier_basis"):
        e.append("[2] missing verification_tier_basis")
    if not src.get("cover_page_verbatim_ar"):
        e.append("[2] missing cover_page_verbatim_ar")
    hist = {h.get("decree") for h in src.get("amendment_history", [])}
    if EXPECTED_DECREE not in hist:
        e.append("[2] amendment_history does not open with the issuing resolution")
    if not EXPECTED_AMENDING <= hist:
        e.append("[2] amendment_history missing %s" % sorted(EXPECTED_AMENDING - hist))
    parent = src.get("parent_law") or {}
    if parent.get("decree") != "المرسوم الملكي رقم (م/86)":
        e.append("[2] parent_law does not cite Royal Decree M/86")
    if parent.get("corpus_track") != "excise_tax_law":
        e.append("[2] parent_law does not point at the excise_tax_law track")

    # [3] per-article integrity
    sc = Counter()
    for k, a in sorted(arts.items()):
        n, mk = _parse(k)
        if a.get("status") != STATUS:
            e.append("[3] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        if a.get("is_mukarrar") != mk:
            e.append("[3] %s: is_mukarrar does not match its key" % k)
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[3] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[3] %s: section/status divergence" % k)
        txt = a.get("text", "")
        if not txt.strip():
            e.append("[3] %s: empty text" % k)
        if re.search(r"[A-Za-z<>&]", txt):
            e.append("[3] %s: latin/html leftovers in Arabic text" % k)
        if not a.get("section_ar"):
            e.append("[3] %s: missing section_ar" % k)
        if not a.get("title_ar"):
            e.append("[3] %s: missing title_ar (every article of this Regulation "
                     "carries a printed title)" % k)
        if _bad_tatweel(txt):
            e.append("[3] %s: in-word decorative tatweel survived extraction" % k)
        if ("(((" in txt) or ("(((" in a.get("title_ar", "")):
            e.append("[3] %s: undecoded footnote-reference glyph left in the text" % k)
        # amended/added articles MUST carry the source's own footnote verbatim
        if ls in ("معدلة", "مضافة"):
            if not a.get("history"):
                e.append("[3] %s: %s article without amendment history" % (k, ls))
            for h in a.get("history", []):
                if not h.get("footnote_verbatim_ar"):
                    e.append("[3] %s: history entry lacks the verbatim footnote" % k)
                if not h.get("instrument"):
                    e.append("[3] %s: history entry lacks the amending instrument" % k)
                if not h.get("source"):
                    e.append("[3] %s: history entry lacks its source citation" % k)
        elif a.get("history"):
            e.append("[3] %s: unamended article carries amendment history" % k)
        for f in a:
            if "original_" in f and "text" in f:
                e.append("[3] %s: unexpected reconstructed field %r" % (k, f))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[3] status %s: %s != %d" % (st, sc.get(st, 0), want))
    if src.get("status_counts") != EXPECTED_COUNTS:
        e.append("[3] status_counts block does not match the articles")

    # [4] honesty apparatus
    if not src.get("verification_methodology_note"):
        e.append("[4] missing verification_methodology_note")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[4] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[4] expected discrepancy entries missing for: %s" % sorted(missing))
        for d in disc:
            if not d.get("description"):
                e.append("[4] discrepancy %r has no description" % d.get("article_key"))

    # [5] verified records layer
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[5] %d verified records != %d" % (len(ver), N))
    seen = set()
    for r in ver:
        k = r["article_key"]
        seen.add(k)
        if k not in arts:
            e.append("[5] %s: unknown article_key" % k)
            continue
        a = arts[k]
        if r["article_text_verified"] != a["text"]:
            e.append("[5] %s: text != source" % k)
        if r.get("verification_status") != a.get("status"):
            e.append("[5] %s: verification_status mismatch" % k)
        if r.get("verification_tier") != EXPECTED_TIER:
            e.append("[5] %s: verification_tier missing/incorrect" % k)
        if r.get("is_mukarrar") != a.get("is_mukarrar"):
            e.append("[5] %s: is_mukarrar mismatch" % k)
        if r.get("is_amended") != (a["legal_status_ar"] == "معدلة"):
            e.append("[5] %s: is_amended mismatch" % k)
        if r.get("is_added") != (a["legal_status_ar"] == "مضافة"):
            e.append("[5] %s: is_added mismatch" % k)
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[5] %s: %s must be False" % (k, f))
    if seen != set(arts):
        e.append("[5] verified layer does not cover every source article")

    # [6] summary layer
    summ = json.load(open(SUMMARY, encoding="utf-8"))
    if summ.get("record_count") != N:
        e.append("[6] summary record_count != %d" % N)
    if summ.get("highest_article_number") != HIGHEST:
        e.append("[6] summary highest_article_number != %d" % HIGHEST)
    if summ.get("verification_tier") != EXPECTED_TIER:
        e.append("[6] summary verification_tier incorrect")
    if summ.get("decree") != EXPECTED_DECREE:
        e.append("[6] summary decree drifted")
    if not summ.get("known_unresolved_discrepancies"):
        e.append("[6] summary does not carry the discrepancy list")
    if len(summ.get("amendment_history", [])) != 6:
        e.append("[6] summary amendment_history should carry all six resolutions")

    # [7] LLM layer
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[7] llm count != %d" % N)
    if llm.get("article_range") != [1, HIGHEST]:
        e.append("[7] llm article_range != [1, %d]" % HIGHEST)
    if llm.get("mukarrar_count") != len(MUKARRAR):
        e.append("[7] llm mukarrar_count != %d" % len(MUKARRAR))
    ids = set()
    for r in recs:
        k = r["article_key"]
        ids.add(r["record_id"])
        if k not in arts:
            e.append("[7] %s: unknown article_key" % k)
            continue
        if r["article_text_ar"] != arts[k]["text"]:
            e.append("[7] %s: llm text != source" % k)
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[7] %s: hash mismatch" % k)
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[7] %s: missing retrieval metadata" % k)
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[7] %s: bad source_status in source_trust" % k)
        if r.get("source_trust", {}).get("verification_tier") != EXPECTED_TIER:
            e.append("[7] %s: source_trust missing verification_tier" % k)
        if r.get("english_used_for_correction") is not False:
            e.append("[7] %s: english_used_for_correction must be False" % k)
    if len(ids) != N:
        e.append("[7] record_id values are not unique across the %d records" % N)

    if e:
        print("FAIL: %d error(s) in Excise Tax Regulation track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: اللائحة التنفيذية للضريبة الانتقائية / Excise Tax Implementing "
          "Regulation — 67 records")
    print("  - REAL count 67 = 64 numbered articles + 3 مكرر (22/37/52); the corpus")
    print("    census figure 64 is the highest article number, recorded as a")
    print("    documented divergence")
    print("  - 48 اصلية / 16 معدلة / 3 مضافة, 23 chapters")
    print("  - IN-FORCE Board Resolution (9-1-17), 13 Ramadan 1438H, under Royal")
    print("    Decree M/86; consolidated through Resolution (06-06-25),")
    print("    8 Rajab 1447H / 28 Dec 2025")
    print("  - TIER_2: ZATCA official consolidated PDF x independent secondary")
    print("    cross-check (58/67 records have a counterpart; 9 do not)")
    print("  - resolutions (8-2-19), (2-3-19) and (14-6-22) are consolidated with NO")
    print("    per-article attribution in the source: flagged, never guessed")
    print("  - %d unresolved discrepancies recorded" % len(disc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
