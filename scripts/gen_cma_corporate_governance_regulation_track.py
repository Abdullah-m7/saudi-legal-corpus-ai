#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the CMA Corporate Governance Regulations track (لائحة حوكمة
الشركات, CMA Board Resolution No. 2017-16-8, dated 16/5/1438H = 13/2/2017G,
issued pursuant to the Companies Law and the Capital Market Law, as amended
by Resolutions 2018-35-1, 2018-52-4, 2022-94-1 and 2023-5-8).

VERIFICATION TIER -- see cma_corporate_governance_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: the official regulation PDF hosted on cma.gov.sa (CMA's own
regulations domain; cma.org.sa 301-redirects to it) --
https://cma.gov.sa/RulesRegulations/Regulations/Documents/CorpGovReg.pdf --
fetched directly this pass (HTTP 200, 65-page born-digital PDF). This is the
CURRENT, CMA-published, consolidated text as amended through Resolution
2023-5-8 (25/6/1444H = 18/1/2023G).

CRITICAL CORRECTION OF THIS TRACK'S OWN COMMISSIONING PREMISE: the prior
research brief described the instrument as "CMA Board Decision 1-212-2006 ...
amended 15/9/1440H". Independent verification found Resolution 1-212-2006
(21/10/1427H) was a REAL, separate, EARLIER regulation that was FULLY
SUPERSEDED (not merely amended) by this entirely new regulation in 2017. This
track ingests the CURRENT (2017-issued, 2023-amended) 95-article regulation --
NOT the ~19-article figure a prior light pass cited (which almost certainly
described the superseded 2006 instrument, not the current law). The 15/9/1440H
(2019) amendment is independently confirmed REAL via a CMA press release, but
could not be matched with certainty to a footnote in the CURRENT numbering
(most likely now Article 44, given the 2023 resolution's confirmed
renumbering of the regulation) -- see known_unresolved_discrepancies in the
source artifact for the full account; Article 44 is NOT flagged معدلة absent
a current-text footnote confirming it.

95 articles, 12 أبواب (5 further divided into فصول). 11 articles carry a
confirmed, footnote-cited textual/status amendment (20, 24, 27, 37, 52, 54,
73, 74, 75, 87, 90) via 4 distinct CMA Board Resolutions (2018-35-1,
2018-52-4, 2022-94-1, 2023-5-8) plus the original 2017-16-8 issuance. No
pre-amendment wording is reconstructed for any amended article -- current
text only, per this corpus's zero-fabrication policy.

The source PDF's embedded font also carries a confirmed text-layer defect
(certain two-letter Arabic sequences extracted in reversed order -- at least
5 distinct letter-pairs confirmed, corrected via an explicit, individually
verified whole-word substitution list, never a blind positional rule) --
fully disclosed in the source artifact, including a residual-risk note for
low-frequency vocabulary not individually re-verified against page images.

No legal text is altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cma_corporate_governance_regulation", "law", "official_source",
                    "cma_corporate_governance_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "cma_corporate_governance_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "cma_corporate_governance_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "cma_corporate_governance_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "cma_corporate_governance_regulation_arabic_legal_llm",
                         "cma_corporate_governance_regulation_legal_llm_001_095.json")

LAW_ID = "sa-cma-corporate-governance-regulation-2017-16-8"
LAW_AR = "لائحة حوكمة الشركات"
STATUS = "CMA_GOV_SA_OFFICIAL_PDF_PRIMARY_X_LIGATURE_DEFECT_CORRECTED_X_AMENDMENT_FOOTNOTE_CROSSCHECK"
KEY_RE = r"cma_corporate_governance_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الشركة الإدارة مجلس أعضاء").split())


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
        label = a["number_label_ar"] + ((" — " + title) if title else "")
        ver.append({"law_key": "cma_corporate_governance_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "CMA_CORPORATE_GOVERNANCE_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; PRIMARY source is the "
                                              "official regulation PDF on cma.gov.sa "
                                              "(CMA's own regulations-hosting domain), "
                                              "fetched directly (HTTP 200, born-digital "
                                              "PDF text layer, a confirmed font/CMap "
                                              "letter-transposition defect corrected via "
                                              "an explicit, individually verified "
                                              "whole-word list -- never a blind "
                                              "positional rule). See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the "
                                              "source artifact before relying on this "
                                              "track's text -- in particular: this "
                                              "regulation FULLY SUPERSEDED (did not "
                                              "merely amend) the earlier CMA Board "
                                              "Resolution 1-212-2006 (21/10/1427H); the "
                                              "current text is 95 articles, not the "
                                              "~19 a prior light pass cited; and the "
                                              "15/9/1440H (2019) amendment is confirmed "
                                              "real via a secondary CMA press source "
                                              "but could not be matched with certainty "
                                              "to a footnote in the current numbering."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "cma-corporate-governance-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "cma_corporate_governance_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من لائحة حوكمة الشركات" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("CMA Board Resolution No. "
                                                          "(2017-16-8), dated 16/5/1438H "
                                                          "(13/2/2017G) -- cma.gov.sa "
                                                          "(issuing Authority's own "
                                                          "regulations domain); amended by "
                                                          "Resolutions 2018-35-1, "
                                                          "2018-52-4, 2022-94-1 and "
                                                          "2023-5-8 (25/6/1444H = "
                                                          "18/1/2023G, the largest, "
                                                          "renumbering amendment)"),
                                     "source_authority_ar": ("قرار مجلس هيئة السوق المالية "
                                                            "رقم 2017-16-8 وتاريخ "
                                                            "16/5/1438هـ (الموافق "
                                                            "13/2/2017م) — الموقع الرسمي "
                                                            "لهيئة السوق المالية "
                                                            "(cma.gov.sa)؛ عُدلت بموجب "
                                                            "قرارات 2018-35-1، 2018-52-4، "
                                                            "2022-94-1، و 2023-5-8 "
                                                            "(25/6/1444هـ الموافق "
                                                            "18/1/2023م، وهو أكبر تعديل "
                                                            "وأعاد ترقيم اللائحة)"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "cma_corporate_governance_regulation",
               "layer": "CMA_CORPORATE_GOVERNANCE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "amending_instruments": src.get("amending_instruments"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-cma-corporate-governance-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (95 مادة؛ 84 أصلية، 11 معدلة)",
               "title_en": ("CMA Corporate Governance Regulations — Arabic LLM-ready "
                            "layer (95 records; 84 original, 11 amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 95], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready CMA Corporate Governance Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
