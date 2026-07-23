#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Agriculture Law track (نظام الزراعة, Royal Decree
M/64, 10/8/1442H -- the currently in-force Agriculture Law, administered sector-wise
by the Ministry of Environment, Water and Agriculture (MEWA)).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus (it is
not a companion regulation to an already-ingested law). It was built from scratch
this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام الزراعة is a single, self-standing
Royal-Decree law (M/64, 10/8/1442H), confirmed via cross-checked independent
signals: (1) laws.boe.gov.sa carries it under its own dedicated lawId
d113fa79-5ad8-42b1-9955-acfb00a2c7ed (seen via WebSearch); (2) the official English
reference published by MISA (misa.gov.sa/app/uploads/2025/07/Agriculture-Law.pdf)
confirms "Royal Decree No. M/64", the 37-article count, and the absence of any
chapter/part divisions; (3) nezams.com lists status "ساري" (in force) with "لم يجرى
عليه تعديل" (no amendments); (4) MEWA/Umm Al-Qura/qanoonsa confirm the decree and the
existence of its Implementing Regulation.

SUPERSESSION -- unlike the Electricity Law (whose repeal clause sits inside its
Article 23), this Law's repeal sits in its ISSUING DECREE (clause Second of Royal
Decree M/64 and of Council of Ministers Resolution 431), NOT inside any of the 37
articles. By that clause the Law repeals FIVE named earlier instruments after it
takes effect: the Living Aquatic Resources Law (M/9, 1408H), the Animal Resources
Law (M/13, 1424H), the Beekeeping Law (M/15, 1431H), the Organic Agriculture Law
(M/55, 1435H), and the Council of Ministers Rules for Trading in Agricultural
Machinery (No. 96, 1405H), plus any conflicting provisions. Recorded in supersedes_ar
and preamble_ar; needed later for the corpus-wide supersession graph (not touched
here).

VERIFICATION TIER -- TIER_3. laws.boe.gov.sa (this corpus's usual PRIMARY source)
was checked FIRST per standard methodology but is unreachable this pass (WebFetch:
HTTP 503) -- matching the documented pattern for other tracks in the same period.
Wayback (web.archive.org) is egress-blocked and was NOT circumvented. The full
verbatim Arabic text of all 37 articles was extracted from ONE full-text aggregator,
nezams.com (a clean born-digital HTML page, HTTP 200 -- no scan/OCR/ligature
defects). Every governing metadata fact and the flat 37-article structure are
independently cross-verified (most notably by the official MISA English PDF, which
confirms M/64, the 37-article count, and the no-chapter structure). A follow-up
re-verification of the verbatim text against laws.boe.gov.sa is recommended once
reachable.

37 articles, no chapter divisions (flat); all 37 اصلية; 0 معدلة, 0 ملغاة, 0 مضافة
(the Law has had no amendments). Diacritics (tashkeel) and decorative kashida are
stripped uniformly for consistency with this corpus's other BOE-family tracks; two
Farsi-yeh characters (Articles 23 and 35) are normalized to Arabic yeh. Disclosed
source-rendering quirks (mixed Arabic-Indic/Western digits, the Article-19 label
missing its taa marbuta, a glued "محققا للمصلحة العامة" in the decree) are preserved
verbatim, not silently fixed. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "agriculture", "law", "official_source",
                   "agriculture_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "agriculture", "law", "verified")
RECORDS = os.path.join(OUT_VER, "agriculture_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "agriculture_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "agriculture_arabic_legal_llm",
                        "agriculture_law_legal_llm_001_037.json")

LAW_ID = "sa-agriculture-law-m64-1442"
LAW_AR = "نظام الزراعة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"agriculture_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير الهيئة القطاع الزراعي الزراعية الأنشطة").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    n = int(m.group(1))
    suf = m.group(2)
    if suf is None:
        return (n, 0)
    if suf == "":
        return (n, 1)
    return (n, 1 + int(suf))


def _top_status(key):
    if key in AMENDED_KEYS:
        return STATUS_AMENDED
    if key in ADDED_KEYS:
        return STATUS_ADDED
    return STATUS_UNCHANGED


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        top_status = _top_status(key)
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "agriculture", "law_component": "law",
                    "language": "ar",
                    "record_layer": "AGRICULTURE_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; this is the currently in-force "
                                              "Agriculture Law (Royal Decree M/64, 10/8/1442H), a "
                                              "brand-new base-law track built from scratch this pass "
                                              "(not previously in this corpus). By clause Second of "
                                              "its ISSUING DECREE (not any article) it repeals five "
                                              "named earlier instruments (M/9 1408H, M/13 1424H, "
                                              "M/15 1431H, M/55 1435H, CoM Rules 96 1405H) plus "
                                              "conflicting provisions. laws.boe.gov.sa was checked "
                                              "FIRST per standard methodology but is unreachable "
                                              "this pass (HTTP 503) and Wayback is egress-blocked; "
                                              "the verbatim text of all 37 articles was extracted "
                                              "from nezams.com (a single clean born-digital HTML "
                                              "aggregator, no scan/OCR/ligature defects). All "
                                              "governing metadata and the flat 37-article/no-chapter "
                                              "structure are cross-verified against multiple "
                                              "independent sources (most notably the official MISA "
                                              "English PDF). TIER_3. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source artifact "
                                              "before relying on this track."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "agriculture-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "agriculture/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الزراعة" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/64), 10/8/1442H "
                                                          "(Council of Ministers Resolution 431, "
                                                          "3/8/1442H; Shura Resolutions 219/40, "
                                                          "17/9/1441H and 362/61, 25/2/1442H; Umm "
                                                          "Al-Qura 20/8/1442H) — the currently "
                                                          "in-force Agriculture Law, which by clause "
                                                          "Second of its issuing decree repealed five "
                                                          "named earlier instruments. Verbatim text "
                                                          "from nezams.com (single full-text "
                                                          "aggregator; laws.boe.gov.sa unreachable "
                                                          "this pass, Wayback egress-blocked); all "
                                                          "metadata and the flat 37-article/no-chapter "
                                                          "structure cross-verified against multiple "
                                                          "independent sources (incl. official MISA "
                                                          "English PDF). TIER_3."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/64) وتاريخ 10/8/1442هـ (قرار مجلس الوزراء 431 وتاريخ 3/8/1442هـ؛ قراري مجلس الشورى 219/40 وتاريخ 17/9/1441هـ و362/61 وتاريخ 25/2/1442هـ؛ نشر أم القرى 20/8/1442هـ) — نظام الزراعة النافذ حالياً، الذي ألغى بموجب البند (ثانياً) من مرسوم إصداره خمسة أنظمة/أدوات سابقة مسمّاة. النص الحرفي من nezams.com (مصدر نص كامل واحد؛ laws.boe.gov.sa غير قابل للوصول هذه الجولة، وWayback محظور)؛ وجميع البيانات الوصفية والبنية المسطّحة (37 مادة دون فصول) متقاطعة عبر مصادر مستقلة متعددة (منها الملف الرسمي الإنجليزي على misa.gov.sa). المستوى TIER_3.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "agriculture",
               "layer": "AGRICULTURE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-agriculture-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (37 مادة؛ 37 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ دون تقسيم إلى فصول)",
               "title_en": ("The Saudi Arabian Agriculture Law (Royal Decree M/64, 10/8/1442H) — "
                            "Arabic LLM-ready layer (37 records: 37 original, 0 amended, 0 added, "
                            "0 repealed; no chapter divisions)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 37], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Agriculture Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
