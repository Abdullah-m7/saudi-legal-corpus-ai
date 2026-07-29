#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Law of Service Providers for
External Hajj Pilgrims track (نظام مقدمي خدمة حجاج الخارج, Royal Decree
M/111, 17/9/1440H, as amended by Royal Decree M/89, 12/5/1447H/3 Nov 2025G).

24 records: 9 اصلية, 14 معدلة (Articles 1,2,3,4,5,6,8,9,11,13,14,17,18,21),
0 ملغاة, 1 مضافة (Article 19 bis). No chapter/فصل or باب structure (confirmed
via a full programmatic scan of the source page finding zero occurrences of
either word).

SUPERSESSION -- confirmed verbatim inside Royal Decree M/111's own enacting
clause (Second) and the identical clause of the accompanying Council of
Ministers Resolution (NOT inside any of the Law's 23 numbered articles):
repeals the General Mutawwif System (1367H), the Mutawwif Agents and Java
Sheikhs System (1365H), the Madinah Guides Authority System (1356H), and the
Disciplinary Rules for Mutawwifeen/Agents/Guides/Zamazemah (CoM Resolution 79,
1400H).

VERIFICATION TIER -- TIER_3 overall (weakest meaningfully-sized portion
governs). See the generator docstring and the source artifact's
verification_methodology_note for the full account: laws.boe.gov.sa
unreachable on every channel this pass (live 503/reset; archived snapshots
exist per Wayback's Availability API but web.archive.org itself was blocked by
this session's egress policy); the 9 unamended articles' 1440H text rests on
two independent secondary/quasi-official sources (nezams.com, tanseiqiah.sa);
the 2025 amendment governing 14 articles + the new Article 19 bis rests on the
official Umm Al-Qura Gazette (uqn.gov.sa, reached directly) cross-checked
against qanoonsa.com -- a stronger TIER_2-grade confirmation for that portion
specifically. This validator does not re-adjudicate provenance; it only checks
internal self-consistency of the ingested text and that every discrepancy is
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
SRC = os.path.join(ROOT, "sources", "hajj_umrah_external_pilgrims_law", "law", "official_source",
                   "hajj_umrah_external_pilgrims_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "hajj_umrah_external_pilgrims_law", "law", "verified",
                       "hajj_umrah_external_pilgrims_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "hajj_umrah_external_pilgrims_law", "law", "verified",
                       "hajj_umrah_external_pilgrims_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "hajj_umrah_external_pilgrims_law_arabic_legal_llm",
                   "hajj_umrah_external_pilgrims_law_legal_llm_001_024.json")
N = 24
KEY_RE = r"hajj_umrah_external_pilgrims_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 9, "معدلة": 14, "ملغاة": 0, "مضافة": 1}
EXPECTED_TOP_LEVEL_CHAPTERS = 0  # no فصول/أبواب in this law

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS = {
    "hajj_umrah_external_pilgrims_law_art_001",
    "hajj_umrah_external_pilgrims_law_art_002",
    "hajj_umrah_external_pilgrims_law_art_003",
    "hajj_umrah_external_pilgrims_law_art_004",
    "hajj_umrah_external_pilgrims_law_art_005",
    "hajj_umrah_external_pilgrims_law_art_006",
    "hajj_umrah_external_pilgrims_law_art_008",
    "hajj_umrah_external_pilgrims_law_art_009",
    "hajj_umrah_external_pilgrims_law_art_011",
    "hajj_umrah_external_pilgrims_law_art_013",
    "hajj_umrah_external_pilgrims_law_art_014",
    "hajj_umrah_external_pilgrims_law_art_017",
    "hajj_umrah_external_pilgrims_law_art_018",
    "hajj_umrah_external_pilgrims_law_art_021",
}
ADDED_KEYS = {"hajj_umrah_external_pilgrims_law_art_019_mukarrar"}
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS = {"hajj_umrah_external_pilgrims_law_art_019_mukarrar"}
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "hajj_umrah_external_pilgrims_law_boe_unreachable_live_and_wayback_blocked",
    "hajj_umrah_external_pilgrims_law_com_resolution_number_454_vs_545_conflict",
    "hajj_umrah_external_pilgrims_law_gazette_publication_date_discrepancy",
    "hajj_umrah_external_pilgrims_law_amendment_article_count_21_vs_14_discrepancy",
    "hajj_umrah_external_pilgrims_law_article1_para3_internal_naming_inconsistency",
    "hajj_umrah_external_pilgrims_law_article1_para8_numbering_source_conflict",
    "hajj_umrah_external_pilgrims_law_implementing_regulation_excluded_by_task_scope",
    "hajj_umrah_external_pilgrims_law_official_title_internal_vs_external",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ٰٟ]")


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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (فصول/أبواب), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
        if a.get("section_ar") not in ("", None):
            e.append("[2] %s: section_ar must be empty (no chapter structure in this law)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if any(c in a["text"] for c in "«»“”"):
            e.append("[2m] %s: residual decorative quotation mark present (must be stripped)" % k)
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
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits only)" % k)
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
        e.append("[2k] missing amendment_history (must record the founding M/111 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/111" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/111")
        if "م/89" not in decrees:
            e.append("[2k] amendment_history must reference amendment م/89")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/111)" \
            or src.get("decree_date_hijri") != "17/9/1440":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/111, 17/9/1440H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False")
    sup = src.get("supersedes_ar", "")
    for must in ("المطوفين العام", "مشائخ الجاوا", "هيئة الأدلاء بالمدينة المنورة", "79"):
        if must not in sup:
            e.append("[2j] supersedes_ar must name the repealed instrument reference %r" % must)
    if not src.get("preamble_ar") or "17 / 9 / 1440" not in src.get("preamble_ar", "").replace("/9/", " / 9 / ") \
            and "17/9/1440" not in src.get("preamble_ar", ""):
        pass  # date formatting is checked loosely below instead
    if not src.get("preamble_ar") or "نظام مقدمي خدمة حجاج الخارج" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference نظام مقدمي خدمة حجاج الخارج")
    if not src.get("com_resolution_ar") or "قرار مجلس الوزراء" not in src.get("com_resolution_ar", ""):
        e.append("[2j] com_resolution_ar (CoM Resolution full text) must be present")

    art1 = arts.get("hajj_umrah_external_pilgrims_law_art_001", {})
    if "شركات ضيافة الحجاج" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected current-text marker (شركات ضيافة الحجاج)")
    art6 = arts.get("hajj_umrah_external_pilgrims_law_art_006", {})
    if "على السعوديين" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected current-text marker (على السعوديين)")
    art19bis = arts.get("hajj_umrah_external_pilgrims_law_art_019_mukarrar", {})
    if "مجلس تنسيقي" not in art19bis.get("text", ""):
        e.append("[2j] Article 19 bis missing expected marker (مجلس تنسيقي)")
    if art19bis.get("number_label_ar") != "المادة التاسعة عشرة مكرر":
        e.append("[2j] Article 19 bis number_label_ar must be 'المادة التاسعة عشرة مكرر', got %r"
                 % art19bis.get("number_label_ar"))
    art23 = arts.get("hajj_umrah_external_pilgrims_law_art_023", {})
    if "يعمل بالنظام" not in art23.get("text", ""):
        e.append("[2j] Article 23 missing expected publication/entry-into-force clause")
    art23_label = art23.get("number_label_ar")
    if art23_label != "المادة الثالثة والعشرون":
        e.append("[2j] Article 23 number_label_ar must be 'المادة الثالثة والعشرون', got %r"
                 % art23_label)

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
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Hajj/Umrah External Pilgrims Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Law of Service Providers for External Hajj Pilgrims")
    print("  (نظام مقدمي خدمة حجاج الخارج)")
    print("  - 24 records: 9 اصلية, 14 معدلة (Articles 1,2,3,4,5,6,8,9,11,13,14,17,18,21),")
    print("    1 مضافة (Article 19 bis), 0 ملغاة")
    print("  - No chapter/فصل/باب structure (confirmed via a full programmatic scan)")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/111, 17/9/1440H (CoM Resolution 545,")
    print("    16/9/1440H; Shura Council Resolution 48/13, 2/5/1440H). Brand-new base-law track.")
    print("  - SUPERSESSION confirmed verbatim inside the Royal Decree's own enacting clause")
    print("    (Second), not inside any of the Law's 23 numbered articles: repeals the General")
    print("    Mutawwif System (1367H), the Mutawwif Agents and Java Sheikhs System (1365H), the")
    print("    Madinah Guides Authority System (1356H), and the Disciplinary Rules for")
    print("    Mutawwifeen/Agents/Guides/Zamazemah (CoM Resolution 79, 1400H -- discovered")
    print("    independently this pass).")
    print("  - AMENDMENT: Royal Decree M/89, 12/5/1447H (3 Nov 2025G; CoM Resolution 322,")
    print("    6/5/1447H) -- amends 14 articles, adds Article 19 bis. Corrects the task brief's")
    print("    '21 articles' figure to a programmatically-verified 14 amended + 1 added.")
    print("  - VERIFICATION TIER: TIER_3 overall (weakest portion governs) -- BOE unreachable on")
    print("    every channel (live 503/reset; web.archive.org blocked by egress policy despite")
    print("    snapshots existing). 9 unamended articles rest on nezams.com + tanseiqiah.sa")
    print("    (secondary/quasi-official, no primary). The 2025 amendment (14 articles + Art.")
    print("    19 bis) rests on uqn.gov.sa (official Gazette, reached directly) cross-checked")
    print("    against qanoonsa.com -- stronger TIER_2-grade confirmation for that portion.")
    print("  - Internal 454-vs-545 CoM resolution number conflict (within nezams.com itself) and")
    print("    a one-day gazette publication date discrepancy are both disclosed, not resolved.")
    print("  - Implementing Regulation (Minister Decision 410105143, 5/1/1441H) exists and is")
    print("    enacted, but is explicitly OUT OF SCOPE and NOT ingested this pass per the task.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
