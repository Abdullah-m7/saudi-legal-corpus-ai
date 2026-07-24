#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Child Protection Law track
(26 records: 21 اصلية, 4 معدلة [Articles 12, 15, 19, 23], 0 ملغاة, 1 مضافة
[Article 23-mukarrar]; 5 chapters فصول; 25 numbered articles + 1 mukarrar).

VERIFICATION TIER -- see the generator's module docstring and
sources/child_protection/law/official_source/child_protection_law_official_source.json's
verification_methodology_note: laws.boe.gov.sa HAS a dedicated lawId page for
this law (2d3cb83a-0379-4cde-8e0b-a9a700f272bd) but it was unreachable this pass
(HTTP 503 live; Wayback NOT attempted -- egress-policy-blocked). Full verbatim
text from nezams.com (HTTP 200); decree identity + 5-chapter structure + the
original 25-article text independently confirmed by the OFFICIAL Ministry of
Justice Adl-journal PDF (pre-amendment 1436H), and the 1443H amendment (CoM 427
/ RD M/72) via the Umm Al-Qura gazette + WebSearch -> TIER_3. This validator does
not re-adjudicate provenance; it checks internal self-consistency and that every
discrepancy is recorded.

AMENDED-ARTICLE TEXT POLICY checked: for the 4 amended articles the `text` field
holds the ORIGINAL verbatim wording with the verbatim CoM-427 amendment preserved
in `history` (never silently merged); the added Article 23-mukarrar holds its
added verbatim text.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "child_protection", "law", "official_source",
                   "child_protection_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "child_protection", "law", "verified",
                       "child_protection_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "child_protection", "law", "verified",
                       "child_protection_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "child_protection_arabic_legal_llm",
                   "child_protection_law_legal_llm_001_025.json")
N = 26                 # total records
N_NUMBERED = 25        # numbered articles 1..25
KEY_RE = r"child_protection_law_art_(\d{3})(?:_mukarrar)?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 21, "معدلة": 4, "ملغاة": 0, "مضافة": 1}
EXPECTED_TOP_LEVEL_CHAPTERS = 5  # 5 فصول

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
STATUS_ADDED_DATED = "ADDED_DATED"
AMENDED_KEYS = {
    "child_protection_law_art_012",
    "child_protection_law_art_015",
    "child_protection_law_art_019",
    "child_protection_law_art_023",
}
ADDED_KEYS = {"child_protection_law_art_023_mukarrar"}
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS = {"child_protection_law_art_023_mukarrar"}
HISTORY_KEYS = AMENDED_KEYS | ADDED_KEYS
EXPECTED_STATUS_BY_KEY = {k: STATUS_AMENDED_DATED for k in AMENDED_KEYS}
EXPECTED_STATUS_BY_KEY.update({k: STATUS_ADDED_DATED for k in ADDED_KEYS})
FLAGGED_DISCREPANCY_KEYS = {
    "child_protection_law_boe_dedicated_page_exists_but_unreachable",
    "child_protection_law_amended_by_com_427_1443",
    "child_protection_law_amended_articles_text_is_original_not_consolidated",
    "child_protection_law_added_mukarrar_23",
    "child_protection_law_chapter4_boundary_nezams_vs_moj",
    "child_protection_law_moj_pdf_bidi_artifacts",
    "child_protection_law_implementing_regulation_out_of_scope",
    "child_protection_law_distinct_from_juveniles_and_abuse",
    "child_protection_law_gregorian_date_not_pinpointed",
    "child_protection_law_preamble_source_typo_preserved",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one chapter range" % n)
            covered.add(n)
    if covered != set(range(1, N_NUMBERED + 1)):
        missing = sorted(set(range(1, N_NUMBERED + 1)) - covered)
        extra = sorted(covered - set(range(1, N_NUMBERED + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    titles = [c.get("title_ar") for c in chs]
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
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        # history discipline: amended/added carry history; others empty
        if k in HISTORY_KEYS and not a.get("history"):
            e.append("[2] %s: amended/added article missing history" % k)
        if k not in HISTORY_KEYS and a.get("history"):
            e.append("[2i] %s: original article must have empty history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source supplies no inline "
                     "per-article titles -- section_ar carries the chapter title)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact (should be straight quotes)" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

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
        e.append("[2k] missing amendment_history (must record founding decree + amendment)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/14" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/14")
        if "م/72" not in decrees:
            e.append("[2k] amendment_history must reference amending decree م/72 (1443H)")

    # ---- amended/added article content spot-checks (anchoring the disclosed amendment) ----
    def hist_join(k):
        return " ".join(json.dumps(h, ensure_ascii=False) for h in arts.get(k, {}).get("history", []))

    a12 = arts.get("child_protection_law_art_012", {})
    if a12.get("legal_status_ar") != "معدلة":
        e.append("[3] Article 12 must be معدلة")
    if "السلوكي أو الفكري" not in hist_join("child_protection_law_art_012"):
        e.append("[3] Article 12 history must contain the added phrase (السلوكي أو الفكري)")
    if "السلوكي أو الفكري" in a12.get("text", ""):
        e.append("[3] Article 12 text must be the ORIGINAL wording (added phrase belongs in history)")
    if "حضانة" not in hist_join("child_protection_law_art_015"):
        e.append("[3] Article 15 history must contain the added custody paragraph (حضانة)")
    if "وزارة الموارد البشرية" not in hist_join("child_protection_law_art_019"):
        e.append("[3] Article 19 history must contain the amended text (وزارة الموارد البشرية)")
    if "الثالثة والعشرين مكرر" not in hist_join("child_protection_law_art_023"):
        e.append("[3] Article 23 history must reference the new Article 23-mukarrar")
    mk = arts.get("child_protection_law_art_023_mukarrar", {})
    if mk.get("legal_status_ar") != "مضافة" or not mk.get("is_mukarrar"):
        e.append("[3] Article 23-mukarrar must be مضافة and is_mukarrar=true")
    if "السجن" not in mk.get("text", "") or "مائة" not in mk.get("text", ""):
        e.append("[3] Article 23-mukarrar text must contain the criminal penalty (السجن / مائة ألف)")
    if mk.get("number_label_ar") != "المادة الثالثة والعشرون مكرر":
        e.append("[3] Article 23-mukarrar number_label_ar mismatch")

    # ---- original-article spot-checks ----
    a1 = arts.get("child_protection_law_art_001", {})
    if "الثامنة عشرة" not in a1.get("text", "") or "الطفل" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected definition of الطفل (under 18)")
    a25 = arts.get("child_protection_law_art_025", {})
    if "تسعين" not in a25.get("text", ""):
        e.append("[2j] Article 25 missing expected 90-day effective-date clause")

    if src.get("decree") != "المرسوم الملكي رقم م/14" or src.get("decree_date_hijri") != "3/2/1436":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/14, 3/2/1436H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this law HAS a dated amendment)")
    pre = src.get("preamble_ar", "")
    if not pre or "(50)" not in pre or "نظام حماية الطفل" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 50 and نظام حماية الطفل")

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
        print("FAIL: %d error(s) in Child Protection Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Child Protection Law")
    print("  - 26 records: 21 اصلية, 4 معدلة (Articles 12, 15, 19, 23), 0 ملغاة, 1 مضافة")
    print("    (Article 23-mukarrar); 25 numbered articles + 1 mukarrar; 5 chapters (فصول)")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa HAS a dedicated lawId page")
    print("    (2d3cb83a-0379-4cde-8e0b-a9a700f272bd) but was unreachable this pass (live HTTP 503;")
    print("    Wayback NOT attempted -- egress-policy-blocked). Full verbatim text from nezams.com;")
    print("    decree identity + 5-chapter structure + original 25-article text independently")
    print("    confirmed by the OFFICIAL Ministry of Justice Adl-journal PDF (pre-amendment 1436H),")
    print("    and the 1443H amendment (CoM 427 / RD M/72) via the Umm Al-Qura gazette + WebSearch")
    print("  - Royal Decree M/14 (3/2/1436H, ~2014G), CoM Resolution 50 (24/1/1436H), published")
    print("    4/3/1436H; administered by the Ministry of Human Resources and Social Development")
    print("  - AMENDMENT: CoM Resolution 427 (5/8/1443H) / Royal Decree M/72 (6/8/1443H) amended")
    print("    Articles 12, 15, 19, 23 and ADDED Article 23-mukarrar (criminal penalties for child")
    print("    abuse). Amended articles keep ORIGINAL verbatim text in `text`; the verbatim CoM-427")
    print("    amendment is preserved in `history` (never silently merged)")
    print("  - DISTINCT statute from juveniles_law (نظام الأحداث, M/113 1439H, 24 articles) and from")
    print("    the separate protection_from_abuse candidate (نظام الحماية من الإيذاء)")
    print("  - Implementing regulation (ministerial decision 56386, 16/6/1436H) identified but NOT")
    print("    ingested this pass (one-instrument-per-pass); follow-up candidate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
