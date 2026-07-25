#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Non-Saudi Real Estate Ownership
Law track (اللائحة التنفيذية لنظام تملك غير السعوديين للعقار).

This regulation is EXTREMELY FRESH (published essentially the same week as
this track's construction): Official Gazette (Umm al-Qura) display date 18
Muharram 1448H (3 July 2026); Council of Ministers decision/issuance date per
rega.gov.sa ~8 Muharram 1448H (~23 June 2026, corroborated by aleqt.com's
cabinet-approval report dated 23 June 2026). 14 articles + a penalties annex
table explicitly referenced as binding by Article 12 ("العقوبات الواردة في
الجدول الملحق باللائحة") -- not a courtesy attachment, so it is modeled here
as its own additional record (record 15), following this corpus's
labor_annex1 precedent for mechanically-linearized official tables.

VERIFICATION TIER -- see sources/foreign_ownership_regulation/law/
official_source/foreign_ownership_regulation_official_source.json's
verification_methodology_note and known_unresolved_discrepancies for the full
account. Summary: TWO independent PRIMARY Saudi government sources --
uqn.gov.sa (Official Umm al-Qura Gazette portal) and rega.gov.sa (Real Estate
General Authority, the administering/issuing authority's own legislation
portal) -- were both reached live (HTTP 200) and both host the complete
regulation text directly as HTML (not a scanned PDF). Article-by-article
normalized comparison: 8/14 articles byte-identical; the other 6 differ only
in single-character/punctuation-level formatting (a space, a comma glyph, a
ZWNJ, one grammatical gender-agreement letter, one comma) with zero legal-
substance difference; the penalties annex differs in exactly 3 one-word
violation-description labels (rows 5, 6, 7) with no difference in any penalty
amount or tier. This satisfies this corpus's own documented TIER_1 criterion
(two independent official entities agreeing, no unresolved access gap) ->
TIER_1_PRIMARY_MULTI_SOURCE.

CAVEATS DESPITE TIER_1 (all disclosed in known_unresolved_discrepancies, read
before relying on this track for a precise legal/administrative citation):
this Regulation is days old at research time; a potential third primary
source (ncar.gov.sa, successor to laws.boe.gov.sa) was unreachable this pass
(TLS connection reset / HTTP 503, not circumvented); no explicit Council of
Ministers resolution NUMBER nor Umm al-Qura gazette issue NUMBER could be
confirmed from any primary source (a secondary aggregator's claim of
"Resolution No. 43" / "issue No. 5169" is NOT adopted, because that same
aggregator independently misstates the base law's own decree date elsewhere);
and this task's own prior-research briefing's claimed gazette date (11 Safar
1448H) could not be reproduced this pass against the live uqn.gov.sa fetch
(18 Muharram 1448H) -- the directly re-observed date is adopted instead, with
the conflict disclosed rather than silently dropped.

14 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة) + 1 penalties-table record
(also اصلية). No فصول/أبواب (chapters/parts) -- a flat sequential 1..14
article structure. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "foreign_ownership_regulation", "law", "official_source",
                   "foreign_ownership_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "foreign_ownership_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "foreign_ownership_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "foreign_ownership_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "foreign_ownership_regulation_arabic_legal_llm",
                        "foreign_ownership_regulation_legal_llm_001_015.json")

LAW_ID = "sa-foreign-ownership-regulation-2026"
LAW_AR = "اللائحة التنفيذية لنظام تملك غير السعوديين للعقار"
STATUS = "UQN_GAZETTE_PRIMARY_X_REGA_PRIMARY_CROSS_VERIFIED"
N_ARTICLES = 14
KEY_RE = r"foreign_ownership_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي غير السعودي السعودية الهيئة").split())


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


GOV_NOTE = ("Arabic governs; TWO independent PRIMARY Saudi government sources -- uqn.gov.sa "
            "(Official Umm al-Qura Gazette portal) and rega.gov.sa (Real Estate General "
            "Authority, the administering/issuing authority's own legislation portal) -- were "
            "both reached live this pass and both host the complete text directly as HTML. "
            "8/14 articles byte-identical between the two; the rest differ only at the "
            "punctuation/formatting level with zero legal-substance difference -> TIER_1. "
            "This Regulation is extremely fresh (days old); see known_unresolved_discrepancies "
            "in the source artifact for the decree-number/gazette-issue-number caveats before "
            "relying on this track for a precise legal/administrative citation.")

SRC_AUTH = ("Council of Ministers Resolution (exact number unconfirmed from any primary "
            "source -- see known_unresolved_discrepancies), implementing Article 13 of the "
            "Non-Saudi Real Estate Ownership Law (Royal Decree M/14, 19/1/1447H). Full text "
            "cross-verified between uqn.gov.sa (Official Gazette, PRIMARY) and rega.gov.sa "
            "(Real Estate General Authority, PRIMARY) -> TIER_1_PRIMARY_MULTI_SOURCE.")

SRC_AUTH_AR = ("قرار مجلس الوزراء (رقمه غير مؤكَّد من أي مصدر أساسي -- انظر "
               "known_unresolved_discrepancies)، تنفيذا للمادة الثالثة عشرة من نظام تملك غير "
               "السعوديين للعقار (المرسوم الملكي م/14، 19/1/1447هـ). النص الكامل متقاطع بين "
               "uqn.gov.sa (الجريدة الرسمية، مصدر أساسي) وrega.gov.sa (الهيئة العامة للعقار، "
               "مصدر أساسي) -- TIER_1_PRIMARY_MULTI_SOURCE.")


def _linearize_penalty_row(row):
    cells = ["%s: %s" % (c["label_ar"], c["value_ar"]) for c in row["penalty_cells"]
              if str(c["value_ar"]).strip()]
    return "البند %d: %s\n%s" % (row["band_no"], row["violation_ar"], " | ".join(cells))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    penalties_table = src["penalties_table"]
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        text = a["text"]
        ver.append({"law_key": "foreign_ownership_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "FOREIGN_OWNERSHIP_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "cross_source_variance_note": a.get("cross_source_variance_note", ""),
                    "official_text_status": STATUS,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "foreign-ownership-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "foreign_ownership_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d من اللائحة التنفيذية لنظام تملك غير السعوديين للعقار" % n],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    # record 15: the penalties annex table (mechanical linearization; every
    # cell verbatim, only row/column labels and separators added)
    p_lines = [_linearize_penalty_row(r) for r in penalties_table["rows"]]
    p_text = "\n".join(p_lines)
    p_key = "foreign_ownership_regulation_penalties_table"
    p_n = N_ARTICLES + 1
    ver.append({"law_key": "foreign_ownership_regulation", "law_component": "regulation",
                "language": "ar",
                "record_layer": "FOREIGN_OWNERSHIP_REGULATION_PENALTIES_TABLE_VERIFIED",
                "article_number": p_n, "is_mukarrar": False, "article_key": p_key,
                "number_label_ar": penalties_table["title_ar"],
                "section_ar": "ملحق العقوبات",
                "article_text_verified": p_text,
                "verification_status": penalties_table["status"],
                "legal_status_ar": penalties_table["legal_status_ar"],
                "is_repealed": False, "is_amended": False, "is_added": False,
                "amendment_history": [],
                "row_count": penalties_table["row_count"],
                "table_linearization_note": ("Mechanical linearization of the official annex "
                                              "table referenced as binding by Article 12: every "
                                              "cell verbatim; only row numbers, column labels "
                                              "and separators added."),
                "cross_source_variance_note": penalties_table.get("cross_source_variance_note", ""),
                "official_text_status": STATUS,
                "governing_source_note": GOV_NOTE,
                "translation_performed": False, "legal_interpretation_performed": False,
                "summarized_or_paraphrased": False, "english_used_for_correction": False})
    llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": p_n,
                "is_mukarrar": False, "article_key": p_key,
                "article_title_ar": penalties_table["title_ar"],
                "section_ar": "ملحق العقوبات",
                "legal_status_ar": penalties_table["legal_status_ar"],
                "is_repealed": False, "is_amended": False, "is_added": False,
                "record_id": "foreign-ownership-regulation-llm-penalties-table",
                "record_type": "verified_arabic_table", "language": "ar",
                "governing_text_language": "ar", "article_text_ar": p_text,
                "article_text_hash_sha256": hashlib.sha256(p_text.encode("utf-8")).hexdigest(),
                "row_count": penalties_table["row_count"],
                "llm_title_ar": "%s — %s" % (LAW_AR, penalties_table["title_ar"]),
                "retrieval_title_ar": "%s - جدول تصنيف المخالفات والعقوبات" % LAW_AR,
                "article_path": "foreign_ownership_regulation/law/penalties_table",
                "keywords_ar": _kw(p_text),
                "search_queries_ar": ["جدول عقوبات اللائحة التنفيذية لنظام تملك غير السعوديين للعقار",
                                      "عقوبات مخالفة تملك غير السعوديين للعقار",
                                      "جدول تصنيف مخالفات نظام تملك غير السعوديين للعقار"],
                "text_status": penalties_table["status"],
                "source_trust": {"source_authority": SRC_AUTH, "source_authority_ar": SRC_AUTH_AR,
                                 "source_status": penalties_table["status"].lower(),
                                 "source_document_ar": LAW_AR,
                                 "legal_status_ar": penalties_table["legal_status_ar"],
                                 "verification_status": penalties_table["status"]},
                "translation_performed": False, "legal_interpretation_performed": False,
                "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "foreign_ownership_regulation",
               "layer": "FOREIGN_OWNERSHIP_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "article_count": N_ARTICLES,
               "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "verification_tier": src["verification_tier"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-foreign-ownership-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (14 مادة + ملحق العقوبات)",
               "title_en": ("Implementing Regulation of the Non-Saudi Real Estate Ownership "
                            "Law — Arabic LLM-ready layer (14 articles + 1 penalties-table "
                            "record, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, N_ARTICLES], "text_status": STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Foreign Ownership Regulation records "
          "(14 articles + 1 penalties table)" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
