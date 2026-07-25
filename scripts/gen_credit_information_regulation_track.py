#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Credit Information Law track
(اللائحة التنفيذية لنظام المعلومات الائتمانية, SAMA Governor's Decision
No. أق/13709, dated 22/9/1432H = 21/8/2011G).

This is the companion-regulation track for this corpus's own credit_information
base-law track (see sources/credit_information/law/official_source/
credit_information_law_official_source.json, which notes: "NO IMPLEMENTING
REGULATION TEXT IS INCLUDED IN THIS TRACK ... following this corpus's
established precedent ... of tracking a law's Implementing Regulation as a
separate future track."). This track ingests that companion Implementing
Regulation.

VERIFICATION TIER -- see credit_information_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: the born-digital Arabic PDF originally published by bayancb.com
(a licensed Saudi credit bureau), fetched via a Wayback Machine snapshot after
the prior-research-pass URL's opaque media-GUID rotated and 404'd on this pass
(a fresh CDX lookup located the identical filename, 426561 bytes / 24 pages,
under a different, earlier media GUID, archived 2023-09-27). www.sama.gov.sa's
own listed PDF URL for this Regulation returned a SAMA error page on every
attempt (direct curl, r.jina.ai proxy, WebFetch) and was not reachable as a
primary source in this environment.

EXTRACTION METHODOLOGY (two independent pipelines, reconciled): the source PDF
exhibits the same systematic Arabic bidi/justification text-ordering defect
documented for this corpus's rett_regulation/vat_regulation tracks, plus a
document-specific OCR defect misreading the hamza in ائتمان (credit) as
ث/ت/ن throughout. Two independent extractions were reconciled: (1) Tesseract
Arabic OCR of 300dpi page renders (correct reading order; occasional
character-level misreads and, in three places, dropped list items/clauses at
page boundaries); (2) PyMuPDF character-exact geometric extraction (exact
glyphs, RTL-reversed order), used to verify every digit and to recover the
OCR's dropped digits/clauses. Diacritics (tashkeel) and tatweel are stripped
uniformly. Arabic governs; no translation/paraphrase/interpretation.

55 articles, flat with 12 informal (unlabeled -- no فصل/باب numbering)
topical headings reproduced verbatim from the source document's own table of
contents: all 55 اصلية. A dedicated amendment search (رقم أق/13709 plus
"تعديل") found no evidence this Regulation has been amended since its
21/8/2011G issuance; rulebook.sama.gov.sa (SAMA's own regulator portal)
independently corroborates the instrument number/date, the 55-article count,
the 12 topical groupings, and numerous specific facts (capital thresholds,
retention periods, procedural day-counts) matching this track's extracted
text. See known_unresolved_discrepancies in the source artifact for open,
honestly-flagged gaps (Gazette issue/date not independently confirmed;
sama.gov.sa unreachable).

No legal text is altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "credit_information_regulation", "law", "official_source",
                   "credit_information_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "credit_information_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "credit_information_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "credit_information_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "credit_information_regulation_arabic_legal_llm",
                        "credit_information_regulation_legal_llm_001_055.json")

LAW_ID = "sa-credit-information-regulation-aq-13709-1432"
LAW_AR = "اللائحة التنفيذية لنظام المعلومات الائتمانية"
STATUS = "BAYANCB_WAYBACK_PRIMARY_TWO_PIPELINE_OCR_X_SAMA_RULEBOOK_SECONDARY_CROSS_VERIFIED"
KEY_RE = r"credit_information_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم المؤسسة الشركة الشركات العضو الأعضاء المستهلك").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    return int(re.match(KEY_RE, key).group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        text = a["text"]
        section = a.get("section_ar", "")
        label = a["number_label_ar"] + ((" — " + section) if section else "")
        ver.append({"law_key": "credit_information_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "CREDIT_INFORMATION_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": "",
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; PRIMARY source is a Wayback "
                                              "Machine snapshot of the bayancb.com (licensed "
                                              "Saudi credit bureau) born-digital PDF -- the "
                                              "prior-pass live URL's opaque media-GUID had "
                                              "rotated and 404'd, so a fresh CDX lookup located "
                                              "the identical 426561-byte/24-page filename under "
                                              "a different, earlier GUID via the Wayback "
                                              "Machine. www.sama.gov.sa's own listed PDF URL "
                                              "for this Regulation returned a SAMA error page "
                                              "on every attempt and was not reachable as a "
                                              "primary source. Text reconciled from two "
                                              "independent extraction pipelines (Tesseract OCR "
                                              "x PyMuPDF geometric cross-check); every digit "
                                              "and three OCR-dropped list items/clauses were "
                                              "recovered and verified against the PyMuPDF pass. "
                                              "Cross-checked for instrument number/date, "
                                              "55-article count, 12 topical groupings, and "
                                              "numerous specific facts against "
                                              "rulebook.sama.gov.sa (SAMA's own regulator "
                                              "portal). See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text -- "
                                              "in particular that the Official Gazette issue/"
                                              "date is not independently confirmed."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "credit-information-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "credit_information_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من اللائحة التنفيذية لنظام المعلومات الائتمانية" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("SAMA Governor's Decision No. "
                                                          "أق/13709 (22/9/1432H = 21 Aug "
                                                          "2011G) -- Wayback Machine snapshot "
                                                          "of bayancb.com's official PDF (a "
                                                          "prior live media-GUID URL had "
                                                          "rotated/404'd); www.sama.gov.sa's "
                                                          "own listed PDF URL was unreachable "
                                                          "in this environment; "
                                                          "rulebook.sama.gov.sa (SAMA's "
                                                          "regulator portal) independently "
                                                          "corroborates instrument number/"
                                                          "date and structure"),
                                     "source_authority_ar": ("قرار محافظ مؤسسة النقد العربي "
                                                            "السعودي رقم أق/13709 وتاريخ "
                                                            "22/9/1432هـ (الموافق "
                                                            "21/8/2011م) — عبر نسخة مؤرشفة "
                                                            "(Wayback Machine) للنص الرسمي "
                                                            "المنشور على موقع بيان "
                                                            "(bayancb.com)؛ تعذر الوصول "
                                                            "المباشر لملف sama.gov.sa في هذه "
                                                            "البيئة؛ تم التحقق الهيكلي "
                                                            "المستقل عبر بوابة "
                                                            "rulebook.sama.gov.sa"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "credit_information_regulation",
               "layer": "CREDIT_INFORMATION_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "publication_source": src.get("publication_source"),
               "publication_date_hijri": src.get("publication_date_hijri"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "parent_law": src.get("parent_law"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-credit-information-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (55 مادة؛ نص أصلي: 55 أصلية)",
               "title_en": ("Implementing Regulation of the Credit Information Law — "
                            "Arabic LLM-ready layer (55 records, original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 55], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Credit Information Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
