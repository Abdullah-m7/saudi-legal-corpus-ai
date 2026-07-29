#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Copyright Law track (نظام حقوق
المؤلف, Royal Decree M/169, 14/8/1447H, approving CoM Resolution 560,
8/8/1447H; Umm Al-Qura Year 104 Issue 5144, 25/8/1447H = 13 February 2026,
pp. 13-17).

61 records: 61 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة. NO chapter/فصل structure --
a directly numbered law running flat from Article 1 to Article 61.

This validator exists to make four specific failure modes impossible to ship
silently, on top of the usual structural/self-consistency checks:

  [A] NOT-YET-IN-FORCE must stay recorded. Article 61 defers operation 180
      days from gazette publication. 13 Feb 2026 + 180 d = 2026-08-12, and
      the build date (2026-07-29) is 166 days in, so the Law is NOT in force.
      The validator recomputes the arithmetic from stored dates rather than
      trusting the stored answer, and rejects a track that claims otherwise.

  [B] THE ONE-DAY AMBIGUITY must stay DISCLOSED, not silently resolved.
      «بعد (مائة وثمانين) يوما» admits both 2026-08-12 and 2026-08-13. The
      artifact must store BOTH candidates and in_force_date_resolved must be
      false. A single asserted effective date is a validation failure. The
      unsupported 2026-08-01 figure is rejected outright wherever it appears.

  [C] THE DECREE-CLAUSE TRAP. Clause SECOND of Royal Decree M/169 is a
      substantive foreign-reciprocity rule with no numbered article of its
      own. It must be present at decree level (preamble_ar AND
      decree_clauses_outside_articles, flagged substantive) and must NOT have
      leaked into any of the 61 article records. Both directions are checked.

  [D] THE REPEAL'S LOCATION. The repeal of M/41 must sit inside Article 59 --
      a numbered article of the Law -- and must NOT appear in the enacting
      decree's clauses. Both directions are checked, because this corpus's
      supersession graph depends on the distinction. Article 24 must retain
      the reference that keeps the predecessor `copyright` track necessary.

VERIFICATION TIER -- TIER_1_PRIMARY_MULTI_SOURCE. See the generator docstring
and the source artifact's verification_methodology_note. This validator does
not re-adjudicate provenance; it checks internal self-consistency of the
ingested text and that every disclosure is still recorded.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "copyright_law_1447", "law", "official_source",
                   "copyright_law_1447_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "copyright_law_1447", "law", "verified",
                       "copyright_law_1447_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "copyright_law_1447", "law", "verified",
                       "copyright_law_1447_verified_summary.json")
LLM = os.path.join(ROOT, "data", "copyright_law_1447_arabic_legal_llm",
                   "copyright_law_1447_legal_llm_001_061.json")
N = 61
KEY_RE = r"copyright_law_1447_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 61, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 0  # no فصول in this law

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED

FLAGGED_DISCREPANCY_KEYS = {
    "copyright_law_1447_not_yet_in_force_at_build",
    "copyright_law_1447_entry_into_force_day_ambiguity_unresolved",
    "copyright_law_1447_royal_decree_clause_thanian_outside_articles",
    "copyright_law_1447_repeal_inside_article_59_not_decree",
    "copyright_law_1447_article_24_keeps_predecessor_m41_relevant",
    "copyright_law_1447_qanoonsa_article_59_date_order_cosmetic",
    "copyright_law_1447_decree_line_breaks_are_structural_not_textual",
    "copyright_law_1447_no_chapter_structure",
    "copyright_law_1447_implementing_regulation_not_yet_issued",
    "copyright_law_1447_gregorian_dates_of_decree_and_resolution_uncomputed",
    "copyright_law_1447_boe_unreachable_and_saip_does_not_list_it",
}

PUBLICATION = datetime.date(2026, 2, 13)
DEFERRAL_DAYS = 180
BUILD_DATE = datetime.date(2026, 7, 29)
BAD_EFFECTIVE_DATE = "2026-08-01"   # unsupported by any clause; must never reappear
# distinctive fragment of Royal Decree M/169 clause SECOND (foreign reciprocity)
DECREE_CLAUSE2_MARKER = "لا تحمي مواطني المملكة بموجب الاتفاقيات والمعاهدات الدولية"

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

    # ---------------------------------------------------------------- [1] structure
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)
    expected_keys = {"copyright_law_1447_art_%03d" % i for i in range(1, N + 1)}
    missing = expected_keys - set(arts)
    if missing:
        e.append("[1] missing article keys (no gaps allowed): %s" % sorted(missing)[:6])

    chs = src.get("chapter_structure") or []
    if len(chs) != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (فصول), got %d"
                 % (EXPECTED_TOP_LEVEL_CHAPTERS, len(chs)))

    # ---------------------------------------------------------------- [2] per-article
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
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if a.get("section_ar"):
            e.append("[2] %s: section_ar must be empty (this law has no فصول)" % k)
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
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (this track normalizes to Western)" % k)
        if re.search(r"[یکے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh)" % k)
        if "‏" in a["text"] or "‎" in a["text"]:
            e.append("[2g] %s: residual RLM/LRM directional-mark artifact detected" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    # ---------------------------------------------------------------- [3] disclosures
    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    else:
        vmn = src["verification_methodology_note"]
        if "TIER_1_PRIMARY_MULTI_SOURCE" not in vmn:
            e.append("[2d] verification_methodology_note must state the assigned tier verbatim")
        for probe in ("uqn.gov.sa", "5144", "qanoonsa.com", "laws.boe.gov.sa", "saip.gov.sa"):
            if probe not in vmn:
                e.append("[2d] verification_methodology_note must document source %r" % probe)
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        miss = FLAGGED_DISCREPANCY_KEYS - flagged
        if miss:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(miss))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record the founding M/169 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/169" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/169")

    # ---------------------------------------------------------------- [3b] citation chain
    if src.get("decree") != "المرسوم الملكي رقم (م/169)" \
            or src.get("decree_date_hijri") != "14/8/1447":
        e.append("[3b] decree/decree_date_hijri mismatch with verified Royal Decree M/169, "
                 "14/8/1447H")
    com = src.get("council_of_ministers_decision", "")
    if "560" not in com or "8/8/1447" not in com:
        e.append("[3b] council_of_ministers_decision must cite CoM Resolution 560, 8/8/1447H")
    gaz = src.get("gazette_publication_hijri", "")
    for probe in ("5144", "104", "25/8/1447"):
        if probe not in gaz:
            e.append("[3b] gazette_publication_hijri must record %r (Year 104, Issue 5144, "
                     "25/8/1447H)" % probe)
    if src.get("gazette_publication_gregorian") != "13/2/2026":
        e.append("[3b] gazette_publication_gregorian must be 13/2/2026")
    if src.get("document") != "نظام حقوق المؤلف":
        e.append("[3b] document title must be نظام حقوق المؤلف (the new title DROPS حماية)")
    if "حماية" in (src.get("document") or ""):
        e.append("[3b] document title must NOT contain حماية -- that is the predecessor M/41 "
                 "title (نظام حماية حقوق المؤلف); the new law drops it")
    if src.get("consolidated_amended_law") is not False:
        e.append("[3b] consolidated_amended_law must be False")

    # ---------------------------------------------------------------- [A] not yet in force
    eif = src.get("entry_into_force") or {}
    if not eif:
        e.append("[A] missing entry_into_force block")
    else:
        try:
            pub = datetime.date.fromisoformat(eif.get("publication_date_gregorian", ""))
        except ValueError:
            pub = None
            e.append("[A] entry_into_force.publication_date_gregorian missing/unparseable")
        if pub is not None and pub != PUBLICATION:
            e.append("[A] publication_date_gregorian %s != verified gazette date %s"
                     % (pub, PUBLICATION))
        if eif.get("deferral_days") != DEFERRAL_DAYS:
            e.append("[A] deferral_days must be %d per Article 61" % DEFERRAL_DAYS)
        if pub is not None:
            recomputed = pub + datetime.timedelta(days=DEFERRAL_DAYS)
            if eif.get("computed_day_180_gregorian") != recomputed.isoformat():
                e.append("[A] computed_day_180_gregorian %r != recomputed %s (arithmetic must "
                         "be reproducible from the stored publication date, not asserted)"
                         % (eif.get("computed_day_180_gregorian"), recomputed))
        if src.get("in_force_as_of_build_date") is not False:
            e.append("[A] in_force_as_of_build_date must be False -- the Law was not in force "
                     "at the 2026-07-29 build date")
        if eif.get("in_force_at_build") is not False:
            e.append("[A] entry_into_force.in_force_at_build must be False")
        try:
            bd = datetime.date.fromisoformat(eif.get("track_build_date_gregorian", ""))
        except ValueError:
            bd = None
            e.append("[A] entry_into_force.track_build_date_gregorian missing/unparseable")
        if bd is not None and pub is not None:
            if eif.get("days_elapsed_at_build") != (bd - pub).days:
                e.append("[A] days_elapsed_at_build %r != recomputed %d"
                         % (eif.get("days_elapsed_at_build"), (bd - pub).days))
            if (bd - pub).days >= DEFERRAL_DAYS and eif.get("in_force_at_build") is False:
                e.append("[A] inconsistent: %d days elapsed >= %d yet in_force_at_build is "
                         "False -- rebuild the track and re-assess"
                         % ((bd - pub).days, DEFERRAL_DAYS))
        art61 = arts.get("copyright_law_1447_art_061", {})
        if eif.get("governing_article_text_ar") != art61.get("text"):
            e.append("[A] entry_into_force.governing_article_text_ar must be Article 61 verbatim")

    # ---------------------------------------------------------------- [B] ambiguity disclosed
    cands = (eif or {}).get("in_force_date_candidates_gregorian")
    if cands != ["2026-08-12", "2026-08-13"]:
        e.append("[B] in_force_date_candidates_gregorian must disclose BOTH readings of «بعد» "
                 "as ['2026-08-12', '2026-08-13'], got %r" % (cands,))
    if (eif or {}).get("in_force_date_resolved") is not False:
        e.append("[B] in_force_date_resolved must be False -- no source reached this pass "
                 "settles the inclusive/exclusive reading; it must not be silently resolved")
    if not (eif or {}).get("ambiguity_note_ar"):
        e.append("[B] entry_into_force.ambiguity_note_ar must explain the undecided one-day gap")
    if (eif or {}).get("in_force_date_gregorian"):
        e.append("[B] a single scalar in_force_date_gregorian must NOT be asserted while the "
                 "reading is unresolved -- use the candidate range")
    blob = json.dumps(src, ensure_ascii=False)
    if BAD_EFFECTIVE_DATE in blob:
        idx = blob.find(BAD_EFFECTIVE_DATE)
        ctx = blob[max(0, idx - 60):idx + 60]
        if "غير مستمد" not in ctx and "يجب ألا" not in ctx and "لا يجب" not in ctx:
            e.append("[B] the unsupported effective date %s appears without being explicitly "
                     "repudiated -- it is not derivable from any clause of the instrument"
                     % BAD_EFFECTIVE_DATE)

    # ---------------------------------------------------------------- [C] decree-clause trap
    preamble = src.get("preamble_ar", "")
    if not preamble:
        e.append("[C] preamble_ar (Royal Decree M/169 verbatim) is missing")
    else:
        for probe in ("بعون الله تعالى", "رسمنا بما هو آت", "أولا:", "ثانيا:", "ثالثا:"):
            if probe not in preamble:
                e.append("[C] preamble_ar missing expected decree component %r" % probe)
        if DECREE_CLAUSE2_MARKER not in preamble:
            e.append("[C] preamble_ar must carry Royal Decree clause SECOND (the substantive "
                     "foreign-reciprocity restriction) verbatim")
    dcl = src.get("decree_clauses_outside_articles")
    if not dcl or len(dcl) != 3:
        e.append("[C] decree_clauses_outside_articles must record all 3 decree clauses, got %r"
                 % (len(dcl) if dcl else None))
    else:
        labels = [c.get("clause_label_ar") for c in dcl]
        if labels != ["أولا", "ثانيا", "ثالثا"]:
            e.append("[C] decree clause labels must be ['أولا','ثانيا','ثالثا'], got %r" % labels)
        second = dcl[1]
        if DECREE_CLAUSE2_MARKER not in second.get("text", ""):
            e.append("[C] decree clause ثانيا text is not the verbatim reciprocity restriction")
        if second.get("is_substantive_rule") is not True:
            e.append("[C] decree clause ثانيا must be flagged is_substantive_rule=True -- it is "
                     "a live rule, not boilerplate")
        if second.get("has_corresponding_numbered_article") is not False:
            e.append("[C] decree clause ثانيا must be flagged "
                     "has_corresponding_numbered_article=False")
        if not second.get("note"):
            e.append("[C] decree clause ثانيا must carry a note explaining the ingestion trap")
        for c in dcl:
            if c.get("has_corresponding_numbered_article") is not False:
                e.append("[C] decree clause %r wrongly claims a corresponding numbered article"
                         % c.get("clause_label_ar"))
    # the trap's other half: decree-level content must not have leaked into article records
    for k, a in arts.items():
        if DECREE_CLAUSE2_MARKER in a["text"]:
            e.append("[C] %s: Royal Decree clause SECOND has leaked into an ARTICLE record -- "
                     "decree-level content must stay out of the 61 numbered articles" % k)
        if "رسمنا بما هو آت" in a["text"] or "بعون الله تعالى" in a["text"]:
            e.append("[C] %s: enacting-decree preamble text has leaked into an article" % k)
    if not src.get("com_resolution_ar"):
        e.append("[C] com_resolution_ar (CoM Resolution 560 verbatim) is missing")
    else:
        cr = src["com_resolution_ar"]
        if "قرار رقم (560)" not in cr or "عاشرا:" not in cr:
            e.append("[C] com_resolution_ar must be the verbatim Resolution 560 including its "
                     "tenth clause (عاشرا), the source of decree clause ثانيا")

    # ---------------------------------------------------------------- [D] repeal location
    art59 = arts.get("copyright_law_1447_art_059", {})
    if "يحل النظام محل" not in art59.get("text", "") \
            or "نظام حماية حقوق المؤلف" not in art59.get("text", "") \
            or "م/41" not in art59.get("text", "") \
            or "1424/7/2" not in art59.get("text", "") \
            or "ويلغي كل ما يتعارض معه من أحكام" not in art59.get("text", ""):
        e.append("[D] Article 59 must carry the verbatim repeal of نظام حماية حقوق المؤلف "
                 "(م/41، 1424/7/2هـ) including the residual implied-repeal sweep")
    if art59.get("number_label_ar") != "المادة التاسعة والخمسون":
        e.append("[D] Article 59 number_label_ar must be 'المادة التاسعة والخمسون', got %r"
                 % art59.get("number_label_ar"))
    # the repeal must live in the LAW, not in the enacting instruments
    if "يحل النظام محل" in preamble or "م/41" in preamble:
        e.append("[D] the enacting decree (preamble_ar) must NOT contain repeal language -- "
                 "this corpus's supersession graph depends on the repeal being carried by "
                 "Article 59 of the enacted text")
    for k, a in arts.items():
        if k != "copyright_law_1447_art_059" and "يحل النظام محل" in a["text"]:
            e.append("[D] %s: repeal clause must appear only in Article 59" % k)
    sup = src.get("supersedes_ar", "")
    if not sup or "م/41" not in sup or "المادة التاسعة والخمسين" not in sup:
        e.append("[D] supersedes_ar must name the repealed instrument (م/41) and anchor the "
                 "repeal to Article 59 of this Law's own text")
    # Article 24 keeps the predecessor track necessary
    art24 = arts.get("copyright_law_1447_art_024", {})
    if "نظام حماية حقوق المؤلف السابق" not in art24.get("text", "") \
            or "قبل بدء سريان هذا النظام" not in art24.get("text", ""):
        e.append("[D] Article 24 must retain the transitional reference to the predecessor law "
                 "-- it is why the `copyright` (M/41) track must not be deleted")
    art61 = arts.get("copyright_law_1447_art_061", {})
    if "مائة وثمانين" not in art61.get("text", "") \
            or "الجريدة الرسمية" not in art61.get("text", ""):
        e.append("[D] Article 61 must carry the verbatim 180-day entry-into-force clause")
    if art61.get("number_label_ar") != "المادة الحادية والستون":
        e.append("[D] Article 61 number_label_ar must be 'المادة الحادية والستون', got %r"
                 % art61.get("number_label_ar"))
    if "يحل النظام محل" in art61.get("text", ""):
        e.append("[D] Article 61 must NOT contain the repeal clause -- it lives in Article 59")
    art60 = arts.get("copyright_law_1447_art_060", {})
    if "اللائحة" not in art60.get("text", "") or "مائة وثمانين" not in art60.get("text", ""):
        e.append("[D] Article 60 must carry the verbatim implementing-regulation mandate")
    art1 = arts.get("copyright_law_1447_art_001", {})
    if "النظام: نظام حقوق المؤلف." not in art1.get("text", "") \
            or "الهيئة: الهيئة السعودية للملكية الفكرية." not in art1.get("text", ""):
        e.append("[D] Article 1 missing expected definitions (النظام self-designation / الهيئة)")

    # ---------------------------------------------------------------- [4] verified records
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
        if r.get("in_force_at_record_build") is not False:
            e.append("[4] %s: record must carry in_force_at_record_build=False"
                     % r["article_key"])
        if r.get("in_force_date_resolved") is not False:
            e.append("[4] %s: record must carry in_force_date_resolved=False" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("in_force_as_of_build_date") is not False:
        e.append("[4b] summary must carry in_force_as_of_build_date=False")
    if summary.get("entry_into_force") != eif:
        e.append("[4b] summary entry_into_force != source entry_into_force")
    if summary.get("predecessor_track_key") != "copyright":
        e.append("[4b] summary must name the predecessor track key `copyright`")
    if summary.get("predecessor_must_not_be_deleted") is not True:
        e.append("[4b] summary must assert predecessor_must_not_be_deleted=True (Article 24)")
    if summary.get("decree_clauses_outside_articles") != dcl:
        e.append("[4b] summary decree_clauses_outside_articles != source")

    # ---------------------------------------------------------------- [5] LLM layer
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("article_range") != [1, N]:
        e.append("[5] llm article_range must be [1, %d]" % N)
    if llm.get("in_force_as_of_build_date") is not False:
        e.append("[5] llm layer must carry in_force_as_of_build_date=False")
    if llm.get("decree_clauses_outside_articles") != dcl:
        e.append("[5] llm layer must carry the decree clauses so downstream consumers of the "
                 "LLM layer alone still see the non-article rule")
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
        if r.get("in_force_at_record_build") is not False:
            e.append("[5] %s: llm record must carry in_force_at_record_build=False"
                     % r["article_key"])
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust"
                     % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Copyright Law (M/169, 1447H) track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Copyright Law (نظام حقوق المؤلف)")
    print("  - 61 records: 61 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة")
    print("  - NO chapter (فصول) structure -- a flat, directly-numbered 61-article law")
    print("  - TITLE: نظام حقوق المؤلف -- the new title DROPS «حماية» relative to the")
    print("    predecessor نظام حماية حقوق المؤلف (M/41). Distinct track, distinct key.")
    print("  - CITATION CHAIN CONFIRMED: Royal Decree M/169, 14/8/1447H, approving CoM")
    print("    Resolution 560, 8/8/1447H (Shura Resolutions 305/30 of 21/11/1446H and")
    print("    121/11 of 10/6/1447H). Umm Al-Qura Year 104, Issue 5144, Friday 25 Sha'ban")
    print("    1447H = 13 February 2026, pages 13-17.")
    print("  - *** NOT YET IN FORCE at the 2026-07-29 build date ***: Article 61 defers")
    print("    operation 180 days from publication. 2026-02-13 + 180 d = 2026-08-12;")
    print("    166 of 180 days had elapsed at build. The one-day «بعد» ambiguity is")
    print("    DISCLOSED as the candidate range [2026-08-12, 2026-08-13] with")
    print("    in_force_date_resolved=False -- deliberately NOT silently resolved.")
    print("    (The previously circulating 2026-08-01 figure is unsupported by any clause.)")
    print("  - REPEAL LOCATION: Article 59 -- a NUMBERED ARTICLE of the Law itself, NOT a")
    print("    clause of the enacting decree -- replaces M/41 (2/7/1424H) by name and date.")
    print("    Neither Royal Decree M/169's three clauses nor CoM Resolution 560's ten")
    print("    contain any repeal language. Verified in both directions.")
    print("  - DECREE-CLAUSE TRAP GUARDED: clause SECOND of Royal Decree M/169 carries a")
    print("    substantive foreign-reciprocity restriction with NO numbered article of its")
    print("    own. It is captured at decree level (preamble_ar +")
    print("    decree_clauses_outside_articles, flagged substantive) and is confirmed ABSENT")
    print("    from all 61 article records. An ingestion reading only Articles 1-61 drops it.")
    print("  - PREDECESSOR PRESERVED: Article 24 keeps M/41 necessary for protection terms")
    print("    accrued before cutover, so the existing 28-article `copyright` track is a")
    print("    permanent dependency and must not be deleted. Untouched by this pass.")
    print("  - VERIFICATION TIER: TIER_1_PRIMARY_MULTI_SOURCE -- the Umm Al-Qura portal's")
    print("    server-rendered pages (the Law, the Decree, the Resolution) against the")
    print("    official gazette PDF for issue 5144, the latter verified via independently")
    print("    rendered page images (pp. 13, 17) rather than its ligature-damaged pdftotext")
    print("    output; plus a secondary cross-check against qanoonsa.com (60/61 exact, the")
    print("    61st differing only in date-component ordering). Both official legs share one")
    print("    publisher -- disclosed in the source artifact so a reviewer may downgrade.")
    print("    laws.boe.gov.sa reset the connection on both attempts; saip.gov.sa WAS")
    print("    reachable but its full 18-document legislation list does not carry this Law")
    print("    at all, still listing only M/41. Re-verify against both after 2026-08-12.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
