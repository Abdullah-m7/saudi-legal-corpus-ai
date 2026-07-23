#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Anti-Money Laundering Law track
(اللائحة التنفيذية لنظام مكافحة غسل الأموال), the companion regulation to this
corpus's aml_law track (نظام مكافحة غسل الأموال, Royal Decree M/20, 14/2/1439H).

The Regulation is issued/amended under Article 50 of the AML Law by the President
of State Security in agreement with the Minister of Finance, the Public
Prosecutor and the Governor of the Saudi Central Bank. Its founding approval is
cable (برقية) No. 14525 dated 19/2/1439H (the number/date SAMA's rulebook
canonicalises as the Regulation's official reference, status "in-force"); it was
amended by Administrative Decision No. 98752 (12/5/1446H, Article 17) and the
current consolidated text was promulgated by Administrative Decision No. 266507
dated 9/12/1447H ("تحديث اللائحة ... وفق الصيغة المرفقة") following the base
Law's own M/223 (27/10/1447H) amendments.

VERIFICATION TIER -- see aml_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

laws.boe.gov.sa was checked FIRST per this corpus's standard methodology; it is
unreachable this pass (connection reset) and has no dedicated lawId page for
this Regulation (BOE does not catalogue State-Security/administrative executive
regulations as standalone lawId records). web.archive.org is blocked in this
session and was not attempted.

PRIMARY SOURCE: the official SCANNED PDF published on aml.gov.sa (the issuing
Permanent Committee / Presidency of State Security's own site), fetched directly
(HTTP 200, 34 pages, sha256 96a4250a...). It is a 300dpi scanned-image PDF with
NO embedded text layer; page 1 is Admin Decision 266507, pages 2-34 are the
Regulation body ("Page 1 of 33" .. "Page 33 of 33").

Text was reconciled from TWO independent channels (like this corpus's vat /
income_tax tracks):
 (a) a clean BORN-DIGITAL source for articles 1,2,5,7,8,9,10,14,15,16 --
     qanoniah.com's official API (api.qanoniah.com/v1/files/..., meta.isText
     true), confirmed to be the SAME current/consolidated version (last-modified
     1447-12-09 = Admin Decision 266507; its Article 1 defines the newer terms
     المحفظة الإلكترونية / تسليم مراقب). Unauthenticated it exposes only these
     ten articles (all of the present articles in the 1-16 range), so it was
     used only for those.
 (b) the remaining fifteen articles (17,20,22,23,24,36,37,38,39,40,41,42,43,48,
     49) were OCR-extracted from the scanned PRIMARY source (tesseract-ara,
     200-300dpi) and then VISUALLY ADJUDICATED article-by-article against the
     rendered page images. qanoniah's articles 2,5,10,16 were matched verbatim
     against the scan, confirming both channels carry the same in-force text.

STRUCTURE: the Regulation does NOT elaborate every Law article -- it covers only
the 25 Law articles that need implementing detail, numbering provisions at the
PARAGRAPH level as "س/ع" (paragraph س of article ع). article_number is the ع
value; number_label_ar ("المادة (ع) من اللائحة") is constructed (the source
prints no explicit article headers). Present articles: 1,2,5,7,8,9,10,14,15,16,
17,20,22,23,24,36,37,38,39,40,41,42,43,48,49 across nine chapters carrying the
Law's own chapter numbers (I-VI, VIII-X); chapter VII (العقوبات) has no
counterpart, so chapter numbering jumps from VI (الرقابة) to VIII (المصادرة).
24 articles اصلية, 1 معدلة (Article 17, per Admin Decision 98752; prior sub-
paragraph text not recovered -- flagged, not fabricated), 0 ملغاة, 0 مضافة.

Arabic governs; no translation/paraphrase/interpretation. Western digits in the
qanoniah channel were normalised to Arabic-Indic to match the scanned source and
the aml_law family (a numeral-glyph display normalisation only). Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "aml", "regulation", "official_source",
                   "aml_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "aml", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "aml_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "aml_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "aml_regulation_arabic_legal_llm",
                        "aml_regulation_legal_llm_001_025.json")

LAW_ID = "sa-aml-regulation-14525-1439"
LAW_AR = "اللائحة التنفيذية لنظام مكافحة غسل الأموال"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"aml_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = {"aml_regulation_art_017"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم النظام الأموال المملكة الجهة الجهات").split())


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
        return STATUS_AMENDED
    if key in ADDED_KEYS:
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
        top_status = _top_status(key)
        ver.append({"law_key": "aml", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "AML_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_mukarrar,
                    "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "source_channel": a.get("source_channel"),
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "official_text_status": top_status,
                    "governing_source_note": ("Arabic governs; PRIMARY source is the aml.gov.sa "
                                              "official SCANNED PDF (Admin Decision 266507, "
                                              "9/12/1447H). laws.boe.gov.sa was checked first but "
                                              "is unreachable this pass and has no dedicated "
                                              "lawId page. Articles 1,2,5,7,8,9,10,14,15,16 come "
                                              "from qanoniah.com's born-digital API (confirmed "
                                              "same current version); the rest were OCR-extracted "
                                              "from the scan and visually adjudicated. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies before relying on "
                                              "this track -- in particular the scanned-source/OCR "
                                              "tier for the 15 scan-sourced articles, the "
                                              "paragraph-level 'س/ع' numbering (no explicit "
                                              "article headers), and the deliberately skipped Law "
                                              "article numbers."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "aml-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "aml/regulation/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام مكافحة غسل الأموال" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("AML Implementing Regulation "
                                                          "(founding approval cable No. 14525, "
                                                          "19/2/1439H; consolidated by Admin "
                                                          "Decision No. 266507, 9/12/1447H) — "
                                                          "PRIMARY: aml.gov.sa scanned PDF; "
                                                          "articles 1,2,5,7,8,9,10,14,15,16 "
                                                          "cross-sourced from qanoniah.com "
                                                          "born-digital API; SAMA rulebook "
                                                          "metadata (no.14525) for cross-check; "
                                                          "laws.boe.gov.sa unreachable, no "
                                                          "dedicated lawId page"),
                                     "source_authority_ar": "اللائحة التنفيذية لنظام مكافحة غسل الأموال (الاعتماد التأسيسي بالبرقية رقم 14525 وتاريخ 19/2/1439هـ، والنص الموحَّد الحالي بالقرار الإداري رقم 266507 وتاريخ 9/12/1447هـ) — المصدر الأساسي: ملف aml.gov.sa الممسوح ضوئيا؛ المواد 1 و2 و5 و7 و8 و9 و10 و14 و15 و16 من واجهة qanoniah.com الرقمية الأصلية؛ بيانات البنك المركزي الوصفية (الرقم 14525) للتحقق المتقاطع؛ بوابة هيئة الخبراء غير قابلة للوصول ولا تملك صفحة مخصصة",
                                     "source_status": a["status"].lower(),
                                     "source_channel": a.get("source_channel"),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "aml",
               "layer": "AML_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "article_numbers_present": src.get("article_numbers_present"),
               "verification_tier": src.get("verification_tier"),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-aml-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (25 مادة؛ 24 أصلية، 1 معدلة، 0 ملغاة، 0 مضافة)",
               "title_en": ("Implementing Regulation of the Anti-Money Laundering Law — Arabic "
                            "LLM-ready layer (25 records: 24 original, 1 amended, 0 repealed, "
                            "0 added)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_numbers_present": src.get("article_numbers_present"),
               "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready AML Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
