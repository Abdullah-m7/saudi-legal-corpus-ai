#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Law of Audiovisual Media track
(نظام الإعلام المرئي والمسموع; 25 records: 24 اصلية, 1 معدلة [art 1],
0 ملغاة, 0 مضافة; FLAT statute -- no chapters/فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/audiovisual_media/law/official_source/
audiovisual_media_law_official_source.json's verification_methodology_note for the
full account: laws.boe.gov.sa HAS a dedicated lawId page for this law
(ed5fdbc0-c183-4a8a-a8b7-a9ed004b5900) but it was unreachable this pass (HTTP 503
live / connection reset; web.archive.org refused by the WebFetch tool itself and
NOT bypassed). PRIMARY full text is from nezams.com, strongly cross-checked
against an archived print/scan of the actual BOE portal Viewer page (cyrilla.org)
and against the official BOE English translation (misa.gov.sa) whose Appendix
independently confirms the 1440H amendment -> TIER_2. This validator does not
re-adjudicate provenance; it only checks internal self-consistency and that every
discrepancy is still recorded.

MATERIAL FACTS checked: flat structure (chapter_structure == []); article 1 carries
amendment_current history documenting the Resolution-374 terminology substitution
(its `text` field is the UNCHANGED original enacted wording, per the
associations_ngo_law precedent for a pure horizontal substitution); NO predecessor
repeal exists; the distinction from the press (نظام المطبوعات والنشر) track is
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
SRC = os.path.join(ROOT, "sources", "audiovisual_media", "law", "official_source",
                   "audiovisual_media_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "audiovisual_media", "law", "verified",
                       "audiovisual_media_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "audiovisual_media", "law", "verified",
                       "audiovisual_media_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "audiovisual_media_arabic_legal_llm",
                   "audiovisual_media_law_legal_llm_001_025.json")
N = 25
KEY_RE = r"audiovisual_media_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 24, "معدلة": 1, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = {
    "audiovisual_media_law_art_001",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {k: STATUS_AMENDED_DATED for k in AMENDED_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "audiovisual_media_law_boe_dedicated_page_exists_but_unreachable",
    "audiovisual_media_law_amendment_res374_1440h_ministry_rename",
    "audiovisual_media_law_art1_substitution_note_not_operative_rewrite",
    "audiovisual_media_law_no_named_predecessor_repeal",
    "audiovisual_media_law_distinct_from_press_publications_law",
    "audiovisual_media_law_gcam_establishment_regulation_out_of_scope",
    "audiovisual_media_law_regulator_renamed_gamr",
    "audiovisual_media_law_implementing_regulation_out_of_scope",
    "audiovisual_media_law_gazette_publication_date_unconfirmed",
    "audiovisual_media_law_gregorian_date_secondary_corroborated",
    "audiovisual_media_law_com_res170_12_month_compliance_grace_period",
    "audiovisual_media_law_tashkeel_and_normalization",
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

    # continuous 1..25, no gaps/dupes
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
        # NOTE: this corpus stores `status` as a descriptive free-text verification
        # string (not a fixed enum); we only require it be present and non-empty.
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
        # amended-article history integrity: a PURE terminology-substitution note
        # (no full-text replacement), so history holds amendment_current-only entries
        # citing Resolution 374, and `text` equals the UNCHANGED original wording.
        if k in AMENDED_KEYS:
            hist = a.get("history") or []
            if not hist:
                e.append("[2m] %s: amended article must carry at least one history entry" % k)
            for h in hist:
                if h.get("type") != "amendment_current":
                    e.append("[2m] %s: history entries must be type=amendment_current "
                             "(pure substitution note, no full-text replacement)" % k)
                if "374" not in (h.get("decree_note") or ""):
                    e.append("[2m] %s: amendment_current decree_note must cite CoM "
                             "Resolution 374" % k)
            # the enacted text must still show the ORIGINAL ministry naming (not
            # rewritten) -- the substitution is documented, not silently applied
            if "وزارة الثقافة والإعلام" not in a["text"] or "وزير الثقافة والإعلام" not in a["text"]:
                e.append("[2m] %s: enacted text must preserve original (وزارة/وزير الثقافة "
                         "والإعلام) wording verbatim -- substitution is documented in "
                         "history only, not applied to the stored text" % k)

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
        if "م/33" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/33")
        if "374" not in decrees:
            e.append("[2k] amendment_history must reference amending resolution 374")

    # spot-checks anchoring key facts
    art1 = arts.get("audiovisual_media_law_art_001", {}).get("text", "")
    if "الإعلام المرئي والمسموع" not in art1 or "التعريفات" not in art1:
        e.append("[2j] Article 1 missing expected definitions header")
    if "اللجنة الابتدائية" not in art1 or "نظام المطبوعات والنشر" not in art1:
        e.append("[2j] Article 1 missing expected Preliminary/Appeal Committee "
                 "cross-reference to the Press and Publications Law")
    art2 = arts.get("audiovisual_media_law_art_002", {}).get("text", "")
    if "يهدف النظام" not in art2:
        e.append("[2j] Article 2 missing expected objectives clause")
    art17 = arts.get("audiovisual_media_law_art_017", {}).get("text", "")
    for token in ("عشرة ملايين ريال", "ستة أشهر", "إلغاء الترخيص"):
        if token not in art17:
            e.append("[2j] Article 17 (penalties) missing expected token %r" % token)
    art22 = arts.get("audiovisual_media_law_art_022", {}).get("text", "")
    if "هيئة الإذاعة والتلفزيون" not in art22:
        e.append("[2j] Article 22 missing expected grandfathering clause")
    art23 = arts.get("audiovisual_media_law_art_023", {}).get("text", "")
    if "اللائحة" not in art23 or "تسعين" not in art23:
        e.append("[2j] Article 23 missing expected implementing-regulation mandate")
    art24 = arts.get("audiovisual_media_law_art_024", {}).get("text", "")
    if "تسعين" not in art24:
        e.append("[2j] Article 24 missing expected 90-day effective-date clause")
    art25 = arts.get("audiovisual_media_law_art_025", {}).get("text", "")
    if "يتعارض" not in art25:
        e.append("[2j] Article 25 missing expected generic conflict/repeal clause")

    # NO named predecessor repeal anywhere (founding statute; only a generic clause
    # in Article 25 is allowed)
    for k, a in arts.items():
        if re.search(r"يلغي|يُلغي|يلغى", a["text"]) and k != "audiovisual_media_law_art_025":
            e.append("[2j] %s: unexpected repeal clause outside Article 25" % k)
    if re.search(r"يلغي\s+\S+\s+رقم|إلغاء\s+نظام|إلغاء\s+لائحة", art25):
        e.append("[2j] Article 25 unexpectedly names a specific repealed instrument "
                 "(expected only a generic conflict clause)")

    if src.get("decree") != "المرسوم الملكي رقم م/33" or src.get("decree_date_hijri") != "25/3/1439":
        e.append("[2j] decree/decree_date_hijri mismatch with Royal Decree M/33, 25/3/1439H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this law HAS an amendment "
                 "incorporated)")
    pre = src.get("preamble_ar", "")
    if not pre or "170" not in pre or "نظام الإعلام المرئي والمسموع" not in pre:
        e.append("[2j] preamble_ar must be present and reference CoM Resolution 170 and "
                 "the law name")
    if "اثني عشر شهرا" not in pre:
        e.append("[2j] preamble_ar must record the 12-month compliance grace period "
                 "(CoM Resolution 170, clause ثانيا)")

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
        print("FAIL: %d error(s) in Audiovisual Media Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Law of Audiovisual Media (نظام الإعلام المرئي والمسموع)")
    print("  - 25 records: 24 اصلية, 1 معدلة (art 1, terminology substitution only), "
          "0 ملغاة, 0 مضافة")
    print("  - FLAT statute: continuous 1-25, NO chapters/فصول (chapter_structure == [],")
    print("    section_ar empty by design)")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa HAS a dedicated lawId page")
    print("    (ed5fdbc0-c183-4a8a-a8b7-a9ed004b5900) but was unreachable this pass (live HTTP")
    print("    503; web.archive.org refused by the WebFetch tool itself, not bypassed). PRIMARY")
    print("    text from nezams.com, strongly cross-checked against an archived scan of the")
    print("    actual BOE portal page (cyrilla.org) and the official BOE English translation")
    print("    (misa.gov.sa), whose Appendix independently confirms the 1440H amendment")
    print("  - Royal Decree M/33 (25/3/1439H, ~13 Dec 2017G), CoM Resolution 170 (24/3/1439H);")
    print("    amended by CoM Resolution 374 (28/6/1440H, ~5 Mar 2019G): pure ministry/minister")
    print("    terminology substitution affecting only Article 1's definitions")
    print("  - NO predecessor repeal (founding statute; Article 25 is only a generic conflict")
    print("    clause)")
    print("  - DISTINCT from press (نظام المطبوعات والنشر, M/32 1421H): Article 1 only")
    print("    cross-references two committees formed under that law, no merge")
    print("  - Follow-up candidates NOT ingested: Implementing Regulation (art 23) and the")
    print("    GCAM establishment regulation (CoM Resolution 332, 16/10/1433H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
