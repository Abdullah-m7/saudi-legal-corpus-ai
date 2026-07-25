#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Arabian Child Protection
Law track (اللائحة التنفيذية لنظام حماية الطفل, Ministerial Resolution No.
56386, 16/6/1436H). This is a STANDALONE track, independent of the base law's
own child_protection_law track and its shared pipeline files -- it does not
modify any shared pipeline code.

VERIFICATION TIER -- see sources/child_protection_regulation/law/official_source/
child_protection_regulation_official_source.json's verification_methodology_note
for the full account. Summary:

PRIMARY SOURCE (laws.boe.gov.sa) -- checked first as this corpus's methodology
requires. The live portal was unreachable this pass (HTTP 000 connection-reset
via direct curl; HTTP 503 via WebFetch), and no dedicated lawId page for this
REGULATION (as distinct from the base law's own confirmed lawId
2d3cb83a-0379-4cde-8e0b-a9a700f272bd) was found via indexed search.

SECONDARY SOURCES: (1) nezams.com (independent Arabic legal-text aggregator),
fetched via curl (HTTP 200), supplied the full verbatim text -- exactly 25
"subject" elements (subject-1..subject-25), each opening with a verbatim
reproduction of the corresponding base-law article followed by the
regulation's own numbered implementing sub-clauses (e.g. 6/1, 6/2). Its page
metadata table explicitly states "التعديلات: لم يجرِ عليه تعديل" (no amendment
made). (2) An OFFICIAL government document -- the Ministry of Justice's
Adl-journal PDF (adlm.moj.gov.sa/attach/1463.pdf, HTTP 200, 68 pages) --
independently confirmed the decree identity (Ministerial Resolution 56386,
16/6/1436H), the five-chapter structure and boundaries, and that the
regulation comprises exactly 25 articles with no mukarrar. Its Arabic PDF
extraction carried the same bidi/ligature reordering artifacts documented in
the base law's own track, so it was used for identity/structure/count
confirmation, not char-level verbatim; verbatim text is from nezams.com.
-> TIER_3 (matching the base law track's tier).

CENTRAL VERIFICATION FINDING: CoM Resolution 427 (5/8/1443H) / Royal Decree
M/72, which amended the BASE LAW's Articles 12, 15, 19, 23 and added Article
23-mukarrar (see child_protection_law track), did NOT amend this regulation.
This was confirmed via two independent primary sources: nezams.com's own
metadata table for this regulation's page ("لم يجرِ عليه تعديل"), and the Umm
Al-Qura gazette's title for CoM 427 ("تعديل نظامي الحماية من الإيذاء وحماية
الطفل" -- amending the two LAWS, not "ولائحتيهما" their regulations). A general
WebSearch query returned an AI-generated summary that incorrectly conflated
the base law's amendments with this regulation (falsely claiming Articles 12
and 19 of "the regulation" were amended); that summary was rejected in favor
of the direct primary-source check, per this corpus's trust rule. See
known_unresolved_discrepancies for the full account.

25 records, all اصلية (0 معدلة, 0 ملغاة, 0 مضافة, no mukarrar) -- this
regulation predates the base law's 1443H amendment and has no amendment of
its own. 5 chapters (فصول), mirroring the base law's chapter structure and
article ranges exactly (1-4, 5-7, 8-14, 15-21, 22-25), with one confirmed
verbatim wording difference: this regulation titles Chapter 2 "حقوق الطفل في
الحماية" (plural) vs. the base law's "حق الطفل في الحماية" (singular) --
verified from this regulation's own two independent sources and preserved
as-is (not silently harmonized with the base law's title).

STRUCTURAL NOTE: each article's `text` field is the FULL verbatim article
entry as published -- both the reproduced base-law article text (in its
original, pre-1443H-amendment wording, since this regulation was issued in
1436H) and the regulation's own detailed numbered implementing sub-clauses.
This dual structure is intentional in the regulation's own primary sources
(confirmed by both nezams.com and the official MOJ PDF) and is preserved
whole, per this corpus's no-silent-omission policy; only nezams.com's own
website-navigation chrome (repeated chapter/article-number headers, share
buttons) was stripped as non-legal-text noise.

Arabic governs; no translation/paraphrase/interpretation performed.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "child_protection_regulation", "law", "official_source",
                    "child_protection_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "child_protection_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "child_protection_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "child_protection_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "child_protection_regulation_arabic_legal_llm",
                         "child_protection_regulation_legal_llm_001_025.json")

LAW_ID = "sa-child-protection-regulation-mr-56386-1436"
LAW_AR = "اللائحة التنفيذية لنظام حماية الطفل"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"child_protection_regulation_art_(\d{3})$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الطفل الجهات ذات العلاقة الوزارة الوزير").split())


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
    return int(m.group(1))


def _top_status(key):
    if key in AMENDED_KEYS:
        return "AMENDED_DATED"
    if key in ADDED_KEYS:
        return "ADDED_DATED"
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
        ver.append({"law_key": "child_protection_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "CHILD_PROTECTION_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; laws.boe.gov.sa was unreachable this "
                                              "pass (HTTP 000 connection-reset direct; HTTP 503 via "
                                              "WebFetch) and no dedicated lawId page for this "
                                              "REGULATION (distinct from the base law's own confirmed "
                                              "lawId) was found via indexed search. Full verbatim "
                                              "text is from nezams.com (independent aggregator, HTTP "
                                              "200); the decree identity, five-chapter structure and "
                                              "25-article count were independently confirmed by the "
                                              "OFFICIAL Ministry of Justice Adl-journal PDF "
                                              "(adlm.moj.gov.sa/attach/1463.pdf, HTTP 200). CoM "
                                              "Resolution 427 (1443H), which amended the BASE LAW, "
                                              "was independently confirmed NOT to have amended this "
                                              "regulation (nezams.com's own metadata: \"لم يجرِ عليه "
                                              "تعديل\"; Umm Al-Qura gazette title references amending "
                                              "the two LAWS, not their regulations) -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies before relying on this "
                                              "track's text or provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "child-protection-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "child_protection_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام حماية الطفل" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Resolution No. 56386 (16/6/1436H), "
                                                          "issued pursuant to Article 24 of the Child "
                                                          "Protection Law (Royal Decree M/14, 3/2/1436H). "
                                                          "Full text from nezams.com (independent "
                                                          "aggregator); decree identity, 5-chapter "
                                                          "structure and 25-article count independently "
                                                          "confirmed via the OFFICIAL Ministry of Justice "
                                                          "Adl-journal PDF; laws.boe.gov.sa was "
                                                          "unreachable this pass and no dedicated lawId "
                                                          "page for this regulation was found. No "
                                                          "amendment to this regulation found (distinct "
                                                          "from the base law's own 1443H amendment) -- "
                                                          "confirmed via nezams.com's own metadata and "
                                                          "the Umm Al-Qura gazette title for CoM 427"),
                                     "source_authority_ar": "القرار الوزاري رقم (56386) وتاريخ 16/6/1436هـ، الصادر تنفيذا للمادة (24) من نظام حماية الطفل (المرسوم الملكي م/14، 3/2/1436هـ). النص الكامل من nezams.com (مصدر ثانوي مستقل)، مع تحقق مستقل من هوية القرار وبنية الفصول الخمسة وعدد المواد (25) عبر وثيقة مجلة العدل الرسمية بوزارة العدل؛ تعذر الوصول لـlaws.boe.gov.sa هذه الجولة ولم يُعثر على صفحة lawId مخصصة لهذه اللائحة. لم يثبت أي تعديل على هذه اللائحة (خلافا لتعديل 1443هـ الذي طال النظام الأساس فقط) -- مؤكد عبر البيانات الوصفية لـnezams.com وعنوان قرار مجلس الوزراء 427 في جريدة أم القرى",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "child_protection_regulation",
               "layer": "CHILD_PROTECTION_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-child-protection-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (25 سجلا؛ جميعها أصلية)",
               "title_en": "Implementing Regulation of the Saudi Arabian Child Protection Law — "
                           "Arabic LLM-ready layer (25 records, all original/unamended)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 25], "includes_mukarrar": [],
               "text_status": "ORIGINAL_NO_AMENDMENT_FOUND",
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Child Protection Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
