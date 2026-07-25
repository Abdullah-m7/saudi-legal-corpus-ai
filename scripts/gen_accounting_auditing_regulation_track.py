#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Law of the Accounting and
Auditing Profession track (اللائحة التنفيذية لنظام مهنة المحاسبة والمراجعة,
Minister of Commerce Resolution No. 00658, 14/11/1442H, issued under Article
22 of the base Law -- Royal Decree M/59, 27/7/1442H, already tracked
separately at sources/accounting_auditing/).

VERIFICATION TIER -- see sources/accounting_auditing_regulation/law/
official_source/accounting_auditing_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: SOCPA's own official PDF of the complete 15-article
Regulation (socpa.org.sa/SOCPA/files/45/459dbec2-4d34-43a8-ad1e-
5c3548f0b10d.pdf). Direct fetch to socpa.org.sa failed this pass (curl exit
35 / connection reset); the exact PDF URL was recovered via a single
reachable Wayback Machine snapshot (20251213225823, 13 Dec 2025).

CRITICAL EXTRACTION FINDING: this PDF's own embedded text layer is
systematically corrupted -- both pdftotext and PyMuPDF reproduce identical
letter-transposition defects (e.g. "في" -> "يف", "على" -> "عىل", "المادة" ->
"املادة"), baked into the file's own font/ToUnicode mapping. Since no clean
already-Unicode source exists for this Regulation (unlike
accounting_auditing_law's BOE changelog-popup), this track instead used
Tesseract Arabic OCR of 300dpi page-image renders as the PRIMARY text
source (OCR reads correct visual/logical glyph order), cross-checking every
digit/percentage/figure against the text-layer extraction (digits are not
subject to the same defect) and against two independent secondary sources
(argaam.com, darkhabr.com). See known_unresolved_discrepancies (key
accounting_auditing_regulation_pdf_textlayer_ligature_defect).

AMENDMENT: Ministry of Commerce Resolution No. 28 (3/2/1447H / 28 Jul
2025G) amended paragraphs (4) and (5) of Article (6) -- transferring the
license-application decision from the Ministry to the Authority (deciding
within 15 business days) -- confirmed via qanoonsa.com, and published Umm
al-Qura Gazette Issue 5099 (1 Aug 2025G). This mirrors, at the Regulation
level, the same policy shift Royal Decree M/169 made at the base-Law level.
The single available primary-source PDF snapshot already postdates this
amendment; no source recovered this pass quotes the pre-amendment wording
of paragraphs (4)/(5) verbatim (see known_unresolved_discrepancies, key
accounting_auditing_regulation_pre_2025_article6_text_not_recovered).

15 records: 14 اصلية, 1 معدلة (Article 6), 0 ملغاة, 0 مضافة. No
أبواب/فصول structure (flat 1-15). No inline per-article titles in the
source PDF -- no title_ar field is used. Article 9's staffing-percentage
table is linearized into prose sentences without altering any value.

No legal text is altered beyond whitespace normalization and the disclosed
OCR/text-layer reconciliation. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "accounting_auditing_regulation", "law", "official_source",
                   "accounting_auditing_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "accounting_auditing_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "accounting_auditing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "accounting_auditing_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "accounting_auditing_regulation_arabic_legal_llm",
                        "accounting_auditing_regulation_legal_llm_001_015.json")

LAW_ID = "sa-accounting-auditing-regulation-moc658-1442"
LAW_AR = "اللائحة التنفيذية لنظام مهنة المحاسبة والمراجعة"
TOP_STATUS = ("MIXED_TIER_SEE_PER_ARTICLE_STATUS_SOCPA_PDF_VIA_WAYBACK_TESSERACT_OCR_PRIMARY_X_"
              "PDFTOTEXT_DIGIT_CROSSCHECK_X_SECONDARY_SOURCES_LIVE_SOCPA_UNREACHABLE")
KEY_RE = r"accounting_auditing_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"accounting_auditing_regulation_art_006"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المحاسب القانوني الترخيص "
            "خلال كل أنه إليها إليه عليها منهم بينهم الوزارة الوزير المجلس مزاولة المهنة").split())


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
        ver.append({"law_key": "accounting_auditing_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "ACCOUNTING_AUDITING_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track's PRIMARY source is "
                                              "SOCPA's own official PDF of the Regulation (fetched "
                                              "via a single Wayback Machine snapshot, "
                                              "20251213225823, live socpa.org.sa unreachable this "
                                              "pass). The PDF's own text layer carries a systematic "
                                              "letter-transposition defect (baked into its embedded "
                                              "font mapping, reproduced identically by pdftotext and "
                                              "PyMuPDF); this record's text instead derives from "
                                              "Tesseract Arabic OCR of 300dpi page renders, "
                                              "cross-checked digit-for-digit against the text-layer "
                                              "extraction and against argaam.com/darkhabr.com "
                                              "secondary sources. Article 6 carries a 2025 "
                                              "amendment (Ministry of Commerce Resolution 28, "
                                              "3/2/1447H) to paragraphs 4-5, sourced from this same "
                                              "PDF snapshot (which already postdates the amendment) "
                                              "and cross-verified against qanoonsa.com -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text as "
                                              "necessarily reflecting a clean born-digital "
                                              "transcription."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "accounting-auditing-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "accounting_auditing_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام مهنة المحاسبة والمراجعة"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministry of Commerce Resolution No. "
                                                          "00658 (14/11/1442H) -- SOCPA's own "
                                                          "official PDF via Wayback Machine "
                                                          "archive (primary, OCR-derived text), "
                                                          "cross-verified against argaam.com and "
                                                          "darkhabr.com; live socpa.org.sa "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "قرار وزير التجارة رقم (00658) — نسخة الهيئة السعودية للمراجعين والمحاسبين الرسمية (PDF) عبر أرشيف Wayback Machine، مستخرجة بالتعرف الضوئي (OCR) ومطابقة مع argaam.com وdarkhabr.com",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "accounting_auditing_regulation",
               "layer": "ACCOUNTING_AUDITING_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-accounting-auditing-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (15 مادة؛ 14 أصلية ومادة واحدة معدلة)",
               "title_en": ("Implementing Regulation of the Law of the Accounting and Auditing "
                            "Profession — Arabic LLM-ready layer (15 records: 14 original, 1 "
                            "amended)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 15], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Accounting and Auditing Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
