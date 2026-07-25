#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Shura Council Internal Regulation track (اللائحة الداخلية
لمجلس الشورى, Royal Order أ/15, 3/3/1414H).

Companion instrument of the Shura Council Law (already tracked at
sources/shura_council/), issued pursuant to that Law's own Article 29. This
is a "لائحة داخلية" (internal-governance regulation for the Council itself) —
a distinct naming convention from a "لائحة تنفيذية" because it governs the
Council's own internal proceedings rather than implementing a law directed at
another body.

SINGLE-TIER VERIFICATION — GOVERNMENT_PRIMARY_OFFICIAL_COUNCIL_PUBLICATION_
VIA_WAYBACK_VISUAL_VERIFICATION. Primary source: the Shura Council's own
official compiled publication "نظام مجلس الشورى" (6th edition, 1437H),
hosted at shura.gov.sa/img/ar/books/nezamNew.pdf, retrieved via a Wayback
Machine snapshot (direct shura.gov.sa fetch was blocked/reset in this
sandbox, matching the base law track's own documented BOE-unreachable
experience). This specific PDF's font/ToUnicode encoding is broken for naive
programmatic text extraction (confirmed by direct codepoint inspection on
both pypdf and poppler pdftotext output); therefore every one of the 34
articles, all 6 chapter headers, and all 6 amendment footnotes were
transcribed by DIRECT VISUAL INSPECTION of high-resolution page renders of
the primary source, not by trusting raw extracted text.

See sources/shura_council_internal_regulation/law/official_source/
shura_council_internal_regulation_official_source.json for the full
methodology note and documented unresolved discrepancies — most importantly,
this research independently RE-VERIFIED (and corrects) the amendment chain:
the task's prior-research premise assumed أ/198 (1424H) touched this
instrument, but an exhaustive text search of the primary source found أ/198
touches only the base LAW's Articles 17/23, not this Internal Regulation.
This Internal Regulation's actual amendment chain is أ/181 (14/12/1428H,
touching the الباب الأول chapter title plus Articles 6, 8, 17, 27) and أ/44
(29/2/1434H = 11 Jan 2013, touching Article 22 — the same royal order that
added the base Law's Article 3 female-representation quota).

34 articles across 6 أبواب/chapters: 29 اصلية / 5 معدلة / 0 ملغاة / 0 مضافة.
No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "shura_council_internal_regulation", "law",
                   "official_source",
                   "shura_council_internal_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "shura_council_internal_regulation",
                       "law", "verified")
RECORDS = os.path.join(OUT_VER,
                       "shura_council_internal_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER,
                       "shura_council_internal_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data",
                        "shura_council_internal_regulation_arabic_legal_llm",
                        "shura_council_internal_regulation_legal_llm_001_034.json")

LAW_ID = "sa-shura-council-internal-regulation-a15-1414"
LAW_AR = "اللائحة الداخلية لمجلس الشورى"
KEY_RE = r"shura_council_internal_regulation_art_(\d{3})$"
AMENDED_KEYS = {"shura_council_internal_regulation_art_%03d" % n
                for n in (6, 8, 17, 22, 27)}
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
        is_amended = ls == "معدلة"
        text = a["text"]
        tier = a["verification_tier"]
        ver.append({"law_key": "shura_council_internal_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "SHURA_COUNCIL_INTERNAL_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": tier,
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "original_1414h_text": a.get("original_1414h_text"),
                    "official_text_status": tier,
                    "governing_source_note": ("Arabic governs; verified by direct visual "
                                              "inspection of the primary source's rendered "
                                              "pages (this PDF's ToUnicode CMap is broken for "
                                              "naive programmatic text extraction) — see the "
                                              "source artifact's verification_methodology_note "
                                              "for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "shura-council-internal-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "shura_council_internal_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d اللائحة الداخلية لمجلس الشورى" % n],
                    "text_status": tier,
                    "source_trust": {"source_authority": ("Royal Order — official Shura "
                                                          "Council publication, verified by "
                                                          "direct visual inspection (Wayback "
                                                          "snapshot; live fetch blocked)"),
                                     "source_authority_ar": "أمر ملكي — نشرة رسمية لمجلس الشورى، تم التحقق بالمعاينة البصرية المباشرة",
                                     "source_status": tier.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"],
                                     "verification_tier": tier},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "shura_council_internal_regulation",
               "layer": "SHURA_COUNCIL_INTERNAL_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "official_text_status": src["articles"][keys[0]]["verification_tier"],
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "gazette_name_ar": src.get("gazette_name_ar"),
               "gazette_issue_no": src.get("gazette_issue_no"),
               "gazette_issue_date_hijri": src.get("gazette_issue_date_hijri"),
               "companion_instrument_of": src.get("companion_instrument_of"),
               "consolidated_amended_law": True,
               "chapter_structure": src.get("chapter_structure"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-shura-council-internal-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (34 مادة؛ نص موحّد: 29 أصلية، 5 معدّلة)",
               "title_en": "Saudi Shura Council Internal Regulation — Arabic LLM-ready layer (34 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 34],
               "text_status": src["articles"][keys[0]]["verification_tier"],
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Shura Council Internal Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
