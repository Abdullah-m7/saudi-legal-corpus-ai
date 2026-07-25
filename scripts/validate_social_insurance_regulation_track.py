#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the (New) Social
Insurance Law track (اللائحة التنفيذية لنظام التأمينات الاجتماعية; 107
records, ALL اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 7 أبواب with أبواب 2/3/4/6
subdivided into نested فصول).

SCOPE NOTE -- this validates the implementing regulation of the NEW Social
Insurance Law (Royal Decree M/273, 26/12/1445H) only. It is a separate
track from the implementing regulation of the OLD/legacy Social Insurance
Law (M/33, 3/9/1421H), built independently -- see
social_insurance_regulation_base_law_naming_collision_inherited in the
source JSON's known_unresolved_discrepancies.

VERIFICATION TIER -- see the generator's module docstring and
sources/social_insurance_regulation/law/official_source/
social_insurance_regulation_official_source.json's verification_methodology_note
for the full account: PRIMARY source is the official Umm al-Qura Gazette
portal (uqn.gov.sa) itself -- direct HTML text, not scanned -- cross-checked
article-by-article against qanoonsa.com (independent secondary aggregator)
and corroborated by argaam.com (tertiary). laws.boe.gov.sa was unreachable
live this pass (connection reset), not circumvented. This validator does
not re-adjudicate provenance; it only checks internal self-consistency and
that every discrepancy is still recorded.

MATERIAL FACTS checked: 107-article, 7-باب structure (4 أبواب further split
into نested فصول, covering exactly articles 1-107 with no gaps/overlaps);
all 107 articles اصلية with empty history; the approving instrument is a
Minister of Finance Resolution (230/تأمينات), NOT Royal Decree M/273 itself
(a corrected prior-research misconception, explicitly flagged).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "social_insurance_regulation", "law", "official_source",
                   "social_insurance_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "social_insurance_regulation", "law", "verified",
                       "social_insurance_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "social_insurance_regulation", "law", "verified",
                       "social_insurance_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "social_insurance_regulation_arabic_legal_llm",
                   "social_insurance_regulation_legal_llm_001_107.json")
N = 107
KEY_RE = r"social_insurance_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 107, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 7  # 7 أبواب
EXPECTED_SUB_SECTIONS = {"الباب الثاني": 4, "الباب الثالث": 3, "الباب الرابع": 2,
                         "الباب السادس": 2}

AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "social_insurance_regulation_approving_instrument_not_royal_decree_m273",
    "social_insurance_regulation_uqn_paragraph_enumeration_gap",
    "social_insurance_regulation_chapter_three_empty_fasl_title",
    "social_insurance_regulation_gazette_issue_5038_secondary_source_only",
    "social_insurance_regulation_boe_unreachable_not_circumvented",
    "social_insurance_regulation_qatar_almeezan_name_collision_warning",
    "social_insurance_regulation_no_amendments_since_enactment",
    "social_insurance_regulation_base_law_naming_collision_inherited",
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


def _iter_chapter_ranges(chs):
    for ch in chs:
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        yield (lo, hi)
        for sec in ch.get("sections") or []:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            yield (slo, shi)


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
        e.append("[1b] article numbers not a clean 1..%d sequence" % N)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (أبواب), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))
    for ch in chs:
        label = ch.get("label_ar")
        n_sections = len(ch.get("sections") or [])
        expected = EXPECTED_SUB_SECTIONS.get(label, 0)
        if n_sections != expected:
            e.append("[1c] %s: expected %d nested فصل sections, got %d" % (label, expected, n_sections))

    # top-level باب ranges must cover 1..N with no gap/overlap
    covered = set()
    for ch in chs:
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one باب range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] top-level chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] top-level chapter_structure covers out-of-range article(s): %s" % extra[:20])

    # nested فصل ranges (where present) must exactly partition their parent باب
    for ch in chs:
        secs = ch.get("sections") or []
        if not secs:
            continue
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        sec_covered = set()
        for sec in secs:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            for n in range(slo, shi + 1):
                if n in sec_covered:
                    e.append("[1d] %s: article %d covered by >1 فصل" % (ch["label_ar"], n))
                sec_covered.add(n)
        if sec_covered != set(range(lo, hi + 1)):
            e.append("[1d] %s: nested فصل ranges do not exactly partition %d-%d"
                     % (ch["label_ar"], lo, hi))

    if not src.get("preamble_ar", "").strip():
        e.append("[1e] missing/empty preamble_ar")

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
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (باب/فصل title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if a.get("history"):
            e.append("[2i] %s: no article in this unamended regulation should carry history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2g] %s: residual Eastern-Arabic-Indic digit found (must be Western)" % k)
        if "‌" in a["text"] or "￼" in a["text"]:
            e.append("[2h] %s: stray ZWNJ/object-replacement character present" % k)

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
        e.append("[2k] missing amendment_history (must record founding resolution)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "230" not in decrees:
            e.append("[2k] amendment_history must reference founding resolution (230/تأمينات)")

    # spot-checks anchoring key facts
    art1 = arts.get("social_insurance_regulation_art_001", {}).get("text", "")
    if "المؤسسة العامة للتأمينات الاجتماعية" not in art1:
        e.append("[2j] Article 1 missing expected definition of المؤسسة")
    art107 = arts.get("social_insurance_regulation_art_107", {}).get("text", "")
    if "تُنشر اللائحة في الجريدة الرسمية" not in art107:
        e.append("[2j] Article 107 missing expected publication/effective-date clause")

    if src.get("decree") != "قرار وزير المالية رقم (230/تأمينات)" \
            or src.get("decree_date_hijri") != "26/12/1445":
        e.append("[2j] decree/decree_date_hijri mismatch with Minister of Finance Resolution "
                 "230/تأمينات, 26/12/1445H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendments exist)")
    if src.get("law_component") != "regulation":
        e.append("[2j] law_component must be 'regulation'")
    pre = src.get("preamble_ar", "")
    if "230" not in pre or "م/273" not in pre:
        e.append("[2j] preamble_ar must reference both the Resolution number (230) and the "
                 "base law's Royal Decree (M/273) as legal basis")
    # guard against the corrected prior-research misconception creeping back in
    if src.get("decree") == "المرسوم الملكي رقم (م/273)":
        e.append("[2j] REGRESSION: decree field must NOT be the base law's Royal Decree M/273 "
                 "-- this Regulation was approved by Minister of Finance Resolution 230/تأمينات")

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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Social Insurance Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the (New) Social Insurance Law")
    print("  (اللائحة التنفيذية لنظام التأمينات الاجتماعية)")
    print("  - 107 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة) -- no amendment found since issuance")
    print("  - 7 أبواب, with أبواب 2/3/4/6 subdivided into 4/3/2/2 نested فصول respectively")
    print("  - VERIFICATION TIER: PRIMARY official Umm al-Qura Gazette portal (uqn.gov.sa, direct")
    print("    HTML text, not scanned) cross-checked article-by-article against qanoonsa.com")
    print("    (independent secondary aggregator; 0 substantive differences across all 107")
    print("    articles), corroborated by argaam.com (tertiary); laws.boe.gov.sa unreachable live")
    print("    this pass (connection reset, not circumvented)")
    print("  - CORRECTED prior-research misconception: approved by Minister of Finance Resolution")
    print("    No. (230/تأمينات), 26/12/1445H -- NOT by Royal Decree M/273 (that decree issues the")
    print("    base Law only)")
    print("  - This is the NEW Social Insurance Law's (M/273) regulation, distinct from the")
    print("    OLD/legacy Social Insurance Law's (M/33) own regulation (separate track)")
    print("  - uqn.gov.sa paragraph/sub-paragraph enumeration-marker gap (~63/107 articles)")
    print("    disclosed, not silently corrected using the secondary source's numbering")
    print("  - IN-FORCE from 3/7/2024G")
    return 0


if __name__ == "__main__":
    sys.exit(main())
