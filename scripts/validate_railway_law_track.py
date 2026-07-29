#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Railway Law track (نظام الخطوط
الحديدية, Royal Decree M/159, 22/8/1445H -- the currently in-force Railway
Law).

50 records: 50 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (no evidence of any amendment
to this Law was found this pass). NO formal فصل/باب chapter labels in the
source text -- 10 unlabeled topical section headings instead (recorded via
section_ar only).

SUPERSESSION -- confirmed, but NOT inside the Law's own 50 numbered Articles.
The enacting Royal Decree M/159 states in its own clause (Second): "يحل
النظام -المشار إليه في البند (أولا) من هذا المرسوم- عند نفاذه، محل نظام
النقل بالخطوط الحديدية الصادر بالمرسوم الملكي رقم (م / 33) بتاريخ 24 / 5 /
1433هـ، ويلغي كل ما يتعارض معه من أحكام." -- identical, word-for-word, to
Council of Ministers Resolution 692's own clause (Second).

VERIFICATION TIER -- TIER_3. See the generator docstring and the source
artifact's verification_methodology_note: zero official/primary government
source was reached this pass (laws.boe.gov.sa unreachable live and via its
one located wayback snapshot; uqn.gov.sa's search results require JS not
available to curl). Two independent secondary sources (qanoonsa.com,
nezams.com) were fetched directly and cross-verified article-by-article by
script, with one disclosed, corrected duplication glitch (Article 1). This
validator does not re-adjudicate provenance; it only checks internal
self-consistency of the ingested text and that every discrepancy is still
recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "railway_law", "law", "official_source",
                   "railway_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "railway_law", "law", "verified",
                       "railway_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "railway_law", "law", "verified",
                       "railway_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "railway_law_arabic_legal_llm",
                   "railway_law_legal_llm_001_050.json")
N = 50
KEY_RE = r"railway_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 50, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 10  # 10 unlabeled topical section headings (no formal فصل numbering)

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
    "railway_law_boe_and_wayback_unreachable",
    "railway_law_uqn_gazette_search_no_js",
    "railway_law_article1_qanoonsa_duplication_glitch_corrected",
    "railway_law_no_formal_fasl_labels",
    "railway_law_implementing_regulation_not_ingested",
    "railway_law_repeal_in_decree_not_in_articles",
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
        e.append("[1c] expected %d topical sections, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))
    else:
        covered = set()
        for c in chs:
            fa, la = c.get("first_article"), c.get("last_article")
            if fa is None or la is None or fa > la:
                e.append("[1c] malformed chapter_structure entry: %r" % c)
                continue
            covered.update(range(fa, la + 1))
        if covered != set(range(1, N + 1)):
            e.append("[1c] chapter_structure article ranges do not exactly cover 1..%d" % N)
        for c in chs:
            if "الفصل" in (c.get("section_ar") or "") or "الباب" in (c.get("section_ar") or ""):
                e.append("[1c] section_ar must not fabricate الفصل/الباب labels not present in "
                         "the source text: %r" % c)

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
        if re.search(r"[ی]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh) present" % k)
        if "٫" in a["text"]:
            e.append("[2g] %s: residual Arabic decimal/thousands separator (٫) present" % k)
        if "نظام الخطوط الحديدية الراكب" in a["text"]:
            e.append("[2m] %s: unresolved qanoonsa.com Article-1 duplication glitch present" % k)

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
        e.append("[2k] missing amendment_history (must record the founding M/159 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/159" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/159")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/159)" \
            or src.get("decree_date_hijri") != "22/8/1445":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/159, 22/8/1445H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendments found this pass)")
    sup = src.get("supersedes_ar", "")
    if not sup or "م/33" not in sup or "ثانيا" not in sup:
        e.append("[2j] supersedes_ar must name the repealed instrument (م/33) and anchor the "
                 "repeal to clause (ثانيا) of the enacting Royal Decree, not to a numbered Article")
    if not src.get("preamble_ar") or "22 / 8 / 1445هـ" not in src.get("preamble_ar", "") \
            or "نظام الخطوط الحديدية" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "22/8/1445H decree date and نظام الخطوط الحديدية")
    com_res = src.get("com_resolution_ar", "")
    if not com_res or "17 / 8 / 1445هـ" not in com_res or "نظام الخطوط الحديدية" not in com_res:
        e.append("[2j] com_resolution_ar (CoM Resolution 692 text) must be present this pass "
                 "(unlike contractors_classification_law, it WAS located and fetched here) and "
                 "reference its own 17/8/1445H issuance date and نظام الخطوط الحديدية")

    art1 = arts.get("railway_law_art_001", {})
    if "الهيئة: الهيئة العامة للنقل" not in art1.get("text", "") \
            or "الراكب:" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الهيئة / الراكب)")
    art49 = arts.get("railway_law_art_049", {})
    if "اللائحة" not in art49.get("text", "") or "تسعين" not in art49.get("text", ""):
        e.append("[2j] Article 49 missing expected implementing-regulation mandate (اللائحة/تسعين)")
    art50 = arts.get("railway_law_art_050", {})
    if "الجريدة الرسمية" not in art50.get("text", "") or "تسعين" not in art50.get("text", ""):
        e.append("[2j] Article 50 missing expected entry-into-force clause (تسعين يوما)")
    if "يحل النظام محل" in art50.get("text", "") or "م / 33" in art50.get("text", ""):
        e.append("[2j] Article 50 must NOT contain the repeal clause -- it lives in the enacting "
                 "decree only, per this track's disclosed design")
    art50_label = art50.get("number_label_ar")
    if art50_label != "المادة الخمسون":
        e.append("[2j] Article 50 number_label_ar must be 'المادة الخمسون', got %r" % art50_label)

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
        print("FAIL: %d error(s) in Railway Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Railway Law (نظام الخطوط الحديدية)")
    print("  - 50 records: 50 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (no amendment found this pass)")
    print("  - NO formal فصل/باب chapter labels in source -- 10 unlabeled topical section headings")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/159, 22/8/1445H (CoM Resolution 692, ")
    print("    17/8/1445H; Shura Resolution 279/43, 22/11/1443H). Umm Al-Qura Gazette Issue 5024,")
    print("    15 March 2024. Brand-new base-law track, not previously in this corpus.")
    print("  - SUPERSESSION confirmed in the ENACTING ROYAL DECREE's clause (ثانيا) -- NOT inside")
    print("    any of the Law's own 50 numbered Articles: replaces the prior Railway Transport Law")
    print("    (M/33, 24/5/1433H). Identical wording independently confirmed in CoM Resolution 692.")
    print("  - ARTICLE 1 DUPLICATION GLITCH disclosed and corrected: qanoonsa.com's copy read")
    print("    'نظام الخطوط الحديدية الراكب:' -- corrected to 'الراكب:' using nezams.com's")
    print("    independent, grammatically-sound text.")
    print("  - VERIFICATION TIER: TIER_3 -- zero official/primary source reached this pass")
    print("    (laws.boe.gov.sa unreachable live and via its one located wayback snapshot;")
    print("    uqn.gov.sa search requires JS). Two independent secondary sources (qanoonsa.com,")
    print("    nezams.com) fetched directly and cross-verified article-by-article by script.")
    print("    Re-verify verbatim text vs laws.boe.gov.sa/uqn.gov.sa when reachable.")
    print("  - Implementing Regulation (Article 49 mandate) exists (TGA Board adopted it")
    print("    25 October 2024, 91 articles, per spa.gov.sa/argaam.com/sabq.org) but is NOT")
    print("    ingested this pass -- flagged as a follow-up candidate (railway_regulation).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
