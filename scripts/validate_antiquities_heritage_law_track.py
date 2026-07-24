#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Antiquities, Museums and Urban Heritage
Law track (نظام الآثار والمتاحف والتراث العمراني, Royal Decree M/3, 9/1/1436H, as
amended).

94 records: 78 اصلية, 16 معدلة, 0 ملغاة, 0 مضافة. GENUINELY FLAT structure -- the law
has NO أبواب/فصول (confirmed from two independent sources: nezams.com and a BOE-content
print PDF), so chapter_structure is [] and section_ar is empty for every article.

By its own Article 92 this law EXPLICITLY replaces, BY NAME, the older Antiquities Law
(نظام الآثار, Royal Decree M/26, 23/6/1392H) and repeals all conflicting provisions.

16 معدلة articles across 6 amendment instruments (M/16 1439H; CoM 693 1441H; M/67 1442H
= CoM 453; M/103 1442H; CoM 1012 1445H) -- amendments NEVER silently merged: the
pre-amendment text is preserved in each amended article's history[].

VERIFICATION TIER -- TIER_3. See the generator docstring and the source artifact's
verification_methodology_note for the full account (laws.boe.gov.sa HAS a dedicated
lawId page a7d4493b-7c03-4c2d-b3c6-a9a700f275cd but was unreachable this pass, Wayback
egress-blocked; verbatim text from nezams.com, corroborated by a BOE-content print PDF
and the Umm Al-Qura Gazette). This validator does not re-adjudicate provenance; it only
checks internal self-consistency of the ingested text and that every discrepancy is
still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "antiquities_heritage", "law", "official_source",
                   "antiquities_heritage_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "antiquities_heritage", "law", "verified",
                       "antiquities_heritage_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "antiquities_heritage", "law", "verified",
                       "antiquities_heritage_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "antiquities_heritage_arabic_legal_llm",
                   "antiquities_heritage_law_legal_llm_001_094.json")
N = 94
KEY_RE = r"antiquities_heritage_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 78, "معدلة": 16, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
# The 16 amended articles (all معدلة; none مضافة/ملغاة/مكرر in this law).
AMENDED_NUMS = {1, 3, 12, 29, 54, 65, 71, 72, 73, 74, 75, 76, 77, 85, 90, 93}
AMENDED_KEYS = {"antiquities_heritage_art_%03d" % n for n in AMENDED_NUMS}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
# Article whose in-force (M/103-amended) text preserves a source Farsi-yeh quirk verbatim.
FARSI_YEH_ALLOWED_KEYS = {"antiquities_heritage_art_003"}
FLAGGED_DISCREPANCY_KEYS = {
    "antiquities_heritage_boe_dedicated_page_exists_but_unreachable",
    "antiquities_heritage_flat_structure_no_chapters",
    "antiquities_heritage_art003_m103_farsi_yeh_preserved",
    "antiquities_heritage_m67_paired_with_com453",
    "antiquities_heritage_com_only_citations_for_1012_and_693",
    "antiquities_heritage_ministry_name_history_gap_arts_12_29_54",
    "antiquities_heritage_partial_amendments_not_spliced",
    "antiquities_heritage_named_repeal_of_m26_1392",
    "antiquities_heritage_gazette_issue_unconfirmed",
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
    # continuous 1..94, no mukarrar
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers are not the continuous set 1..%d" % N)

    # FLAT law: chapter_structure MUST be empty (no أبواب/فصول)
    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1c] chapter_structure must be [] for this flat law (no أبواب/فصول), got %r"
                 % (chs,))

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
        # section_ar MUST be empty for this flat law (no chapter titles to carry)
        if a.get("section_ar"):
            e.append("[2] %s: section_ar must be empty (flat law, no chapters)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
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
        # residual tashkeel guard (all harakat/shadda/tanwin/superscript-alef must be stripped)
        if re.search(r"[ً-ٰٟ]", a["text"]):
            e.append("[2g] %s: residual tashkeel/diacritics not stripped" % k)
        # Farsi keheh/yeh-with-hamza never allowed; Farsi yeh (ی) only in the one disclosed article
        if re.search(r"[کے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi keheh/yeh) present" % k)
        if "ی" in a["text"] and k not in FARSI_YEH_ALLOWED_KEYS:
            e.append("[2g] %s: Farsi yeh (ی) present outside the one disclosed article" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    # the one disclosed Farsi-yeh quirk MUST actually still be present in Article 3
    if "ی" not in arts.get("antiquities_heritage_art_003", {}).get("text", ""):
        e.append("[2g] Article 3 expected to preserve the disclosed source Farsi-yeh (ی) quirk verbatim")

    # amended articles: history must preserve pre-amendment text and cite the amending instrument
    for k in AMENDED_KEYS:
        hist = arts.get(k, {}).get("history") or []
        joined = " ".join((h.get("decree", "") + " " + h.get("decree_note", "")) for h in hist)
        if not any("المرسوم الملكي" in joined or "مجلس الوزراء" in joined for _ in [0]):
            e.append("[2h] %s: amendment history missing an amending-instrument citation" % k)
        types = {h.get("type") for h in hist}
        # full-replacement amendments must keep BOTH the current and the original text
        if k in {"antiquities_heritage_art_%03d" % n for n in (3, 65, 71, 72, 73, 74, 75, 76, 77, 93)}:
            if "amendment_current" not in types or "original" not in types:
                e.append("[2h] %s: full-replacement amendment must carry both "
                         "amendment_current and original in history" % k)

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if src.get("verification_tier") != "TIER_3":
        e.append("[2d] verification_tier must be TIER_3")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record the founding M/3 decree + amendments)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        for tok in ("م/3", "م/67", "م/103", "693", "1012", "م/16"):
            if tok not in decrees:
                e.append("[2k] amendment_history must reference instrument %s" % tok)

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/3)" \
            or src.get("decree_date_hijri") != "9/1/1436":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/3, 9/1/1436H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this law carries 16 amended articles)")
    if not src.get("supersedes_ar") or "م/26" not in src.get("supersedes_ar", ""):
        e.append("[2j] supersedes_ar must record the named replacement of the older M/26 (1392H) Law")
    pre = src.get("preamble_ar", "")
    if not pre or not re.search(r"م\s*/\s*3\b", pre) or "348" not in pre:
        e.append("[2j] preamble_ar must be present and reference decree م/3 and CoM Resolution 348")

    art1 = arts.get("antiquities_heritage_art_001", {})
    if "يقصد بالألفاظ والعبارات" not in art1.get("text", "") \
            or "التراث العمراني" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions header / التراث العمراني term")
    # Article 71 must carry the M/67-amended penalty (six months .. seven years / 50k .. 500k)
    art71 = arts.get("antiquities_heritage_art_071", {})
    t71 = art71.get("text", "")
    if "(ستة) أشهر" not in t71 or "(سبع) سنوات" not in t71 or "(خمسين ألف)" not in t71:
        e.append("[2j] Article 71 must carry the M/67-amended penalty (ستة أشهر / سبع سنوات / خمسين ألف)")
    if art71.get("legal_status_ar") != "معدلة":
        e.append("[2j] Article 71 must be legal_status_ar=معدلة")
    # Article 92: the EXPLICIT NAMED repeal of the M/26 (1392H) predecessor law
    art92 = arts.get("antiquities_heritage_art_092", {})
    t92 = art92.get("text", "")
    if "يحل هذا النظام محل نظام الآثار" not in t92 or "م/26" not in t92 or "1392" not in t92:
        e.append("[2j] Article 92 must contain the explicit named repeal of نظام الآثار (م/26, 1392H)")
    # Article 94: effective 120 days after gazette publication
    art94 = arts.get("antiquities_heritage_art_094", {})
    if "مائة وعشرين" not in art94.get("text", "") or "الجريدة الرسمية" not in art94.get("text", ""):
        e.append("[2j] Article 94 missing expected 120-day effective-date clause")
    # Article 90: partial (para-1) amendment kept enacted body on top + note in history
    art90 = arts.get("antiquities_heritage_art_090", {})
    if art90.get("legal_status_ar") != "معدلة" or not art90.get("history"):
        e.append("[2j] Article 90 must be معدلة with an amendment note in history")

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
        if r.get("amendment_history") != a.get("history"):
            e.append("[4] %s: verified amendment_history != source history" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("chapter_structure") != []:
        e.append("[4b] summary chapter_structure must be []")

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
        print("FAIL: %d error(s) in Antiquities/Heritage Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Antiquities, Museums and Urban Heritage Law")
    print("       (نظام الآثار والمتاحف والتراث العمراني)")
    print("  - 94 records: 78 اصلية, 16 معدلة, 0 مضافة, 0 ملغاة")
    print("  - GENUINELY FLAT: no أبواب/فصول (chapter_structure [], section_ar empty) -- confirmed")
    print("    from two independent sources (nezams.com + a BOE-content print PDF)")
    print("  - Royal Decree M/3, 9/1/1436H (CoM Resolution 348, 25/8/1435H; Shura 194/78 & 67/38)")
    print("  - NAMED PREDECESSOR REPEAL: Article 92 explicitly replaces نظام الآثار (M/26, 23/6/1392H)")
    print("    and repeals all conflicting provisions")
    print("  - AMENDMENTS (never silently merged; pre-amendment text preserved in history):")
    print("      M/16 1439H -> Art 85 | CoM 693 1441H -> Arts 12/29/54 | M/67 1442H (=CoM 453) ->")
    print("      Arts 71-77 + Art 90(1) | M/103 1442H -> Art 3 | CoM 1012 1445H -> Arts 1/65/93")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa HAS a dedicated lawId page")
    print("    (a7d4493b-7c03-4c2d-b3c6-a9a700f275cd) but was unreachable this pass (HTTP 503 /")
    print("    connection reset), Wayback egress-blocked (not circumvented). Verbatim text from")
    print("    nezams.com (independent born-digital HTML aggregator); decree identity/preamble/")
    print("    named-repeal/original text corroborated by a BOE-content print PDF (unesco.org);")
    print("    M/67 amendment scope independently corroborated by the Umm Al-Qura Gazette.")
    print("  - Implementing Regulations (اللوائح, Article 93) exist and are a companion candidate,")
    print("    NOT ingested this pass (one-instrument-per-pass).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
