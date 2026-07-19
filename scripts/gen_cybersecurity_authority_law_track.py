#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Statute (Organizational Regulation) of the National
Cybersecurity Authority track (تنظيم الهيئة الوطنية للأمن السيبراني,
Royal Order 6801, 11/2/1439H, amended by Royal Order 7053, 2/2/1443H).

VERIFICATION TIER -- see sources/cybersecurity_authority/law/official_source/
cybersecurity_authority_law_official_source.json's verification_methodology_note
for the full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa could NOT be located for this exact statute
this pass (repeated WebSearch queries surfaced only OTHER BOE-catalogued
laws that merely cite this statute in passing; a direct curl to the portal
returned "Connection reset by peer"). The PRIMARY source actually used is
the National Cybersecurity Authority's OWN official website (nca.gov.sa),
specifically an official PDF hosted on its own CDN subdomain, fetched live
this pass (HTTP 200 via direct curl, after the WebFetch tool itself
returned HTTP 503 for the same URL). That PDF's own title page states, in
the regulator's own words, that this is the تنظيم "الصادر بالأمر الملكي
رقم 6801 بتاريخ 1439/02/11هـ، المعدّل بالأمر الملكي رقم 7053 بتاريخ
1443/02/02هـ" -- matching this corpus's own coverage_gap_map estimate
exactly.

A GENUINE TEXT-EXTRACTION ANOMALY: the source PDF's embedded text layer has
a confirmed, systematic character-transposition artifact (both pdftotext
and PyMuPDF independently produce the SAME corrupted local letter-pair
order, e.g. "السيبراني" extracting as "السيرباين"). This was worked around
by rendering each page to a 300dpi PNG and OCR'ing with Tesseract 5's
Arabic model, then cross-reading the OCR output word-by-word against the
flawed-but-complete pdftotext/fitz extraction (used only to confirm
article/item boundaries and counts) and against qistas.com's independent
excerpt for Articles 1-3.

SECONDARY CROSS-VERIFICATION: qistas.com (partial, Arts. 1-3, structural
match), NCA's own separate laws-and-regulations listing page (same
authority, not independently counted), saudipedia.com (independent
establishment-date corroboration), and multiple WebSearch press
aggregations (Saudi press, Nov 2017). No second INDEPENDENT official/
primary source was found (laws.boe.gov.sa's own page for this exact
statute could not be located) -- this track is honestly assessed at
TIER_2, not TIER_1.

15 records: all اصلية (0 معدلة, 0 ملغاة, 0 مضافة) at the per-article
level. The source PDF's own title page confirms at least one amendment
(Royal Order 7053) exists and consolidated_amended_law is set to true
at the document level, but NO source found this pass identifies which
specific article that amendment touched, and no pre-amendment text was
located for a diff -- per this corpus's anti-fabrication policy, no
individual article is marked معدلة absent specific evidence. See
known_unresolved_discrepancies (key
cybersecurity_authority_7053_amendment_article_unattributed).

Flat structure, no أبواب/فصول. No inline per-article titles in the
source. This track's own final article (15) contains only a GENERIC
repeal clause -- no named predecessor organizational statute is repealed
by this instrument (a confirmed negative finding; contrast nazaha_law and
awqaf_law's explicit named-predecessor repeals). A separate, newer,
Royal-Decree-level instrument (م/117, 21/6/1446H, "الممكنات النظامية")
dealing with licensing/violations/penalties was found but is NOT ingested
here -- textually and substantively distinct from this organizing statute
(see known_unresolved_discrepancies).

No legal text is altered beyond: OCR-based recovery of the correct letter
order where the PDF's own text layer is corrupted (a read-only
transcription correction of a source-side extraction artifact, not a
substantive edit); omission of list-rendering numeral markers per this
corpus's nazaha_law/awqaf_law convention (lettered sub-items in Article 12
are preserved); whitespace/line-break normalization. Arabic governs; no
translation/paraphrase/interpretation performed. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cybersecurity_authority", "law", "official_source",
                   "cybersecurity_authority_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "cybersecurity_authority", "law", "verified")
RECORDS = os.path.join(OUT_VER, "cybersecurity_authority_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "cybersecurity_authority_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "cybersecurity_authority_arabic_legal_llm",
                        "cybersecurity_authority_law_legal_llm_001_015.json")

LAW_ID = "sa-cybersecurity-authority-law-6801-1439"
LAW_AR = "تنظيم الهيئة الوطنية للأمن السيبراني"
TOP_STATUS = ("NCA_OFFICIAL_SITE_PDF_PRIMARY_TESSERACT_OCR_TRANSCRIBED_X_QISTAS_"
              "STRUCTURAL_PARTIAL_CROSSCHECK_TIER2_BOE_PAGE_NOT_LOCATED")
KEY_RE = r"cybersecurity_authority_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المجلس الرئيس المراكز").split())


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
        ver.append({"law_key": "cybersecurity_authority", "law_component": "law",
                    "language": "ar",
                    "record_layer": "CYBERSECURITY_AUTHORITY_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on an official "
                                              "PDF hosted on the National Cybersecurity "
                                              "Authority's own website (nca.gov.sa/cdn.nca.gov.sa) "
                                              "as the PRIMARY source (no laws.boe.gov.sa page for "
                                              "this exact statute could be located this pass), "
                                              "transcribed via Tesseract OCR to work around a "
                                              "confirmed text-layer letter-transposition artifact "
                                              "in the PDF itself, cross-verified against "
                                              "qistas.com (partial, Arts. 1-3) and saudipedia.com "
                                              "(establishment-date corroboration). All 15 articles "
                                              "are اصلية at the per-article level; the source's own "
                                              "title page confirms an amendment (Royal Order 7053, "
                                              "2/2/1443H) exists at the document level "
                                              "(consolidated_amended_law=true) but no source found "
                                              "this pass attributes it to a specific article -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact, in particular the unattributed-amendment "
                                              "and BOE-page-not-located findings, before relying on "
                                              "this track's text as necessarily complete."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "cybersecurity-authority-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "cybersecurity_authority/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من تنظيم الهيئة الوطنية للأمن السيبراني" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Order 6801 (amended by Royal "
                                                          "Order 7053) — official PDF on the "
                                                          "National Cybersecurity Authority's own "
                                                          "website (nca.gov.sa), OCR-transcribed "
                                                          "to work around a text-layer artifact, "
                                                          "cross-verified against qistas.com and "
                                                          "saudipedia.com; no laws.boe.gov.sa page "
                                                          "for this exact statute could be located "
                                                          "this pass"),
                                     "source_authority_ar": "الأمر الملكي رقم (6801) (المعدل بالأمر الملكي رقم 7053) — نسخة PDF رسمية من الموقع الرسمي للهيئة الوطنية للأمن السيبراني (nca.gov.sa)، مفرَّغة بالتعرف الضوئي على الحروف (OCR) لتجاوز خلل في طبقة النص، مطابقة مع qistas.com وsaudipedia.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "cybersecurity_authority",
               "layer": "CYBERSECURITY_AUTHORITY_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": TOP_STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-cybersecurity-authority-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (15 مادة أصلية، بلا تقسيم إلى أبواب)",
               "title_en": "Statute (Organizational Regulation) of the National Cybersecurity Authority — Arabic LLM-ready layer (15 records, all original)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Cybersecurity Authority Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
