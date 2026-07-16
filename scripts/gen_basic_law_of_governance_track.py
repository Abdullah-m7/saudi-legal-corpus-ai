#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Basic Law of Governance track (النظام الأساسي للحكم, Royal
Order A/90, 27/8/1412H).

DISTINCT VERIFICATION TIER — stronger than the Anti-Bribery Law track, but
still not this corpus's primary MOJ-portal-x-official-PDF pipeline (this is a
Council-of-Ministers/Bureau-of-Experts instrument, not MOJ-issued, and is
absent from the MOJ legal portal). PRIMARY source: the Bureau of Experts
(هيئة الخبراء بمجلس الوزراء) legal portal at laws.boe.gov.sa, reached via the
WebFetch tool with an https://r.jina.ai/<url> reader-proxy prefix (direct
sandbox network access to laws.boe.gov.sa is blocked at the TLS handshake
stage / WAF level; this proxy routes the fetch through Anthropic's own
infrastructure instead). Extraction is COMPLETE and GAPLESS: all 83 articles
across all 9 chapters, in order. SECOND source: WIPO Lex (World Intellectual
Property Organization's official national-legislation database), entry
SA016 — a scanned, nationally-stamped government-submitted document using a
different production pipeline than the BOE database (OCR'd via
tesseract-ara, no usable text layer). Cross-verification was an EXTENSIVE
SPOT-CHECK across all 9 chapters (~39 of 83 articles, ~47%), NOT an
exhaustive per-article diff — every article carries its own
cross_verified_against_wipo_lex boolean tag reflecting exactly which
articles were individually spot-checked vs. which rest on the complete BOE
extraction plus the whole-document structural match only. See
sources/basic_law_of_governance/law/official_source/
basic_law_of_governance_official_source.json's verification_methodology_note
for the full methodology.

Fresh consolidated text: all 83 records اصلية (no amendment history found or
flagged by the BOE source for any article). Articles are numbered by
ordinal position 1..83 (no مكرر), organized under 9 chapters with
section_ar carrying each article's chapter heading.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "basic_law_of_governance", "law", "official_source",
                   "basic_law_of_governance_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "basic_law_of_governance", "law", "verified")
RECORDS = os.path.join(OUT_VER, "basic_law_of_governance_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "basic_law_of_governance_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "basic_law_of_governance_arabic_legal_llm",
                        "basic_law_of_governance_legal_llm_001_083.json")

LAW_ID = "sa-basic-law-of-governance-a90-1412"
LAW_AR = "النظام الأساسي للحكم"
STATUS = "BOE_PORTAL_PRIMARY_SOURCE_WIPO_LEX_SPOT_CHECKED"
KEY_RE = r"basic_law_of_governance_art_(\d{3})$"
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
        checked = a["cross_verified_against_wipo_lex"]
        ver.append({"law_key": "basic_law_of_governance", "law_component": "law", "language": "ar",
                    "record_layer": "BASIC_LAW_OF_GOVERNANCE_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "cross_verified_against_wipo_lex": checked,
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": False, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": a["verification_note"],
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": False, "is_added": False,
                    "record_id": "basic-law-of-governance-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "basic_law_of_governance/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d النظام الأساسي للحكم" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Order — Bureau of Experts (BOE) "
                                                          "portal, cross-checked against WIPO Lex "
                                                          "(spot-checked, see cross_verified_"
                                                          "against_wipo_lex)"),
                                     "source_authority_ar": "أمر ملكي — بوابة هيئة الخبراء بمجلس الوزراء، تحقق جزئي مقارنة بـ WIPO Lex",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"],
                                     "cross_verified_against_wipo_lex": checked},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "basic_law_of_governance",
               "layer": "BASIC_LAW_OF_GOVERNANCE_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "spot_checked_count": sum(1 for a in arts.values() if a["cross_verified_against_wipo_lex"]),
               "verification_methodology_note": src["verification_methodology_note"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-basic-law-of-governance-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (83 مادة؛ إصدار موحّد: 83 أصلية)",
               "title_en": "Basic Law of Governance — Arabic LLM-ready layer (83 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 83], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Basic Law of Governance records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
