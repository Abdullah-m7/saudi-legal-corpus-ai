#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Anti-Money
Laundering Law track (27 records: 26 اصلية, 1 معدلة, 0 ملغاة, 0 مضافة; nine
chapters carrying the base Law's own chapter numbers I-VI and VIII-X -- chapter
VII العقوبات has no counterpart in the Regulation, a genuine structural feature,
not a gap).

VERIFICATION TIER (upgraded 2026-07-29) -- see the generator's module docstring
and sources/aml/regulation/official_source/aml_regulation_official_source.json's
verification_methodology_note for the full account. PRIMARY is now the Kingdom's
official gazette: the BORN-DIGITAL full text of the consolidated Regulation
attached to Administrative Decision 266507 (9/12/1447H), published by Umm al-Qura
on 11/1/1448H at uqn.gov.sa/decisions-and-regulations/4001243 (128 numbered
paragraphs, 27 articles). The aml.gov.sa official SCANNED PDF is RETAINED as a
documented SECONDARY cross-check (it was the previous pass's PRIMARY and the
source of the OCR defects corrected on 2026-07-29); qanoniah.com's born-digital
feed (articles 1,2,5,7,8,9,10,14,15,16) is a third channel.

This pass also (a) re-homed three paragraphs out of article 17 into the newly
created articles 18 and 19 (٦/١٧->١/١٨, ٧/١٧->٢/١٨, ٨/١٧->١/١٩) -- disclosed, not
silent, with prior state kept in rehomed_from / restructuring_note_ar; (b)
RETRACTED the prior false assertion that articles 18 and 19 were "deliberately
absent from the source" (prior wording preserved verbatim in
prior_description_RETRACTED); (c) applied 25 recorded OCR corrections across 23 paragraphs in 11 articles,
two of them meaning-changing (17/4(ج) «الأخرى برئاسة أمن الدولة», 49/1 «يسمح»),
each with prior state in corrections_applied.

This validator checks internal self-consistency only; it does not re-adjudicate
provenance.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "aml", "regulation", "official_source",
                   "aml_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "aml", "regulation", "verified",
                       "aml_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "aml", "regulation", "verified",
                       "aml_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "aml_regulation_arabic_legal_llm",
                   "aml_regulation_legal_llm_001_027.json")
N = 27
KEY_RE = r"aml_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 26, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
EXPECTED_CHAPTERS = 9
EXPECTED_NUMBERS = [1, 2, 5, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24,
                    36, 37, 38, 39, 40, 41, 42, 43, 48, 49]
# The three paragraphs re-homed out of article 17 on 2026-07-29, and where they went.
REHOMED_KEYS = {"aml_regulation_art_018": ["٦/١٧", "٧/١٧"],
                "aml_regulation_art_019": ["٨/١٧"]}
# Articles whose text carries at least one correction applied from the gazette.
CORRECTED_KEYS = {"aml_regulation_art_015", "aml_regulation_art_017",
                  "aml_regulation_art_022", "aml_regulation_art_023",
                  "aml_regulation_art_024", "aml_regulation_art_038",
                  "aml_regulation_art_039", "aml_regulation_art_040",
                  "aml_regulation_art_041", "aml_regulation_art_043",
                  "aml_regulation_art_049"}
EXPECTED_TIER = "TIER_1_BORN_DIGITAL_OFFICIAL_GAZETTE_X_OFFICIAL_SCAN_CROSS_VERIFIED"
PRIOR_TIER = "TIER_3_OCR_SCAN_PLUS_PARTIAL_BORN_DIGITAL"
GAZETTE_STATUS = "MATCHES_UQN_GAZETTE_BORN_DIGITAL"
GAZETTE_URL = "uqn.gov.sa/decisions-and-regulations/4001243"
# the two meaning-changing omissions the gazette restored on 2026-07-29
SUBSTANTIVE_17_4 = "الجهات الأخرى برئاسة أمن الدولة"
SUBSTANTIVE_49_1 = "أمر مسبب يسمح لرجل ضبط جنائي"
ABSENT_LIST_RE = ("الأرقام غير الموجودة " + r"\(([^)]*)\)")

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS = {"aml_regulation_art_017"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "aml_regulation_article17_paragraphs_rehomed_to_18_19",
    "aml_regulation_ocr_corrections_applied_from_gazette",
    "aml_regulation_orthographic_normalisation_vs_gazette",
    "aml_regulation_paragraph_tag_digit_order_unresolved",
    "aml_regulation_uqn_preamble_cites_m223_as_issuing_decree",
    "aml_regulation_base_law_decree_date_corrected",
    "aml_regulation_gazette_not_a_new_instrument",
    "aml_regulation_boe_unreachable_no_dedicated_page",
    "aml_regulation_primary_source_is_scanned_pdf",
    "aml_regulation_qanoniah_partial_subset",
    "aml_regulation_no_explicit_article_headers",
    "aml_regulation_skipped_law_articles",
    "aml_regulation_article17_amended_paragraph_not_isolated",
    "aml_regulation_older_1430_predecessor",
    "aml_regulation_supersession",
    "aml_regulation_sama_serves_older_version",
    "aml_regulation_qanoniah_confirmed_current_version",
}
AR = "ء-ي"


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

    # article numbers present must match the enumerated set
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != EXPECTED_NUMBERS:
        e.append("[1b] present article numbers %s != expected %s" % (nums, EXPECTED_NUMBERS))
    if src.get("article_numbers_present") != EXPECTED_NUMBERS:
        e.append("[1b] article_numbers_present field mismatch")

    chs = src.get("chapter_structure") or []
    if len(chs) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTERS, len(chs)))
    covered = []
    for ch in chs:
        nl = ch.get("article_numbers") or []
        covered.extend(nl)
    if sorted(covered) != EXPECTED_NUMBERS:
        e.append("[1c] chapter_structure article coverage %s != %s"
                 % (sorted(covered), EXPECTED_NUMBERS))
    if len(covered) != len(set(covered)):
        e.append("[1c] an article is covered by more than one chapter")
    # chapter VII (العقوبات) must be absent -> jump from السادس to الثامن
    labels = [c.get("label_ar") for c in chs]
    if "الفصل السابع" in labels:
        e.append("[1d] chapter VII (العقوبات) should be ABSENT in the Regulation")
    if "الفصل السادس" not in labels or "الفصل الثامن" not in labels:
        e.append("[1d] expected chapters السادس (الرقابة) and الثامن (المصادرة) present")

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        want_prefix = {"UNCHANGED": (GAZETTE_STATUS,), "AMENDED": (GAZETTE_STATUS,)}
        if a.get("status") not in want_prefix.get(expected_status, ()):
            e.append("[2] %s: unexpected status %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("source_channel") != "uqn_gazette":
            e.append("[2] %s: missing/invalid source_channel" % k)
        # honesty: the pre-gazette channel/status of every carried-over article
        # must be recorded, never silently dropped
        if k in REHOMED_KEYS:
            if a.get("prior_source_channel") != "scan":
                e.append("[2m] %s: re-homed article must record prior_source_channel" % k)
        else:
            if a.get("prior_source_channel") not in ("qanoniah", "scan"):
                e.append("[2m] %s: missing prior_source_channel" % k)
            if a.get("prior_status") not in ("MATCHES_SOURCE_QANONIAH",
                                             "MATCHES_SCAN_OCR_VISUALLY_ADJUDICATED"):
                e.append("[2m] %s: missing prior_status" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact" % k)
        # digit normalisation: paragraph tags must be Arabic-Indic (no ASCII digits)
        if re.search(r"[0-9]", a["text"]):
            e.append("[2g] %s: ASCII digit present (should be normalised to Arabic-Indic)" % k)
        # number_label must reference the article number
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("number_label_ar") != "المادة (%d) من اللائحة" % n:
            e.append("[2h] %s: number_label_ar mismatch" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    # ---- [3] the 2026-07-29 restructure must stay disclosed and intact --------
    a17 = arts.get("aml_regulation_art_017", {})
    tags17 = re.findall(r"(?m)^([٠-٩]+)/([٠-٩]+)-", a17.get("text", ""))
    if [t[0] for t in tags17] != ["١", "٢", "٣", "٤", "٥"]:
        e.append("[3a] article 17 must carry exactly paragraphs 1..5 (gazette-confirmed); "
                 "found %s" % ([t[0] for t in tags17],))
    if not a17.get("restructuring_note_ar"):
        e.append("[3a] article 17 must disclose the paragraph re-homing (restructuring_note_ar)")
    for k, prior_tags in REHOMED_KEYS.items():
        a = arts.get(k)
        if a is None:
            e.append("[3b] %s: missing (should have been created from re-homed "
                     "article-17 paragraphs)" % k)
            continue
        rh = a.get("rehomed_from") or {}
        if rh.get("prior_article_key") != "aml_regulation_art_017":
            e.append("[3b] %s: rehomed_from.prior_article_key must be aml_regulation_art_017" % k)
        if rh.get("prior_paragraph_tags") != prior_tags:
            e.append("[3b] %s: rehomed_from.prior_paragraph_tags %r != %r"
                     % (k, rh.get("prior_paragraph_tags"), prior_tags))
        if not rh.get("note_ar"):
            e.append("[3b] %s: re-homing must carry an explicit note_ar" % k)
        if a.get("section_ar") != "الإدارة العامة للتحريات المالية":
            e.append("[3b] %s: wrong chapter section" % k)
    # the two meaning-changing omissions the gazette restored must be present
    if SUBSTANTIVE_17_4 not in a17.get("text", ""):
        e.append("[3c] article 17 para 4 sub-(j) is missing the gazette wording restored on "
                 "2026-07-29 (a substantive OCR omission)")
    if SUBSTANTIVE_49_1 not in arts.get("aml_regulation_art_049", {}).get("text", ""):
        e.append("[3c] article 49 para 1 is missing the gazette verb restored on 2026-07-29 "
                 "(a substantive OCR omission)")
    # prior state of every applied correction must be recorded, never dropped
    for k in CORRECTED_KEYS:
        ca = (arts.get(k) or {}).get("corrections_applied")
        if not ca:
            e.append("[3d] %s: corrections were applied but corrections_applied is missing" % k)
            continue
        for c in ca:
            if not c.get("prior_text_ar") or not c.get("corrected_text_ar"):
                e.append("[3d] %s: a correction does not record its prior state" % k)
                continue
            if not c.get("paragraph") or not c.get("class"):
                e.append("[3d] %s: a correction is not classified/located" % k)
            if c["prior_text_ar"] not in c["corrected_text_ar"] and \
                    c["prior_text_ar"] in arts[k]["text"]:
                e.append("[3d] %s: uncorrected prior wording still present: %r"
                         % (k, c["prior_text_ar"][:40]))
    for k, a in arts.items():
        if a.get("corrections_applied") and k not in CORRECTED_KEYS:
            e.append("[3d] %s: undeclared corrections_applied" % k)

    # ---- [3e] the false "articles 18/19 deliberately absent" claim is retracted
    dmap = {d["article_key"]: d for d in (src.get("known_unresolved_discrepancies") or [])}
    skip = dmap.get("aml_regulation_skipped_law_articles")
    if skip is None:
        e.append("[3e] missing aml_regulation_skipped_law_articles entry")
    else:
        if not skip.get("prior_description_RETRACTED"):
            e.append("[3e] the retracted prior wording must be preserved verbatim in "
                     "prior_description_RETRACTED (nothing is deleted)")
        if not skip.get("retraction_note_ar"):
            e.append("[3e] the retraction must state why the prior assertion was wrong")
        m = re.search(ABSENT_LIST_RE, skip.get("description", ""))
        if not m:
            e.append("[3e] could not locate the absent-numbers list to re-check")
        else:
            nums = re.findall(r"\d+", m.group(1))
            if "18" in nums or "19" in nums:
                e.append("[3e] articles 18/19 are STILL listed as absent from the source")

    # ---- [3f] verification tier upgraded, prior tier and old primary recorded -
    if src.get("verification_tier") != EXPECTED_TIER:
        e.append("[3f] verification_tier %r != %r" % (src.get("verification_tier"), EXPECTED_TIER))
    if src.get("prior_verification_tier") != PRIOR_TIER:
        e.append("[3f] prior_verification_tier must record the superseded %s" % PRIOR_TIER)
    prov = src.get("provenance") or {}
    if GAZETTE_URL not in str(prov.get("primary_source", "")):
        e.append("[3f] primary_source must be the Umm al-Qura born-digital gazette page 4001243")
    if prov.get("primary_source_kind") != "born_digital_official_gazette_html_no_ocr":
        e.append("[3f] primary_source_kind must state the born-digital gazette channel")
    if prov.get("primary_source_paragraph_count") != 128 or \
            prov.get("primary_source_article_count") != N:
        e.append("[3f] gazette paragraph/article counts must be recorded as 128/%d" % N)
    if "aml.gov.sa" not in str(prov.get("secondary_cross_check_scan", "")):
        e.append("[3f] the aml.gov.sa scan must be retained as a documented SECONDARY channel")
    if not prov.get("prior_primary_source"):
        e.append("[3f] the superseded primary source must stay recorded")
    lp = prov.get("primary_source_local_copy")
    if not lp or not os.path.isfile(os.path.join(ROOT, lp)):
        e.append("[3f] the extracted gazette body must be committed at primary_source_local_copy")

    # ---- [3g] base-law decree date corrected in place, prior state kept ------
    bl = src.get("base_law") or {}
    if bl.get("decree_date_hijri") != "5/2/1439":
        e.append("[3g] base_law.decree_date_hijri must be 5/2/1439 (the DECREE date)")
    if bl.get("publish_date_hijri") != "14/2/1439":
        e.append("[3g] base_law.publish_date_hijri must be 14/2/1439 (the PUBLICATION date)")
    if bl.get("prior_recorded_decree_date_hijri") != "14/2/1439":
        e.append("[3g] base_law must preserve the prior (wrong) recorded date")
    if not bl.get("decree_date_correction_note_ar"):
        e.append("[3g] base_law must explain the date correction")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        for token in ("14525", "98752", "266507"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference instrument %s" % token)

    # spot-checks anchoring key facts established this pass
    a1 = arts.get("aml_regulation_art_001", {})
    if "المحفظة الإلكترونية" not in a1.get("text", "") or "الموارد الاقتصادية" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing regulation-distinctive definitions "
                 "(المحفظة الإلكترونية / الموارد الاقتصادية)")
    a17 = arts.get("aml_regulation_art_017", {})
    if "الإيقمونت" not in a17.get("text", ""):
        e.append("[2j] Article 17 missing expected Egmont-Group (الإيقمونت) reference")
    a49 = arts.get("aml_regulation_art_049", {})
    if "الضبط الجنائي" not in a49.get("text", ""):
        e.append("[2j] Article 49 missing expected criminal-investigation content")
    mnote = src.get("verification_methodology_note", "")
    if GAZETTE_URL not in mnote:
        e.append("[2d] methodology note must cite the born-digital gazette source")
    for _tok in ("الأخرى برئاسة أمن الدولة", "يسمح",
                 "٦/١٧", "١/١٨"):
        if _tok not in mnote:
            e.append("[2d] methodology note must disclose %r" % _tok)
    if src.get("decree_date_hijri") != "19/2/1439":
        e.append("[2j] decree_date_hijri must be 19/2/1439 (SAMA canonical no. 14525)")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True")
    if "preamble_ar" in src:
        e.append("[2j] preamble_ar should be ABSENT (not fabricated)")

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
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in AML Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Anti-Money Laundering Law")
    print("  - 27 records: 26 اصلية, 1 معدلة (Article 17, per Admin Decision 98752), 0 ملغاة, 0 مضافة")
    print("  - 9 chapters (Law-numbered I-VI, VIII-X; chapter VII العقوبات has no counterpart)")
    print("  - present article numbers: %s" % EXPECTED_NUMBERS)
    print("  - VERIFICATION TIER: %s" % EXPECTED_TIER)
    print("    PRIMARY = Umm al-Qura official gazette, BORN-DIGITAL full text of the consolidated")
    print("    Regulation attached to Admin Decision 266507, published 11/1/1448H at")
    print("    %s (128 paragraphs, 27 articles)." % GAZETTE_URL)
    print("    SECONDARY (retained, documented): aml.gov.sa official scanned PDF -- the previous")
    print("    pass's PRIMARY and the source of the OCR defects fixed here. THIRD: qanoniah.com")
    print("    born-digital API (articles 1,2,5,7,8,9,10,14,15,16).")
    print("    Superseded tier: %s" % PRIOR_TIER)
    print("  - DISCLOSED RESTRUCTURE (2026-07-29): three paragraphs re-homed out of article 17,")
    print("    creating articles 18 and 19. Article count 25 -> 27; paragraph count unchanged at")
    print("    128; no text added or removed. See rehomed_from / restructuring_note_ar.")
    print("  - RETRACTED: the prior assertion that articles 18 and 19 were 'deliberately absent")
    print("    from the source' was FALSE; prior wording preserved in prior_description_RETRACTED.")
    print("  - 25 recorded OCR corrections across 23 paragraphs in 11 articles, two of them")
    print("    meaning-changing (art 17 para 4 sub-(j), art 49 para 1). Prior state of every")
    print("    correction kept in corrections_applied.")
    print("  - base_law decree date corrected in place 14/2/1439 -> 5/2/1439 (14/2/1439 is the")
    print("    PUBLICATION date); prior value preserved, three official sources cited.")
    print("  - Founding approval cable No. 14525 (19/2/1439H) = SAMA's canonical in-force no.;")
    print("    amended by Admin Decision 98752 (Art. 17); consolidated by 266507 (9/12/1447H).")
    print("  - Predecessor/supersession: the base Law (M/20) replaced M/31 (Law art. 51); a")
    print("    separate older 1430H regulation exists and is NOT mixed in.")
    print("  - OPEN, DISCLOSED: paragraph tags are stored 'paragraph/article' while the gazette")
    print("    prints 'article/paragraph' -- deliberately NOT changed this pass, see")
    print("    aml_regulation_paragraph_tag_digit_order_unresolved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
