#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Anti-Smoking Law track (نظام مكافحة
التدخين; 20 records: all اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; FLAT statute --
no chapters/فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/anti_smoking/law/official_source/anti_smoking_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa HAS a
dedicated lawId page for this law (93b6f7f3-1083-46e7-b30e-a9a700f291b0) but
it was unreachable this pass (HTTP 503 live / connection-reset via curl; a
Wayback snapshot of this exact page was confirmed to exist via
archive.org/wayback/available, but fetching its content over web.archive.org
itself returned "Blocked by egress policy" and was NOT bypassed). ORIGINAL
full text is from an OFFICIAL Ministry of Health PDF (moh.gov.sa, joint
MOH/National Committee for Tobacco Control publication), cross-checked
verbatim against nezams.com (raw HTML, BeautifulSoup-parsed, not merely an
AI-mediated fetch-tool summary) and a bilingual cloudfront.net legislation
PDF -> TIER_2. This validator does not re-adjudicate provenance; it only
checks internal self-consistency and that every discrepancy is still
recorded.

MATERIAL FACTS checked: flat structure (chapter_structure == []); ALL 20
articles اصلية with empty history[]; NO predecessor repeal clause exists (but
a transitional continuation clause is documented); NO amendment to the Law
itself (only its Implementing Regulation, out of scope, has been amended).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_smoking", "law", "official_source",
                   "anti_smoking_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "anti_smoking", "law", "verified",
                       "anti_smoking_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "anti_smoking", "law", "verified",
                       "anti_smoking_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "anti_smoking_arabic_legal_llm",
                   "anti_smoking_law_legal_llm_001_020.json")
N = 20
KEY_RE = r"anti_smoking_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {k: STATUS_AMENDED_DATED for k in AMENDED_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "anti_smoking_boe_dedicated_page_exists_but_unreachable",
    "anti_smoking_no_named_predecessor_repeal_but_transitional_clause",
    "anti_smoking_no_amendment_to_law_itself_confirmed",
    "anti_smoking_implementing_regulation_out_of_scope",
    "anti_smoking_moh_pdf_pdftotext_extraction_failure_visual_reading_used",
    "anti_smoking_tashkeel_stripped",
    "anti_smoking_gregorian_date_not_pinpointed",
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

    # continuous 1..20, no gaps/dupes
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    # FLAT statute: chapter_structure MUST be empty (no chapters/فصول)
    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1c] this statute is flat (no chapters); chapter_structure must be [] but is %r"
                 % (chs,))

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
        # FLAT statute: section_ar MUST be empty for every article (no chapter titles)
        if a.get("section_ar") != "":
            e.append("[2] %s: section_ar must be empty for this flat statute" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

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
        if "م/56" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/56")

    # spot-checks anchoring key facts
    art1 = arts.get("anti_smoking_law_art_001", {}).get("text", "")
    if "مكافحة التدخين" not in art1:
        e.append("[2j] Article 1 missing expected objective clause")
    art3 = arts.get("anti_smoking_law_art_003", {}).get("text", "")
    if "تحظر زراعة" not in art3:
        e.append("[2j] Article 3 missing expected growing/manufacturing ban")
    art7 = arts.get("anti_smoking_law_art_007", {}).get("text", "")
    for token in ("المساجد", "9 -", "ثمانية عشر"):
        if token not in art7:
            e.append("[2j] Article 7 missing expected token %r" % token)
    art8 = arts.get("anti_smoking_law_art_008", {}).get("text", "")
    if "8 -" not in art8 or "ثمانية عشر" not in art8:
        e.append("[2j] Article 8 missing expected 8-item sale-restriction structure")
    art13 = arts.get("anti_smoking_law_art_013", {}).get("text", "")
    if "20.000" not in art13:
        e.append("[2j] Article 13 missing expected 20,000 SAR fine")
    art14 = arts.get("anti_smoking_law_art_014", {}).get("text", "")
    if "200" not in art14:
        e.append("[2j] Article 14 missing expected 200 SAR fine")
    art15 = arts.get("anti_smoking_law_art_015", {}).get("text", "")
    if "5000" not in art15:
        e.append("[2j] Article 15 missing expected 5,000 SAR cap")
    art19 = arts.get("anti_smoking_law_art_019", {}).get("text", "")
    if "اللائحة التنفيذية" not in art19 or "ستة أشهر" not in art19:
        e.append("[2j] Article 19 missing expected implementing-regulation mandate")
    art20 = arts.get("anti_smoking_law_art_020", {}).get("text", "")
    if "سنة" not in art20:
        e.append("[2j] Article 20 missing expected 1-year effective-date clause")

    # NO predecessor repeal anywhere (the law has only a transitional continuation clause)
    for k, a in arts.items():
        if re.search(r"يلغى|يُلغى|يلغي|إلغاء كل|كل ما يتعارض", a["text"]):
            e.append("[2j] %s: unexpected repeal clause in a law with no repeal (transitional "
                     "continuation clause only, recorded in preamble/known_unresolved_"
                     "discrepancies, not in article text)" % k)

    if src.get("decree") != "المرسوم الملكي رقم م/56" or src.get("decree_date_hijri") != "28/7/1436":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/56, 28/7/1436H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendment to the Law itself)")
    pre = src.get("preamble_ar", "")
    if not pre or "90" not in pre or "نظام مكافحة التدخين" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 90 and the law name")
    if "استمرار الجهات الحكومية" not in pre:
        e.append("[2j] preamble_ar must retain the transitional continuation clause verbatim")

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
        if (r.get("is_amended")) != (r["article_key"] in AMENDED_KEYS):
            e.append("[4] %s: is_amended flag mismatch" % r["article_key"])
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
        print("FAIL: %d error(s) in Anti-Smoking Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Anti-Smoking Law (نظام مكافحة التدخين)")
    print("  - 20 records: all اصلية, 0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - FLAT statute: continuous 1-20, NO chapters/فصول (chapter_structure == [],")
    print("    section_ar empty by design)")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa HAS a dedicated lawId page")
    print("    (93b6f7f3-1083-46e7-b30e-a9a700f291b0) but was unreachable this pass (live HTTP")
    print("    503 / connection-reset; a confirmed Wayback snapshot's content could not be")
    print("    fetched -- web.archive.org egress-blocked, not bypassed). ORIGINAL full text from")
    print("    an official Ministry of Health PDF (moh.gov.sa), cross-checked verbatim against")
    print("    nezams.com (raw HTML) and a bilingual cloudfront.net legislation PDF")
    print("  - Royal Decree M/56 (28/7/1436H, ~2015G), CoM Resolution 90 (23/3/1434H), published")
    print("    Umm al-Qura 2/9/1436H. NO amendment to the Law itself (only its Implementing")
    print("    Regulation has been amended, out of scope)")
    print("  - NO named-predecessor repeal clause; the Royal Decree/CoM Resolution 90 preambles")
    print("    instead carry a TRANSITIONAL clause letting unnamed prior agency-level")
    print("    anti-smoking regulations continue temporarily until this Law's own Implementing")
    print("    Regulation issues -- documented, not treated as a confirmed repeal")
    print("  - Follow-up candidate NOT ingested: Implementing Regulation (3rd edition 2019;")
    print("    amended inter alia by Ministerial Resolution 797557, 1/5/1441H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
