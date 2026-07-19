#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Arabian
Nationality Law track (35 records: 34 اصلية, 0 معدلة, 1 ملغاة [Article 28],
0 مضافة; flat 35-article structure, no formal أبواب/فصول numbering).

VERIFICATION TIER -- see the generator's module docstring and
sources/nationality/regulation/official_source/
nationality_regulation_official_source.json's verification_methodology_note
for the full account: laws.boe.gov.sa was checked FIRST (per this corpus's
standard methodology) but confirmed to host NO dedicated page at all for
this Implementing Regulation. The PRIMARY source actually used is
moi.gov.sa (the issuing Ministry's own site, byte-identical across Wayback
snapshots spanning 2011-2024), cross-verified against nezams.com (decree
number/date) and alriyadh.com's 2005G contemporaneous full-text
reproduction (which independently resolves this corpus's own prior
"~25 articles" gap-map estimate to the true count of 35). Article 28 was
deleted by a 2023 Minister of Interior decision (independently confirmed by
5+ news outlets) but moi.gov.sa's own PDF remains stale and still shows its
pre-deletion text -- preserved here verbatim with legal_status_ar=ملغاة, per
this corpus's binding rule that repealed articles are flagged, never
deleted. This validator does not re-adjudicate any of this; it only checks
internal self-consistency of the text this track actually ingests, and that
every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "nationality", "regulation", "official_source",
                   "nationality_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "nationality", "regulation", "verified",
                       "nationality_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "nationality", "regulation", "verified",
                       "nationality_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "nationality_regulation_arabic_legal_llm",
                   "nationality_regulation_legal_llm_001_035.json")
N = 35
KEY_RE = r"nationality_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 34, "معدلة": 0, "ملغاة": 1, "مضافة": 0}
EXPECTED_TOP_LEVEL_SECTIONS = 1  # single flat range, no أبواب/فصول

REPEALED_NUMS = (28,)
REPEALED_KEYS = {"nationality_regulation_art_%03d" % n for n in REPEALED_NUMS}
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "nationality_regulation_gap_map_article_count_corrected_25_to_35",
    "nationality_regulation_boe_no_dedicated_page",
    "nationality_regulation_moi_live_unreachable",
    "nationality_regulation_no_preamble_in_primary_source",
    "nationality_regulation_article28_repealed",
    "nationality_regulation_no_named_predecessor",
    "nationality_regulation_ligature_drop_and_rtl_reorder_fixed",
    "nationality_regulation_secondary_transcription_typos_fixed",
    "nationality_regulation_spelled_ordinal_headers_no_baab_fasl",
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


def _iter_section_ranges(chs):
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
    if n_top != EXPECTED_TOP_LEVEL_SECTIONS:
        e.append("[1c] expected %d flat section (no formal أبواب/فصول), "
                  "got %d" % (EXPECTED_TOP_LEVEL_SECTIONS, n_top))

    covered = set()
    for lo, hi in _iter_section_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one section range" % n)
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
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in REPEALED_KEYS and not a.get("history"):
            e.append("[2] %s: repealed article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in AMENDED_KEYS and k not in REPEALED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended/non-repealed article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # ligature-drop-bug regression guard (المخ/المختص family must never collapse to اتص/اتصة)
        for w in re.findall(r"[%s]*اتص[%s]*" % (AR, AR), a["text"]):
            e.append("[2g] %s: unresolved ligature-drop artifact (اتص for مختص): %r" % (k, w))
        # any tashkeel residue (this track strips diacritics uniformly)
        if re.search(r"[ً-ْ]", a["text"]):
            e.append("[2h] %s: residual tashkeel (diacritics) not stripped" % k)

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
        e.append("[2k] missing amendment_history (must record founding decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "74" not in decrees or "زو" not in decrees:
            e.append("[2k] amendment_history must reference founding decree 74/زو")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("nationality_regulation_art_001", {})
    if "سن الرشد" not in art1.get("text", "") or "8/20/5604" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (سن الرشد) or reference to the "
                 "parent Law's own decree number (8/20/5604)")
    art28 = arts.get("nationality_regulation_art_028", {})
    if "يصدر وزير الداخلية القرارات اللازمة لمنح الجنسية بموجب المادة (8)" not in art28.get("text", ""):
        e.append("[2j] Article 28 must preserve its pre-repeal text verbatim (not fabricated, "
                 "not blanked)")
    if art28.get("legal_status_ar") != "ملغاة":
        e.append("[2j] Article 28 must be marked ملغاة (repealed)")
    art35 = arts.get("nationality_regulation_art_035", {})
    if "تنشر هذه اللائحة في الجريدة الرسمية" not in art35.get("text", ""):
        e.append("[2j] Article 35 must be the closing publication/effective-date article")
    if src.get("decree") != "القرار الوزاري رقم (74/زو)" or src.get("decree_date_hijri") != "9/3/1426":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Ministerial Decision "
                 "74/زو, 9/3/1426H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (single-version instrument with "
                 "one article-level repeal, not a consolidated multi-amendment law)")

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

    if e:
        print("FAIL: %d error(s) in Nationality Implementing Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Arabian Nationality Law")
    print("  - 35 records: 34 اصلية, 0 معدلة, 1 ملغاة (المادة 28), 0 مضافة")
    print("  - flat 35-article structure, no formal أبواب/فصول numbering, spelled-ordinal headers")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa checked first but confirmed to host NO")
    print("    dedicated page at all for this Implementing Regulation; PRIMARY source is moi.gov.sa")
    print("    (issuing Ministry's own site, byte-identical across Wayback snapshots 2011-2024),")
    print("    cross-verified against nezams.com (decree number/date) and alriyadh.com's 2005G")
    print("    contemporaneous full-text reproduction (35 articles, word-for-word match)")
    print("  - Ministerial Decision No. 74/زو (9/3/1426H / 22 Apr 2005G), issued by the Minister of")
    print("    Interior under Nationality Law Article 27 (as amended by M/54, 29/10/1425H)")
    print("  - ARTICLE COUNT CORRECTED: 35 articles, not ~25 as this corpus's own prior gap-map")
    print("    light-verification pass estimated -- traced to an internal self-contradiction in a")
    print("    single 2005G news source (its own prose said 25; its own reproduced full text ran")
    print("    to Article 35), resolved via two independent, cross-matching full-text sources")
    print("  - CONFIRMED REPEAL: Article 28 deleted by a 2023 Minister of Interior decision")
    print("    (5+ independent news outlets), following M/88 (11/6/1444H) transferring the parent")
    print("    Law's Article 8 grant authority to the Prime Minister; moi.gov.sa's own PDF is")
    print("    confirmed STALE and still shows Article 28's pre-repeal text -- preserved here")
    print("    verbatim, legal_status_ar=ملغاة, not deleted or merged away")
    print("  - CONFIRMED NEGATIVE FINDING: this Regulation names no repealed predecessor of its own")
    print("    (it is the first and only Implementing Regulation for this Law since 1374H)")
    print("  - Two source-artifact-layer (not content) defects in moi.gov.sa's own PDF corrected by")
    print("    using alriyadh.com's 2005G contemporaneous full-text as the base transcription: a")
    print("    font ligature-drop bug (المختص/المختصة -> اتص/اتصة, 5 places) and an RTL")
    print("    line-reordering artifact (2 short paragraphs); plus two single-letter typos in")
    print("    alriyadh's own text fixed against moi.gov.sa's spelling. Diacritics stripped uniformly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
