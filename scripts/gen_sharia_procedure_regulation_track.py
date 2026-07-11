#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Sharia Procedure implementing-regulation track.

Source: the official MOJ legal-portal consolidated text of the Implementing
Regulation of the Law of Sharia Procedure (Minister of Justice decree 39933,
19/5/1435H), fetched provision-by-provision and cross-verified against the
official MOJ PDF from the same portal (637 distinct provisions; 2 exact portal redundancies removed to
match the PDF; all MATCHES_PDF after visual adjudication of 6 flagged provisions).

DUAL-STATUS MODEL. This consolidated regulation carries two official statuses
per provision, both recorded, neither hidden:
  * pdf_document_status_ar — the badge the official PDF actually prints
    (اصلية/معدلة/ملغاة/مضافة). This is the GOVERNING anchor: it drives
    is_repealed / is_amended / is_added and the text we verify against the PDF.
  * portal_legal_status_ar — the MOJ portal's live legal database status. It
    additionally marks 149 provisions ملغاة (the evidence chapters + the
    cassation/reconsideration chapters) because the standalone Law of Evidence
    (نظام الإثبات م/43, 1443H) superseded them, even though the published
    regulation PDF still prints them in force. Those carry is_superseded=True
    and superseded_by_ar, and the retrieval title is marked so an LLM never
    presents a superseded provision as current.

Repealed provisions keep their full text and are FLAGGED, not deleted. Arabic
governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "sharia_procedure", "regulation", "official_source",
                   "sharia_procedure_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "sharia_procedure", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "sharia_procedure_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "sharia_procedure_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "sharia_procedure_arabic_legal_llm",
                        "sharia_procedure_regulation_legal_llm_001_637.json")

LAW_ID = "sa-sharia-procedure-regulation-39933-1435"
REG_AR = "اللائحة التنفيذية لنظام المرافعات الشرعية"
REG_SHORT_AR = "لائحة المرافعات الشرعية"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
SUPERSEDE_MARK = "مستبدلة بنظام الإثبات م/43"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الفقرة الدائرة").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [REG_SHORT_AR]


def _pos(key):
    return int(re.match(r"mur_reg_art_(\d+)$", key).group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_pos)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        pos = _pos(key)                       # document order 1..637 (unique, sortable)
        label = a["number_label_ar"]          # official X/Y citation label (may repeat)
        pdf_st = a["pdf_document_status_ar"]  # governing anchor status (as printed)
        portal_st = a["portal_legal_status_ar"]
        is_superseded = bool(a["is_superseded"])
        is_repealed = pdf_st == "ملغاة"
        is_amended = pdf_st == "معدلة"
        is_added = pdf_st == "مضافة"
        text = a["text"]
        rid = "sharia-procedure-regulation-llm-prov-%03d" % pos
        # retrieval-title marker: repealed-in-print, else superseded-by-Evidence-Law
        if is_repealed:
            mark = " (ملغاة)"
        elif is_superseded:
            mark = " (%s)" % SUPERSEDE_MARK
        else:
            mark = ""

        ver.append({"law_key": "sharia_procedure", "law_component": "implementing_regulation",
                    "language": "ar",
                    "record_layer": "SHARIA_PROCEDURE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "document_order": pos, "article_key": key,
                    "number_label_ar": label, "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "pdf_document_status_ar": pdf_st,
                    "portal_legal_status_ar": portal_st,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "is_superseded": is_superseded, "superseded_by_ar": a.get("superseded_by_ar"),
                    "amendment_history": a.get("history") or [],
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ consolidated regulation "
                                              "cross-verified against the official MOJ PDF; PDF badge "
                                              "is the governing status, portal legal status and "
                                              "Evidence-Law supersession also recorded."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})

        title_extra = mark
        llm.append({"law_id": LAW_ID, "law_component": "implementing_regulation",
                    "article_number": pos, "document_order": pos, "article_key": key,
                    "number_label_ar": label, "article_title_ar": label,
                    "section_ar": a.get("section_ar", ""),
                    "pdf_document_status_ar": pdf_st, "portal_legal_status_ar": portal_st,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "is_superseded": is_superseded, "superseded_by_ar": a.get("superseded_by_ar"),
                    "record_id": rid, "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — الفقرة %s%s" % (REG_SHORT_AR, label, title_extra),
                    "retrieval_title_ar": "%s - %s" % (REG_SHORT_AR, label),
                    "article_path": "sharia_procedure/regulation/provisions/%03d" % pos,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["الفقرة %s %s" % (label, REG_SHORT_AR),
                                          "%s الفقرة %s" % (REG_SHORT_AR, label),
                                          "لائحة المرافعات الشرعية %s" % label],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": REG_AR,
                                     "pdf_document_status_ar": pdf_st,
                                     "portal_legal_status_ar": portal_st,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "sharia_procedure",
               "layer": "SHARIA_PROCEDURE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "pdf_document_status_counts": src["pdf_document_status_counts"],
               "portal_legal_status_counts": src["portal_legal_status_counts"],
               "superseded_by_evidence_law_count": src["superseded_by_evidence_law_count"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True, "dual_status_model": True,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-sharia-procedure-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "implementing_regulation",
               "title_ar": REG_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (637 فقرة؛ نص موحّد بحالة مزدوجة)",
               "title_en": "Implementing Regulation of the Law of Sharia Procedure — Arabic LLM-ready layer (637 records, consolidated, dual-status)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "text_status": STATUS, "consolidated_amended_law": True, "dual_status_model": True,
               "pdf_document_status_counts": src["pdf_document_status_counts"],
               "portal_legal_status_counts": src["portal_legal_status_counts"],
               "superseded_by_evidence_law_count": src["superseded_by_evidence_law_count"],
               "superseded_by_ar": "نظام الإثبات (م/43)",
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Sharia Procedure Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
