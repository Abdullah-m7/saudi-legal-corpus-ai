#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Arabian VAT Law track
(اللائحة التنفيذية لنظام ضريبة القيمة المضافة, ZATCA Board of Directors Resolution
No. (3839), 14 Dhul-Hijjah 1438H, issued under the authority of the VAT Law,
Royal Decree M/113, 2/11/1438H, and the GCC Unified VAT Agreement).

This is the companion-regulation follow-up candidate explicitly flagged by this
corpus's own vat_law track (see sources/vat/law/official_source/
vat_law_official_source.json, verification_methodology_note: "A companion
Implementing Regulation is confirmed to exist (ZATCA Board Decision 3839,
14 Dhul-Hijjah 1438H, amended at least 12 times ...) but is not extracted in
this track."). This track ingests the CURRENT consolidated text.

VERIFICATION TIER -- see vat_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: ZATCA's (Zakat, Tax and Customs Authority) own official
consolidated Arabic PDF of the VAT Implementing Regulation, downloaded directly
from zatca.gov.sa (HTTP 200, 160 pages, a born-digital Microsoft-Print-To-PDF
file, internal CreationDate 16 April 2025). This is the "Tenth Edition"
(النسخة العاشرة, Shawwal 1446H / April 2025, printed on the cover), which
consolidates the founding Resolution (3839) with ELEVEN subsequent amending
Board resolutions -- all eleven printed with their own numbers and dual
Hijri/Gregorian dates on the file's own cover page, recorded in full in the
source artifact's amendment_history. laws.boe.gov.sa was checked first per this
corpus's standard methodology but has NO dedicated lawId page for this
Implementing Regulation (Board-level regulations are not catalogued as
standalone lawId records there), so the issuing Authority's own site is the
authoritative source for the current consolidated text.

DATE ANOMALY (resolved this pass, not merely copied from the parent track):
ZATCA's own cover prints "14 ذو الحجة 1438هـ الموافق 14 نوفمبر 2016م". The
printed Gregorian is WRONG: 14 Dhul-Hijjah 1438H converts independently (via
hijri_converter, and confirmed by the Eid al-Adha anchor -- 10 Dhul-Hijjah
1438H = 1 Sep 2017G) to 5 September 2017G, not November 2016. Moreover
14 Nov 2016 would be ~14 Safar 1438H and would predate the parent VAT Law
itself (M/113, 2 Dhul-Qadah 1438H = 25 July 2017G), which is impossible for its
own Implementing Regulation. The Hijri date governs; the printed Gregorian is a
disclosed source error (see known_unresolved_discrepancies).

EXTRACTION METHODOLOGY (two fully independent pipelines, reconciled): this PDF
stores Arabic in presentation forms with a systematic bidi ordering defect
(word order reversed on many lines, accusative tanwin-alef detached and
fronted, mirrored punctuation/parentheses). Two independent extractions were
reconciled: (1) a character-level geometric reconstruction from PyMuPDF
(rawdict) glyph coordinates, RTL-ordered by x-position -- exact source glyphs +
correct word order, but retaining the tanwin/split/mirror artifacts; (2)
Tesseract Arabic OCR of 300dpi page renders -- correct visual reading order,
tanwin and punctuation, but with occasional dropped lines and character errors
(hamza / alef-maksura). The two were aligned (difflib): OCR order is the
structural base, OCR character errors are corrected from the exact source
glyphs on canonical-form match, OCR-dropped lines are spliced from the
geometric reconstruction, and a detached-tanwin-alef correction dictionary is
learned from the alignment pairs themselves and applied to spliced spans. The
result is content-complete and correctly ordered, with limited disclosed
residual extraction-layer artifacts (see known_unresolved_discrepancies).
Diacritics (tashkeel) and tatweel are stripped uniformly, consistent with this
corpus's other tracks. Arabic governs; no translation/paraphrase/interpretation.

82 articles across 12 chapters: 37 اصلية, 42 معدلة, 3 مضافة, 0 ملغاة. The three
مضافة articles are the "mukarrar" articles added by later amendments
(32-mukarrar, 36-mukarrar, 36-mukarrar-2); the 42 معدلة are derived from the
amendment footnotes printed inline in the source itself and from its own
"ما طرأ على اللائحة التنفيذية من تعديلات" (list of amendments) section --
article-level, with disclosed attribution uncertainty. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "vat", "regulation", "official_source",
                   "vat_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "vat", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "vat_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "vat_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "vat_regulation_arabic_legal_llm",
                        "vat_regulation_legal_llm_001_082.json")

LAW_ID = "sa-vat-regulation-3839-1438"
LAW_AR = "اللائحة التنفيذية لنظام ضريبة القيمة المضافة"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"vat_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة النظام الضريبة الضريبية للضريبة التوريد التوريدات").split())


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


def _top_status(a):
    ls = a.get("legal_status_ar")
    if ls == "معدلة":
        return STATUS_AMENDED
    if ls == "مضافة":
        return STATUS_ADDED
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
        top_status = _top_status(a)
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "vat", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "VAT_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "text_complete": text_complete,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; PRIMARY source is zatca.gov.sa "
                                              "(the issuing Authority's own official consolidated "
                                              "PDF, 'Tenth Edition' / April 2025, a born-digital "
                                              "file) -- laws.boe.gov.sa was checked first per "
                                              "standard methodology but has no dedicated lawId page "
                                              "for this Implementing Regulation at all. Article/"
                                              "chapter count (82 articles incl. 3 mukarrar, 12 "
                                              "chapters) confirmed against the file's own printed "
                                              "table of contents and body chapter headings; the "
                                              "founding Resolution 3839 plus its eleven amending "
                                              "Board resolutions are all printed with numbers and "
                                              "dual Hijri/Gregorian dates on the file's own cover. "
                                              "See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text -- in "
                                              "particular the two-pipeline (PyMuPDF-geometric x "
                                              "Tesseract-OCR) reconciliation and its disclosed "
                                              "residual extraction-layer artifacts, the resolved "
                                              "'14 November 2016' printed-Gregorian date error, "
                                              "and the article-level (not paragraph-level) "
                                              "amendment classification."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "vat-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "vat/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام ضريبة القيمة المضافة" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("ZATCA Board of Directors Resolution "
                                                          "No. (3839) (14 Dhul-Hijjah 1438H = 5 Sep "
                                                          "2017G), consolidated Tenth Edition (Apr "
                                                          "2025) incorporating eleven amending Board "
                                                          "resolutions through Resolution (01-06-24) "
                                                          "(19 Nov 2024G) — zatca.gov.sa (issuing "
                                                          "Authority's own site); laws.boe.gov.sa "
                                                          "has no dedicated lawId page for this "
                                                          "Implementing Regulation"),
                                     "source_authority_ar": "قرار مجلس إدارة الهيئة العامة للزكاة والدخل رقم (3839) وتاريخ 14 ذو الحجة 1438هـ (الموافق 5 سبتمبر 2017م) — النسخة العاشرة المُوحَّدة (أبريل 2025م) المُدمِجة أحد عشر قرارًا تعديليًّا حتى القرار رقم (01-06-24) بتاريخ 19 نوفمبر 2024م — الموقع الرسمي لهيئة الزكاة والضريبة والجمارك (zatca.gov.sa)؛ بوابة هيئة الخبراء لا تملك صفحة مخصصة لهذه اللائحة التنفيذية",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "vat",
               "layer": "VAT_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-vat-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (82 مادة؛ 37 أصلية، 42 معدلة، 3 مضافة، 0 ملغاة)",
               "title_en": ("Implementing Regulation of the Saudi Arabian VAT Law — Arabic "
                            "LLM-ready layer (82 records: 37 original, 42 amended, 3 added, "
                            "0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 79], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready VAT Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
