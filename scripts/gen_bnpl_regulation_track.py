#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Rules for Regulating Buy-Now-Pay-Later (BNPL) Companies track
(قواعد تنظيم شركات الدفع الآجل (BNPL), Governor's Decision No. 145/م ش ت,
dated 23/5/1445H, transmitted via SAMA Circular No. 450360390000, dated
5/6/1445H = 17/12/2023G).

Standalone SAMA instrument governing BNPL companies (licensed joint-stock
finance companies practicing the deferred-payment/BNPL activity), issued
pursuant to the Finance Companies Control Law (Royal Decree No. M/51, dated
13/8/1433H) -- CONFIRMED DISTINCT from this corpus's already-ingested
finance_companies_law / finance_companies_regulation tracks (which this task
was explicitly told not to touch): those tracks govern finance companies in
general; this track is SAMA's own separate, subject-specific instrument for
the BNPL activity in particular, with its own licensing chapter, its own
credit-limit article, etc.

VERIFICATION TIER -- see bnpl_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: rulebook.sama.gov.sa (SAMA's own official Rulebook portal),
Arabic full-text 'entiresection' view (https://rulebook.sama.gov.sa/ar/
entiresection/6523, HTTP 200, fetched directly via curl, born-digital
structured HTML -- no OCR needed). Arabic governs; the equivalent English
entiresection view was fetched and used ONLY for structural/footnote-
substance cross-verification, never as a source of Arabic wording.

6 chapters (الفصول), 31 articles (المواد) -- all numbered, all falling
within one of the six chapters (unlike this corpus's debt_collection_
regulation track, whose final chapter carried no numbered article).

Article 22 (حدود الائتمان / Credit Limits) is the only معدلة (amended)
article: paragraph (1)'s SAR cap was raised from 5,000 to 10,000 via a
separate, later, independently-verified circular (No. 472038475, dated
4/7/1447H = 24/12/2025G) whose own page quotes the pre-amendment wording
verbatim -- both pre- and post-amendment text are preserved in this
article's history[] entry. Article 20 carries an in-page footnote about a
SAMA decision (14/2/1446H) suspending part of its application (administrative
fees up to 1% / SAR 50) WITHOUT editing Article 20's own text -- it therefore
stays اصلية, with the footnote's substance flagged as a
known_unresolved_discrepancy rather than modeled as a textual amendment.

An actual Arabic-original PDF of the promulgating transmittal circular was
independently located directly on rulebook.sama.gov.sa's own file store
(node 11012's download link) and confirmed to be a SCANNED (JBIG2 image,
zero extractable text layer), not born-digital, PDF -- its metadata matches
the entiresection page exactly but a full OCR pass was not completed this
run; documented as a known limitation, not used as the governing text.

All 31 articles are legal_status_ar-tagged (30 اصلية + 1 معدلة). No legal
text is altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "bnpl_regulation", "law", "official_source",
                   "bnpl_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "bnpl_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "bnpl_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "bnpl_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "bnpl_regulation_arabic_legal_llm",
                        "bnpl_regulation_legal_llm_001_031.json")

LAW_ID = "sa-bnpl-regulation-450360390000-1445"
LAW_AR = "قواعد تنظيم شركات الدفع الآجل (BNPL)"
STATUS = "SAMA_RULEBOOK_PRIMARY_AR_EN_BILINGUAL_HTML_AMENDMENT_NODE_CROSS_VERIFIED"
KEY_RE = r"bnpl_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة القواعد أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم البنك المركزي الشركة العميل").split())


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
        ver.append({"law_key": "bnpl_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "BNPL_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; PRIMARY source is "
                                              "rulebook.sama.gov.sa (SAMA's own official "
                                              "Rulebook portal), Arabic 'entiresection' "
                                              "full-text view (node 6523), HTTP 200, "
                                              "born-digital structured HTML (no OCR). "
                                              "Cross-checked structurally (chapter/article "
                                              "count and titles, plus footnote substance) "
                                              "against the equivalent English entiresection "
                                              "view -- English was NEVER used as a source of "
                                              "Arabic wording. See verification_methodology_note "
                                              "and known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text -- "
                                              "in particular Article 22's amended credit cap "
                                              "(history[] carries both pre- and post-amendment "
                                              "wording), Article 20's non-textual suspension "
                                              "footnote, and the transmittal circular's own "
                                              "unrelated Article-19 SAR-2,000 exemption note "
                                              "(preserved only in preamble_ar, not inline here)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "bnpl-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "bnpl_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من قواعد تنظيم شركات الدفع الآجل" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Governor's Decision No. 145/M Sh T, "
                                                          "dated 23/5/1445H, transmitted via SAMA "
                                                          "Circular No. 450360390000, dated "
                                                          "5/6/1445H = 17/12/2023G -- "
                                                          "rulebook.sama.gov.sa (issuing "
                                                          "Authority's own site)"
                                                          + ("; Article 22 amended by Circular "
                                                             "No. 472038475, dated 4/7/1447H"
                                                             if is_amended else "")),
                                     "source_authority_ar": ("قرار معالي محافظ البنك المركزي "
                                                            "السعودي رقم (145/م ش ت) وتاريخ "
                                                            "23/5/1445هـ، المنقول بتعميم البنك "
                                                            "المركزي رقم (450360390000) وتاريخ "
                                                            "5/6/1445هـ الموافق 17/12/2023م — "
                                                            "الموقع الرسمي لبوابة SAMA "
                                                            "Rulebook (rulebook.sama.gov.sa)"
                                                            + ("؛ عُدّلت هذه المادة بتعميم رقم "
                                                               "(472038475) وتاريخ 4/7/1447هـ"
                                                               if is_amended else "")),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "bnpl_regulation",
               "layer": "BNPL_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "governor_decision": src.get("governor_decision"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "amendment_history": src.get("amendment_history"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-bnpl-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (31 مادة، 30 اصلية و1 معدلة)",
               "title_en": ("Rules for Regulating Buy-Now-Pay-Later (BNPL) Companies — Arabic "
                            "LLM-ready layer (31 records, 30 original/اصلية + 1 amended/معدلة)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 31], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready BNPL Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
