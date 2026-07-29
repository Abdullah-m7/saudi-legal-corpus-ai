#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Real Estate
Contributions Law track (اللائحة التنفيذية لنظام المساهمات العقارية, REGA Board
of Directors Resolution by circulation No. Q/M/E/H/2024/1/T, 18/7/1445H).

40 records: 40 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (never amended as of this pass).
7 top-level structural blocks: Articles 1-7 (no chapter title in any of the 4
independently-fetched sources -- disclosed, not fabricated) plus 6 explicitly
titled chapters (الفصل الأول..السادس) covering Articles 8-40.

VERIFICATION TIER -- TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. See the generator
docstring and the source artifact's verification_methodology_note: FOUR
independent channels were reached (rega.gov.sa's own regulation page,
rega.gov.sa's own hosted signed/scanned PDF read visually in full, the Umm
Al-Qura Gazette's own website, and qanoonsa.com), matching exactly on 37/40
articles and the full chapter structure, but with THREE disclosed, unresolved
substantive conflicts remaining between the two REGA-hosted channels and the
Gazette+aggregator pair. This validator does not re-adjudicate provenance; it
only checks internal self-consistency of the ingested text and that every
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
TRACK = "real_estate_contributions_implementing_regulation"
SRC = os.path.join(ROOT, "sources", TRACK, "law", "official_source",
                   TRACK + "_official_source.json")
RECORDS = os.path.join(ROOT, "sources", TRACK, "law", "verified",
                       TRACK + "_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", TRACK, "law", "verified",
                       TRACK + "_verified_summary.json")
LLM = os.path.join(ROOT, "data", TRACK + "_arabic_legal_llm",
                   TRACK + "_legal_llm_001_040.json")
N = 40
KEY_RE = r"real_estate_contributions_implementing_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 40, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 7  # 1 untitled preliminary block + 6 numbered فصول

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
    "real_estate_contributions_implementing_regulation_decision_number_segment_order_variance",
    "real_estate_contributions_implementing_regulation_article8_item11_crossref_variance",
    "real_estate_contributions_implementing_regulation_article40_effective_date_clause_variance",
    "real_estate_contributions_implementing_regulation_article8_ministry_name_modernized_on_rega_website",
    "real_estate_contributions_implementing_regulation_website_typo_ikhtisasatuhum",
    "real_estate_contributions_implementing_regulation_articles_1_7_no_chapter_title_in_source",
    "real_estate_contributions_implementing_regulation_boe_not_checked",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰ]")


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
        parts = ch["articles"].split("-")
        lo = int(parts[0])
        hi = int(parts[1]) if len(parts) > 1 else lo
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

    if src.get("law_component") != "regulation":
        e.append("[1b] law_component must be 'regulation'")

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level structural blocks, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one chapter range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    # exactly one block (Articles 1-7) is allowed to carry a null label/title,
    # disclosing that no chapter heading exists in-source for those articles;
    # every other block must carry a unique, non-empty title.
    untitled = [c for c in chs if c.get("title_ar") is None]
    if len(untitled) != 1 or untitled[0].get("articles") != "1-7":
        e.append("[1c] expected exactly one untitled block covering Articles 1-7")
    titles = [c.get("title_ar") for c in chs if c.get("title_ar") is not None]
    if len(set(titles)) != len(titles):
        e.append("[1d] unexpected duplicate chapter title(s): %s"
                 % [t for t in titles if titles.count(t) > 1])

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
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        m = re.match(KEY_RE, k)
        n = int(m.group(1))
        # Articles 1-7 are disclosed as carrying no chapter title in-source;
        # all other articles must have a non-empty section_ar.
        if n > 7 and not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (chapter title)" % k)
        if n <= 7 and a.get("section_ar"):
            e.append("[2] %s: expected empty section_ar for undisclosed pre-chapter article" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
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
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[کیہ]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)
        if "‌" in a["text"] or "‍" in a["text"]:
            e.append("[2f] %s: residual ZWNJ/ZWJ artifact detected" % k)
        if "–" in a["text"] or "—" in a["text"]:
            e.append("[2f] %s: residual en/em-dash not normalized to hyphen-minus" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: unexpected residual Arabic-Indic digit (none expected/disclosed "
                     "for this track)" % k)

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
        e.append("[2k] missing amendment_history (must record the founding board resolution)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "ق/م/إ/هـ/2024/1/ت" not in decrees:
            e.append("[2k] amendment_history must reference founding decree ق/م/إ/هـ/2024/1/ت")

    # spot-checks anchoring key facts established this pass
    if src.get("decree_date_hijri") != "18/07/1445":
        e.append("[2j] decree_date_hijri mismatch with verified Board Resolution date 18/07/1445H")
    if src.get("legal_status_ar") != "نافذ":
        e.append("[2j] legal_status_ar must be نافذ")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (never amended)")
    if src.get("parent_law_track_id") != "real_estate_contributions_law":
        e.append("[2j] parent_law_track_id must reference real_estate_contributions_law")
    gaz = src.get("gazette_publication") or {}
    if gaz.get("issue_no") != "5020" or gaz.get("date_hijri") != "06/08/1445":
        e.append("[2j] gazette_publication must record Umm Al-Qura issue 5020, 06/08/1445H")

    art1 = arts.get("real_estate_contributions_implementing_regulation_art_001", {})
    if "طالب الترخيص" not in art1.get("text", "") or "اتفاقية المساهمة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (طالب الترخيص / اتفاقية المساهمة)")
    art40 = arts.get("real_estate_contributions_implementing_regulation_art_040", {})
    if "تنشر اللائحة في الجريدة الرسمية" not in art40.get("text", ""):
        e.append("[2j] Article 40 missing expected publication clause")
    art40_label = art40.get("number_label_ar")
    if art40_label != "المادة الأربعون":
        e.append("[2j] Article 40 number_label_ar must be 'المادة الأربعون', got %r" % art40_label)

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
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
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
    if llm.get("law_component") != "regulation":
        e.append("[5] llm law_component must be 'regulation'")
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
        print("FAIL: %d error(s) in Real Estate Contributions Implementing Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Real Estate Contributions Law")
    print("  - 40 records: 40 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (never amended)")
    print("  - 7 top-level structural blocks: Articles 1-7 (no chapter title in any of the 4")
    print("    independently-fetched sources -- disclosed) + 6 numbered chapters (Arts 8-40);")
    print("    article ranges verified to tile 1-40 exactly once")
    print("  - INSTRUMENT CONFIRMED: REGA Board of Directors Resolution (by circulation) No.")
    print("    (Q/M/E/H/2024/1/T), 18/7/1445H, issued under Article 37 of the parent Real Estate")
    print("    Contributions Law (Royal Decree M/203) and in agreement with CMA. Brand-new")
    print("    regulation track, flagged as a follow-up candidate by the parent law's own build.")
    print("  - VERIFICATION TIER: TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED -- 4 independent")
    print("    channels reached (rega.gov.sa page, rega.gov.sa signed PDF read visually in full,")
    print("    Umm Al-Qura Gazette, qanoonsa.com); 37/40 articles + full chapter structure match")
    print("    exactly, but 3 disclosed substantive conflicts remain unresolved between the two")
    print("    REGA-hosted channels and the Gazette+aggregator pair (decision-number digit order;")
    print("    Article 8 item 11's cross-reference number; Article 40's own effective-date")
    print("    clause) -- see known_unresolved_discrepancies before relying on Article 40.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
