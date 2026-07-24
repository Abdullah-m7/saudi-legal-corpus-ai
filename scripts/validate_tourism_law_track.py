#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Tourism Law track (نظام السياحة; 19
records, all اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; FLAT statute -- no
chapters/فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/tourism/law/official_source/tourism_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa HAS a
dedicated lawId page for this law (7d777c66-d28b-43de-9305-af23013b1738) but
it was unreachable this pass (HTTP 503 live via WebFetch; the Umm al-Qura
gazette page also 503'd via WebFetch and returned an un-rendered SPA shell
via direct curl; web.archive.org refused by WebFetch and returned HTTP 403
via direct proxy curl, neither bypassed). ORIGINAL full text is from an
OFFICIAL Ministry of Tourism PDF (cdn.mt.gov.sa) cross-checked against
nezams.com, and structurally cross-checked (English, reference-only) against
the official BOE translation (misa.gov.sa) -> TIER_2. This validator does
not re-adjudicate provenance; it only checks internal self-consistency and
that every discrepancy is still recorded.

MATERIAL FACTS checked: flat structure (chapter_structure == []); all 19
articles اصلية (no amendments known); Article 18 carries the literal
named-predecessor repeal clause (Royal Decree M/2, 9/1/1436H); the
Article-18/repeal fact is recorded in known_unresolved_discrepancies.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "tourism", "law", "official_source",
                   "tourism_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "tourism", "law", "verified",
                       "tourism_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "tourism", "law", "verified",
                       "tourism_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "tourism_arabic_legal_llm",
                   "tourism_law_legal_llm_001_019.json")
N = 19
KEY_RE = r"tourism_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 19, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {}
FLAGGED_DISCREPANCY_KEYS = {
    "tourism_law_boe_dedicated_page_exists_but_unreachable",
    "tourism_law_named_predecessor_repeal_confirmed",
    "tourism_law_no_known_amendments",
    "tourism_law_implementing_regulations_out_of_scope",
    "tourism_law_com_resolution_item8_separate_org_amendment",
    "tourism_law_gregorian_date_variance",
    "tourism_law_tashkeel_stripped",
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

    # continuous 1..19, no gaps/dupes
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
        if "م/18" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/18")

    # spot-checks anchoring key facts
    art1 = arts.get("tourism_law_art_001", {}).get("text", "")
    if "السياحة" not in art1 or "المرخص له" not in art1:
        e.append("[2j] Article 1 missing expected definitions (السياحة / المرخص له)")
    art2 = arts.get("tourism_law_art_002", {}).get("text", "")
    if "الترخيص" not in art2:
        e.append("[2j] Article 2 missing expected licensing requirement")
    art6 = arts.get("tourism_law_art_006", {}).get("text", "")
    if "الوجهات السياحية" not in art6 or "مجلس الوزراء" not in art6:
        e.append("[2j] Article 6 missing expected tourist-destinations clause")
    art13 = arts.get("tourism_law_art_013", {}).get("text", "")
    if "مفتشون" not in art13:
        e.append("[2j] Article 13 missing expected inspectors clause")
    art16 = arts.get("tourism_law_art_016", {}).get("text", "")
    for token in ("مليون ريال", "الإنذار", "إلغاء الترخيص"):
        if token not in art16:
            e.append("[2j] Article 16 missing expected token %r" % token)
    art17 = arts.get("tourism_law_art_017", {}).get("text", "")
    if "تسعين" not in art17 or "اللائحة" not in art17:
        e.append("[2j] Article 17 missing expected implementing-regulation mandate")
    art18 = arts.get("tourism_law_art_018", {}).get("text", "")
    if "م/2" not in art18 or "1436" not in art18 or "يحل النظام محل" not in art18:
        e.append("[2j] Article 18 missing expected named-predecessor repeal clause")
    art19 = arts.get("tourism_law_art_019", {}).get("text", "")
    if "تسعين" not in art19:
        e.append("[2j] Article 19 missing expected 90-day effective-date clause")

    # exactly ONE repeal clause referencing the named predecessor (Article 18 only)
    repeal_hits = [k for k, a in arts.items() if "يحل النظام محل" in a["text"]]
    if repeal_hits != ["tourism_law_art_018"]:
        e.append("[2j] named-predecessor repeal clause must appear in Article 18 only, found: %s"
                 % repeal_hits)

    if src.get("decree") != "المرسوم الملكي رقم م/18" or src.get("decree_date_hijri") != "26/1/1444":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/18, 26/1/1444H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no known amendments to this law)")
    pre = src.get("preamble_ar", "")
    if not pre or "79" not in pre or "نظام السياحة" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 79 and the law name")
    if "م/2" not in pre or "1436" not in pre:
        e.append("[2j] preamble_ar must reference the predecessor decree (م/2, 1436H)")

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
        print("FAIL: %d error(s) in Tourism Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Tourism Law (نظام السياحة)")
    print("  - 19 records: all اصلية, 0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - FLAT statute: continuous 1-19, NO chapters/فصول (chapter_structure == [],")
    print("    section_ar empty by design)")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa HAS a dedicated lawId page")
    print("    (7d777c66-d28b-43de-9305-af23013b1738) but was unreachable this pass (live HTTP 503;")
    print("    Umm al-Qura gazette page also 503/un-rendered SPA; web.archive.org refused/403, not")
    print("    bypassed). ORIGINAL full text from an official Ministry of Tourism PDF")
    print("    (cdn.mt.gov.sa) cross-checked verbatim against nezams.com, and structurally")
    print("    cross-checked (English, reference-only) against the official BOE translation")
    print("    (misa.gov.sa)")
    print("  - Royal Decree M/18 (26/1/1444H, ~2022G), CoM Resolution 79 (25/1/1444H), published")
    print("    Umm al-Qura 7/2/1444H")
    print("  - NAMED-PREDECESSOR REPEAL CONFIRMED: Article 18 repeals the prior Tourism Law")
    print("    (Royal Decree M/2, 9/1/1436H) by name -- confirmed from BOTH directions (this law's")
    print("    Article 18 text AND the predecessor's own nezams.com status record)")
    print("  - No known amendments to this law as of this pass")
    print("  - Follow-up candidates NOT ingested: predecessor law's full text (M/2, 1436H);")
    print("    ten-plus Implementing Regulations issued under this law (cdn.mt.gov.sa)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
