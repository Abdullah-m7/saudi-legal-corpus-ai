#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Arrangements for Hearing Claims to Prove Marriage Contracts
Concluded Without Required Official Permission (الترتيبات الخاصة بسماع الدعوى
بإثبات عقد الزواج الذي أُبرم دون إذن الجهة المختصة فيما يشترط له الإذن).

Source: the official MOJ legal-portal text (Minister of Justice Decision
5121, 3/7/1447H), fetched article-by-article (get-Section-Changes, a single
current-text entry with no history for every article) and cross-verified
against the official MOJ PDF. This PDF is a pure scanned/image document with
NO extractable text layer at all (PyMuPDF get_text() returns empty on every
page), so verification relied entirely on 300dpi tesseract-ara OCR per page,
segmented per article and scored with a windowed difflib SequenceMatcher
ratio against NFKC-normalized/diacritic-stripped/hamza-taa-marbuta-folded/
digit-folded text. 8 of 10 articles matched the >=0.90 floor outright (mean
of those 8: 0.9689); overall mean 0.9425, min 0.7848. Articles 5 and 10 —
the last article on each of the two content pages — scored below floor
(0.8889, 0.7848) purely as an OCR-segmentation artifact (trailing
notary-stamp/footer noise before the next المادة boundary), not a text
mismatch; both were individually visually adjudicated against 400dpi zoomed
crops of the rendered PDF and confirmed exact verbatim matches. This
instrument is IN FORCE. FRESH FULL ISSUANCE: all 10 اصلية (0 معدلة / 0 ملغاة
/ 0 مضافة). No source anomalies found — all 10 articles read identically in
the portal DB and the official PDF. Substantive dependencies found in the
article text: Article 1 defines النظام as نظام الأحوال الشخصية (law_key
personal_status) and اللائحة as لائحة زواج السعودي بغير سعودية والسعودية
بغير سعودي (law_key marriage_non_saudi, already ingested); Article 5
cross-references Articles 9 and 11 of the Personal Status Law (minor /
unsound-mind marriage authorization).

Articles are numbered by their ordinal position (1..10; no مكرر), flat
structure with no chapter/section wrapper (section_ar empty for every
article).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "marriage_contract_hearing", "regulation", "official_source",
                   "marriage_contract_hearing_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "marriage_contract_hearing", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "marriage_contract_hearing_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "marriage_contract_hearing_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "marriage_contract_hearing_arabic_legal_llm",
                        "marriage_contract_hearing_regulation_legal_llm_001_010.json")

LAW_ID = "sa-marriage-contract-hearing-regulation-1447"
LAW_AR = "الترتيبات الخاصة بسماع الدعوى بإثبات عقد الزواج الذي أُبرم دون إذن الجهة المختصة فيما يشترط له الإذن"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"marriage_contract_hearing_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())


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
        text = a["text"]
        ver.append({"law_key": "marriage_contract_hearing", "law_component": "regulation", "language": "ar",
                    "record_layer": "MARRIAGE_CONTRACT_HEARING_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ portal text cross-verified "
                                              "against the official MOJ PDF (verbatim; the PDF is a pure "
                                              "scanned/image document with no extractable text layer, so "
                                              "verification relied on 300dpi tesseract-ara OCR per page, "
                                              "segmented per article and scored with a windowed difflib "
                                              "SequenceMatcher ratio against NFKC-normalized/"
                                              "diacritic-stripped/hamza-taa-marbuta-folded/digit-folded "
                                              "text; 8 of 10 articles matched the >=0.90 floor outright, "
                                              "mean 0.9425, min 0.7848; articles 5 and 10, each the last "
                                              "article on its PDF page, were individually visually "
                                              "adjudicated by reading 400dpi zoomed crops of the exact "
                                              "rendered PDF regions against the portal text -- the low "
                                              "automated scores were an OCR-segmentation artifact from "
                                              "trailing page-footer/notary-stamp noise, not a text "
                                              "mismatch -- and confirmed as exact verbatim matches. All "
                                              "10 articles were additionally read in full against the "
                                              "rendered 400dpi PDF page images as a direct visual "
                                              "cross-check, alongside a 600dpi crop of the decree line "
                                              "confirming decree number 5121 dated 3/7/1447H)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "marriage-contract-hearing-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "marriage_contract_hearing/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d الترتيبات الخاصة بسماع الدعوى بإثبات عقد الزواج" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Minister of Justice — official MOJ legal portal",
                                     "source_authority_ar": "وزير العدل — المنصة القانونية الرسمية لوزارة العدل",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "marriage_contract_hearing",
               "layer": "MARRIAGE_CONTRACT_HEARING_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-marriage-contract-hearing-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (10 مواد؛ إصدار جديد كامل: 10 أصلية)",
               "title_en": "Arrangements for Hearing Claims to Prove Marriage Contracts Concluded Without Required Official Permission — Arabic LLM-ready layer (10 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 10], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Marriage Contract Hearing Arrangements records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
