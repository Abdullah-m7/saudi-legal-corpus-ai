#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Contractors Classification Law track (نظام تصنيف
المقاولين, Royal Decree M/9, 18/1/1443H -- the currently in-force Contractors
Classification Law, administered by the Ministry of Municipal, Rural Affairs
and Housing (MOMAH/MOMRAH, momah.gov.sa)).

BRAND-NEW BASE-LAW TRACK -- this statute was NOT previously in this corpus. It
was built from scratch this pass.

WHICH INSTRUMENT, AND HOW CONFIRMED -- نظام تصنيف المقاولين is a single,
self-standing Royal-Decree law (M/9, 18/1/1443H), fetched DIRECTLY from an
official PDF hosted on the Ministry's own domain (momah.gov.sa/sites/default/
files/2025-10/nzam%20tsnyf%20almqawlyn.pdf -- HTTP 200, 874666 bytes, 7 pages,
PDF v1.7). Cross-checked via independent signals: (1) laws.boe.gov.sa carries
it under its own dedicated lawId 66eccea3-fc1c-471f-bcfa-ad9d009a7ec0 (seen
via WebSearch), with the PREDECESSOR law's lawId
(5c351f5d-0814-4b94-86a0-a9a700f1b1f8, نظام تصنيف المقاولين 1427هـ) also
independently located; (2) nezams.com carries only the OLD (1427H) law's page,
whose own metadata table independently confirms the new decree's number/date
("ألغي بصدور النظام الجديد الصادر بمرسوم ملكي رقم (م/9) وتاريخ 18/01/1443هـ");
(3) qanoonsa.com confirms the Implementing Regulation's existence and several
amending ministerial decisions (2021, 2023, 2025); (4) argaam.com (a financial
news secondary source) substantively corroborates several specific provisions
(classification criteria, 90-day entry into force, joint-venture rule, penalty
tiers) matching the extracted articles.

FONT-ENCODING DEFECT DISCOVERED AND CORRECTED -- the PDF's born-digital text
layer on pages 3-6 (Articles 1-19) has a systematic cmap/font bug: every
"الم" (alef-lam-meem) letter sequence is extracted reversed as "امل"
(alef-meem-lam) -- e.g. "المادة" extracts as "املادة". This was verified
exhaustively: ALL 37 unique affected words resolve to a valid, sensible
Arabic word when corrected, with zero counterexamples. The correction was
cross-validated two additional, independent ways against the SAME official
PDF: (a) an independent Tesseract Arabic OCR pass over 300dpi page renders
(unaffected by the cmap bug, since OCR reads glyph shapes, not the encoding
table); (b) direct visual reading of the rendered page images by the model
itself. All three methods agree on the final article text.

PREAMBLE (Royal Decree text, PDF page 2) -- unlike pages 3-6, page 2 is a
SCANNED IMAGE with no extractable text layer at all (pdftotext yields only
the "المرسوم الملكي" heading and the page number). Its text was transcribed
via direct visual reading of a 600dpi render (OCR was attempted but produced
unreliable digit recognition). Confidence in this transcription is reinforced
by its three foundational boilerplate citations (Basic Law of Governance
A/90 27/8/1412H; Council of Ministers Law A/13 3/3/1414H; Shura Council Law
A/91 27/8/1412H) matching, verbatim and by date, the same three citations
independently transcribed in this corpus's waste_management_law preamble.
Digits are normalized from the scan's Eastern Arabic-Indic numerals to
Western digits for corpus consistency (purely a numeral-script normalization,
discloses no information change).

SUPERSESSION -- CONFIRMED INSIDE THE LAW'S OWN TEXT: Article 19 states
verbatim: "يحل النظام محل نظام تصنيف المقاولين الصادر بالمرسوم الملكي رقم
(م / 18) وتاريخ 20 / 3 / 1427هـ، ويلغي كل ما يتعارض معه من أحكام." A ONE-DAY
date discrepancy with nezams.com's metadata for the repealed law (19/3/1427H
vs this Law's own 20/3/1427H) is disclosed, not silently resolved. The
enacting Royal Decree's own clause (Second) additionally carves out a
transitional EXCEPTION to this repeal for specific provisions of former CoM
Resolution 405 (1435H) and two Royal/Sublime Orders (33635/1436H,
44302/1438H) -- recorded in preamble_ar/issuing_authority_ar, outside the 19
numbered Articles.

VERIFICATION TIER -- TIER_2. Exactly ONE official/primary source
(momah.gov.sa) was reached and used as the governing text -- but that single
source was cross-verified via an independent OCR pass AND a direct visual
read of the SAME official document (which caught and let us correct the
font-encoding defect above), then further cross-checked for identity/
structure against nezams.com, qanoonsa.com, and argaam.com. laws.boe.gov.sa
(this corpus's usual second primary source) was checked FIRST per standard
methodology but is unreachable this pass: repeated direct curl attempts and
WebFetch returned "Connection reset by peer" / HTTP 503; web.archive.org was
also explicitly attempted and returned the same connection-reset failure --
consistent with the same block pattern documented in this corpus's
waste_management_law track this session. Because no second official source
was reached, this track is NOT classified TIER_1; because the governing text
is drawn from an actual official primary document (not merely a secondary
aggregator), it is stronger than TIER_3.

19 articles, NO chapter/فصل structure (a short, flat, directly-numbered law);
all 19 اصلية; 0 معدلة, 0 ملغاة, 0 مضافة. Diacritics (tashkeel, incl. tanween
and shadda) are stripped uniformly for consistency with this corpus's other
BOE-family tracks; the source's article-body text (pages 3-6) uses ONLY
Western digits (no mixed-digit rendering to disclose there).

IMPLEMENTING REGULATION -- exists (per qanoonsa.com: ministerial decisions in
2021, 2023, and 2025) but NOT built this pass; flagged as a follow-up
candidate track (contractors_classification_regulation, law_component
"regulation").

Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "contractors_classification_law", "law", "official_source",
                   "contractors_classification_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "contractors_classification_law", "law", "verified")
RECORDS = os.path.join(OUT_VER, "contractors_classification_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "contractors_classification_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "contractors_classification_law_arabic_legal_llm",
                        "contractors_classification_law_legal_llm_001_019.json")

LAW_ID = "sa-contractors-classification-law-m9-1443"
LAW_AR = "نظام تصنيف المقاولين"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"contractors_classification_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الوزارة الوزير المقاول المقاولين التصنيف").split())


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
        ver.append({"law_key": "contractors_classification_law", "law_component": "law",
                    "language": "ar",
                    "record_layer": "CONTRACTORS_CLASSIFICATION_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "Contractors Classification Law (Royal Decree M/9, "
                                              "18/1/1443H), a brand-new base-law track built from "
                                              "scratch this pass (not previously in this corpus). "
                                              "Article 19 OF THE LAW ITSELF states it replaces the "
                                              "prior Contractors Classification Law (M/18, "
                                              "20/3/1427H). Fetched directly from the official "
                                              "momah.gov.sa PDF; a font-encoding defect in the "
                                              "PDF's text layer (لم/مل letter-pair reversal after "
                                              "alef) was discovered, corrected, and cross-verified "
                                              "via an independent OCR pass and a direct visual read "
                                              "of the same rendered PDF pages. laws.boe.gov.sa was "
                                              "checked FIRST per standard methodology but "
                                              "unreachable this pass (connection reset/HTTP 503); "
                                              "web.archive.org was also explicitly attempted and "
                                              "returned the same connection-reset failure. TIER_2. "
                                              "See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track -- notably the "
                                              "disclosed one-day date conflict for the repealed "
                                              "predecessor law."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "contractors-classification-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "contractors_classification_law/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام تصنيف المقاولين" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/9), 18/1/1443H "
                                                          "(Council of Ministers Resolution 49, "
                                                          "16/1/1443H; Shura Council Resolution "
                                                          "5/28, 16/4/1442H) — the currently "
                                                          "in-force Contractors Classification Law, "
                                                          "which by its own Article 19 replaces the "
                                                          "prior Contractors Classification Law "
                                                          "(M/18, 20/3/1427H -- date disclosed as "
                                                          "conflicting with nezams.com's 19/3/1427H, "
                                                          "see known_unresolved_discrepancies). "
                                                          "Verbatim text fetched directly from the "
                                                          "official momah.gov.sa PDF; a font-"
                                                          "encoding defect in its text layer was "
                                                          "corrected and cross-verified via "
                                                          "independent OCR + direct visual reading "
                                                          "of the same document. laws.boe.gov.sa "
                                                          "and web.archive.org both unreachable "
                                                          "this pass. TIER_2."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/9) وتاريخ 18/1/1443هـ (قرار مجلس الوزراء رقم (49) وتاريخ 16/1/1443هـ؛ قرار مجلس الشورى رقم (5/28) وتاريخ 16/4/1442هـ) — نظام تصنيف المقاولين النافذ حالياً، الذي يحل -بنص المادة التاسعة عشرة منه ذاتها- محل نظام تصنيف المقاولين السابق (م/18، 20/3/1427هـ -- تاريخه متعارض مع 19/3/1427هـ الوارد في nezams.com، انظر known_unresolved_discrepancies). النص الحرفي جُلب مباشرة من ملف momah.gov.sa الرسمي؛ صُحح عيب في ترميز الخط داخل طبقة نصه وتحقق منه عبر OCR مستقل وقراءة بصرية مباشرة لنفس المستند. laws.boe.gov.sa وweb.archive.org كلاهما غير قابلين للوصول هذه الجولة. المستوى TIER_2.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "contractors_classification_law",
               "layer": "CONTRACTORS_CLASSIFICATION_LAW_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-contractors-classification-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (19 مادة؛ 19 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة؛ بلا فصول)",
               "title_en": ("The Saudi Arabian Contractors Classification Law (Royal Decree M/9, "
                            "18/1/1443H) — Arabic LLM-ready layer (19 records: 19 original, 0 "
                            "amended, 0 added, 0 repealed; no chapter structure)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 19], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Contractors Classification Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
