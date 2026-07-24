#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Civil Defense Law track (نظام الدفاع
المدني; 36 records: 34 اصلية, 2 معدلة [arts 5, 28 -- original text only,
current text unconfirmed], 0 ملغاة, 0 مضافة; FLAT statute -- no chapters/فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/civil_defense/law/official_source/civil_defense_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa HAS a
dedicated lawId page (f09eda85-7150-4803-b87a-a9a700f189f3) and
istitlaa.ncc.gov.sa HAS dedicated per-article pages (Military/998) for this
law, but BOTH were unreachable this pass (HTTP 503; web.archive.org
environment-blocked and NOT bypassed). ORIGINAL 1406H text is cross-verified
verbatim between mohamah.net and islamport.com (independent, non-derivative
sources) -> TIER_3. Articles 5 and 28 are KNOWN to have been amended (per
saudipedia.com citing the Bureau of Experts) but the CURRENT verbatim text
could NOT be confirmed -- their `text` field stores ONLY the confirmed
ORIGINAL wording, deliberately NOT a fabricated current replacement. This
validator does not re-adjudicate provenance; it only checks internal
self-consistency and that every discrepancy is still recorded.

MATERIAL FACTS checked: flat structure (chapter_structure == []); the 2 known-
amended articles carry a single history[type=original] entry whose text equals
the current `text` (since no confirmed current text exists) and whose
decree_note discloses the unconfirmed-current-text situation explicitly; NO
named-predecessor-law repeal exists (Article 35 is a general conflict clause
only); the saudipedia "majority of articles amended" completeness caveat is
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
SRC = os.path.join(ROOT, "sources", "civil_defense", "law", "official_source",
                   "civil_defense_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "civil_defense", "law", "verified",
                       "civil_defense_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "civil_defense", "law", "verified",
                       "civil_defense_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "civil_defense_arabic_legal_llm",
                   "civil_defense_law_legal_llm_001_036.json")
N = 36
KEY_RE = r"civil_defense_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 34, "معدلة": 2, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_UNCONFIRMED = "AMENDED_CURRENT_TEXT_UNCONFIRMED"
AMENDED_KEYS: set[str] = {
    "civil_defense_law_art_005",
    "civil_defense_law_art_028",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {k: STATUS_AMENDED_UNCONFIRMED for k in AMENDED_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "civil_defense_law_boe_dedicated_page_exists_but_unreachable",
    "civil_defense_law_istitlaa_platform_dedicated_pages_unreachable",
    "civil_defense_law_amendments_confirmed_existence_current_text_unconfirmed",
    "civil_defense_law_saudipedia_majority_amended_completeness_caveat",
    "civil_defense_law_unconfirmed_leads_art34_mukarrar_and_appeal_committees",
    "civil_defense_law_article11_cross_source_discrepancy",
    "civil_defense_law_abjad_vs_alphabetical_lettering_convention",
    "civil_defense_law_no_named_predecessor_law_repeal",
    "civil_defense_law_gazette_issue_and_gregorian_date_not_pinpointed",
    "civil_defense_law_related_implementing_instruments_out_of_scope",
    "civil_defense_law_tashkeel_and_spacing_normalized",
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

    # continuous 1..36, no gaps/dupes
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
        if re.search(r"\s[،.:؛؟]", a["text"]):
            e.append("[2f] %s: residual space-before-punctuation artifact detected" % k)
        # amended-article history integrity: THIS TRACK'S DELIBERATE DEVIATION --
        # only an `original` entry exists (no `amendment_current`) because the
        # current post-amendment text could not be confirmed from any reachable
        # source. The `original` text MUST equal the current `text` field (since
        # `text` stores only the confirmed original wording), and decree_note
        # MUST explicitly disclose that current text is unconfirmed.
        if k in AMENDED_KEYS:
            hist = a.get("history") or []
            types = [h.get("type") for h in hist]
            if types != ["original"]:
                e.append("[2m] %s: amended-but-unconfirmed article must carry exactly one "
                         "history entry of type=original (no fabricated amendment_current)" % k)
            orig = next((h for h in hist if h.get("type") == "original"), None)
            if orig and orig.get("text") != a["text"]:
                e.append("[2m] %s: history original text must equal current `text` field "
                         "(text stores the confirmed original wording only)" % k)
            note = (orig or {}).get("decree_note", "")
            if "غير مؤكد" not in note and "تعذر" not in note:
                e.append("[2m] %s: decree_note must explicitly disclose that current "
                         "post-amendment text is unconfirmed" % k)

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
        if "م/10" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/10")
        if "م/66" not in decrees:
            e.append("[2k] amendment_history must reference amending decree م/66")
        if "م/63" not in decrees:
            e.append("[2k] amendment_history must reference amending decree م/63")

    # spot-checks anchoring key facts
    art1 = arts.get("civil_defense_law_art_001", {}).get("text", "")
    if "الدفاع المدني هو مجموعة الإجراءات" not in art1:
        e.append("[2j] Article 1 missing expected civil-defense definition")
    art2 = arts.get("civil_defense_law_art_002", {}).get("text", "")
    if "الكارثة" not in art2:
        e.append("[2j] Article 2 missing expected disaster definition")
    art5 = arts.get("civil_defense_law_art_005", {}).get("text", "")
    if "وزير الداخلية رئيسا" not in art5:
        e.append("[2j] Article 5 (known-amended, original text) missing expected council "
                 "composition wording")
    art11 = arts.get("civil_defense_law_art_011", {}).get("text", "")
    if "مجلس الدفاع الأعلى" not in art11:
        e.append("[2j] Article 11 missing expected 'مجلس الدفاع الأعلى' wording (see "
                 "civil_defense_law_article11_cross_source_discrepancy)")
    art28 = arts.get("civil_defense_law_art_028", {}).get("text", "")
    if "لا يجوز نزع أو تعطيل" not in art28:
        e.append("[2j] Article 28 (known-amended, original text) missing expected wording")
    art35 = arts.get("civil_defense_law_art_035", {}).get("text", "")
    if "يلغي هذا النظام كل ما يتعارض مع أحكامه" not in art35:
        e.append("[2j] Article 35 missing expected general conflict-repeal clause")
    art36 = arts.get("civil_defense_law_art_036", {}).get("text", "")
    if "ستة أشهر" not in art36:
        e.append("[2j] Article 36 missing expected 6-month effective-date clause")

    # NO named-predecessor-LAW repeal anywhere (general conflict clause only)
    named_repeal_re = re.compile(r"يلغي (?:نظام|لائحة) .{0,40}(?:الصادر|رقم)")
    for k, a in arts.items():
        if named_repeal_re.search(a["text"]):
            e.append("[2j] %s: unexpected named-predecessor-law repeal wording in a statute "
                     "expected to carry only a general conflict clause" % k)

    if src.get("decree") != "المرسوم الملكي رقم م/10" or src.get("decree_date_hijri") != "10/5/1406":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/10, 10/5/1406H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this law HAS known amendments)")
    pre = src.get("preamble_ar", "")
    if not pre or "25" not in pre or "نظام الدفاع المدني" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 25 and the law name")

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
        print("FAIL: %d error(s) in Civil Defense Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Civil Defense Law (نظام الدفاع المدني)")
    print("  - 36 records: 34 اصلية, 2 معدلة (arts 5, 28 -- original 1406H text preserved, "
          "current post-amendment text UNCONFIRMED), 0 ملغاة, 0 مضافة")
    print("  - FLAT statute: continuous 1-36, NO chapters/فصول (chapter_structure == [],")
    print("    section_ar empty by design)")
    print("  - VERIFICATION TIER: TIER_3 for the base 1406H text -- laws.boe.gov.sa and")
    print("    istitlaa.ncc.gov.sa BOTH have dedicated pages for this law but were unreachable")
    print("    this pass (HTTP 503; web.archive.org environment-blocked, NOT bypassed).")
    print("    ORIGINAL text cross-verified verbatim between mohamah.net and islamport.com")
    print("    (independent, non-derivative sources).")
    print("  - Royal Decree M/10 (10/5/1406H, ~1986G), CoM Resolution 25 (23/1/1406H).")
    print("    KNOWN amendments confirmed to EXIST (Royal Decree M/66 2/10/1424H, Royal Decree")
    print("    M/63 13/9/1436H per saudipedia.com citing the Bureau of Experts) but their")
    print("    verbatim CURRENT text could NOT be confirmed this pass -- NOT fabricated.")
    print("  - saudipedia.com states 'the majority of the law's articles were amended on")
    print("    various dates' -- the true amendment scope across four decades likely EXCEEDS")
    print("    what could be confirmed here; flagged as a completeness caveat, not concealed.")
    print("  - NO named-predecessor-LAW repeal (Article 35 is a general conflict clause only)")
    print("  - Follow-up candidates NOT ingested: implementing regulations (rights/duties of")
    print("    persons called upon in civil defense work; fire/rescue operations regulation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
