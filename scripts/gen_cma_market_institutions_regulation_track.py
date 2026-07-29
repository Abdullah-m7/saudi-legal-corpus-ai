#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the CMA Capital Market Institutions Regulations track (لائحة
مؤسسات السوق المالية, CMA Board Resolution No. (1-83-2005), dated 21/5/1426H =
28/6/2005G, issued pursuant to the Capital Market Law promulgated by Royal
Decree M/30 dated 2/6/1424H, as amended through Resolution (2-3-2026), dated
18/07/1447H = 07/01/2026G).

VERIFICATION TIER: TIER_2 -- see the source artifact's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: the official Arabic PDF linked from CMA's own regulations
catalogue --
https://cma.org.sa/RulesRegulations/Regulations/Documents/the_Capital_Market_Institutions_Regulations-ar.pdf
-- fetched directly this pass (HTTP 200, 111-page born-digital PDF). ARABIC
GOVERNS. The CMA English edition was used ONLY to corroborate the citation and
the article count, NEVER to correct or reconstruct Arabic -- and it is in any
case a STALE vintage (amended through 4-87-2024, not 2-3-2026).

RENAME HISTORY, established rather than assumed: Resolution 1-83-2005 issued
this instrument as «لائحة الأشخاص المرخص لهم» (Authorised Persons
Regulations). CMA's own announcement CMA_N_2764 records the Board's approval
of «تعديل اسم «لائحة الأشخاص المرخص لهم» ليكون «لائحة مؤسسات السوق المالية»»
with effect from 15/3/1442H (1/11/2020G), certain provisions from 28/5/1443H
(1/1/2022G). Same instrument, same founding resolution, renamed in 2020. CMA
does not publish the NUMBER of the renaming resolution; it is recorded as
unknown, not guessed.

ARTICLE COUNT: 99 -- verified independently, not taken from the commissioning
brief: the Arabic PDF's own table of contents, an expected-ordinal
segmentation of the enacting text yielding an unbroken 1..99 run, and the CMA
English edition's Article 1..99. The census figure of 99 is confirmed.

9 أبواب, 13 فصول, plus 11 annexes which are NOT ingested (disclosed). The PDF
carries NO per-article amendment footnotes, so NO article is flagged معدلة --
all 99 are اصلية in the sense this corpus uses for a consolidated current text
without published per-article attribution. That records the ABSENCE of
attribution, not an assertion that nothing was ever amended.

Text was extracted at glyph level because pdftotext/PyMuPDF reverse the
characters inside this PDF's Arabic ligature glyphs and pypdf drops some of
them; all 99 texts were then cross-checked article-by-article against an
independent secondary rendering (median agreement 1.0000, mean 0.9902), with
every divergence resolved in favour of the official CMA PDF.

No legal text is altered. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = "cma_market_institutions_regulation"
SRC = os.path.join(ROOT, "sources", KEY, "regulation", "official_source",
                   "%s_official_source.json" % KEY)
OUT_VER = os.path.join(ROOT, "sources", KEY, "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "%s_verified_records.jsonl" % KEY)
SUMMARY = os.path.join(OUT_VER, "%s_verified_summary.json" % KEY)
LLM_PATH = os.path.join(ROOT, "data", "%s_arabic_legal_llm" % KEY,
                        "%s_legal_llm_001_099.json" % KEY)

LAW_ID = "sa-cma-market-institutions-regulation-1-83-2005"
LAW_AR = "لائحة مؤسسات السوق المالية"
STATUS = ("CMA_GOV_SA_OFFICIAL_PDF_PRIMARY_X_GLYPH_LEVEL_LIGATURE_SAFE_EXTRACTION"
          "_X_INDEPENDENT_SECONDARY_TEXT_CROSSCHECK")
KEY_RE = r"cma_market_institutions_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة مؤسسة السوق المالية مؤسسات العميل العملاء").split())

GOVERNING_NOTE = (
    "Arabic governs. PRIMARY source is the official Arabic PDF of لائحة "
    "مؤسسات السوق المالية linked from cma.gov.sa's own regulations catalogue "
    "and fetched directly (HTTP 200, 111-page born-digital PDF). Because this "
    "PDF's embedded fonts use Arabic ligature glyphs that pdftotext/PyMuPDF "
    "expand and then reverse (المملكة -> اململكة) and that pypdf silently "
    "drops, the text was extracted at GLYPH level with each multi-character "
    "CMap expansion kept atomic -- no character is substituted, invented or "
    "reconstructed, and no whole-word guess list is used. All 99 texts were "
    "cross-checked against an independent secondary rendering (median "
    "agreement 1.0000); every divergence was resolved in favour of the "
    "official PDF. See verification_methodology_note and "
    "known_unresolved_discrepancies in the source artifact before relying on "
    "this track -- in particular: the instrument was issued in 2005 as «لائحة "
    "الأشخاص المرخص لهم» and RENAMED «لائحة مؤسسات السوق المالية» with effect "
    "from 15/3/1442H (1/11/2020G); the source PDF carries NO per-article "
    "amendment footnotes, so no article is flagged معدلة; the amendment chain "
    "listed is verified but NOT complete; and the 11 annexes are not ingested.")

SOURCE_AUTHORITY_EN = (
    "CMA Board Resolution No. (1-83-2005), dated 21/5/1426H (28/6/2005G), "
    "issued pursuant to the Capital Market Law (Royal Decree M/30, 2/6/1424H) "
    "-- cma.gov.sa, the issuing Authority's own domain; consolidated text as "
    "amended through Resolution (2-3-2026), dated 18/07/1447H (07/01/2026G). "
    "Issued originally as the Authorised Persons Regulations and renamed the "
    "Capital Market Institutions Regulations with effect from 15/3/1442H "
    "(1/11/2020G).")
SOURCE_AUTHORITY_AR = (
    "قرار مجلس هيئة السوق المالية رقم (1-83-2005) وتاريخ 21/5/1426هـ (الموافق "
    "28/6/2005م)، الصادر بناءً على نظام السوق المالية الصادر بالمرسوم الملكي "
    "رقم (م/30) وتاريخ 2/6/1424هـ — الموقع الرسمي لهيئة السوق المالية "
    "(cma.gov.sa)؛ والنص المستوعب هنا هو النص النافذ المعدَّل بموجب القرار رقم "
    "(2-3-2026) وتاريخ 18/07/1447هـ (الموافق 07/01/2026م). وقد صدرت اللائحة "
    "أصلاً باسم «لائحة الأشخاص المرخص لهم» وعُدّل مسماها ليكون «لائحة مؤسسات "
    "السوق المالية» اعتباراً من 15/3/1442هـ الموافق 1/11/2020م.")


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
        section = a.get("section_ar", "")
        title = a.get("article_title_ar", "")
        label = a["number_label_ar"] + ((" — " + title) if title else "")
        ver.append({"law_key": KEY, "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "CMA_MARKET_INSTITUTIONS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "verification_tier": src["verification_tier"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "per_article_amendment_attribution_published": False,
                    "official_text_status": STATUS,
                    "governing_source_note": GOVERNING_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "cma-market-institutions-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "%s/regulation/articles/%03d" % (KEY, n),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من لائحة مؤسسات السوق المالية" % a["number_label_ar"],
                                          "%s من لائحة الأشخاص المرخص لهم" % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": SOURCE_AUTHORITY_EN,
                                     "source_authority_ar": SOURCE_AUTHORITY_AR,
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "former_source_document_ar": src["former_title_ar"],
                                     "verification_tier": src["verification_tier"],
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": KEY,
               "layer": "CMA_MARKET_INSTITUTIONS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "verification_tier": src["verification_tier"],
               "verification_tier_basis": src["verification_tier_basis"],
               "document_ar": src["document"], "document_en": src["document_en"],
               "former_title_ar": src["former_title_ar"],
               "former_title_en": src["former_title_en"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "administering_authority_en": src.get("administering_authority_en"),
               "official_source_url": src["official_source_url"],
               "corroborating_official_url": src["corroborating_official_url"],
               "secondary_crosscheck_url": src["secondary_crosscheck_url"],
               "consolidated_amended_law": True,
               "per_article_amendment_attribution_published": False,
               "chapter_structure": src["chapter_structure"],
               "annexes_not_ingested": src["annexes_not_ingested"],
               "amending_instruments": src.get("amending_instruments"),
               "amending_instruments_note": src.get("amending_instruments_note"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-cma-market-institutions-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (99 مادة)",
               "title_en": ("Capital Market Institutions Regulations — Arabic "
                            "LLM-ready layer (99 records)"),
               "former_title_ar": src["former_title_ar"],
               "former_title_en": src["former_title_en"],
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 99], "text_status": STATUS,
               "verification_tier": src["verification_tier"],
               "consolidated_amended_law": True,
               "per_article_amendment_attribution_published": False,
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready CMA Capital Market Institutions "
          "Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
