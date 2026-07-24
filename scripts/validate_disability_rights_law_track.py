#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Rights of Persons with Disabilities Law
track (نظام حقوق الأشخاص ذوي الإعاقة; 33 records, ALL اصلية, 0 معدلة, 0 ملغاة,
0 مضافة; 5 chapters أبواب).

VERIFICATION TIER -- see the generator's module docstring and
sources/disability_rights/law/official_source/disability_rights_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa HAS a
dedicated lawId page for this law (e52b691a-785c-42a7-8916-b07d00e4fd38) but it
was unreachable this pass (HTTP 503 live / connection reset). web.archive.org
was CONFIRMED egress-blocked for this session (explicit "Blocked by egress
policy" from curl and an explicit WebFetch refusal) and NOT bypassed. Full
verbatim text is from nezams.com, cross-checked article-by-article against
qanoonsa.com (a second, technically unrelated independent aggregator) -- exact
match for all 33 articles modulo enumeration-digit glyph style -> TIER_3. This
validator does not re-adjudicate provenance; it only checks internal
self-consistency and that every discrepancy is still recorded.

MATERIAL FACTS checked: 5-chapter structure (chapter_structure covers exactly
articles 1-33 with no gaps/overlaps); all 33 articles اصلية with empty history;
Article 32 carries the EXPLICIT named-predecessor repeal of نظام رعاية
المعوقين (Royal Decree M/37, 23/9/1421H) -- a genuine, rare, confirmed
named-predecessor repeal, not a vague general-conflict clause.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "disability_rights", "law", "official_source",
                   "disability_rights_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "disability_rights", "law", "verified",
                       "disability_rights_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "disability_rights", "law", "verified",
                       "disability_rights_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "disability_rights_arabic_legal_llm",
                   "disability_rights_law_legal_llm_001_033.json")
N = 33
KEY_RE = r"disability_rights_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 33, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 5  # 5 أبواب

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "disability_rights_law_boe_dedicated_page_exists_but_unreachable",
    "disability_rights_law_web_archive_blocked",
    "disability_rights_law_named_repeal_of_predecessor_m37_1421h",
    "disability_rights_law_no_amendments_since_enactment",
    "disability_rights_law_implementing_regulation_out_of_scope",
    "disability_rights_law_violations_committee_rules_out_of_scope",
    "disability_rights_law_digit_glyph_style_normalized",
    "disability_rights_law_hrsd_page_unproductive",
    "disability_rights_law_uqn_primary_gazette_page_not_located",
    "disability_rights_law_gregorian_dates_cross_referenced",
    "disability_rights_law_tashkeel_stripped",
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

    # continuous 1..33, no gaps/dupes
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    # 5-chapter structure covers exactly 1..33
    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (أبواب), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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

    titles = [c.get("title_ar") for c in chs]
    if len(set(titles)) != len(titles):
        e.append("[1d] unexpected duplicate chapter title(s): %s"
                 % [t for t in titles if titles.count(t) > 1])

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a.get("status") or not str(a.get("status")).strip():
            e.append("[2] %s: empty verification status string" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (chapter title)" % k)
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
        if a.get("history"):
            e.append("[2i] %s: no article in this unamended law should carry history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # this corpus normalizes enumeration digits to Western glyphs
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2g] %s: residual Eastern-Arabic-Indic digit found (must be normalized "
                     "to Western digits per known discrepancy note)" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

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

    ah = src.get("amendment_history")
    if not ah:
        e.append("[2k] missing amendment_history (must record founding decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "م/27" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/27")

    # spot-checks anchoring key facts
    art1 = arts.get("disability_rights_law_art_001", {}).get("text", "")
    if "الشخص ذو الإعاقة" not in art1 or "الهيئة" not in art1:
        e.append("[2j] Article 1 missing expected definitions (الشخص ذو الإعاقة / الهيئة)")
    art2 = arts.get("disability_rights_law_art_002", {}).get("text", "")
    if "عدم التمييز" not in art2:
        e.append("[2j] Article 2 missing expected non-discrimination principle")
    art31 = arts.get("disability_rights_law_art_031", {}).get("text", "")
    if "اللائحة" not in art31 or "مائة وعشرين" not in art31:
        e.append("[2j] Article 31 missing expected implementing-regulation mandate (120 days)")
    art32 = arts.get("disability_rights_law_art_032", {}).get("text", "")
    for token in ("رعاية المعوقين", "م/37", "1421", "يلغي"):
        if token not in art32:
            e.append("[2j] Article 32 (named-predecessor repeal) missing expected token %r" % token)
    art33 = arts.get("disability_rights_law_art_033", {}).get("text", "")
    if "مائة وعشرين" not in art33:
        e.append("[2j] Article 33 missing expected 120-day effective-date clause")

    # exactly ONE repeal clause in the whole statute (Article 32), and it names M/37
    repeal_hits = [k for k, a in arts.items() if re.search(r"يلغي|يلغى|يُلغى|يلغ", a["text"])]
    if repeal_hits != ["disability_rights_law_art_032"]:
        e.append("[2j] expected exactly one repeal-bearing article (032), found: %s" % sorted(repeal_hits))

    if src.get("decree") != "المرسوم الملكي رقم م/27" or src.get("decree_date_hijri") != "11/2/1445":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/27, 11/2/1445H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendments exist for this law)")
    pre = src.get("preamble_ar", "")
    if not pre or "110" not in pre or "نظام حقوق الأشخاص ذوي الإعاقة" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 110 and the law name")
    if "م/37" not in pre or "1421" not in pre:
        e.append("[2j] preamble_ar (CoM Resolution 110 recitals) must reference the repealed "
                 "predecessor نظام رعاية المعوقين (م/37, 1421H)")

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
        if r.get("legal_status_ar") != a.get("legal_status_ar"):
            e.append("[4] %s: legal_status_ar mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("consolidated_amended_law") is not False:
        e.append("[4b] summary consolidated_amended_law must be False")

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
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Disability Rights Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Rights of Persons with Disabilities Law (نظام حقوق الأشخاص ذوي الإعاقة)")
    print("  - 33 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- no amendment since enactment")
    print("  - 5 chapters (أبواب): تعريفات ومبادئ عامة (1-2), الحقوق والخدمات (3-14),")
    print("    الدعم الاجتماعي والاقتصادي (15-20), المخالفات والعقوبات (21-28), أحكام ختامية (29-33)")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa HAS a dedicated lawId page")
    print("    (e52b691a-785c-42a7-8916-b07d00e4fd38) but was unreachable this pass (live HTTP 503;")
    print("    connection reset via curl). web.archive.org CONFIRMED egress-blocked for this session")
    print("    (explicit block message + explicit WebFetch refusal) and NOT bypassed. Full text from")
    print("    nezams.com cross-checked verbatim article-by-article against qanoonsa.com (a second,")
    print("    technically unrelated independent aggregator) -- exact match for all 33 articles")
    print("  - Royal Decree M/27 (11/2/1445H, ~2023G), CoM Resolution 110 (6/2/1445H), published")
    print("    Umm al-Qura gazette issue 4997 (8 September 2023G)")
    print("  - NAMED-PREDECESSOR REPEAL (Article 32, confirmed 3 independent ways: nezams.com text,")
    print("    qanoonsa.com text, AND CoM Resolution 110's own recitals): this law EXPLICITLY repeals")
    print("    نظام رعاية المعوقين (Royal Decree M/37, 23/9/1421H)")
    print("  - Follow-up candidates NOT ingested: Implementing Regulation (Article 31 mandate,")
    print("    published Umm al-Qura) and Violations-Committee procedural rules (Resolution 27,")
    print("    22/1/1446H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
