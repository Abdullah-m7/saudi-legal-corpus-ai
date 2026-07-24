#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Prison and Detention Law track
(نظام السجن والتوقيف; 31 records: 28 اصلية, 3 معدلة [arts 4, 20, 25],
0 ملغاة, 0 مضافة; FLAT statute -- no chapters/أبواب/فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/prison_detention/law/official_source/
prison_detention_law_official_source.json's verification_methodology_note for
the full account: laws.boe.gov.sa HAS a dedicated lawId page for this law
(19945fe2-e690-4b24-9ab0-a9a700f17d03) and an official Ministry of Interior
PDF also exists, but BOTH were unreachable this pass (HTTP 503 / connection
reset; web.archive.org was not attempted -- WebFetch itself reported it
cannot fetch that host this session, not bypassed). ORIGINAL full text is
cross-verified verbatim between nezams.com and islamport.com (al-Mawsuea
al-Shamela) -> TIER_3. This validator does not re-adjudicate provenance; it
only checks internal self-consistency and that every discrepancy is still
recorded.

MATERIAL FACTS checked: flat structure (chapter_structure == []); Article 4
is uniquely amended TWICE and must carry THREE history entries (original,
amendment_intermediate, amendment_current) whose current text equals `text`;
Articles 20 and 25 carry the ordinary two-entry history (original,
amendment_current); NO predecessor-repeal assertion is made (recorded as
unconfirmed, not as a settled founding-statute fact).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "prison_detention", "law", "official_source",
                   "prison_detention_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "prison_detention", "law", "verified",
                       "prison_detention_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "prison_detention", "law", "verified",
                       "prison_detention_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "prison_detention_arabic_legal_llm",
                   "prison_detention_law_legal_llm_001_031.json")
N = 31
KEY_RE = r"prison_detention_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 28, "معدلة": 3, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = {
    "prison_detention_law_art_004",
    "prison_detention_law_art_020",
    "prison_detention_law_art_025",
}
DOUBLE_AMENDED_KEYS: set[str] = {"prison_detention_law_art_004"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {k: STATUS_AMENDED_DATED for k in AMENDED_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "prison_detention_boe_lawid_exists_but_unreachable",
    "prison_detention_moi_pdf_exists_but_unreachable",
    "prison_detention_full_text_source_tier",
    "prison_detention_article4_typo_suspected",
    "prison_detention_article4_double_amendment_history",
    "prison_detention_com_resolution_alone_amends_royal_decree_article",
    "prison_detention_no_named_predecessor_repeal",
    "prison_detention_implementing_regulation_out_of_scope",
    "prison_detention_gazette_issue_and_date_reported_not_confirmed",
    "prison_detention_tashkeel_and_typography_normalized",
    "prison_detention_flat_structure_confirmed",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕؕٓٔ]")


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before not in ("ه", "ج")
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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

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
        if re.search(r" [\.,،؛:]", a["text"]):
            e.append("[2f] %s: residual space-before-punctuation artifact detected" % k)

        # amended-article history integrity
        if k in AMENDED_KEYS:
            hist = a.get("history") or []
            types = [h.get("type") for h in hist]
            if k in DOUBLE_AMENDED_KEYS:
                if types != ["original", "amendment_intermediate", "amendment_current"]:
                    e.append("[2m] %s: double-amended article must carry exactly "
                             "[original, amendment_intermediate, amendment_current] in order, got %r"
                             % (k, types))
            else:
                if "amendment_current" not in types or "original" not in types:
                    e.append("[2m] %s: amended history must include amendment_current AND original" % k)
                if len(hist) != 2:
                    e.append("[2m] %s: singly-amended article must carry exactly 2 history entries" % k)
            cur = next((h for h in hist if h.get("type") == "amendment_current"), None)
            if cur and cur.get("text") != a["text"]:
                e.append("[2m] %s: history amendment_current text must equal current `text`" % k)
            orig = next((h for h in hist if h.get("type") == "original"), None)
            if orig and orig.get("text") == a["text"]:
                e.append("[2m] %s: original history text must DIFFER from amended current text" % k)
            for h in hist:
                if h.get("type") != "original" and not (h.get("decree_note") or "").strip():
                    e.append("[2m] %s: %s history entry missing decree_note" % (k, h.get("type")))
                if HARAKAT.search(h.get("text", "")):
                    e.append("[2h] %s: %s history text retains harakat" % (k, h.get("type")))

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
        for must in ("م/31", "م/75", "م/45", "م/28", "217"):
            if must not in decrees:
                e.append("[2k] amendment_history must reference decree/resolution %r" % must)

    # spot-checks anchoring key facts
    art1 = arts.get("prison_detention_law_art_001", {}).get("text", "")
    if "تنفذ عقوبات السجن" not in art1:
        e.append("[2j] Article 1 missing expected opening clause")
    art4 = arts.get("prison_detention_law_art_004", {}).get("text", "")
    if "رئيس أمن الدولة" not in art4:
        e.append("[2j] Article 4 (twice-amended, current) missing expected رئيس أمن الدولة clause")
    art20 = arts.get("prison_detention_law_art_020", {}).get("text", "")
    if "الجلد" in art20:
        e.append("[2j] Article 20 (amended) must NOT retain the deleted الجلد penalty in current text")
    art20_orig = next((h["text"] for h in arts["prison_detention_law_art_020"]["history"]
                        if h["type"] == "original"), "")
    if "الجلد" not in art20_orig:
        e.append("[2j] Article 20 original history text must retain the original الجلد penalty")
    art25 = arts.get("prison_detention_law_art_025", {}).get("text", "")
    for token in ("عفو إضافية", "خمسة عشر في المائة"):
        if token not in art25:
            e.append("[2j] Article 25 (amended) missing expected paragraph (ب) token %r" % token)
    art30 = arts.get("prison_detention_law_art_030", {}).get("text", "")
    if "اللوائح التنفيذية" not in art30:
        e.append("[2j] Article 30 missing expected implementing-regulations mandate")
    art31 = arts.get("prison_detention_law_art_031", {}).get("text", "")
    if "الجريدة الرسمية" not in art31:
        e.append("[2j] Article 31 missing expected publication effective-date clause")
    if arts.get("prison_detention_law_art_031", {}).get("number_label_ar") != "المادة الحادية والثلاثون":
        e.append("[2j] Article 31 number_label_ar must be المادة الحادية والثلاثون (islamport.com cross-check)")

    if src.get("decree") != "المرسوم الملكي رقم م/31" or src.get("decree_date_hijri") != "21/6/1398":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/31, 21/6/1398H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this law HAS amendments incorporated)")
    pre = src.get("preamble_ar", "")
    if not pre or "441" not in pre or "نظام السجن والتوقيف" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 441 and the law name")

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
        print("FAIL: %d error(s) in Prison and Detention Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Prison and Detention Law (نظام السجن والتوقيف)")
    print("  - 31 records: 28 اصلية, 3 معدلة (arts 4, 20, 25), 0 ملغاة, 0 مضافة")
    print("  - FLAT statute: continuous 1-31, NO chapters/أبواب/فصول (chapter_structure == [],")
    print("    section_ar empty by design)")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa HAS a dedicated lawId page")
    print("    (19945fe2-e690-4b24-9ab0-a9a700f17d03) and an official MOI PDF also exists, but BOTH were")
    print("    unreachable this pass (live 503/connection-reset; web.archive.org not attempted -- WebFetch")
    print("    itself reported it cannot fetch that host, not bypassed). ORIGINAL text cross-verified")
    print("    verbatim between nezams.com and islamport.com (al-Mawsuea al-Shamela)")
    print("  - Royal Decree M/31 (21/6/1398H, ~1978G), CoM Resolution 441 (8/6/1398H)")
    print("  - Article 4 UNIQUELY amended TWICE: Royal Decree M/28 (1/5/1435H), then CoM Resolution 217")
    print("    (29/4/1439H, superseding); all three versions preserved (original/intermediate/current)")
    print("  - Article 20 amended by Royal Decree M/75 (14/9/1428H, deleted flogging penalty)")
    print("  - Article 25 amended by Royal Decree M/45 (11/9/1430H, added paragraph ب on extra pardon time)")
    print("  - NO predecessor-repeal assertion made (unconfirmed either way, not a settled founding-statute")
    print("    claim, given the statute's age)")
    print("  - Follow-up candidate NOT ingested: Implementing Regulation(s) referenced in Article 30")
    return 0


if __name__ == "__main__":
    sys.exit(main())
