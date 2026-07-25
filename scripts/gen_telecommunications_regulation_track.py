#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Telecommunications and
Information Technology Law track (اللائحة التنفيذية لنظام الاتصالات وتقنية
المعلومات, Ministerial Decision No. (13), 14/5/1444H).

STANDALONE COMPANION TRACK to the base Telecommunications and IT Act, already
tracked in this corpus at sources/telecommunications/. Article (40) of the
base law (Royal Decree M/106, 2/11/1443H) mandated this Implementing
Regulation within 180 days of the base law's Gazette publication; it was
approved by the Minister of Communications and Information Technology via
Ministerial Decision No. (13) dated 14/5/1444H (7/12/2022G), following Board
Resolution No. 1-176-2022 (13/5/1444H) of the Communications, Space and
Technology Commission (CST).

DUAL PRIMARY, BORN-DIGITAL SOURCES this pass: (1) cst.gov.sa's own official
PDF (the regulator itself; Microsoft Word, created 2022-12-11, 39 pages), and
(2) mcit.gov.sa's official PDF (the Ministry; Adobe InDesign, created
2023-10-19, 68 pages). Both agree verbatim on all 108 articles across 16
chapters once a set of well-understood, thoroughly cross-validated text-layer
extraction artifacts common to both PDFs are corrected (a systematic
lam+alef-ligature letter-order swap in all four alef variants, a handful of
reversed-order numeral cross-references, reversed enumeration-marker digits,
and five isolated paragraph/sub-item reading-order scrambles resolved against
150dpi renders of the source pages) -- see the source artifact's
verification_methodology_note for the full account. laws.boe.gov.sa carries
no dedicated page for this ministerial-decision-level bylaw (BOE indexes Royal
Decrees/Laws, not ministerial regulations); the Umm Al-Qura Gazette links
named in this track's research brief did not resolve to their archived 2022
content this pass (flagged, not blocking, since both primary PDFs independently
confirm the same decision number/date/text). No confirmed amendment to this
Implementing Regulation (post-dating its 14/5/1444H approval) was found; all
108 articles are ingested as اصلية (original, unamended).

See sources/telecommunications_regulation/law/official_source/
telecommunications_regulation_official_source.json for the full methodology
note and documented unresolved discrepancies.

108 articles, all اصلية, organized under 16 chapters with section_ar carrying
each article's chapter heading. No مكرر articles.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "telecommunications_regulation", "law",
                   "official_source",
                   "telecommunications_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "telecommunications_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "telecommunications_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "telecommunications_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "telecommunications_regulation_arabic_legal_llm",
                        "telecommunications_regulation_legal_llm_001_108.json")

LAW_ID = "sa-telecommunications-regulation-md13-1444"
LAW_AR = "اللائحة التنفيذية لنظام الاتصالات وتقنية المعلومات"
STATUS = "MCIT_CST_DUAL_PRIMARY_SOURCE_TEXT_LAYER_REMEDIATED"
KEY_RE = r"telecommunications_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
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
        ver.append({"law_key": "telecommunications_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "TELECOMMUNICATIONS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": False, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; cst.gov.sa (the "
                                              "regulator's own portal) and "
                                              "mcit.gov.sa (the Ministry) both served "
                                              "as independent born-digital primary "
                                              "sources this research pass, "
                                              "cross-verified against each other and "
                                              "against 150dpi renders of the source "
                                              "PDF pages for structural anomalies -- "
                                              "see verification_methodology_note in "
                                              "the source artifact for the full "
                                              "extraction-artifact remediation "
                                              "account (ligature-swap correction, "
                                              "digit-transposition correction, and "
                                              "five resolved reading-order scrambles)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": False, "is_added": False,
                    "record_id": "telecommunications-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "telecommunications_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d اللائحة التنفيذية للاتصالات" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Ministerial Decision No. 13 "
                                                          "(14/5/1444H) -- cst.gov.sa "
                                                          "(regulator) primary source, "
                                                          "cross-checked against MCIT's "
                                                          "own official PDF"),
                                     "source_authority_ar": "قرار وزاري رقم (13) — بوابة هيئة الاتصالات والفضاء والتقنية (مصدر أساسي)، مطابقة نص وزارة الاتصالات وتقنية المعلومات",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "telecommunications_regulation",
               "layer": "TELECOMMUNICATIONS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "verification_tier": src.get("verification_tier"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-telecommunications-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (108 مادة؛ لائحة تنفيذية كاملة: 108 أصلية)",
               "title_en": "Implementing Regulation of the Telecommunications and IT "
                           "Act — Arabic LLM-ready layer (108 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 108], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Telecommunications Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
