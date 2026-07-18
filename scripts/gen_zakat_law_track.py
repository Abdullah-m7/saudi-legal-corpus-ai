#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Zakat Collection Implementing Regulation track (اللائحة
التنفيذية لجباية الزكاة, Minister of Finance Resolution No. 1007,
19/8/1445H; amended once by Resolution No. 1248, 11/10/1446H).

DISTINCT, WEAKER VERIFICATION TIER than this corpus's cross-verified
tracks -- STATUS constant ZATCA_PDF_PRIMARY_SINGLE_SOURCE_GAZETTE_SPOT_
VERIFIED reflects that ZATCA's own official consolidated Arabic PDF is
the SOLE full-text primary source for all 128 articles this pass; the
Umm Al-Qura Gazette portal (uqn.gov.sa) was successfully reached this
pass (unlike laws.boe.gov.sa, which again returned HTTP 503) and used
only for targeted spot-verification of specific facts (Resolution 1007's
number/date, Article 13's title), not as a second full-text copy
diffed word-for-word against ZATCA's PDF.

This PDF's font/ToUnicode-CMap carries a systematic character-
transposition bug: LAM immediately followed by any alef form (ا/أ/إ/آ --
i.e. the mandatory Arabic "لا" ligature) is emitted transposed, silently
corrupting extremely common vocabulary (الأصول, الإقرار, الآتية, اللائحة,
etc.), not just rare ligature-heavy words. Fixed via a general boundary
regex plus a curated ~140-entry whole-word dictionary plus context-
anchored fixes for two genuine homograph ambiguities (ثالث/ثلاثة,
مالك/ملاك) -- see sources/zakat/law/official_source/
zakat_law_official_source.json's verification_methodology_note for the
full methodology and known_unresolved_discrepancies for every documented
gap, including the single-source tier, the un-recovered base-decree and
pre-amendment Article 73 texts, and the debunked 200k/400k SAR claim.

No legal text is altered by this script. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "zakat", "law", "official_source",
                   "zakat_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "zakat", "law", "verified")
RECORDS = os.path.join(OUT_VER, "zakat_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "zakat_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "zakat_arabic_legal_llm",
                        "zakat_law_legal_llm_001_128.json")

LAW_ID = "sa-zakat-law-mof1007-1445"
LAW_AR = "اللائحة التنفيذية لجباية الزكاة"
STATUS = "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_GAZETTE_SPOT_VERIFIED"
KEY_RE = r"zakat_law_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك هذه الزكوي الزكاة المكلف الهيئة").split())


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
        ver.append({"law_key": "zakat", "law_component": "law", "language": "ar",
                    "record_layer": "ZAKAT_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "title_ar": a.get("title_ar", ""),
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "original_1445h_text": a.get("original_1445h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track rests on ZATCA's "
                                              "own official consolidated PDF as the sole "
                                              "full-text primary source (single-source "
                                              "tier, distinct from this corpus's "
                                              "cross-verified tracks) -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the "
                                              "source artifact for the full caveats, "
                                              "including the PDF's systematic lam-alef "
                                              "ligature extraction bug and its fix "
                                              "methodology, and that no original_1445h_text "
                                              "is populated for Article 73 (the sole "
                                              "amended article)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"] + (" — " + a["title_ar"] if a.get("title_ar") else ""),
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "zakat-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s: %s" % (LAW_AR, a["number_label_ar"], a.get("title_ar", "")),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "zakat/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d اللائحة التنفيذية لجباية الزكاة" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Minister of Finance Resolution — "
                                                          "ZATCA official PDF (sole primary "
                                                          "source); Umm Al-Qura Gazette "
                                                          "spot-verified for select facts"),
                                     "source_authority_ar": "قرار وزير المالية — ملف PDF الرسمي لهيئة الزكاة والضريبة والجمارك (ZATCA)، المصدر الأساسي الوحيد؛ جريدة أم القرى للتحقق النقطي من وقائع محددة",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "zakat",
               "layer": "ZAKAT_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-zakat-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (128 مادة؛ 127 أصلية، 1 معدّلة)",
               "title_en": "Saudi Zakat Collection Implementing Regulation — Arabic LLM-ready layer (128 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 128], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Zakat Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
