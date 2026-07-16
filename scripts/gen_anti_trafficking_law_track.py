#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Anti-Trafficking in Persons Law track (نظام مكافحة جرائم
الاتجار بالأشخاص, Royal Decree M/40, 21/7/1430H).

DISTINCT VERIFICATION TIER: full text extracted from a Wayback Machine
capture (dated 2025-12-12) of the Bureau of Experts (BOE) legal portal —
the usual https://r.jina.ai/<url> reader-proxy method stopped working for
this research pass (Jina 401'd, direct/WebFetch to BOE also failed). The
Wayback capture is genuine BOE-served HTML (raw markup inspected, not just
cleaned text). Cross-verified for SUBSTANCE (not exact Arabic wording, since
the second source is an English translation) against UNODC's official
English translation, genuinely independent of BOE; every substantive
element of every article matched exactly in meaning. Additionally
corroborated by the 2025 US State Department TIP report. Weaker tier than
this corpus's usual Arabic-to-Arabic comparison, since no second full-text
ARABIC source was reachable this session. IMPORTANT: a 33-article draft
replacement law cleared public consultation in 2022 but remains UNENACTED
per the 2025 TIP report and the Dec-2025 BOE snapshot — documented in
known_unresolved_discrepancies, not silently ignored. See
sources/anti_trafficking/law/official_source/
anti_trafficking_law_official_source.json for the full methodology note.

Fresh full issuance: all 17 records اصلية. Articles are numbered by ordinal
position 1..17 (no مكرر), flat structure with no chapter/section wrapper.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_trafficking", "law", "official_source",
                   "anti_trafficking_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_trafficking", "law", "verified")
RECORDS = os.path.join(OUT_VER, "anti_trafficking_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_trafficking_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_trafficking_arabic_legal_llm",
                        "anti_trafficking_law_legal_llm_001_017.json")

LAW_ID = "sa-anti-trafficking-law-m40-1430"
LAW_AR = "نظام مكافحة جرائم الاتجار بالأشخاص"
STATUS = "BOE_WAYBACK_SNAPSHOT_UNODC_ENGLISH_SUBSTANCE_VERIFIED"
KEY_RE = r"anti_trafficking_art_(\d{3})$"
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
        ver.append({"law_key": "anti_trafficking", "law_component": "law", "language": "ar",
                    "record_layer": "ANTI_TRAFFICKING_LAW_ARABIC_VERIFIED_TEXT",
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
                                              "verification tier (BOE Wayback snapshot, "
                                              "substance-cross-checked against UNODC's "
                                              "official English translation, not a second "
                                              "Arabic source) — see the source artifact's "
                                              "verification_methodology_note for the full "
                                              "caveat, including a documented but unenacted "
                                              "draft replacement law."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": False, "is_added": False,
                    "record_id": "anti-trafficking-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_trafficking/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مكافحة جرائم الاتجار بالأشخاص" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — BOE portal via "
                                                          "Wayback snapshot, UNODC English "
                                                          "substance-verified"),
                                     "source_authority_ar": "مرسوم ملكي — بوابة هيئة الخبراء (نسخة أرشيفية)، تحقق جوهري عبر ترجمة UNODC الرسمية",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "anti_trafficking", "layer": "ANTI_TRAFFICKING_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "verification_methodology_note": src["verification_methodology_note"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-anti-trafficking-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (17 مادة؛ إصدار جديد كامل: 17 أصلية)",
               "title_en": "Saudi Anti-Trafficking in Persons Law — Arabic LLM-ready layer (17 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 17], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Trafficking Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
