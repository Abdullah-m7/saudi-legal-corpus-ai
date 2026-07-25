#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the track for the Implementing Regulation of the Water Law for
MEWA's mandate (اللائحة التنفيذية لنظام المياه الخاصة بمهام وزارة البيئة
والمياه والزراعة).

VERIFICATION TIER -- see sources/water_regulation/law/official_source/
water_regulation_official_source.json's verification_methodology_note for the
full account. Summary:

PRIMARY SOURCE, DIRECT FETCH SUCCEEDED THIS PASS: the regulation was fetched
directly via curl (HTTP 200) from mewa.gov.sa's own RulesLibrary document
path (InformationCenter/DocsCenter/RulesLibrary/Documents) -- the Ministry's
own site, not a mirror or secondary aggregator. 60-page PDF, internal cover
marked "نسخة رقم (1) - أكتوبر 2020م" (Version 1, October 2020).

TEXT EXTRACTION METHOD: the PDF's embedded text layer has a partial font/
ToUnicode encoding defect (confirmed by direct comparison against OCR and
against the rendered page images) that silently substitutes some characters
in some words (concentrated around ب/ح and لا/را letter sequences) --
extracting it programmatically (pdftotext, PyMuPDF) would risk introducing
wrong words. To avoid ANY guessed/inferred correction, every one of the 156
articles was transcribed by directly reading the rendered page images
(300dpi) rather than the corrupted text layer -- i.e. every word in this
track's text was visually read from the primary document, not extracted
through a lossy pipeline or reconstructed by pattern-guessing.

156 records, ALL اصلية (156 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة) across 16
chapters (فصول). No inline per-article titles beyond spelled-ordinal "المادة
..." labels -- no title_ar field is used; section_ar carries each article's
chapter (and, where the source prints one, sub-heading) title.

DECREE NUMBER/DATE -- HONEST NON-CONFIRMATION (a material correction to this
pass's own starting brief): the official cover page published by MEWA itself
has BLANK decree-number and day/month fields ("قرار وزاري رقم (   ) بتاريخ
  /   /1442هـ"). Independent search confirms the number/date supplied in this
pass's initial brief (140115/1/1442, 7/3/1442H) actually belongs to the
SIBLING regulation issued under Article 76(2) of the Water Law -- the
Authority's regulation for service-provision activities (the FAOLEX PDF
sau213419.pdf) -- not to this Article-76(1) Ministry regulation. This track
therefore records only the confirmed legal basis (Water Law Article 76(1),
Royal Decree M/159, 11/11/1441H) and does NOT fabricate a decree number/date
for this regulation itself. See known_unresolved_discrepancies.

ANNEXES (not ingested as articles): three technical annexes (quality-standard
tables for treated water, pages 56-59) follow Article 156. They carry no
"المادة" numbering and are out of scope for this track's 156-article body;
their existence and content are disclosed in known_unresolved_discrepancies.

Read-only over input; deterministic over outputs. Arabic governs; no
translation/paraphrase/interpretation performed on the Arabic text.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "water_regulation", "law", "official_source",
                   "water_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "water_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "water_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "water_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "water_regulation_arabic_legal_llm",
                        "water_regulation_legal_llm_001_0156.json")

LAW_ID = "sa-water-regulation-mewa-mandate"
LAW_AR = "اللائحة التنفيذية لنظام المياه الخاصة بمهام وزارة البيئة والمياه والزراعة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
KEY_RE = r"water_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم المياه الوزارة الوزير الهيئة").split())


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


def _top_status(key):
    if key in AMENDED_KEYS:
        return STATUS_AMENDED_DATED
    return STATUS_UNCHANGED


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
        top_status = _top_status(key)
        ver.append({"law_key": "water_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "WATER_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; full text fetched directly via curl "
                                              "(HTTP 200) from mewa.gov.sa's own RulesLibrary document "
                                              "path (not a mirror/aggregator). The PDF's embedded text "
                                              "layer has a partial font/ToUnicode encoding defect "
                                              "(confirmed by comparison against OCR and rendered page "
                                              "images); to avoid any guessed correction, every article "
                                              "was transcribed by directly reading the rendered page "
                                              "images (300dpi), not the corrupted text layer. The "
                                              "Ministerial Decision's own number/day/month are BLANK on "
                                              "the official cover page and are not fabricated here; the "
                                              "140115/1/1442 (7/3/1442H) number surfaced in this pass's "
                                              "initial brief was independently found to belong to the "
                                              "SIBLING Article-76(2) Authority regulation, not this "
                                              "Article-76(1) Ministry regulation -- see "
                                              "known_unresolved_discrepancies in the source artifact "
                                              "before relying on this track's provenance."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "water-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "water_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام المياه" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Ministerial Decision under Water Law "
                                                          "Article 76(1) (Royal Decree M/159, "
                                                          "11/11/1441H) -- full text fetched directly "
                                                          "(HTTP 200) from mewa.gov.sa's own "
                                                          "RulesLibrary; the Decision's own number/date "
                                                          "are blank on the official cover and are not "
                                                          "confirmed this pass (see "
                                                          "known_unresolved_discrepancies); every "
                                                          "article's text was read directly from "
                                                          "rendered page images to avoid the PDF's "
                                                          "partial text-layer font-encoding defect"),
                                     "source_authority_ar": "قرار وزاري استناداً للفقرة (1) من المادة (76) من نظام المياه (المرسوم الملكي رقم م/159 وتاريخ 11/11/1441هـ) — النص الكامل جُلب مباشرة (HTTP 200) من مكتبة اللوائح على mewa.gov.sa؛ رقم القرار وتاريخه اليومي/الشهري غير مؤكدين هذه الجولة (حقلان فارغان في نسخة الغلاف الرسمية، انظر known_unresolved_discrepancies)؛ كل مادة قُرئت مباشرة من صور الصفحات المصورة تفادياً لعطب ترميز الخط في طبقة نص الملف",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "water_regulation",
               "layer": "WATER_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-water-regulation-mewa-mandate-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (156 مادة؛ 156 أصلية)",
               "title_en": ("Implementing Regulation of the Water Law for MEWA's mandate — Arabic "
                            "LLM-ready layer (156 records: 156 original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 156], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Water Regulation (MEWA mandate) records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
