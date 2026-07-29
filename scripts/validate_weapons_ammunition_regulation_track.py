#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Weapons and
Ammunition Law track (اللائحة التنفيذية لنظام الأسلحة والذخائر; 20 records:
7 اصلية [arts 1,13,15,20,21,22,27], 12 معدلة [arts 5,8,9,10,12,18,19,23,24,25,
28,32], 0 ملغاة, 1 مضافة [art 11]). The Regulation has NO independent article
numbering -- it is organized entirely as implementing text attached to the
PARENT LAW's own article numbers (20 of the Law's 63 articles carry attached
regulation text; the compiled primary source knows only 19 of them).

DECISION 26269 PASS -- Minister of Interior Decision 26269 (28/12/1444H), a
22-item "amend, add and merge" instrument gazetted 10/1/1445H (Umm al-Qura
issue 4991), was applied from the official gazette
(uqn.gov.sa/details?p=23358). It created the Article-11 regulation record
outright (item 16), so record_count moved 19 -> 20. This validator checks that
all 22 items are evidenced in the stored text ([2q]) and that every wording
they superseded still survives in history[] ([2r]) -- nothing deleted, only
superseded.

SOURCE-RELIABILITY (cross-cutting): the qadha.org.sa compiled PDF this track
was built on is STALE BY TWO DECISIONS despite carrying a 4/1/1446H cover
date -- it omits Decision 26269 (gazetted 10/1/1445H, i.e. more than two Hijri
years BEFORE that cover date) and Resolution 1938 (10/4/1446H). A cover date on
that source is NOT evidence of currency. [2t] enforces that this finding is
stated in the artifact's own verification_methodology_note.

VERIFICATION TIER -- see the generator's module docstring and
sources/weapons_ammunition_regulation/law/official_source/
weapons_ammunition_regulation_official_source.json's verification_methodology_note
for the full account: primary source (qadha.org.sa compiled PDF) has a
corrupted digital text layer requiring OCR-based recovery -> TIER_3. This
validator does not re-adjudicate provenance; it checks internal self-
consistency and that every disclosed discrepancy is still recorded.

MATERIAL FACTS checked: sparse law-article-number keying (not a dense 1..N
sequence); the 12 amended articles carry amendment_current history; Article 23
carries an additional amendment_pending entry (Resolution 549, explicitly
marked not-yet-effective by the source); Article 9's current text includes
both independently-discovered amendments (Decision 26269 and Resolution 1938);
Article 11's record is مضافة with empty history (it was created, not amended);
the amendment_history lists 26269 in strict chronological position (after 5656,
before 549); the founding 23-vs-33 conflict is RESOLVED at 23 and RELOCATED to
resolved_discrepancies with its original description and the gazette-preamble
evidence retained ([2p]) -- never deleted; and the fee-schedule-annex exclusion
plus the eight new Decision-26269 disclosures remain recorded as known
discrepancies.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "weapons_ammunition_regulation", "law", "official_source",
                   "weapons_ammunition_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "weapons_ammunition_regulation", "law", "verified",
                       "weapons_ammunition_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "weapons_ammunition_regulation", "law", "verified",
                       "weapons_ammunition_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "weapons_ammunition_regulation_arabic_legal_llm",
                   "weapons_ammunition_regulation_legal_llm_001_020.json")
N = 20
KEY_RE = r"weapons_ammunition_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 7, "معدلة": 12, "ملغاة": 0, "مضافة": 1}
EXPECTED_LAW_ARTICLE_NUMBERS = [1, 5, 8, 9, 10, 11, 12, 13, 15, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 32]

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
STATUS_AMENDED_PENDING = "AMENDED_PENDING_NOT_YET_EFFECTIVE"
AMENDED_KEYS = {
    "weapons_ammunition_regulation_art_005",
    "weapons_ammunition_regulation_art_008",
    "weapons_ammunition_regulation_art_009",
    "weapons_ammunition_regulation_art_010",
    "weapons_ammunition_regulation_art_012",
    "weapons_ammunition_regulation_art_018",
    "weapons_ammunition_regulation_art_019",
    "weapons_ammunition_regulation_art_023",
    "weapons_ammunition_regulation_art_024",
    "weapons_ammunition_regulation_art_025",
    "weapons_ammunition_regulation_art_028",
    "weapons_ammunition_regulation_art_032",
}
PENDING_KEYS = {"weapons_ammunition_regulation_art_023"}
ADDED_KEYS = {"weapons_ammunition_regulation_art_011"}
REPEALED_KEYS: set[str] = set()
# Resolved in the Decision-26269 pass and RELOCATED (not deleted) to
# src["resolved_discrepancies"] -- checked separately below.
RESOLVED_DISCREPANCY_KEYS = {
    "weapons_ammunition_regulation_founding_number_23_vs_33_internal_conflict",
}
FLAGGED_DISCREPANCY_KEYS = {
    "weapons_ammunition_regulation_ocr_corrupted_pdf_text_layer",
    "weapons_ammunition_regulation_res549_pending_not_yet_effective",
    "weapons_ammunition_regulation_res1938_discovered_not_in_prior_four",
    "weapons_ammunition_regulation_fee_schedule_annexes_out_of_scope",
    "weapons_ammunition_regulation_boe_portal_no_dedicated_page_found",
    "weapons_ammunition_regulation_no_preserved_pre_amendment_original_text",
    "weapons_ammunition_regulation_article_13_para_b_uncertain",
    "weapons_ammunition_regulation_19_of_63_law_articles_carry_regulation_text",
    "weapons_ammunition_regulation_article3_content_moved_to_article9",
    # --- Decision 26269 (28/12/1444H) pass ---
    "weapons_ammunition_regulation_qadha_pdf_stale_by_two_decisions",
    "weapons_ammunition_regulation_res26269_annexed_text_single_official_source",
    "weapons_ammunition_regulation_res26269_unnumbered_added_paragraphs",
    "weapons_ammunition_regulation_res26269_art9_merge_renumbering_unresolved",
    "weapons_ammunition_regulation_res26269_vs_res549_article23_numbering_conflict",
    "weapons_ammunition_regulation_res26269_training_condition_deferred_effect",
    "weapons_ammunition_regulation_res26269_article25_licence_duration_displaced",
    "weapons_ammunition_regulation_res1938_cites_superseded_9_11_title",
    "weapons_ammunition_regulation_article11_regulation_added_by_res26269",
}
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


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

    law_nums = sorted(int(a["law_article_number"]) for a in arts.values())
    if law_nums != EXPECTED_LAW_ARTICLE_NUMBERS:
        e.append("[1b] law_article_number set != expected sparse set: %s" % law_nums)

    if src.get("law_article_keys_with_regulation_text") != EXPECTED_LAW_ARTICLE_NUMBERS:
        e.append("[1c] law_article_keys_with_regulation_text mismatch")

    # article_key must encode the law_article_number it attaches to
    for k, a in arts.items():
        m = re.match(KEY_RE, k)
        if int(m.group(1)) != int(a["law_article_number"]):
            e.append("[1d] %s: key number != law_article_number field (%s)" % (k, a["law_article_number"]))

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
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
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
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if k in AMENDED_KEYS:
            hist = a.get("history") or []
            types = [h.get("type") for h in hist]
            if not any(t and t.startswith("amendment_current") for t in types):
                e.append("[2m] %s: amended history must include at least one amendment_current* entry" % k)
        if k in PENDING_KEYS:
            hist = a.get("history") or []
            if not any(h.get("type") == "amendment_pending" for h in hist):
                e.append("[2n] %s: expected an amendment_pending history entry (Resolution 549)" % k)

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
        for must in ("23", "3499", "274833", "5656", "26269", "549", "1938"):
            if must not in decrees:
                e.append("[2k] amendment_history must reference decree/resolution %r" % must)
        if len(ah) != 7:
            e.append("[2k] expected 7 amendment_history entries (founding + 6 amendments incl. the "
                     "two independently-discovered ones, Decision 26269 and Resolution 1938), "
                     "got %d" % len(ah))
        # 26269 must sit chronologically between 5656 (6/5/1442H) and 549 (4/2/1446H)
        order = [i for i, h in enumerate(ah)
                 for tag in ("5656", "26269", "549") if tag in str(h.get("decree", ""))]
        pos = {t: i for i, h in enumerate(ah) for t in ("5656", "26269", "549")
               if t in str(h.get("decree", ""))}
        if not (pos.get("5656", -1) < pos.get("26269", -1) < pos.get("549", 99)):
            e.append("[2k] amendment_history must list 26269 (28/12/1444H) chronologically after "
                     "5656 (6/5/1442H) and before 549 (4/2/1446H)")
        d26269 = next((h for h in ah if "26269" in str(h.get("decree", ""))), None)
        if d26269 is not None and d26269.get("date_hijri") != "28/12/1444":
            e.append("[2k] Decision 26269 date_hijri must be 28/12/1444, got %r"
                     % d26269.get("date_hijri"))

    res = src.get("resolved_discrepancies")
    if not res:
        e.append("[2p] missing resolved_discrepancies (the founding 23-vs-33 conflict was resolved "
                 "by gazette evidence and must be RELOCATED there, never deleted)")
    else:
        rkeys = {d["article_key"] for d in res}
        missing = RESOLVED_DISCREPANCY_KEYS - rkeys
        if missing:
            e.append("[2p] expected resolved_discrepancies entries missing for: %s" % sorted(missing))
        for d in res:
            if d.get("status") != "RESOLVED":
                e.append("[2p] %s: resolved_discrepancies entry must carry status RESOLVED"
                         % d["article_key"])
            if not d.get("original_description"):
                e.append("[2p] %s: resolved entry must retain its original_description "
                         "(nothing deleted, only relocated)" % d["article_key"])
            if "uqn.gov.sa/details?p=17351" not in str(d.get("resolution", "")):
                e.append("[2p] %s: resolution must cite the gazette-preamble evidence URL"
                         % d["article_key"])

    # spot-checks anchoring key facts
    art1 = arts.get("weapons_ammunition_regulation_art_001", {}).get("text", "")
    if "المسدسات" not in art1:
        e.append("[2j] Article 1's regulation missing expected weapon-types enumeration")
    art9 = arts.get("weapons_ammunition_regulation_art_009", {}).get("text", "")
    if "اجتياز الفحص الطبي الخاص بالسموم" not in art9:
        e.append("[2j] Article 9's regulation missing the independently-discovered Resolution 1938 clause")
    if "خمسمئة ألف ريال" not in art9:
        e.append("[2j] Article 9's regulation missing expected bank-guarantee amount")
    art12 = arts.get("weapons_ammunition_regulation_art_012", {}).get("text", "")
    if "اللجنة الدائمة" not in art12:
        e.append("[2j] Article 12's regulation missing expected Standing Committee provisions")
    art23 = arts.get("weapons_ammunition_regulation_art_023", {}).get("text", "")
    if "يسر بعد" not in art23:
        e.append("[2j] Article 23's regulation missing the disclosed not-yet-effective caveat for Resolution 549")

    # ---- Decision 26269 (28/12/1444H): every one of the 22 items must be evidenced ----
    art5 = arts.get("weapons_ammunition_regulation_art_005", {}).get("text", "")
    art10 = arts.get("weapons_ammunition_regulation_art_010", {}).get("text", "")
    art11 = arts.get("weapons_ammunition_regulation_art_011", {}).get("text", "")
    art25 = arts.get("weapons_ammunition_regulation_art_025", {}).get("text", "")
    art28 = arts.get("weapons_ammunition_regulation_art_028", {}).get("text", "")
    ITEM_PROBES = [
        (1,  art5,  "وتجدد اعتبارا من تاريخ انتهائها وفق شروط وإجراءات منحها"),
        (2,  art9,  "لإصدار الرخصة بعد سداد الرسوم المقررة"),
        (3,  art9,  "يجوز إنشاء فروع ضمن حدود المدن والمحافظات الواقع بها الفرع الرئيسي"),
        (4,  art9,  "9/3: إجراءات طلب استيراد الأسلحة النارية الفردية وأسلحة الصيد والبنادق الهوائية"),
        (5,  art9,  "وبيعها في الفعاليات المقامة"),
        (6,  art9,  "المسموح باستيرادها أو شرائها"),
        (7,  art9,  "بالتفتيش الدوري والمفاجئ وضبط المخالفات"),
        (8,  art9,  "ورخصة مدرب رماية ورخصة مأمور حفظ وتخزين أسلحة ورخصة فني صيانة أسلحة"),
        (9,  art9,  "الحصول على الدورة التدريبية اللازمة مع مراعاة ما يلي"),
        (10, art9,  "شروط وإجراءات الحصول على رخصة ممارسة نشاط التدريب"),
        (11, art9,  "أضيفت هذه الفقرة إلى البند (9/12)"),
        (12, art10, "أضيفت هذه الفقرة إلى البند (10/2)"),
        (13, art10, "وإصدار رخص الحيازة الخاصة بها وتجديدها بعد سداد الرسوم المالية المقررة"),
        (14, art10, "بإعداد آلية لتداول الأسلحة والذخائر بين منسوبيها"),
        (15, art10, "وإصدار الشهادات للمتدربين المجتازين"),
        (16, art11, "يصدر الترخيص بعد استحصال الرسوم المالية المقررة، وبعد موافقة الوزير"),
        (17, art12, "يصدر الترخيص من الوزير بعد سداد الرسوم المقررة"),
        (18, art12, "يتم استحصال رسم تسجيل أمني عند كل زيارة"),
        (19, art12, "تصنف فئات الأندية وفقا لما يلي"),
        (20, art23, "إصدار رخصة تنقل (مؤقت) بالسلاح"),
        (21, art25, "يتم استحصال رسوم إصدار وتجديد الرخص والتصريح الواردة في الجدول الملحق بالنظام"),
        (22, art28, "لإصدار الرخصة بعد سداد الرسوم المالية المقررة"),
    ]
    for num, blob, probe in ITEM_PROBES:
        if probe not in blob:
            e.append("[2q] Decision 26269 item %d not evidenced in the stored text (probe %r)"
                     % (num, probe[:48]))

    # superseded wordings must survive in history[] -- nothing deleted, only superseded
    PRESERVED = [
        ("weapons_ammunition_regulation_art_005",
         "لإصدار الرخصة وتجدد متى ما التزم المرخص له بالشروط الواجبة لمنحها"),
        ("weapons_ammunition_regulation_art_009", "9/4: إجراءات طلب استيراد قطع غيار الأسلحة"),
        ("weapons_ammunition_regulation_art_010",
         "تصدر الجهة المستفيدة تصاريح خاصة لحمل الأسلحة لمنسوبيها"),
        ("weapons_ammunition_regulation_art_012", "سداد الرسوم المالية اللازمة لممارسة النشاط"),
        ("weapons_ammunition_regulation_art_025", "مدة سريان رخص حمل أو اقتناء الأسلحة النارية"),
        ("weapons_ammunition_regulation_art_028",
         "بعد استكمال الإجراءات يرفع الطلب إلى الإدارة العامة"),
    ]
    for k, probe in PRESERVED:
        blob = " ".join(h.get("text", "") for h in (arts.get(k, {}).get("history") or []))
        if probe not in blob:
            e.append("[2r] %s: superseded wording not preserved in history[] (probe %r)"
                     % (k, probe[:48]))

    # the new Article-11 record must be an ADDED record with no invented amendment history
    a11 = arts.get("weapons_ammunition_regulation_art_011")
    if a11 is None:
        e.append("[2s] missing the Article-11 regulation record added by Decision 26269 item 16")
    elif a11.get("legal_status_ar") != "مضافة":
        e.append("[2s] Article 11's regulation must be legal_status_ar=مضافة")

    # the cross-cutting source-reliability finding must be stated in the methodology note itself
    meth = src.get("verification_methodology_note", "")
    for probe in ("qadha.org.sa", "4/1/1446", "26269"):
        if probe not in meth:
            e.append("[2t] verification_methodology_note must state the source-staleness finding "
                     "(missing %r)" % probe)

    if src.get("decree") != "القرار الوزاري رقم 23" or src.get("decree_date_hijri") != "19/1/1428":
        e.append("[2j] decree/decree_date_hijri mismatch with Ministerial Resolution 23, 19/1/1428H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (amendments incorporated)")
    if src.get("parent_law_key") != "weapons_ammunition":
        e.append("[2j] parent_law_key must reference weapons_ammunition")

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
        print("FAIL: %d error(s) in Weapons and Ammunition Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Weapons and Ammunition Law (اللائحة التنفيذية لنظام الأسلحة والذخائر)")
    print("  - 20 records (sparse law-article keys 1,5,8,9,10,11,12,13,15,18,19,20,21,22,23,24,25,27,28,32):")
    print("    7 اصلية, 12 معدلة, 0 ملغاة, 1 مضافة (art 11)")
    print("  - VERIFICATION TIER: TIER_3 -- primary source (qadha.org.sa compiled PDF) has a corrupted")
    print("    digital text layer requiring OCR-based recovery; cross-checked against qanoonsa.com and")
    print("    uqn.gov.sa (issuance facts + two amendments the compiled PDF omits entirely)")
    print("  - Ministerial Resolution 23 (19/1/1428H) -- the 23-vs-33 source conflict is RESOLVED at 23")
    print("    by an independent gazette preamble (uqn.gov.sa/details?p=17351); the 33 variant is")
    print("    retained in resolved_discrepancies as a documented defect, not deleted")
    print("  - AMENDMENT CHAIN: 3499 (1434H, superseded), 274833 (1437H), 5656 (1442H, broad),")
    print("    Decision 26269 (28/12/1444H, 22 items, gazette issue 4991 -- ABSENT from the compiled")
    print("    PDF), 549 (1446H, marked NOT YET EFFECTIVE by the source itself), and Resolution 1938")
    print("    (1446H, also absent from the compiled PDF)")
    print("  - SOURCE-RELIABILITY: the qadha.org.sa compiled PDF is STALE BY TWO DECISIONS despite its")
    print("    4/1/1446H cover date (it omits 26269, gazetted 10/1/1445H -- over two Hijri years")
    print("    BEFORE that cover date -- and 1938). Its cover date is NOT evidence of currency.")
    print("  - DISCLOSED GAPS from Decision 26269: 7 added paragraphs whose clause numbers the")
    print("    decision never states; the fate of 9/4, 9/5 and any cascade renumbering after the")
    print("    item-4 merge; the 23/3 numbering collision with Resolution 549; the deferred-effect")
    print("    training condition; and the licence-duration provisions displaced from article 25")
    print("  - Follow-up candidates NOT ingested: fee-schedule annexes (tables 1 & 2)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
