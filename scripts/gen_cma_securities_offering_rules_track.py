#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the CMA Rules on the Offer of Securities and Continuing Obligations
track (قواعد طرح الأوراق المالية والالتزامات المستمرة, CMA Board Resolution No.
2017-123-3 dated 9/4/1439H = 27/12/2017G, issued pursuant to the Capital Market
Law (Royal Decree M/30, 2/6/1424H), as amended by CMA Board Resolution No.
2026-6-3 dated 30/07/1447H = 19/01/2026G).

VERIFICATION TIER: TIER_1 -- two INDEPENDENT OFFICIAL sources.

  1. The issuing authority's own Arabic PDF, fetched this pass from
     cma.gov.sa/RulesRegulations/Regulations/Documents/
     RULES_ON_THE_OFFER_OF_SECURITIES_AND_CONTINUING_OBLIGATIONS_ar2026.pdf
     (HTTP 200, 296-page born-digital PDF). Every Arabic character stored in
     this track comes from that file's own glyphs.
  2. جريدة أم القرى (Umm Al-Qura), the Kingdom's official gazette, at
     uqn.gov.sa/decisions-and-regulations/4001355, which publishes the same
     consolidated text under the identical citation and identical amending
     resolution. Different publisher, therefore an independent official
     witness -- not a secondary aggregator.

ARTICLE COUNT: 112 -- independently confirmed three ways (the PDF's own table
of contents, the 112 blue-set article headings in the body forming a clean
1..112 run, and the gazette's own 112 headings). This matches the figure the
corpus census reported; it was verified, not assumed.

CROSS-CHECK RESULT: 105 of the 112 articles are WORD-IDENTICAL between the two
official publications after a normalisation that strips tashkeel, unifies
alef/ya/ta-marbuta forms and ignores punctuation and numeral presentation. The
7 that differ are individually recorded in known_unresolved_discrepancies;
each is a one- or two-word typographic divergence (mostly apparent typos in
CMA's own PDF, e.g. 'أدوت' for 'أدوات' in Article 6 and 'أي جراء' for 'أي إجراء'
in Article 65), reproduced verbatim rather than silently corrected.

AMENDMENT ATTRIBUTION: the published consolidated text carries NO per-article
footnotes saying which articles Resolution 2026-6-3 changed, and no
pre-amendment official text was reachable this pass. Every article is therefore
recorded اصلية and NONE is flagged معدلة -- a deliberate refusal to guess, fully
disclosed in the source artifact. consolidated_amended_law remains true.

ANNEXES: the instrument's thirteenth Part (الباب الثالث عشر: الملاحق, 38
annexes over pages 99-296 of the source PDF) is NOT ingested by this track;
only the 112 numbered articles are.

Arabic governs. The English CMA PDF of the same instrument was NOT used to
produce, correct or reconstruct any Arabic character.

No legal text is altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = "cma_securities_offering_rules"
SRC = os.path.join(ROOT, "sources", KEY, "law", "official_source",
                   KEY + "_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", KEY, "law", "verified")
RECORDS = os.path.join(OUT_VER, KEY + "_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, KEY + "_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", KEY + "_arabic_legal_llm",
                        KEY + "_legal_llm_001_112.json")

LAW_ID = "sa-cma-securities-offering-rules-2017-123-3"
LAW_AR = "قواعد طرح الأوراق المالية والالتزامات المستمرة"
STATUS = ("CMA_GOV_SA_OFFICIAL_PDF_PRIMARY_X_UMM_AL_QURA_OFFICIAL_GAZETTE_"
          "CROSSCHECK_X_GLYPH_LEVEL_LIGATURE_RECONSTRUCTION")
KEY_RE = KEY + r"_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة القواعد أحكام يجب يجوز "
            "عليه دون فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه "
            "إليها إليه عليها منهم بينهم الهيئة هذا هذه تلك ذلك حسبما ينطبق").split())


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


GOVERNING_NOTE = (
    "Arabic governs. PRIMARY source is the official Arabic PDF published by the "
    "Capital Market Authority on its own domain (cma.gov.sa), fetched directly; "
    "INDEPENDENT OFFICIAL CROSS-CHECK is the Umm Al-Qura official gazette text "
    "(uqn.gov.sa), which carries the same consolidated text under the same "
    "citation -- 105 of 112 articles word-identical after normalisation. The "
    "PDF places glyphs in visual order and uses multi-letter ligature glyphs, so "
    "the Arabic was rebuilt at glyph level strictly from the fonts' own "
    "ToUnicode declarations; no word list, no spell-correction, and no use of "
    "the English text. Read verification_methodology_note and "
    "known_unresolved_discrepancies in the source artifact before relying on "
    "this track -- in particular: the text is the CONSOLIDATED text as amended "
    "by Resolution 2026-6-3 (30/07/1447H) but carries no per-article amendment "
    "footnotes, so no article is flagged معدلة; seven articles diverge by one or "
    "two words from the gazette and are stored as CMA's own PDF prints them; and "
    "the instrument's 38 annexes (Part 13) are not ingested.")

SOURCE_AUTHORITY_EN = (
    "CMA Board Resolution No. (2017-123-3), dated 9/4/1439H (27/12/2017G), "
    "issued pursuant to the Capital Market Law (Royal Decree M/30, 2/6/1424H) -- "
    "cma.gov.sa (the issuing Authority's own regulations domain); consolidated "
    "text as amended by CMA Board Resolution No. (2026-6-3), dated 30/07/1447H "
    "(19/01/2026G); independently cross-checked against the Umm Al-Qura official "
    "gazette (uqn.gov.sa)")

SOURCE_AUTHORITY_AR = (
    "قرار مجلس هيئة السوق المالية رقم (2017-123-3) وتاريخ 9/4/1439هـ (الموافق "
    "27/12/2017م)، الصادر بناءً على نظام السوق المالية الصادر بالمرسوم الملكي رقم "
    "(م/30) وتاريخ 2/6/1424هـ — الموقع الرسمي لهيئة السوق المالية (cma.gov.sa)؛ "
    "والنص المعتمد هنا هو النص المعدّل بقرار مجلس هيئة السوق المالية رقم "
    "(2026-6-3) وتاريخ 30/07/1447هـ (الموافق 19/01/2026م)، وقد قوبل مقابلةً "
    "مستقلة بنص جريدة أم القرى الرسمية (uqn.gov.sa)")


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
        section = a.get("section_ar", "")
        title = a.get("article_title_ar", "")
        lbl = a["number_label_ar"] + ((" — " + title) if title else "")
        ver.append({"law_key": KEY, "law_component": "rules", "language": "ar",
                    "record_layer": "CMA_SECURITIES_OFFERING_RULES_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": GOVERNING_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "rules", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": lbl,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "cma-securities-offering-rules-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, lbl),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, lbl),
                    "article_path": "%s/law/articles/%03d" % (KEY, n),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من قواعد طرح الأوراق المالية والالتزامات المستمرة"
                                          % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": SOURCE_AUTHORITY_EN,
                                     "source_authority_ar": SOURCE_AUTHORITY_AR,
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": KEY,
               "layer": "CMA_SECURITIES_OFFERING_RULES_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": True,
               "verification_tier": "TIER_1",
               "chapter_structure": src["chapter_structure"],
               "annexes_not_ingested": src["annexes_not_ingested"],
               "amending_instruments": src.get("amending_instruments"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-cma-securities-offering-rules-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "rules",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (112 مادة)",
               "title_en": ("CMA Rules on the Offer of Securities and Continuing "
                            "Obligations — Arabic LLM-ready layer (112 records)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 112], "text_status": STATUS,
               "verification_tier": "TIER_1",
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready CMA Securities Offering Rules records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
