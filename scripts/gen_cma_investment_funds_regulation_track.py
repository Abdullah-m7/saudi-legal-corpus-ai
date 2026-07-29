#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the CMA Investment Funds Regulations track (لائحة صناديق
الاستثمار, CMA Board Resolution No. 2006-219-1, dated 3/12/1427H =
24/12/2006G, issued under the Capital Market Law (Royal Decree M/30,
2/6/1424H), as most recently amended by Resolution 2025-135-1, dated
03/06/1447H = 24/11/2025G).

VERIFICATION TIER: TIER_2 -- see the source artifact's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE (Arabic governs; no English text was consulted at any point):
the official consolidated Arabic PDF published by CMA on its own regulations
domain --
https://cma.gov.sa/RulesRegulations/Regulations/Documents/Investment_Funds_Regulations_11_2025_AR.pdf
-- fetched directly (HTTP 200, 1,785,182 bytes, 181-page born-digital PDF),
reached from CMA's own regulations catalogue and corroborated by CMA's own
details.aspx?code=99 page ("تاريخ الإصدار 2006/12/24", "تاريخ التعديل
2025/11/26").

ARTICLE COUNT INDEPENDENTLY VERIFIED: 113. Re-counted twice from the document
itself -- the PDF's own table of contents lists exactly 113 article entries in
an unbroken Arabic-ordinal run from "المادة الأولى" to "المادة الثالثة عشرة بعد
المئة", and the body carries exactly 113 matching headings in the same order.
The census figure of 113 is CONFIRMED, not assumed. (CMA's superseded 2021
consolidation of the same instrument has 111 articles, so the count did move.)

STRUCTURE: 9 أبواب, none subdivided into فصول. 14 ملاحق exist and are NOT
ingested -- disclosed in known_unresolved_discrepancies.

TEXT: extracted glyph-atomically. The PDF stores glyphs in visual order and its
embedded SakkalMajalla subsets map ligature glyphs to correct multi-character
ToUnicode strings; pdftotext reverses those interiors during its
character-level bidi pass and corrupts the Arabic. This track avoids producing
that corruption rather than repairing it afterwards: glyphs are reversed as
atoms and left-to-right runs re-reversed. No character is invented, dropped,
substituted or spell-corrected, and no word list or dictionary is consulted.
Verified against a rendered page image, against twelve corruption canaries
(zero hits), and by scanning all 113 bodies for Latin characters, presentation
forms, bidi controls and leaked page furniture (zero findings).

AMENDMENTS: the consolidated PDF carries NO per-article footnotes. Only the
latest amendment could be mapped to articles: the official gazette text of
Resolution (1-135-2025) substitutes «فئات المستثمرين المؤهلين في السوق
الموازية» for «فئات المستثمرين المؤهلين» in Art. 48(ع) and Art. 49(ك), and both
substituted phrases were confirmed present VERBATIM at exactly those locations
in the primary text. Those two articles alone are flagged معدلة. Four further
amending instruments (2016-61-1; 2021-22-2, a FULL text replacement; 2025-54-1;
plus the 2006 issuance) are recorded at document level with
article_level_mapping_available=false. No pre-amendment wording is
reconstructed anywhere. "اصلية" in this track means "no article-level
amendment attributable from the sources fetched" -- NOT "unchanged since 2006".

No legal text is altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cma_investment_funds_regulation", "law", "official_source",
                   "cma_investment_funds_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "cma_investment_funds_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "cma_investment_funds_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "cma_investment_funds_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "cma_investment_funds_regulation_arabic_legal_llm",
                        "cma_investment_funds_regulation_legal_llm_001_113.json")

LAW_KEY = "cma_investment_funds_regulation"
LAW_ID = "sa-cma-investment-funds-regulation-2006-219-1"
LAW_AR = "لائحة صناديق الاستثمار"
LAW_EN = "Investment Funds Regulations"
N = 113
STATUS = ("CMA_GOV_SA_OFFICIAL_PDF_PRIMARY_X_GLYPH_ATOMIC_BIDI_EXTRACTION"
          "_X_GAZETTE_AMENDMENT_CROSSCHECK")
LAYER = "CMA_INVESTMENT_FUNDS_REGULATION_ARABIC_VERIFIED_TEXT"
KEY_RE = r"cma_investment_funds_regulation_art_(\d{3})$"

GOVERNING_NOTE = (
    "Arabic governs; no English text of this instrument was consulted at any point "
    "(CMA publishes no English PDF for it). PRIMARY source is the official "
    "consolidated Arabic PDF on cma.gov.sa (the issuing Authority's own regulations "
    "domain), fetched directly (HTTP 200, born-digital PDF), extracted "
    "glyph-atomically so that the ligature corruption pdftotext introduces on this "
    "font was never produced -- no character invented, dropped, substituted or "
    "spell-corrected. VERIFICATION TIER: TIER_2. Read verification_methodology_note "
    "and known_unresolved_discrepancies in the source artifact before relying on "
    "this track -- in particular: the consolidated PDF carries NO per-article "
    "amendment footnotes, so only Articles 48 and 49 (amended by Resolution "
    "2025-135-1, confirmed verbatim against the gazette wording) carry an "
    "article-level amendment history; 'اصلية' on the other 111 articles means "
    "'no article-level amendment attributable from the sources fetched', NOT "
    "'unchanged since 2006' -- the entire text was replaced in 2021 by Resolution "
    "2021-22-2; and the regulation's 14 ملاحق are not ingested by this track."
)

SOURCE_AUTHORITY_EN = (
    "CMA Board Resolution No. (2006-219-1), dated 3/12/1427H (24/12/2006G), issued "
    "under the Capital Market Law (Royal Decree M/30, 2/6/1424H) -- cma.gov.sa (the "
    "issuing Authority's own regulations domain); text replaced in full by Resolution "
    "2021-22-2 (12/7/1442H = 24/2/2021G) and subsequently amended by 2025-54-1 "
    "(23/11/1446H) and 2025-135-1 (03/06/1447H = 24/11/2025G, the amendment printed "
    "on the current cover)"
)
SOURCE_AUTHORITY_AR = (
    "قرار مجلس هيئة السوق المالية رقم (2006-219-1) وتاريخ 3/12/1427هـ الموافق "
    "24/12/2006م، الصادر بناءً على نظام السوق المالية (المرسوم الملكي رقم م/30 وتاريخ "
    "2/6/1424هـ) — الموقع الرسمي لهيئة السوق المالية (cma.gov.sa)؛ أُحلّ نصها بالكامل "
    "بموجب القرار رقم (2021-22-2) وتاريخ 12/7/1442هـ، ثم عُدلت بالقرارين (2025-54-1) "
    "وتاريخ 23/11/1446هـ و(2025-135-1) وتاريخ 03/06/1447هـ الموافق 24/11/2025م"
)

STOP = set((
    "من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
    "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
    "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة الالئحة أحكام يجب يجوز "
    "عليه دون فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وذلك وهذا وهذه أنه إليها "
    "إليه عليها منهم بينهم هذين هاتين تاريخ عدد مدة أكثر أقل ذات هيئة الهيئة"
).split())


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
        ls = a["legal_status_ar"]
        text = a["text"]
        section = a.get("section_ar", "")
        title = a.get("article_title_ar", "")
        label = a["number_label_ar"] + ((" — " + title) if title else "")

        ver.append({
            "law_key": LAW_KEY,
            "law_component": "regulation",
            "language": "ar",
            "record_layer": LAYER,
            "article_number": n,
            "is_mukarrar": False,
            "article_key": key,
            "number_label_ar": a["number_label_ar"],
            "article_title_ar": title,
            "section_ar": section,
            "article_text_verified": text,
            "verification_status": a["status"],
            "verification_tier": "TIER_2",
            "legal_status_ar": ls,
            "is_repealed": ls == "ملغاة",
            "is_amended": ls == "معدلة",
            "is_added": ls == "مضافة",
            "amendment_history": a.get("history", []),
            "official_text_status": STATUS,
            "governing_source_note": GOVERNING_NOTE,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
            "english_used_for_correction": False,
        })

        llm.append({
            "law_id": LAW_ID,
            "law_component": "regulation",
            "article_number": n,
            "is_mukarrar": False,
            "article_key": key,
            "article_title_ar": label,
            "section_ar": section,
            "legal_status_ar": ls,
            "is_repealed": ls == "ملغاة",
            "is_amended": ls == "معدلة",
            "is_added": ls == "مضافة",
            "record_id": "cma-investment-funds-regulation-llm-art-%03d" % n,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — %s" % (LAW_AR, label),
            "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
            "article_path": "%s/law/articles/%03d" % (LAW_KEY, n),
            "keywords_ar": _kw(text),
            "search_queries_ar": [
                "المادة %d %s" % (n, LAW_AR),
                "%s المادة %d" % (LAW_AR, n),
                "%s من لائحة صناديق الاستثمار" % a["number_label_ar"],
            ],
            "text_status": STATUS,
            "verification_tier": "TIER_2",
            "source_trust": {
                "source_authority": SOURCE_AUTHORITY_EN,
                "source_authority_ar": SOURCE_AUTHORITY_AR,
                "source_status": STATUS.lower(),
                "source_document_ar": LAW_AR,
                "source_url": src["official_source_url"],
                "verification_tier": "TIER_2",
                "legal_status_ar": ls,
                "verification_status": a["status"],
            },
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "english_used_for_correction": False,
            "text_summarized_or_paraphrased": False,
        })

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    json.dump({
        "law_key": LAW_KEY,
        "layer": LAYER,
        "record_count": len(ver),
        "official_text_status": STATUS,
        "verification_tier": "TIER_2",
        "status_counts": src["status_counts"],
        "decree": src["decree"],
        "decree_date_hijri": src["decree_date_hijri"],
        "decree_date_gregorian": src.get("decree_date_gregorian"),
        "administering_authority_en": src.get("administering_authority_en"),
        "official_source_url": src["official_source_url"],
        "governing_text_language": "ar",
        "english_text_consulted": False,
        "consolidated_amended_law": True,
        "chapter_structure": src["chapter_structure"],
        "annexes_not_ingested": src["annexes_not_ingested"],
        "amending_instruments": src["amending_instruments"],
        "verification_methodology_note": src["verification_methodology_note"],
        "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
        "source_artifact": os.path.relpath(SRC, ROOT),
    }, open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    sc = src["status_counts"]
    json.dump({
        "layer_id": "sa-cma-investment-funds-regulation-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "regulation",
        "title_ar": ("%s — الطبقة العربية الجاهزة للنماذج اللغوية (%d مادة؛ %d بلا تعديل "
                     "منسوب، %d معدلة)" % (LAW_AR, N, sc["اصلية"], sc["معدلة"])),
        "title_en": ("CMA Investment Funds Regulations — Arabic LLM-ready layer "
                     "(%d records; %d with no article-level amendment attributable, "
                     "%d amended)" % (N, sc["اصلية"], sc["معدلة"])),
        "record_type": "verified_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "english_text_consulted": False,
        "record_count": len(llm),
        "article_range": [1, N],
        "text_status": STATUS,
        "verification_tier": "TIER_2",
        "consolidated_amended_law": True,
        "status_counts": sc,
        "not_legal_advice": True,
        "records": llm,
    }, open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("Wrote %d verified + %d LLM-ready CMA Investment Funds Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
