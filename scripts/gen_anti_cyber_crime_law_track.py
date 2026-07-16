#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Anti-Cyber Crime Law track (نظام مكافحة جرائم المعلوماتية,
Royal Decree M/17, 8/3/1428H).

DISTINCT VERIFICATION TIER, but the STRONGEST used anywhere in this corpus
outside the primary MOJ-portal pipeline: full EXHAUSTIVE (not spot-check)
article-by-article cross-verification across THREE independent sources, all
matching word-for-word on all 16 articles. PRIMARY: the Bureau of Experts
(BOE) legal portal at laws.boe.gov.sa, reached via the WebFetch/curl method
through an https://r.jina.ai/<url> reader-proxy prefix (direct sandbox
network access to laws.boe.gov.sa is blocked at the TLS handshake/WAF
level). SECOND: WIPO Lex, hosting the CITC (Communications and Information
Technology Commission) Official Translation Department's Arabic source PDF
— a genuinely different production pipeline/host than BOE. THIRD: the Saudi
Ministry of Finance regulations library, a scanned, officially stamped
certified copy. Both PDFs have no usable text layer; both were rendered to
page images and read visually/OCR'd. See
sources/anti_cyber_crime/law/official_source/
anti_cyber_crime_law_official_source.json's verification_methodology_note
and known_unresolved_discrepancies for a fully documented, investigated but
UNCONFIRMED possible amendment to Article 6 (cited by a UN database but not
found in any of the three primary sources checked, including the
administering regulator's own current text) — that unconfirmed text is
deliberately NOT included in this track.

Fresh consolidated text: all 16 records اصلية. Articles are numbered by
ordinal position 1..16 (no مكرر), flat structure with no chapter/section
wrapper (section_ar empty for every article).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_cyber_crime", "law", "official_source",
                   "anti_cyber_crime_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_cyber_crime", "law", "verified")
RECORDS = os.path.join(OUT_VER, "anti_cyber_crime_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_cyber_crime_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_cyber_crime_arabic_legal_llm",
                        "anti_cyber_crime_law_legal_llm_001_016.json")

LAW_ID = "sa-anti-cyber-crime-law-m17-1428"
LAW_AR = "نظام مكافحة جرائم المعلوماتية"
STATUS = "BOE_PORTAL_TRIPLE_SOURCE_EXHAUSTIVE_VERIFIED"
KEY_RE = r"anti_cyber_crime_art_(\d{3})$"
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
        ver.append({"law_key": "anti_cyber_crime", "law_component": "law", "language": "ar",
                    "record_layer": "ANTI_CYBER_CRIME_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": False, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier (not the primary MOJ-portal "
                                              "pipeline, since this is a Council-of-Ministers/"
                                              "Bureau-of-Experts instrument), but is the "
                                              "STRONGEST tier used outside that primary pipeline "
                                              "in this corpus: full exhaustive (not spot-check) "
                                              "article-by-article cross-verification across three "
                                              "independent sources (BOE portal, WIPO Lex/CITC "
                                              "translation PDF, Ministry of Finance certified "
                                              "copy), all matching word-for-word on all 16 "
                                              "articles. A possible amendment to article 6 (cited "
                                              "by a UN database) was investigated and found "
                                              "unconfirmed against all three primary sources "
                                              "including the administering regulator's own "
                                              "current text; see the source artifact's "
                                              "known_unresolved_discrepancies for the full "
                                              "documentation."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": False, "is_added": False,
                    "record_id": "anti-cyber-crime-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_cyber_crime/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مكافحة جرائم المعلوماتية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — Bureau of Experts (BOE) "
                                                          "portal, triple-source exhaustively "
                                                          "verified (BOE x WIPO Lex/CITC x MOF "
                                                          "certified copy)"),
                                     "source_authority_ar": "مرسوم ملكي — بوابة هيئة الخبراء، تحقق ثلاثي المصادر شامل",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "anti_cyber_crime", "layer": "ANTI_CYBER_CRIME_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "verification_methodology_note": src["verification_methodology_note"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-anti-cyber-crime-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (16 مادة؛ إصدار جديد كامل: 16 أصلية)",
               "title_en": "Saudi Anti-Cyber Crime Law — Arabic LLM-ready layer (16 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 16], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Cyber Crime Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
