#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Fisheries / Marine Resources Law track
(نظام صيد واستثمار وحماية الثروات المائية الحية في المياه الإقليمية للمملكة العربية
السعودية, Royal Decree M/9, 27/3/1408H).

13 records: 12 اصلية, 1 معدلة (Article 10), 0 مضافة, 0 ملغاة at the individual-article
level. NO chapter divisions -- flat list of 13 consecutive articles, confirmed directly
from laws.boe.gov.sa (via Wayback, two independent snapshots six years apart, identical
text). Accordingly chapter_structure is intentionally empty and every article's section_ar
is empty ("").

CRITICAL -- THIS LAW IS CURRENTLY REPEALED (لاغي), not in force. The top-level
legal_status_ar must be "لاغي" and repealed_by_ar must be present and reference the
Agriculture Law (M/64, 1442H) that repealed it via that LATER law's own issuing decree, not
via any provision inside this law's 13 articles. This validator does NOT expect or allow
any individual article's legal_status_ar to be "ملغاة" -- per this track's documented
reasoning (known_unresolved_discrepancies), BOE's blanket "canceled-article" CSS tag on 12
of 13 articles reflects the whole-document repeal, not 13 separate per-article repeal
events, so REPEALED_KEYS is intentionally empty here.

Diacritics (tashkeel) are, UNUSUALLY for this corpus, PRESERVED verbatim in this track (the
opposite of agriculture_law's stripping guard) because this text comes directly from BOE
itself, which retains partial original typesetting diacritics -- so this validator does
NOT reject residual tashkeel. It still rejects double-spaces, NBSP, curly quotes, and
non-standard Farsi-block letters, and requires internal self-consistency and that every
discrepancy is disclosed. It does not re-adjudicate provenance beyond that.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "fisheries_law", "law", "official_source",
                   "fisheries_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "fisheries_law", "law", "verified",
                       "fisheries_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "fisheries_law", "law", "verified",
                       "fisheries_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "fisheries_law_arabic_legal_llm",
                   "fisheries_law_legal_llm_001_013.json")
N = 13
KEY_RE = r"fisheries_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 12, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 0

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS = {"fisheries_law_art_010"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "fisheries_law_boe_direct_via_wayback_dual_snapshot",
    "fisheries_law_repealed_by_agriculture_law_m64_1442h",
    "fisheries_law_article_level_canceled_css_is_document_level_not_per_article",
    "fisheries_law_art010_amendment_note_not_merged_into_main_text",
    "fisheries_law_faolex_ecolex_informea_17_articles_4_headings_conflict",
    "fisheries_law_implementing_regulation_companion_candidate_unverified",
    "fisheries_law_title_spelling_variance_aqlimiyyah_hamza",
    "fisheries_law_partial_tashkeel_preserved_verbatim_from_boe_itself",
    "fisheries_law_predecessor_1351h_fish_oyster_law_not_modeled",
}
AR = "ء-ي"


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

    # This Law is flat -- chapter_structure MUST be empty and every section_ar MUST be "".
    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1c] chapter_structure must be [] for this flat (no-chapter) Law, got %r" % chs)
    if len(chs or []) != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, len(chs or [])))

    # CRITICAL: the whole law must be recorded as repealed, distinctly from article status.
    if src.get("legal_status_ar") != "لاغي":
        e.append("[0] top-level legal_status_ar must be 'لاغي' (this Law is REPEALED)")
    rep = src.get("repealed_by_ar", "")
    if not rep or "م/64" not in rep or "نظام الزراعة" not in rep:
        e.append("[0] repealed_by_ar must be present and reference the Agriculture Law (م/64) "
                 "that repealed this Law via its own issuing decree")

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
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar", "") != "":
            e.append("[2] %s: section_ar must be empty (flat no-chapter Law), got %r"
                     % (k, a.get("section_ar")))
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
        # NOTE: unlike agriculture_law, this track deliberately PRESERVES partial tashkeel
        # (verbatim from BOE itself) -- so no tashkeel-stripping guard is applied here.
        # non-standard Arabic-block letters (Farsi yeh/keheh) must not leak into article text
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)

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
        e.append("[2k] missing amendment_history (must record founding M/9 decree, the M/58 "
                 "amendment, and the M/64 external repeal)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        for tag in ("م/9", "م/58", "م/64"):
            if tag not in decrees:
                e.append("[2k] amendment_history must reference %s" % tag)

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/9)" \
            or src.get("decree_date_hijri") != "27/3/1408":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/9, 27/3/1408H")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False")
    sup = src.get("supersedes_ar", "")
    if not sup or "1351" not in sup:
        e.append("[2j] supersedes_ar must reference the 1351H fish/oyster law this Law itself "
                 "repealed via its own Article 13")
    if not src.get("preamble_ar") or "م/9" not in src.get("preamble_ar", "") \
            or "فهد بن عبد العزيز" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference م/9 and "
                 "the issuing king (فهد بن عبد العزيز)")
    art1 = arts.get("fisheries_law_art_001", {})
    if "وزارة الزراعة والمياه" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected authority (وزارة الزراعة والمياه)")
    art10 = arts.get("fisheries_law_art_010", {})
    if art10.get("legal_status_ar") != "معدلة" or not art10.get("history"):
        e.append("[2j] Article 10 must be معدلة with a non-empty amendment history (M/58, 1437H)")
    art13 = arts.get("fisheries_law_art_013", {})
    if "1351" not in art13.get("text", "") or "يلغي" not in art13.get("text", ""):
        e.append("[2j] Article 13 missing expected repeal-of-1351H-law clause")
    art13_label = art13.get("number_label_ar")
    if art13_label != "المادة الثالثة عشرة":
        e.append("[2j] Article 13 number_label_ar must be 'المادة الثالثة عشرة', got %r"
                 % art13_label)

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
        if r.get("law_current_force_status_ar") != "لاغي":
            e.append("[4] %s: verified record must carry law_current_force_status_ar='لاغي'"
                     % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("legal_status_ar") != "لاغي":
        e.append("[4b] summary legal_status_ar must be 'لاغي'")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("law_current_force_status_ar") != "لاغي":
        e.append("[5] llm layer law_current_force_status_ar must be 'لاغي'")
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
        if r.get("source_trust", {}).get("law_current_force_status_ar") != "لاغي":
            e.append("[5] %s: llm record source_trust missing law_current_force_status_ar='لاغي'"
                     % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Fisheries Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Fisheries / Marine Resources Law (نظام صيد واستثمار وحماية")
    print("  الثروات المائية الحية في المياه الإقليمية للمملكة العربية السعودية)")
    print("  - 13 records: 12 اصلية, 1 معدلة (Article 10), 0 مضافة, 0 ملغاة at article level")
    print("  - NO chapter divisions: flat list of 13 consecutive articles (chapter_structure=[],")
    print("    section_ar empty for all) -- confirmed directly by laws.boe.gov.sa via Wayback.")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/9, 27/3/1408H (CoM Resolution 14, 21/1/1408H;")
    print("    Umm Al-Qura gazette 20/4/1408H). Brand-new base-law track, not previously in this")
    print("    corpus.")
    print("  - *** THIS LAW IS CURRENTLY REPEALED (لاغي) *** -- superseded in its entirety by")
    print("    clause Second/1 of the Agriculture Law's issuing Royal Decree (M/64, 10/8/1442H),")
    print("    NOT by any provision inside this law's own 13 articles. Confirmed independently")
    print("    by: (1) BOE's own 'الحالة' status field (ساري in the Nov-2019 snapshot, لاغي from")
    print("    Aug-2021 onward); (2) this corpus's own agriculture track (supersedes_ar); (3)")
    print("    ECOLEX/InforMEA. See repealed_by_ar in the source artifact.")
    print("  - VERIFICATION TIER: TIER_1 -- full verbatim text obtained DIRECTLY from")
    print("    laws.boe.gov.sa (this corpus's designated primary source) via Wayback Machine,")
    print("    self-consistent across two independent snapshots six years apart (2019, 2025).")
    print("  - UNRESOLVED FLAG (not hidden): ECOLEX/InforMEA (citing FAOLEX) describe 17")
    print("    articles/4 headings, conflicting with BOE's confirmed 13-article flat structure;")
    print("    FAOLEX's own Arabic PDF is unreadable (corrupted font encoding) so this could not")
    print("    be independently adjudicated. BOE is trusted as the primary source.")
    print("  - Implementing Regulation (Ministerial Decision 21911, 27/3/1409H) is known to")
    print("    exist per Lexis Middle East but is UNVERIFIED and NOT ingested this pass --")
    print("    flagged as a follow-up candidate (fisheries_law_regulation) only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
