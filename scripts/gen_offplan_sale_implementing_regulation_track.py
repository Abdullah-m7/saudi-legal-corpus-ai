#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Off-Plan Sale and Lease of Real
Estate Projects Law track ("WAFI") -- اللائحة التنفيذية لنظام بيع وتأجير
مشروعات عقارية على الخارطة, REGA Board of Directors Resolution No.
(ق/م/إ/هـ/8/2024/ت) dated 20/10/1445H (29/4/2024G) -- published in Umm
Al-Qura Official Gazette on 2 Dhul-Qi'dah 1445H (10/5/2024G). This is the
Implementing Regulation of the parent offplan_sale_law track (Royal Decree
No. M/44), issued pursuant to that Law's own Article 28.

VERIFICATION TIER -- see
offplan_sale_implementing_regulation_official_source.json's own
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE (all 49 articles): uqn.gov.sa (Umm Al-Qura Official Gazette,
the constitutionally-designated publication organ), the regulation's own
dedicated page (https://uqn.gov.sa/details?p=24924, HTTP 200, fetched
directly via curl, born-digital structured HTML -- no OCR needed). Parsed
with BeautifulSoup in document order; the page's own #article-content
element reproduces the decree heading and all 49 articles in full, with zero
reachability gap (unlike some other tracks in this corpus). Four Word-pasted
<table> elements (Article 5 x2, Article 6, Article 11) were converted
row-by-row into structured prose, never naive tag-stripped, preserving every
cell's content under its own original column-header label.

STRUCTURAL (not verbatim) SECOND OFFICIAL SOURCE: REGA's own PDF
(rega.gov.sa/media/xftbcgd5/...pdf, 24 pages, born-digital text layer)
agrees exactly on title, decree date, and total article count (49, same
final article ordinal) -- but its embedded font's ToUnicode CMap produces a
systematic two-letter transposition artifact around the "ال" definite
article, making it unsafe for word-level verbatim cross-check (see
known_unresolved_discrepancies). No full-text secondary aggregator
cross-check was available this pass (qanoonsa.com stub-only; nezams.com no
dedicated page for this instrument; argaam.com structural-only, likely
describing an earlier draft, via a WebSearch-tool-mediated summary).

VERIFICATION TIER: TIER_2 (one official primary source reached with zero
gap; structurally, not verbatim, cross-checked against a second official
source). See known_unresolved_discrepancies for every non-obvious judgment
call in this build (the font-cmap corruption, the unlabeled first section,
the absent decree preamble, the qanoonsa.com stub page, the unreachable
nezams.com dedicated page, the argaam.com draft-stage caveat, and BOE
unreachability) before relying on this track's text.

All 49 articles are اصلية (single, first-and-only-confirmed edition since
29/4/2024; no subsequent amendment to this text identified this pass). No
legal text is altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "offplan_sale_implementing_regulation", "law",
                    "official_source",
                    "offplan_sale_implementing_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "offplan_sale_implementing_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "offplan_sale_implementing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "offplan_sale_implementing_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "offplan_sale_implementing_regulation_arabic_legal_llm",
                         "offplan_sale_implementing_regulation_legal_llm_001_049.json")

LAW_ID = "sa-offplan-sale-implementing-regulation-rega-8-2024-t-1445"
LAW_AR = "اللائحة التنفيذية لنظام بيع وتأجير مشروعات عقارية على الخارطة"
KEY_RE = r"offplan_sale_implementing_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة النظام أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة المطور المشروع العقاري").split())


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
        title = a.get("article_title_ar", "")
        label = a["number_label_ar"] + ((": " + title) if title else "")
        status = a["status"]
        source_tier = a.get("source_tier")
        ver.append({"law_key": "offplan_sale_implementing_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "OFFPLAN_SALE_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": status,
                    "source_tier": source_tier,
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": status,
                    "governing_source_note": ("Arabic governs. Full text taken verbatim from "
                                              "uqn.gov.sa (Umm Al-Qura Official Gazette, the "
                                              "issuing authority's own constitutionally-"
                                              "designated publication organ), reached directly "
                                              "with zero reachability gap. Structurally (not "
                                              "verbatim) cross-checked against REGA's own PDF "
                                              "(rega.gov.sa) -- title, decree date, and article "
                                              "count/last-article ordinal all match exactly, but "
                                              "that PDF's own text layer carries a systematic "
                                              "font-cmap letter-transposition artifact making it "
                                              "unsafe for word-level cross-check. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "offplan-sale-implementing-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "offplan_sale_implementing_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من اللائحة التنفيذية لنظام بيع وتأجير مشروعات "
                                          "عقارية على الخارطة" % a["number_label_ar"]],
                    "text_status": status,
                    "source_trust": {"source_authority": ("REGA Board of Directors Resolution "
                                                          "No. (Q/M/I/H/8/2024/T), dated "
                                                          "20/10/1445H = 29/4/2024G -- published "
                                                          "in full in Umm Al-Qura Official "
                                                          "Gazette, 2 Dhul-Qi'dah 1445H = "
                                                          "10/5/2024G. This article: uqn.gov.sa "
                                                          "primary text, structurally "
                                                          "cross-checked (title/date/article-"
                                                          "count only, not verbatim) against "
                                                          "REGA's own PDF."),
                                     "source_authority_ar": ("قرار مجلس إدارة الهيئة العامة "
                                                            "للعقار رقم (ق/م/إ/هـ/8/2024/ت) "
                                                            "وتاريخ 20/10/1445هـ الموافق "
                                                            "29/4/2024م — منشورة كاملة في جريدة "
                                                            "أم القرى بتاريخ 2 ذو القعدة 1445هـ "
                                                            "الموافق 10/5/2024م. هذه المادة: نص "
                                                            "أساسي من uqn.gov.sa، مصالَب بنيوياً "
                                                            "فقط (العنوان/التاريخ/عدد المواد لا "
                                                            "النص الحرفي) مقابل نسخة الهيئة "
                                                            "العامة للعقار PDF."),
                                     "source_status": status.lower(),
                                     "source_tier": source_tier,
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": status},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "offplan_sale_implementing_regulation",
               "layer": "OFFPLAN_SALE_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "source_tier_counts": src.get("source_tier_counts"),
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "parent_law_track_id": src.get("parent_law_track_id"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "gazette_publication": src.get("gazette_publication"),
               "amendment_history": src.get("amendment_history"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-offplan-sale-implementing-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (49 مادة، اصلية جميعها)",
               "title_en": ("Implementing Regulation of the Off-Plan Sale and Lease of Real "
                            "Estate Projects Law (\"WAFI\") — Arabic LLM-ready layer (49 "
                            "records, all original/اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 49], "consolidated_amended_law": False,
               "status_counts": src["status_counts"],
               "source_tier_counts": src.get("source_tier_counts"),
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Offplan Sale Implementing Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
