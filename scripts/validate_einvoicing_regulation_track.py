#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the E-Invoicing Regulation track (لائحة الفوترة
الإلكترونية; 7 records, ALL اصلية; FLAT structure -- no chapters/أبواب).

VERIFICATION TIER -- see the generator's module docstring and sources/
einvoicing_regulation/law/official_source/einvoicing_regulation_official_
source.json's verification_methodology_note for the full account: ZATCA's
own official PDF (zatca.gov.sa, fetched directly, HTTP 200) is the PRIMARY
source; laws.boe.gov.sa is unreachable (HTTP 503) and has no dedicated
lawId page for this decision at all; cross-checked word-for-word against an
independent mirror (aflaksolutions.com) -> TIER_2. This validator does not
re-adjudicate provenance; it only checks internal self-consistency and that
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
SRC = os.path.join(ROOT, "sources", "einvoicing_regulation", "law", "official_source",
                   "einvoicing_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "einvoicing_regulation", "law", "verified",
                       "einvoicing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "einvoicing_regulation", "law", "verified",
                       "einvoicing_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "einvoicing_regulation_arabic_legal_llm",
                   "einvoicing_regulation_legal_llm_001_007.json")
N = 7
KEY_RE = r"einvoicing_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 7, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "einvoicing_regulation_boe_no_dedicated_page",
    "einvoicing_regulation_uqn_gazette_unreachable",
    "einvoicing_regulation_gregorian_date_resolved_high_confidence_not_pinned",
    "einvoicing_regulation_qanoniah_js_rendered_inaccessible",
    "einvoicing_regulation_gazt_zatca_retroactive_naming",
    "einvoicing_regulation_phase_decisions_confirmed_schedules_not_amendments",
    "einvoicing_regulation_minor_spelling_inconsistencies_cross_verified",
    "einvoicing_regulation_no_repeal_confirmed",
    "einvoicing_regulation_tashkeel_stripped",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


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
        e.append("[1b] article numbers not contiguous 1..%d: got %s" % (N, nums))

    # FLAT regulation: chapter_structure MUST be empty (no separate باب structure)
    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1d] this regulation is flat; chapter_structure must be [] but is %r" % (chs,))

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
        if not a.get("verification_tier"):
            e.append("[2] %s: missing verification_tier" % k)
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        # Latin letters are expected ONLY inside the API-acronym parenthetical in
        # Article 5; flag any other latin leftovers.
        latin_hits = re.findall(r"[A-Za-z]+", a["text"])
        allowed_latin = {"Application", "Programming", "Interface", "API"}
        stray = [w for w in latin_hits if w not in allowed_latin]
        if stray:
            e.append("[2] %s: unexpected latin leftovers %r" % (k, stray))
        if a.get("section_ar") != "":
            e.append("[2] %s: section_ar must be empty for this flat regulation" % k)
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
            e.append("[2i] %s: no article is amended/added this pass; history must be empty" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # ligature-extraction-bug regression guards: these specific reversed
        # sequences must never appear in the ingested text (each corresponds to a
        # fix disclosed/applied while hand-verifying the official_source.json).
        for bad in ("اإل", "األ", "اآل", "الالئحة", "الئح"):
            if bad in a["text"] and bad != "الئح":
                e.append("[2g] %s: unresolved ligature-reversal artifact %r" % (k, bad))
        if re.search(r"(?<![ء-ي])الئح", a["text"]):
            e.append("[2g] %s: unresolved لائحة ligature-reversal artifact" % k)
        for bad in ("خالل", "خالف ذلك"):
            if bad in a["text"]:
                e.append("[2g] %s: unresolved mid-root لا-ligature artifact %r" % (k, bad))

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

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record the founding decision)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "2-6-20" not in decrees:
            e.append("[2k] amendment_history must reference founding decree 2-6-20")

    if src.get("decree") != "قرار مجلس إدارة هيئة الزكاة والضريبة والجمارك رقم (2-6-20)" \
            or src.get("decree_date_hijri") != "4/4/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Board Decision "
                 "2-6-20, 4/4/1442H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendments confirmed to the "
                 "founding text)")
    if src.get("preamble_ar") not in ("", None):
        e.append("[2l] preamble_ar must be empty -- no resolution preamble/enacting text was "
                 "located this pass; a non-empty value would risk fabrication")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("einvoicing_regulation_art_001", {}).get("text", "")
    for token in ("الفاتورة الإلكترونية", "الإشعارات الإلكترونية", "ربط أنظمة الفوترة الإلكترونية",
                  "اللائحة:"):
        if token not in art1:
            e.append("[2j] Article 1 missing expected defined term %r" % token)
    art2 = arts.get("einvoicing_regulation_art_002", {}).get("text", "")
    if "جزءا لا يتجزأ من اللائحة التنفيذية لنظام ضريبة القيمة المضافة" not in art2:
        e.append("[2j] Article 2(B) missing the expected 'integral part of the VAT "
                 "Implementing Regulation' clause")
    art3 = arts.get("einvoicing_regulation_art_003", {}).get("text", "")
    if "الشخص الخاضع للضريبة المقيم في المملكة" not in art3:
        e.append("[2j] Article 3 missing expected resident-taxable-person clause")
    art6 = arts.get("einvoicing_regulation_art_006", {}).get("text", "")
    if "(180)" not in art6:
        e.append("[2j] Article 6(B) missing expected 180-day integration-decision window")
    art7 = arts.get("einvoicing_regulation_art_007", {}).get("text", "")
    if "(12)" not in art7 or "الجريدة الرسمية" not in art7:
        e.append("[2j] Article 7(B) missing expected 12-month compliance window / gazette "
                 "publication clause")
    # no repeal language anywhere
    for k, a in arts.items():
        if "يلغى" in a["text"] or "يلغي" in a["text"] or "الملغاة" in a["text"]:
            e.append("[2j] %s: unexpected repeal-language token found (no repeal is expected "
                     "or confirmed for this founding regulation)" % k)

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
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
        if r.get("is_amended") is not False or r.get("is_added") is not False \
                or r.get("is_repealed") is not False:
            e.append("[4] %s: is_amended/is_added/is_repealed must all be False" % r["article_key"])
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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in E-Invoicing Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: E-Invoicing Regulation (لائحة الفوترة الإلكترونية)")
    print("  - 7 records, ALL اصلية (0 معدلة, 0 مضافة, 0 ملغاة)")
    print("  - FLAT regulation (chapter_structure == [], section_ar empty by design)")
    print("  - ZATCA Board of Directors Decision No. (2-6-20), dated 4 Rabi' al-Thani 1442H")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa unreachable (HTTP 503) and has NO")
    print("    dedicated lawId page for this decision at all. PRIMARY source: zatca.gov.sa's")
    print("    own official PDF (Arabic + English, fetched directly, HTTP 200), CROSS-CHECKED")
    print("    word-for-word against an independent mirror (aflaksolutions.com) and against")
    print("    decision-number/date corroboration across multiple other secondary sources")
    print("  - CONFIRMED: the ~24 subsequent 'phase' decisions and the separate Governor")
    print("    Controls Resolution are rollout-schedule/technical-detail instruments issued")
    print("    under this Regulation's own Article 6(B) delegation, NOT textual amendments")
    print("  - NO repeal of any predecessor instrument found or expected")
    print("  - Gregorian publication-date question (Dec 4 2020 vs. independently-converted")
    print("    Nov 19 2020) resolved with high confidence but not pinned to a primary Umm")
    print("    al-Qura Gazette record this pass -- disclosed, not silently asserted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
