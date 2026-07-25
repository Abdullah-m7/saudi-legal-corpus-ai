#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Press and Publications Law track
(اللائحة التنفيذية لنظام المطبوعات والنشر, Ministerial Decision M/W/2759/1/M,
16/6/1422H; amended by Ministerial Decision 91513, 9/11/1439H).

This is the explicit follow-up candidate flagged by this corpus's own press
(base law) track -- see sources/press/law/official_source/
press_law_official_source.json, known_unresolved_discrepancies key
press_art_companion_regulations_not_ingested.

VERIFICATION TIER -- summary (full account in official_source.json):
TIER_2. Primary source: the Ministry of Media's own official PDF of this
regulation (media.gov.sa/s3.media.gov.sa), reached via a Wayback Machine
snapshot dated 23 Nov 2024 (live media.gov.sa was unreachable this pass,
same pattern already documented by this corpus's press track for this
domain). pdftotext/PyMuPDF extraction of this PDF produces word-internal
character scrambling (an embedded-font/ToUnicode defect seen elsewhere in
this corpus), so ALL 99 articles were transcribed via direct vision reading
of every one of the source PDF's 98 pages (rendered to PNG), not OCR --
consistent with this corpus's anti_smoking_regulation precedent. Partial
independent corroboration: an Umm al-Qura Gazette (uqn.gov.sa) article
independently confirms this regulation's Article 69 paragraph (ج) by
number and subject matter. No full second independent full-text source was
found (WIPO Lex, qanoniah.com, laws.boe.gov.sa, islamport.com were all
checked and ruled out -- see known_unresolved_discrepancies).

99 articles, 7 أبواب (Article 1 sits before the first named باب): باب 1
(2-16) شروط وضوابط التراخيص الإعلامية; باب 2 (17-62) ضوابط ممارسة الأنشطة
الإعلامية (contains internal فصول with genuine numbering defects -- missing
فصل 3/4/5, a duplicated فصل 6, and a 17-then-15-then-16 sequence -- all
preserved as printed, not renumbered); باب 3 (63-77) أحكام المطبوعات
وتداولها; باب 4 (78-89) شئون الصحافة; باب 5 (90-92) إنشاء الجمعيات
الإعلامية; باب 6 (93-96) ضبط المخالفات وعرضها على اللجنة; باب 7 (97-99)
الأحكام العامة.

AMENDMENT ATTRIBUTION: this regulation's own cover page confirms it was
amended by Ministerial Decision 91513 (9/11/1439H), but the source is a
flat consolidated PDF with no changelog/redline -- which specific article(s)
this amendment touched could NOT be determined this pass. All 99 articles
are therefore recorded as legal_status_ar="اصلية" (current consolidated
text) with consolidated_amended_law=True, rather than fabricating a
per-article amendment attribution.

Articles 7 and 16 each contain a bracketed in-text placeholder printed in
red in the source, "{ تم تعديل الاجراء تقنياً }", replacing a specific
procedural clause -- preserved verbatim, not deleted or reconstructed.

No legal text is altered beyond whitespace normalisation. Arabic governs;
no translation/paraphrase/interpretation performed. Read-only over input;
deterministic over outputs. Standalone track -- no shared pipeline files
modified.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "press_regulation", "law", "official_source",
                   "press_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "press_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "press_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "press_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "press_regulation_arabic_legal_llm",
                        "press_regulation_legal_llm_001_099.json")

LAW_ID = "sa-press-regulation-m-w-2759-1422h"
LAW_AR = "اللائحة التنفيذية لنظام المطبوعات والنشر"
TOP_STATUS = ("TIER_2_MOM_WAYBACK_NOV2024_VISION_READ_FULL_X_UQN_GOV_SA_PARTIAL_"
              "CROSSCHECK_ART69_LIVE_MOM_UNREACHABLE_DIRECT")
KEY_RE = r"press_reg_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الوزارة الوزير خلال وعلى وذلك وهذا "
            "وهذه أنه إليها إليه عليها منهم بينهم حالة حالات").split())


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


GOV_NOTE = ("Arabic governs; this track rests on the Ministry of Media's own official "
            "PDF of this regulation, reached via a Wayback Machine snapshot (23 Nov "
            "2024) after live media.gov.sa/s3.media.gov.sa proved unreachable this "
            "pass. pdftotext/PyMuPDF extraction of this PDF scrambles Arabic text at "
            "the character level, so all 99 articles were transcribed via direct "
            "vision reading of every one of the source's 98 pages, not OCR. Partial "
            "independent corroboration: an Umm al-Qura Gazette (uqn.gov.sa) article "
            "independently confirms Article 69 paragraph (ج) by number and subject. "
            "No full second independent full-text source was found -> TIER_2. This "
            "regulation was amended by Ministerial Decision 91513 (9/11/1439H) but "
            "which article(s) that amendment touched could not be determined from "
            "this flat, changelog-free consolidated source; all articles are recorded "
            "as legal_status_ar='اصلية' with consolidated_amended_law=True. See "
            "known_unresolved_discrepancies in the source artifact -- including a "
            "genuine فصل-numbering defect internal to Baab 2, an internal "
            "المساحة/السياحة authority-name inconsistency between Articles 72 and 73, "
            "and two in-text procedural-redaction placeholders in Articles 7 and 16 "
            "-- before relying on this track's text or provenance.")

SRC_AUTH = ("Implementing Regulation of the Press and Publications Law, issued by "
            "Ministerial Decision (Minister of Media) No. M/W/2759/1/M (16/6/1422H), "
            "amended by Decision 91513 (9/11/1439H). Full text from the Ministry of "
            "Media's own official PDF (media.gov.sa, via a near-contemporaneous "
            "Wayback Machine snapshot), vision-read in full across all 98 pages. "
            "Partially cross-checked against an Umm al-Qura Gazette article "
            "(Article 69(c)) -> TIER_2")

SRC_AUTH_AR = ("اللائحة التنفيذية لنظام المطبوعات والنشر، صادرة بقرار وزير الإعلام رقم "
               "(م/و/2759/1/م) وتاريخ 16/6/1422هـ، وعُدّلت بقرار رقم (91513) وتاريخ "
               "9/11/1439هـ. النص الكامل من ملف وزارة الإعلام الرسمي عبر لقطة أرشيفية "
               "قريبة الزمن من Wayback Machine، مقروء بصرياً بالكامل عبر 98 صفحة. "
               "تحقق تقاطعي جزئي عبر مقال من جريدة أم القرى (المادة 69/ج) -- TIER_2")


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
        ver.append({"law_key": "press_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "PRESS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": TOP_STATUS,
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "press-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "press_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام المطبوعات والنشر"
                                          % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": SRC_AUTH,
                                     "source_authority_ar": SRC_AUTH_AR,
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "press_regulation",
               "layer": "PRESS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "amendment_decree_ar": src.get("amendment_decree_ar"),
               "amendment_decree_date_hijri": src.get("amendment_decree_date_hijri"),
               "base_law_decree": src.get("base_law_decree"),
               "base_law_decree_date_hijri": src.get("base_law_decree_date_hijri"),
               "base_law_key": src.get("base_law_key"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-press-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (99 مادة)",
               "title_en": ("Implementing Regulation of the Press and Publications Law "
                            "— Arabic LLM-ready layer (99 records)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 99], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Press Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
