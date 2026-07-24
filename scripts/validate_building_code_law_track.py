#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Building Code Application Law track
(نظام تطبيق كود البناء السعودي; 16 records: 12 اصلية, 4 معدلة [arts 1, 8, 9,
15], 0 ملغاة, 0 مضافة; FLAT statute -- no chapters/فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/building_code/law/official_source/building_code_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa's dedicated
lawId page (cfc97985-4a9f-4012-832b-a9a700f21ed2) returned HTTP 503 on live
direct access, but a very recent (2026-01-14) web.archive.org snapshot of the
live BOE page was retrieved directly (web.archive.org was NOT blocked in this
session) -- this IS the official portal's own content, containing all 16
articles plus per-article amendment-history popups. Cross-verified per
amendment: original text + Royal Decree M/15 via an independent Saudi Council
of Engineers PDF; Royal Decree M/88 via the Umm al-Qura OFFICIAL GAZETTE
itself; Royal Decree M/204 via qanoonsa.com -> TIER_1_PRIMARY_MULTI_SOURCE.
This validator does not re-adjudicate provenance; it only checks internal
self-consistency and that every discrepancy is still recorded.

MATERIAL FACTS checked: flat structure (chapter_structure == []); the 4
amended articles carry full amendment-chain history whose final stage equals
`text`; NO predecessor repeal exists; the articles-4/5 terminology-lag
discrepancy is recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "building_code", "law", "official_source",
                   "building_code_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "building_code", "law", "verified",
                       "building_code_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "building_code", "law", "verified",
                       "building_code_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "building_code_arabic_legal_llm",
                   "building_code_law_legal_llm_001_016.json")
N = 16
KEY_RE = r"building_code_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 12, "معدلة": 4, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = {
    "building_code_law_art_001",
    "building_code_law_art_008",
    "building_code_law_art_009",
    "building_code_law_art_015",
}
# articles whose amendment chain has TWO dated stages (original -> intermediate -> current)
TWO_STAGE_KEYS: set[str] = {
    "building_code_law_art_001",
    "building_code_law_art_009",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {k: STATUS_AMENDED_DATED for k in AMENDED_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "building_code_boe_main_body_lags_amendment_popups",
    "building_code_art9_first_amendment_attribution_resolved",
    "building_code_art1_addition_insertion_point_reconstructed",
    "building_code_art15_replaced_phrase_wording_minor_mismatch",
    "building_code_articles_4_5_not_officially_amended_despite_terminology_shift",
    "building_code_no_named_predecessor_repeal",
    "building_code_gazette_issue_founding_not_pinpointed",
    "building_code_com_preamble_typo_verbatim",
    "building_code_implementing_regulation_out_of_scope",
    "building_code_ministry_name_evolution_not_silently_updated",
    "building_code_tashkeel_stripped",
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

    # continuous 1..16, no gaps/dupes
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
        if "“" in a["text"] or "”" in a["text"] or "«" in a["text"] or "»" in a["text"]:
            e.append("[2f] %s: residual curly-quote/guillemet artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # amended-article history integrity
        if k in AMENDED_KEYS:
            hist = a.get("history") or []
            types = [h.get("type") for h in hist]
            if "amendment_current" not in types or "original" not in types:
                e.append("[2m] %s: amended history must include amendment_current AND original" % k)
            cur = next((h for h in hist if h.get("type") == "amendment_current"), None)
            if cur and cur.get("text") != a["text"]:
                e.append("[2m] %s: history amendment_current text must equal current `text`" % k)
            orig = next((h for h in hist if h.get("type") == "original"), None)
            if orig and orig.get("text") == a["text"]:
                e.append("[2m] %s: original history text must DIFFER from amended current text" % k)
            if k in TWO_STAGE_KEYS:
                if "amendment_intermediate_m15" not in types:
                    e.append("[2m] %s: two-stage amended article missing intermediate_m15 stage" % k)
                inter = next((h for h in hist if h.get("type") == "amendment_intermediate_m15"), None)
                if inter and orig and inter.get("text") == orig.get("text"):
                    e.append("[2m] %s: intermediate stage text must differ from original" % k)
                if inter and cur and inter.get("text") == cur.get("text"):
                    e.append("[2m] %s: intermediate stage text must differ from current" % k)
            if cur and not (cur.get("decree_note") or "").strip():
                e.append("[2m] %s: amendment_current missing decree_note citation" % k)

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
        e.append("[2k] missing amendment_history (must record founding + amending decrees)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        for must in ("م/43", "م/15", "م/88", "م/204"):
            if must not in decrees:
                e.append("[2k] amendment_history must reference decree %s" % must)

    # spot-checks anchoring key facts
    art1 = arts.get("building_code_law_art_001", {}).get("text", "")
    if "المركز السعودي لكود البناء" not in art1 or "الهيئة السعودية للمواصفات" not in art1:
        e.append("[2j] Article 1 (amended) missing expected current definitions (المركز / الهيئة السعودية للمواصفات)")
    if "اللجنة الوطنية" in art1:
        e.append("[2j] Article 1 current text should no longer define اللجنة الوطنية (replaced by المركز)")
    art4 = arts.get("building_code_law_art_004", {}).get("text", "")
    if "اللجنة الوطنية" not in art4:
        e.append("[2j] Article 4 (unamended per BOE) must still literally read اللجنة الوطنية")
    art8 = arts.get("building_code_law_art_008", {}).get("text", "")
    if "مسؤولين بالتضامن" not in art8:
        e.append("[2j] Article 8 (amended) missing expected joint-liability paragraph (2)")
    art9 = arts.get("building_code_law_art_009", {}).get("text", "")
    if "للإطلاق الكلي للتيار الكهربائي" not in art9:
        e.append("[2j] Article 9 (amended) missing expected final electricity clause")
    if "لإيصال الخدمات" in art9:
        e.append("[2j] Article 9 current text must NOT retain the original (superseded) services clause")
    art15 = arts.get("building_code_law_art_015", {}).get("text", "")
    if "يعد المركز" not in art15 or "وزير البلديات والإسكان" not in art15:
        e.append("[2j] Article 15 (amended) missing expected current wording (يعد المركز / وزير البلديات والإسكان)")
    art16 = arts.get("building_code_law_art_016", {}).get("text", "")
    if "يتعارض" not in art16 or "سنة" not in art16:
        e.append("[2j] Article 16 missing expected generic-repeal / effective-date clause")

    # NO named predecessor repeal anywhere (founding statute; only generic conflict clause allowed)
    for k, a in arts.items():
        if re.search(r"يلغي نظام|يلغى نظام|بإلغاء نظام", a["text"]):
            e.append("[2j] %s: unexpected NAMED predecessor repeal in a founding statute with none" % k)

    if src.get("decree") != "المرسوم الملكي رقم م/43" or src.get("decree_date_hijri") != "26/4/1438":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/43, 26/4/1438H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this law HAS amendments incorporated)")
    pre = src.get("preamble_ar", "")
    if not pre or "241" not in pre or "نظام تطبيق كود البناء السعودي" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 241 and the law name")

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
    if summary.get("consolidated_amended_law") is not True:
        e.append("[4b] summary consolidated_amended_law must be True")

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
        print("FAIL: %d error(s) in Building Code Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Building Code Application Law (نظام تطبيق كود البناء السعودي)")
    print("  - 16 records: 12 اصلية, 4 معدلة (arts 1, 8, 9, 15), 0 ملغاة, 0 مضافة")
    print("  - FLAT statute: continuous 1-16, NO chapters/فصول (chapter_structure == [],")
    print("    section_ar empty by design)")
    print("  - VERIFICATION TIER: TIER_1_PRIMARY_MULTI_SOURCE -- laws.boe.gov.sa live direct access")
    print("    returned HTTP 503, but a very recent (2026-01-14) web.archive.org snapshot of the")
    print("    live BOE page was retrieved directly (web.archive.org NOT blocked this session),")
    print("    containing the full original text and all amendment-history popups. Cross-verified")
    print("    per amendment: original+M/15 via an independent Saudi Council of Engineers PDF;")
    print("    M/88 via the Umm al-Qura OFFICIAL GAZETTE itself; M/204 via qanoonsa.com")
    print("  - Royal Decree M/43 (26/4/1438H, ~2017G), CoM Resolution 241 (25/4/1438H); amended by")
    print("    M/15 (19/1/1441H: arts 1/8/9), M/88 (10/4/1446H, CoM 286: art 9), and M/204")
    print("    (12/9/1446H, CoM 656: arts 1/15)")
    print("  - NO named-predecessor repeal (founding statute; Art 16 is only a generic conflict")
    print("    clause + 1-year effective-date rule)")
    print("  - DISCLOSED (not silently resolved): Articles 4/5 still literally read the pre-M/204")
    print("    institutional titles (اللجنة الوطنية / وزير التجارة والاستثمار...) that were replaced")
    print("    elsewhere by M/204, because BOE records no textual amendment to arts 4/5 themselves")
    print("  - Follow-up candidate NOT ingested: Implementing Regulation (separate ministerial")
    print("    resolution track)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
