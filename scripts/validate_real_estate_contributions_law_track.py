#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Real Estate Contributions Law track
(نظام المساهمات العقارية, Royal Decree M/203, 28/12/1444H -- the currently
in-force law governing real-estate collective-investment / crowdfunding-style
development schemes).

38 records: 38 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (the Law has had no amendments
per nezams.com: "لم يجرى عليه تعديل"). 7 chapters (فصول) confirmed both from
in-body chapter markers on nezams.com AND visually against the officially-hosted
scanned Royal-Decree PDF on rega.gov.sa (11/11 pages read page-by-page).

SUPERSESSION -- Article 38 repeals conflicting rules only via a GENERIC formula
("ويلغي كل ما يتعارض معه من أحكام"), without naming the predecessor Ministry of
Commerce instrument by number/date anywhere in the Law's own text, the Royal
Decree preamble, or CoM Resolution 881. This is disclosed, not guessed at.

VERIFICATION TIER -- TIER_1_PRIMARY_MULTI_SOURCE. See the generator docstring
and the source artifact's verification_methodology_note: laws.boe.gov.sa was
checked first but is unreachable this pass; instead, two other independent
official sources (rega.gov.sa's own officially-hosted scanned Royal-Decree PDF,
visually read page-by-page in full, and the Umm Al-Qura Gazette's own website)
were cross-verified against each other and against the nezams.com full-text
extraction used for storage, with an exact match apart from one immaterial
digit-script variance (Article 32). This validator does not re-adjudicate
provenance; it only checks internal self-consistency of the ingested text and
that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_contributions_law", "law", "official_source",
                   "real_estate_contributions_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "real_estate_contributions_law", "law", "verified",
                       "real_estate_contributions_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "real_estate_contributions_law", "law", "verified",
                       "real_estate_contributions_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "real_estate_contributions_law_arabic_legal_llm",
                   "real_estate_contributions_law_legal_llm_001_038.json")
N = 38
KEY_RE = r"real_estate_contributions_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 38, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 7  # 7 فصول

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
    "real_estate_contributions_law_boe_unreachable_alt_official_sources_used",
    "real_estate_contributions_law_article_32_penalty_digit_script_variance",
    "real_estate_contributions_law_predecessor_instrument_not_named_in_text",
    "real_estate_contributions_law_implementing_regulation_not_ingested",
    "real_estate_contributions_law_shura_two_resolutions",
}
AR = "ء-ي"
# NOTE: deliberately narrower than some other tracks' copy-pasted range in this
# corpus: U+064B-U+0652 (the actual tashkeel/harakat marks) plus U+0670
# (superscript alef). This EXCLUDES U+0660-U+0669 (Arabic-Indic digits) and
# U+066A-U+066D (percent sign/decimal separator/thousands separator/star),
# which this track's source deliberately preserves verbatim in a few places
# (Article 7's "١٥٪", Article 32's "٫" decimal separator) and which a wider
# range would misclassify as residual diacritics.
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
            e.append("[2] %s: missing section_ar (chapter title)" % k)
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
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)

    # NOTE: unlike waste_management_law, this source deliberately preserves ONE
    # Arabic-Indic digit occurrence verbatim (Article 7: "١٥٪", confirmed present
    # identically in the official rega.gov.sa scan too) -- so, unlike that
    # track's validator, we do NOT blanket-reject Arabic-Indic digits here. We
    # only assert the known occurrence is exactly where expected and disclosed.
    art7 = arts.get("real_estate_contributions_law_art_007", {})
    if not re.search(r"[٠-٩]", art7.get("text", "")):
        e.append("[2f] Article 7: expected preserved Arabic-Indic digit (١٥٪) is missing")
    for k, a in arts.items():
        if k == "real_estate_contributions_law_art_007":
            continue
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: unexpected residual Arabic-Indic digit (only Article 7 is "
                     "disclosed/expected to carry one)" % k)

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
        e.append("[2k] missing amendment_history (must record the founding M/203 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/203" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/203")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/203)" \
            or src.get("decree_date_hijri") != "28/12/1444":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/203, 28/12/1444H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (the Law has no amendments)")
    sup = src.get("supersedes_ar", "")
    if not sup or "المادة الثامنة والثلاثون" not in sup:
        e.append("[2j] supersedes_ar must anchor the (generic) repeal to Article 38 of this "
                 "Law's own text")
    if not src.get("preamble_ar") or "28 /12/ 1444" not in src.get("preamble_ar", "") \
            or "نظام المساهمات العقارية" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "28/12/1444H decree date and نظام المساهمات العقارية")
    if not src.get("com_resolution_ar") or "قرار مجلس الوزراء" not in src.get("com_resolution_ar", ""):
        e.append("[2j] com_resolution_ar (CoM Resolution 881 full text) must be present")

    art1 = arts.get("real_estate_contributions_law_art_001", {})
    if "الهيئة: الهيئة العامة للعقار" not in art1.get("text", "") \
            or "المساهمة العقارية:" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الهيئة / المساهمة العقارية)")
    art37 = arts.get("real_estate_contributions_law_art_037", {})
    if "اللائحة" not in art37.get("text", "") or "مائة وعشرين" not in art37.get("text", ""):
        e.append("[2j] Article 37 missing expected implementing-regulation mandate (اللائحة/مائة وعشرين)")
    art38 = arts.get("real_estate_contributions_law_art_038", {})
    if "ينشر النظام" not in art38.get("text", "") or "مائة وعشرين" not in art38.get("text", ""):
        e.append("[2j] Article 38 missing expected entry-into-force clause (مائة وعشرين يوما)")
    art38_label = art38.get("number_label_ar")
    if art38_label != "المادة الثامنة والثلاثون":
        e.append("[2j] Article 38 number_label_ar must be 'المادة الثامنة والثلاثون', got %r"
                 % art38_label)

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
        print("FAIL: %d error(s) in Real Estate Contributions Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Real Estate Contributions Law (نظام المساهمات العقارية)")
    print("  - 38 records: 38 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (the Law has had no amendments)")
    print("  - 7 chapters (فصول) confirmed both from nezams.com's in-body chapter markers and")
    print("    visually against the officially-hosted scanned Royal-Decree PDF on rega.gov.sa")
    print("    (11/11 pages read page-by-page); article ranges verified to tile 1-38 exactly once")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/203, 28/12/1444H (CoM Resolution 881,")
    print("    23/12/1444H; Shura Resolutions 305/45 and 152/21). Brand-new base-law track, not")
    print("    previously in this corpus; distinct from real_estate_finance_law/investment_law.")
    print("  - SUPERSESSION: Article 38 repeals conflicting rules only via a GENERIC formula,")
    print("    without naming the predecessor Ministry of Commerce instrument by number/date.")
    print("  - VERIFICATION TIER: TIER_1_PRIMARY_MULTI_SOURCE -- laws.boe.gov.sa checked first")
    print("    but unreachable this pass; instead cross-verified word-for-word, article-by-")
    print("    article, against rega.gov.sa's officially-hosted scanned Royal-Decree PDF (visual")
    print("    page-by-page read, 11/11 pages) AND the Umm Al-Qura Gazette's own website")
    print("    (uqn.gov.sa/details?p=23304), both matching exactly apart from one immaterial")
    print("    digit-script variance (Article 32, disclosed).")
    print("  - Implementing Regulation (Article 37 mandate) exists per multiple independent")
    print("    signals (eparticipation.my.gov.sa, rega.gov.sa, argaam.com, qanoonsa.com) but is")
    print("    flagged as a follow-up candidate (real_estate_contributions_law_regulation), NOT")
    print("    ingested this pass -- its exact ministerial-decision citation could not be pinned")
    print("    down and verified within reasonable effort this pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
