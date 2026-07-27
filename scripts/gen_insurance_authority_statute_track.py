#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Statute of the Insurance Authority track (تنظيم هيئة التأمين,
Council of Ministers Resolution No. 85, 28/1/1445H / published Umm Al-Qura
Gazette issue 4995, 25 Aug 2023G).

VERIFICATION TIER -- see sources/insurance_authority_statute/law/
official_source/insurance_authority_statute_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: laws.boe.gov.sa (the exact lawId URL identified in a prior
research pass) was UNREACHABLE this pass, both live (TLS connection reset,
consistent with a prior HTTP 503 finding) and via the Wayback Machine (this
environment's egress policy resets every TLS connection to web.archive.org
itself at the ClientHello stage, even though archive.org's own separate
availability API confirms an archived snapshot exists). Given this, the
GOVERNING PRIMARY source used instead is uqn.gov.sa -- the official Umm
Al-Qura Gazette portal itself, arguably an even stronger primary source than
BOE's own compiled-law database -- live-fetched this pass (HTTP 200) for both
the statute's full 15-article text and its companion Council of Ministers
Resolution text. Cross-verified at BYTE level against qanoonsa.com (an
independent legal aggregator whose own text is identical in every
substantive word, differing only in cosmetic digit style) and at quote level
against argaam.com (a financial news portal quoting several articles
verbatim). ia.gov.sa (the Authority's own site) was reachable but does not
host the statute's full text on any accessible static page.

15 records, all اصلية (original, no amendments found this pass), 0 معدلة,
0 ملغاة, 0 مضافة. Flat structure, no أبواب/فصول. No inline per-article titles
in the source -- no title_ar field is used. Unlike this corpus's
tvtc_organizational_statute track, this statute's own articles contain NO
repeal/succession clause naming a predecessor law; the transfer of
insurance-sector competencies away from SAMA and the Council of Cooperative
Health Insurance is effected entirely through the COMPANION Resolution's own
numbered decisions (not ingested here -- see known_unresolved_discrepancies).

No legal text is altered beyond whitespace normalization needed to render
each site's HTML as plain text, and normalizing to uqn.gov.sa's own
Western-digit rendering as the single governing primary source's digit
style throughout. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "insurance_authority_statute", "law", "official_source",
                   "insurance_authority_statute_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "insurance_authority_statute", "law", "verified")
RECORDS = os.path.join(OUT_VER, "insurance_authority_statute_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "insurance_authority_statute_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "insurance_authority_statute_arabic_legal_llm",
                        "insurance_authority_statute_legal_llm_001_015.json")

LAW_ID = "sa-insurance-authority-statute-85-1445"
LAW_AR = "تنظيم هيئة التأمين"
TOP_STATUS = ("UQN_OFFICIAL_GAZETTE_LIVE_FETCH_PRIMARY_X_QANOONSA_COM_BYTE_LEVEL_"
              "CROSSCHECK_X_ARGAAM_COM_QUOTE_CROSSCHECK_LIVE_BOE_UNREACHABLE")
KEY_RE = r"insurance_authority_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام التنظيم اللائحة أحكام يجب يجوز "
            "عليه دون فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المجلس الرئيس "
            "بوجه خاص").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    n = int(m.group(1))
    suf = m.group(2)
    if suf is None:
        return (n, 0)
    if suf == "":
        return (n, 1)
    return (n, 1 + int(suf))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        m = re.match(KEY_RE, key)
        n = int(m.group(1))
        is_mukarrar = bool(a.get("is_mukarrar"))
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        ver.append({"law_key": "insurance_authority_statute", "law_component": "law",
                    "language": "ar",
                    "record_layer": "INSURANCE_AUTHORITY_STATUTE_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on "
                                              "uqn.gov.sa (the official Umm Al-Qura Gazette "
                                              "portal itself), live-fetched this pass, as the "
                                              "PRIMARY source (live BOE unreachable this pass, "
                                              "and this environment additionally blocks "
                                              "web.archive.org at the TLS layer), "
                                              "cross-verified at byte level against qanoonsa.com "
                                              "(an independent legal aggregator whose text is "
                                              "identical in every substantive word) and at quote "
                                              "level against argaam.com. This statute's own 15 "
                                              "articles contain no repeal/succession clause "
                                              "naming a predecessor law -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact for the companion Resolution's own "
                                              "(non-ingested) competency-transfer decisions."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "insurance-authority-statute-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "insurance_authority_statute/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من تنظيم هيئة التأمين" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Council of Ministers Resolution No. "
                                                          "(85), 28/1/1445H — uqn.gov.sa (the "
                                                          "official Umm Al-Qura Gazette portal), "
                                                          "live-fetched, cross-verified against "
                                                          "qanoonsa.com and argaam.com; live BOE "
                                                          "and web.archive.org unreachable this "
                                                          "pass"),
                                     "source_authority_ar": "قرار مجلس الوزراء رقم (85) وتاريخ 28/1/1445هـ — جريدة أم القرى الرسمية (uqn.gov.sa)، مطابقة مع qanoonsa.com وargaam.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "insurance_authority_statute",
               "layer": "INSURANCE_AUTHORITY_STATUTE_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": TOP_STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-insurance-authority-statute-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (15 مادة؛ جميعها أصلية)",
               "title_en": "Statute of the Insurance Authority — Arabic LLM-ready layer (15 records, all original)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Insurance Authority Statute records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
