#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Anti-Money Laundering Law track
(اللائحة التنفيذية لنظام مكافحة غسل الأموال), the companion regulation to this
corpus's aml_law track (نظام مكافحة غسل الأموال, Royal Decree M/20, dated
5/2/1439H, published 14/2/1439H).

The Regulation is issued/amended under Article 50 of the AML Law by the President
of State Security in agreement with the Minister of Finance, the Public
Prosecutor and the Governor of the Saudi Central Bank. Its founding approval is
cable (برقية) No. 14525 dated 19/2/1439H (the number/date SAMA's rulebook
canonicalises as the Regulation's official reference, status "in-force"); it was
amended by Administrative Decision No. 98752 (12/5/1446H, Article 17) and the
current consolidated text was promulgated by Administrative Decision No. 266507
dated 9/12/1447H ("تحديث اللائحة ... وفق الصيغة المرفقة") following the base
Law's own M/223 (27/10/1447H) amendments.

VERIFICATION TIER (upgraded 2026-07-29) -- see
aml_regulation_official_source.json's verification_methodology_note for the full
account. Summary:

PRIMARY SOURCE: the Kingdom's official gazette. Umm al-Qura published the FULL
text of the consolidated Regulation attached to Administrative Decision 266507
BORN-DIGITAL (HTML, no scan, no OCR) at
https://www.uqn.gov.sa/decisions-and-regulations/4001243 on 11/1/1448H
(= 26/06/2026G); the decision instrument itself is on the adjacent page 4001242.
Fetched directly this pass (HTTP 200); body extracted from
<article id="article-content">: 61,265 chars, 128 numbered paragraphs,
27 articles, ten chapter headings. A copy of the extracted body is kept at
inputs/aml_official_pdfs/aml_regulation_uqn_gazette_4001243_body_ar.txt and its
sha256 is recorded in provenance.

SECONDARY (retained, documented, NOT discarded): (a) the aml.gov.sa official
SCANNED PDF of the same instrument (34 pages, 300dpi JPEG images, no text layer,
sha256 96a4250a...) -- this was the PRIMARY source in the previous pass and is
the channel whose OCR produced the defects corrected this pass; (b)
api.qanoniah.com's born-digital feed (articles 1,2,5,7,8,9,10,14,15,16 only,
last-modified 1447-12-09); (c) rulebook.sama.gov.sa metadata (no. 14525).
laws.boe.gov.sa has no dedicated lawId page for this administrative Regulation --
no longer a constraint now that the official gazette carries the text.

WHAT THE 2026-07-29 MAINTENANCE PASS FIXED (all disclosed in
known_unresolved_discrepancies, nothing deleted):
 1. STRUCTURAL. Article 17 previously carried EIGHT paragraphs and articles 18
    and 19 were absent. The gazette gives article 17 five paragraphs and numbers
    the remaining three 18/1, 18/2 and 19/1. The three paragraphs were RE-HOMED
    explicitly (٦/١٧ -> ١/١٨, ٧/١٧ -> ٢/١٨, ٨/١٧ -> ١/١٩); their text is
    word-for-word identical to the gazette. Article count 25 -> 27; paragraph
    count unchanged at 128. Recorded in each article's rehomed_from /
    restructuring_note_ar.
 2. A FALSE ASSERTION WAS RETRACTED IN PLACE. The discrepancy entry
    aml_regulation_skipped_law_articles used to state that articles 18 and 19
    were "deliberately absent from the source". That is false; the prior wording
    is preserved verbatim in prior_description_RETRACTED with the reason it was
    wrong.
 3. OCR CORRECTIONS. 25 recorded word/punctuation corrections across 23
    paragraphs in 11 articles, two of them meaning-changing: 17/4(ج) had dropped
    «الأخرى برئاسة أمن الدولة» and 49/1 had dropped the verb «يسمح». The prior
    state of every correction is kept in the article's corrections_applied field.
 4. The base Law's decree date in base_law was corrected from 14/2/1439 (the
    PUBLICATION date) to 5/2/1439 (the decree date), verified live against MOJ
    (issuanceDate 1439-02-05 / publishDate 1439-02-14), the BOE decree-viewer
    title, and Council of Ministers Decision 16 of 1/1/1448H.

The track was NOT stale: 128 gazette paragraphs vs 128 stored, same instrument,
same consolidation (266507). It was mis-structured and OCR-damaged.

STRUCTURE: the Regulation does NOT elaborate every Law article -- it covers only
the 27 Law articles that need implementing detail, numbering provisions at the
PARAGRAPH level. article_number is the article component of the paragraph tag;
number_label_ar ("المادة (ع) من اللائحة") is constructed (the source prints no
explicit article headers). Present articles: 1,2,5,7,8,9,10,14,15,16,17,18,19,20,
22,23,24,36,37,38,39,40,41,42,43,48,49 across nine chapters carrying the Law's
own chapter numbers (I-VI, VIII-X); chapter VII (العقوبات) has no counterpart, so
chapter numbering jumps from VI (الرقابة) to VIII (المصادرة). 26 articles اصلية,
1 معدلة (Article 17, per Admin Decision 98752; prior sub-paragraph text not
recovered -- flagged, not fabricated), 0 ملغاة, 0 مضافة.

Arabic governs; no translation/paraphrase/interpretation. Paragraph tags are
stored in Arabic-Indic digits in "paragraph/article" order; the gazette prints
Western digits in "article/paragraph" order -- a disclosed, deliberately
unresolved rendering-direction difference (see
aml_regulation_paragraph_tag_digit_order_unresolved). Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "aml", "regulation", "official_source",
                   "aml_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "aml", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "aml_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "aml_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "aml_regulation_arabic_legal_llm",
                        "aml_regulation_legal_llm_001_027.json")

LAW_ID = "sa-aml-regulation-14525-1439"
LAW_AR = "اللائحة التنفيذية لنظام مكافحة غسل الأموال"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"aml_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"aml_regulation_art_017"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الأموال المملكة الجهة الجهات").split())


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
        ver.append({"law_key": "aml", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "AML_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "source_channel": a.get("source_channel"),
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; PRIMARY source is the BORN-DIGITAL "
                                              "text of the consolidated Regulation published in "
                                              "the Umm al-Qura official gazette on 11/1/1448H "
                                              "(uqn.gov.sa/decisions-and-regulations/4001243), "
                                              "being the text attached to Admin Decision 266507 "
                                              "(9/12/1447H). The aml.gov.sa official SCANNED PDF "
                                              "of the same instrument is retained as a documented "
                                              "SECONDARY cross-check (it was the previous pass's "
                                              "PRIMARY and the source of the OCR defects corrected "
                                              "on 2026-07-29); qanoniah.com's born-digital feed "
                                              "(articles 1,2,5,7,8,9,10,14,15,16) is a third "
                                              "channel. See verification_methodology_note and "
                                              "known_unresolved_discrepancies before relying on "
                                              "this track -- in particular the EXPLICIT re-homing "
                                              "of three paragraphs from article 17 to the newly "
                                              "created articles 18 and 19, the retraction of the "
                                              "prior false 'articles 18/19 deliberately absent' "
                                              "assertion, the 25 recorded OCR corrections (two "
                                              "meaning-changing), the paragraph-level numbering "
                                              "with no explicit article headers and its unresolved "
                                              "digit-order question, and the genuinely skipped Law "
                                              "article numbers."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "aml-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "aml/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام مكافحة غسل الأموال" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("AML Implementing Regulation "
                                                          "(founding approval cable No. 14525, "
                                                          "19/2/1439H; consolidated by Admin "
                                                          "Decision No. 266507, 9/12/1447H) — "
                                                          "PRIMARY: Umm al-Qura official gazette, "
                                                          "born-digital full text published "
                                                          "11/1/1448H "
                                                          "(uqn.gov.sa/decisions-and-regulations/"
                                                          "4001243); SECONDARY cross-check: "
                                                          "aml.gov.sa official scanned PDF (the "
                                                          "previous pass's primary); THIRD: "
                                                          "qanoniah.com born-digital API "
                                                          "(articles 1,2,5,7,8,9,10,14,15,16); "
                                                          "SAMA rulebook metadata (no.14525) for "
                                                          "cross-check; laws.boe.gov.sa has no "
                                                          "dedicated lawId page for this "
                                                          "administrative Regulation"),
                                     "source_authority_ar": "اللائحة التنفيذية لنظام مكافحة غسل الأموال (الاعتماد التأسيسي بالبرقية رقم 14525 وتاريخ 19/2/1439هـ، والنص الموحَّد الحالي بالقرار الإداري رقم 266507 وتاريخ 9/12/1447هـ) — المصدر الأساسي: النص المولود رقميا المنشور في جريدة أم القرى بتاريخ 11/1/1448هـ (uqn.gov.sa/decisions-and-regulations/4001243)؛ قناة ثانوية موثَّقة: ملف aml.gov.sa الممسوح ضوئيا (وكان المصدر الأساسي في الجولة السابقة)؛ قناة ثالثة: واجهة qanoniah.com الرقمية الأصلية للمواد 1 و2 و5 و7 و8 و9 و10 و14 و15 و16؛ بيانات البنك المركزي الوصفية (الرقم 14525) للتحقق المتقاطع؛ بوابة هيئة الخبراء لا تملك صفحة lawId مخصصة لهذه اللائحة الإدارية",
                                     "source_status": a["status"].lower(),
                                     "source_channel": a.get("source_channel"),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "aml",
               "layer": "AML_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "article_numbers_present": src.get("article_numbers_present"),
               "article_count": src.get("article_count"),
               "verification_tier": src.get("verification_tier"),
               "prior_verification_tier": src.get("prior_verification_tier"),
               "provenance": src.get("provenance"),
               "base_law": src.get("base_law"),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-aml-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (27 مادة؛ 26 أصلية، 1 معدلة، 0 ملغاة، 0 مضافة)",
               "title_en": ("Implementing Regulation of the Anti-Money Laundering Law — Arabic "
                            "LLM-ready layer (27 records: 26 original, 1 amended, 0 repealed, "
                            "0 added)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_numbers_present": src.get("article_numbers_present"),
               "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready AML Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
