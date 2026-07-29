#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Road Transport Law track (نظام
النقل البري على الطرق, Royal Decree M/188, 24/8/1446H -- the currently
in-force Road Transport Law).

34 records: 34 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (no evidence of any amendment
to this Law was found this pass). NO chapter/فصل structure -- a directly
numbered law running straight from Article 1 to Article 34.

SUPERSESSION -- confirmed INSIDE the Law's own Article 33: "يحل النظام محل
نظام النقل العام على الطرق بالمملكة العربية السعودية، الصادر بالمرسوم الملكي
رقم (م/25) وتاريخ 21/6/1397هـ، ويلغي جميع ما يتعارض معه."

VERIFICATION TIER -- TIER_2. See the generator docstring and the source
artifact's verification_methodology_note: uqn.gov.sa (the Official Umm
Al-Qura Gazette's own live portal) was fetched directly (a genuine primary
source) and its 34-article text was cross-verified article-by-article
against two independent secondary sources (qanoonsa.com, nezams.com) with
full agreement after Unicode normalization. laws.boe.gov.sa (this corpus's
usual second primary source) was checked first per standard methodology but
has no dedicated page for this brand-new law and is itself unreachable this
pass; tga.gov.sa was also attempted and is unreachable. This validator does
not re-adjudicate provenance; it only checks internal self-consistency of the
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
SRC = os.path.join(ROOT, "sources", "road_transport_law", "law", "official_source",
                   "road_transport_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "road_transport_law", "law", "verified",
                       "road_transport_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "road_transport_law", "law", "verified",
                       "road_transport_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "road_transport_law_arabic_legal_llm",
                   "road_transport_law_legal_llm_001_034.json")
N = 34
KEY_RE = r"road_transport_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 34, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 0  # no فصول in this law

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
    "road_transport_law_boe_no_dedicated_lawid_and_unreachable",
    "road_transport_law_tga_gov_sa_unreachable",
    "road_transport_law_cosmetic_cross_source_differences_resolved",
    "road_transport_law_no_chapter_structure",
    "road_transport_law_repeal_inside_article_33_not_decree",
    "road_transport_law_decree_own_clauses_outside_articles",
    "road_transport_law_decree_signature_lines_from_qanoonsa",
    "road_transport_law_implementing_regulations_cluster_out_of_scope",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ٰٟ]")


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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits only)" % k)
        if re.search(r"[یکے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)
        if "٪" in a["text"]:
            e.append("[2g] %s: residual Arabic percent sign (٪); this track's canonical text uses "
                     "the Latin '%%' per uqn.gov.sa" % k)
        if "‏" in a["text"] or "‎" in a["text"]:
            e.append("[2g] %s: residual RLM/LRM directional-mark artifact detected" % k)

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
        e.append("[2k] missing amendment_history (must record the founding M/188 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/188" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/188")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/188)" \
            or src.get("decree_date_hijri") != "24/8/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/188, 24/8/1446H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendments found this pass)")
    sup = src.get("supersedes_ar", "")
    if not sup or "م/25" not in sup or "المادة الثالثة والثلاثون" not in sup:
        e.append("[2j] supersedes_ar must name the repealed instrument (م/25) and anchor the "
                 "repeal to Article 33 of this Law's own text")
    preamble = src.get("preamble_ar", "")
    if not preamble or "24 من شعبان 1446هـ" not in preamble \
            or "نظام النقل البري على الطرق" not in preamble:
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "24/8/1446H (24 من شعبان 1446هـ) decree date and نظام النقل البري على الطرق")
    com_res = src.get("com_resolution_ar", "")
    if not com_res or "19 من شعبان 1446هـ" not in com_res \
            or "نظام النقل البري على الطرق" not in com_res:
        e.append("[2j] com_resolution_ar (CoM Resolution 614 text) must be present and reference "
                 "its own 19/8/1446H (19 من شعبان 1446هـ) issuance date and نظام النقل البري على "
                 "الطرق")

    art1 = arts.get("road_transport_law_art_001", {})
    if "الهيئة: الهيئة العامة للنقل" not in art1.get("text", "") \
            or "الراكب:" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الهيئة / الراكب)")
    art32 = arts.get("road_transport_law_art_032", {})
    if "اللوائح" not in art32.get("text", "") or "180" not in art32.get("text", ""):
        e.append("[2j] Article 32 missing expected implementing-regulations mandate (اللوائح/180)")
    art33 = arts.get("road_transport_law_art_033", {})
    if "يحل النظام محل" not in art33.get("text", "") or "25" not in art33.get("text", ""):
        e.append("[2j] Article 33 missing expected supersession clause referencing م/25")
    art33_label = art33.get("number_label_ar")
    if art33_label != "المادة الثالثة والثلاثون":
        e.append("[2j] Article 33 number_label_ar must be 'المادة الثالثة والثلاثون', got %r"
                 % art33_label)
    art34 = arts.get("road_transport_law_art_034", {})
    if "الجريدة الرسمية" not in art34.get("text", "") or "180" not in art34.get("text", ""):
        e.append("[2j] Article 34 missing expected entry-into-force clause (الجريدة الرسمية/180)")
    if "يحل النظام محل" in art34.get("text", "") or "م/25" in art34.get("text", ""):
        e.append("[2j] Article 34 must NOT contain the repeal clause -- it lives in Article 33 "
                 "per this track's disclosed design")
    art34_label = art34.get("number_label_ar")
    if art34_label != "المادة الرابعة والثلاثون":
        e.append("[2j] Article 34 number_label_ar must be 'المادة الرابعة والثلاثون', got %r"
                 % art34_label)

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
        print("FAIL: %d error(s) in Road Transport Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Road Transport Law (نظام النقل البري على الطرق)")
    print("  - 34 records: 34 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (no amendment found this pass)")
    print("  - NO chapter (فصول) structure -- a flat, directly-numbered 34-article law")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/188, 24/8/1446H (CoM Resolution 614,")
    print("    19/8/1446H; Shura Resolutions 69/8, 110/11, 183/18). Umm Al-Qura Gazette Issue")
    print("    5073, 28 Feb 2025. Brand-new base-law track, not previously in this corpus.")
    print("  - SUPERSESSION confirmed INSIDE Article 33 of the Law's own text: replaces the prior")
    print("    General Road Transport Law (M/25, 21/6/1397H). Neither the enacting decree nor CoM")
    print("    Resolution 614 mentions the predecessor at all.")
    print("  - VERIFICATION TIER: TIER_2 -- one official primary source (uqn.gov.sa, the Official")
    print("    Gazette's own live portal) reached and used as governing text, cross-verified")
    print("    article-by-article against qanoonsa.com and nezams.com (full agreement after")
    print("    normalization). laws.boe.gov.sa has no dedicated page for this brand-new law and")
    print("    is itself unreachable this pass; tga.gov.sa also unreachable. Re-verify vs BOE/TGA")
    print("    when reachable or indexed.")
    print("  - Implementing Regulations (Article 32 mandate) are a large, not-yet-scoped cluster")
    print("    of activity-specific TGA regulations -- explicitly OUT OF SCOPE this pass per the")
    print("    task brief; flagged as a follow-up candidate requiring its own research pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
