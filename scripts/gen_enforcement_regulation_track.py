#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Enforcement implementing-regulation track.

Source: the official MOJ legal-portal consolidated text of the Implementing
Regulation of the Law of Enforcement (Minister of Justice decision 526,
20/2/1439H), fetched provision-by-provision and cross-verified against the
official MOJ PDF (273/273 MATCHES_PDF). Clause-labeled (X/Y) and keyed by
document order 1..273. This regulation is IN FORCE and lightly amended (by
decision 7207): 266 اصلية / 2 معدلة / 2 ملغاة / 3 مضافة. The repealed provisions
keep their full text and are FLAGGED, not deleted (the official PDF retains
their bodies with ملغاة badges). Unlike the Sharia Procedure regulation there is
NO dual-status divergence — the section-API status equals the PDF status for
every provision — and there are no duplicate labels or redundancies. Every
record carries legal_status_ar plus is_repealed/is_amended/is_added flags.
Arabic governs; no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "enforcement", "regulation", "official_source",
                   "enforcement_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "enforcement", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "enforcement_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "enforcement_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "enforcement_arabic_legal_llm",
                        "enforcement_regulation_legal_llm_001_273.json")

LAW_ID = "sa-enforcement-regulation-526-1439"
REG_AR = "اللائحة التنفيذية لنظام التنفيذ"
REG_SHORT_AR = "لائحة التنفيذ"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
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
    return int(re.match(r"tnf_reg_art_(\d+)$", key).group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_pos)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        pos = _pos(key)                       # document order 1..273 (unique, sortable)
        label = a["number_label_ar"]          # official X/Y citation label
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        rid = "enforcement-regulation-llm-prov-%03d" % pos
        mark = " (ملغاة)" if is_repealed else ""
        ver.append({"law_key": "enforcement", "law_component": "implementing_regulation", "language": "ar",
                    "record_layer": "ENFORCEMENT_REGULATION_ARABIC_VERIFIED_TEXT",
                    "document_order": pos, "article_key": key,
                    "number_label_ar": label, "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history") or [],
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ consolidated regulation "
                                              "cross-verified against the official MOJ PDF; amendment "
                                              "status flagged (see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "implementing_regulation",
                    "article_number": pos, "document_order": pos, "article_key": key,
                    "number_label_ar": label, "article_title_ar": label,
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": rid, "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — الفقرة %s%s" % (REG_SHORT_AR, label, mark),
                    "retrieval_title_ar": "%s - %s" % (REG_SHORT_AR, label),
                    "article_path": "enforcement/regulation/provisions/%03d" % pos,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["الفقرة %s %s" % (label, REG_SHORT_AR),
                                          "%s الفقرة %s" % (REG_SHORT_AR, label),
                                          "لائحة التنفيذ %s" % label],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": REG_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "enforcement", "layer": "ENFORCEMENT_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-enforcement-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "implementing_regulation",
               "title_ar": REG_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (273 مادة؛ نص موحّد: 266 أصلية، 2 معدّلة، 2 ملغاة، 3 مضافة)",
               "title_en": "Implementing Regulation of the Law of Enforcement — Arabic LLM-ready layer (273 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "text_status": STATUS, "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Enforcement Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
