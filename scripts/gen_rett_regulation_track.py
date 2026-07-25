#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Real Estate Transaction Tax
Law track (اللائحة التنفيذية لنظام رسوم التصرفات العقارية, ZATCA Board of
Directors Decision No. (01-03-25), 24/09/1446H = 24 March 2025G, published
Umm al-Qura Gazette Issue (5080)).

This is the companion-regulation track for this corpus's own rett_law track
(see sources/rett/law/official_source/rett_law_official_source.json, which
notes: "The RETT has its own separate ZATCA Implementing Regulation ...; it
is a distinct companion instrument and is deliberately NOT extracted in this
base-Law track."). This track ingests that companion Implementing
Regulation.

VERIFICATION TIER -- see rett_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: ZATCA's (Zakat, Tax and Customs Authority) own official
Arabic PDF of the RETT Implementing Regulation, downloaded directly from
zatca.gov.sa (HTTP 200, 21 pages, born-digital). laws.boe.gov.sa was checked
first per this corpus's standard methodology but -- as with this corpus's
vat_regulation and income_tax_regulation tracks -- has NO dedicated lawId
page for this Board-level Implementing Regulation (a direct site search
returns only the base RETT Law's own existing lawId page, already tracked
in this corpus at sources/rett/).

EXTRACTION METHODOLOGY (two independent pipelines, reconciled): the source
PDF exhibits the same systematic Arabic bidi/justification text-ordering
defect documented for this corpus's vat_regulation track. Two independent
extractions were reconciled: (1) Tesseract Arabic OCR of 300dpi page
renders (correct reading order, occasional character-level misreads,
notably confusable list-marker digits/letters); (2) PyMuPDF character-exact
geometric extraction (exact glyphs, RTL-reversed order), used to verify
every percentage, day/year count and the predecessor regulation's number/
date, and to correct OCR list-marker misreads by cross-reference against
this corpus's own already-verified rett_law Article 3(a) 21-item
enumeration (which this Regulation's Article 3(a) elaborates in identical
order). Diacritics (tashkeel) and tatweel are stripped uniformly. Arabic
governs; no translation/paraphrase/interpretation.

15 articles, flat (no chapters): all 15 اصلية. This is a brand-new
(24 March/9 April 2025) instrument with NO amendments confirmed to date.
IMPORTANT: this track's commissioning brief asserted the Regulation was
"later amended" per spa.gov.sa/N2095607 and argaam.com; independent
verification this pass shows those items are dated May 2024 -- eleven
months BEFORE this Regulation was issued -- and in fact describe amendments
to the PRE-EXISTING predecessor Implementing Regulation (Ministerial
Resolution No. (712), 15/2/1442H), not to this Regulation. See
known_unresolved_discrepancies in the source artifact for the full
chronology and the predecessor-regulation cross-reference recorded in this
Regulation's own Article 14.

No legal text is altered. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "rett_regulation", "law", "official_source",
                   "rett_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "rett_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "rett_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "rett_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "rett_regulation_arabic_legal_llm",
                        "rett_regulation_legal_llm_001_015.json")

LAW_ID = "sa-rett-regulation-01-03-25-1446"
LAW_AR = "اللائحة التنفيذية لنظام رسوم التصرفات العقارية"
STATUS = "ZATCA_PORTAL_PRIMARY_TWO_PIPELINE_OCR_X_SECONDARY_CROSS_VERIFIED"
KEY_RE = r"rett_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة الضريبة الضريبية للضريبة").split())


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
        title = a.get("title_ar", "")
        label = a["number_label_ar"] + ((": " + title) if title else "")
        ver.append({"law_key": "rett_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "RETT_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; PRIMARY source is "
                                              "zatca.gov.sa (the issuing Authority's own "
                                              "official PDF, born-digital, HTTP 200) -- "
                                              "laws.boe.gov.sa was checked first per "
                                              "standard methodology but has no dedicated "
                                              "lawId page for this Implementing "
                                              "Regulation. Text reconciled from two "
                                              "independent extraction pipelines "
                                              "(Tesseract OCR x PyMuPDF geometric "
                                              "cross-check); every percentage, day/year "
                                              "count and the predecessor regulation's "
                                              "number/date were independently verified. "
                                              "Cross-checked for decision number/date and "
                                              "15-article structure against snadlaw.sa "
                                              "and qanoonsa.com. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the "
                                              "source artifact before relying on this "
                                              "track's text -- in particular the "
                                              "correction of this track's own "
                                              "commissioning brief's mistaken premise "
                                              "that this Regulation was 'later amended' "
                                              "per spa.gov.sa/N2095607 (that item in fact "
                                              "predates this Regulation by 11 months and "
                                              "describes an amendment of the different, "
                                              "predecessor Ministerial Resolution 712 "
                                              "regulation)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "rett-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "rett_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من اللائحة التنفيذية لنظام رسوم التصرفات العقارية" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("ZATCA Board of Directors "
                                                          "Decision No. (01-03-25) "
                                                          "(24/09/1446H = 24 Mar 2025G), "
                                                          "published Umm al-Qura Gazette "
                                                          "Issue (5080) -- zatca.gov.sa "
                                                          "(issuing Authority's own site); "
                                                          "laws.boe.gov.sa has no "
                                                          "dedicated lawId page for this "
                                                          "Implementing Regulation"),
                                     "source_authority_ar": ("قرار مجلس إدارة هيئة الزكاة "
                                                            "والضريبة والجمارك رقم "
                                                            "(01-03-25) وتاريخ 24/09/1446هـ "
                                                            "(الموافق 24/03/2025م)، المنشور "
                                                            "في جريدة أم القرى العدد "
                                                            "(5080) — الموقع الرسمي لهيئة "
                                                            "الزكاة والضريبة والجمارك "
                                                            "(zatca.gov.sa)؛ بوابة هيئة "
                                                            "الخبراء لا تملك صفحة مخصصة "
                                                            "لهذه اللائحة التنفيذية"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "rett_regulation",
               "layer": "RETT_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "publication_source": src.get("publication_source"),
               "publication_date_hijri": src.get("publication_date_hijri"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "parent_law": src.get("parent_law"),
               "predecessor_regulation": src.get("predecessor_regulation"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-rett-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (15 مادة؛ نص أصلي: 15 أصلية)",
               "title_en": ("Implementing Regulation of the Real Estate Transaction Tax "
                            "Law — Arabic LLM-ready layer (15 records, original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready RETT Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
