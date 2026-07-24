#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Saudi Standards and Quality Law
track (اللائحة التنفيذية لنظام المواصفات والجودة، قرار وزير التجارة رئيس مجلس
إدارة الهيئة السعودية للمواصفات والمقاييس والجودة رقم (098) وتاريخ 18/5/1446هـ
/ 20 نوفمبر 2024م؛ اعتمدها مجلس إدارة الهيئة بقراره رقم (02/203/2024) في
اجتماعه رقم (203) وتاريخ 15/11/2024م؛ منشورة في جريدة أم القرى العدد (5058)
بتاريخ 29/11/2024م).

FOLLOW-UP CANDIDATE CONFIRMED: the base law's own track (sources/
standards_quality/law/official_source/standards_quality_law_official_source.json,
known_unresolved_discrepancies key
standards_quality_implementing_regulation_out_of_scope) flagged this
Implementing Regulation as an out-of-scope follow-up candidate, confirmed only
via an Umm al-Qura Gazette notice at that time. This track completes that
follow-up: the decision number/date are now independently confirmed from THREE
sources (SASO's own official site, the Umm al-Qura Gazette's own API, and
qanoonsa.com), and the full 23-article text is extracted for the first time.

VERIFICATION TIER: TIER_1 -- see standards_quality_regulation_official_source.json's
verification_methodology_note for the full account. Summary: TWO independent
PRIMARY sources agree exactly on the decision number/date/meeting reference and
Article 1's opening text --
  (1) SASO's own official site (www.saso.gov.sa), the administering/issuing
      authority itself, hosting the full regulation text plus a linked PDF
      explicitly labelled "أصل الوثيقة" (the original document);
  (2) the Umm al-Qura Gazette's own API (uqn.gov.sa/api/article/.../json,
      fetched directly -- not merely search-engine indexed), across TWO
      separate gazette notices, one of which quotes the ministerial decision's
      preamble verbatim including "قرار وزير التجارة رقم (098) وتاريخ 18 /05/
      1446هـ".
The full 23-article text is cross-verified against qanoonsa.com (SECONDARY),
word-for-word identical except for a purely cosmetic numeral-script difference
in enumerated sub-clauses (the official PDF uses Western digits + period,
"1. 2. 3."; qanoonsa.com -- adopted here for consistency with this corpus's own
convention -- uses Eastern Arabic-Indic digits + dash, "١- ٢- ٣-"; content,
count and order are identical across all sources). Supplementary corroboration
from argaam.com (financial news) and independent search-engine indexing of
Articles 22-23. laws.boe.gov.sa has NO dedicated lawId page for this
Implementing Regulation (only for the base law); live access was
connection-reset and NOT circumvented.

23 records, ALL اصلية (no confirmed amendments as of 2026-07-24), 0 ملغاة, 0
مضافة. 7 أبواب (chapters): التعريفات (1) -- أحكام عامة (2-4) -- إعداد واعتماد
وتبني المواصفة والوثيقة ذات الصلة (5-10) -- مراجعة وتطبيق المواصفة السعودية
والوثيقة ذات الصلة (11-13) -- الجودة (14-20) -- إجراءات عمل المفتشين (21) --
الأحكام الختامية (22-23).

NO PREDECESSOR REGULATION: unlike traffic_regulation, this is the FIRST
Implementing Regulation issued under the base law (itself only enacted August
2024); there is no prior regulation for this one to supersede.

NUMERAL-STYLE COSMETIC DIFFERENCE: see verification_methodology_note. Not a
substantive difference -- every enumerated sub-clause's content, count and
order match exactly between the official PDF, SASO's own HTML rendering, and
qanoonsa.com.

law_component IS "regulation" throughout (not "law"), distinguishing every
record here from the separate base-law track (track_id: standards_quality,
law_component: "law").

TASHKEEL: source text (qanoonsa.com) carries no diacritics. Two stray em-dashes
(in Article 1's "الترخيص" definition, and in Article 21 item 6) were normalized
to plain hyphens matching the surrounding document's own dash style elsewhere
in the same two articles (display layer only, no legal text altered). Arabic
governs; no translation, paraphrase or interpretation performed; read-only over
input, deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "standards_quality_regulation", "law", "official_source",
                   "standards_quality_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "standards_quality_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "standards_quality_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "standards_quality_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "standards_quality_regulation_arabic_legal_llm",
                        "standards_quality_regulation_legal_llm_001_023.json")

LAW_ID = "sa-standards-quality-regulation-098-1446"
LAW_AR = "اللائحة التنفيذية لنظام المواصفات والجودة"
STATUS_UNCHANGED = "UNCHANGED"
KEY_RE = r"standards_quality_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي خلال وعلى وذلك وهذا وهذه أنه إليها "
            "إليه عليها منهم بينهم الهيئة المجلس ذات الصلة التالية التالي").split())


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


STATUS_MAIN = ("SASO_OFFICIAL_SITE_PDF_PRIMARY_TEXT_X_UQN_GAZETTE_API_PRIMARY_DECREE_CONFIRMED_"
               "X_QANOONSA_SECONDARY_FULL_TEXT_CROSS_VERIFIED_NUMERAL_STYLE_ONLY_DIFFERENCE_"
               "BOE_LAWID_NOT_FOUND")

GOV_NOTE = ("Arabic governs. Decision number/date (قرار وزير التجارة رقم (098)، 18/5/1446هـ / 20 Nov "
            "2024G) independently confirmed by TWO PRIMARY sources: SASO's own official site (the "
            "administering/issuing authority, hosting the full text plus a linked PDF labelled 'أصل "
            "الوثيقة') and the Umm al-Qura Gazette's own API (uqn.gov.sa/api/article/.../json, "
            "fetched directly, quoting the ministerial decision's preamble verbatim) -- not merely "
            "search-engine indexed. Full 23-article text cross-verified against qanoonsa.com "
            "(SECONDARY); word-for-word identical except a cosmetic numeral-script difference in "
            "enumerated sub-clauses (official PDF: Western digits + period; qanoonsa.com, adopted "
            "here for corpus consistency: Eastern Arabic-Indic digits + dash) -- content/count/order "
            "identical across all sources -> TIER_1. Issued under Article 23 of the base Standards "
            "and Quality Law (Royal Decree M/36, 29/1/1446H, track_id: standards_quality, "
            "law_component: 'law'; this track's law_component is 'regulation'). No predecessor "
            "regulation superseded (this is the first Implementing Regulation under the base law). "
            "laws.boe.gov.sa has NO dedicated lawId page for this Implementing Regulation (search "
            "results surface only the base law's shared Id); live access connection-reset, NOT "
            "circumvented. 23 articles, ALL اصلية, 7 أبواب, no confirmed amendments (checked "
            "2026-07-24). See verification_methodology_note and known_unresolved_discrepancies in "
            "the source artifact before relying on this track's text or provenance.")

SRC_AUTH = ("Decision of the Minister of Commerce (Chairman of SASO's Board) No. (098), 18/5/1446H "
            "(20 Nov 2024G), adopted by SASO Board Resolution 02/203/2024 (203rd meeting, "
            "15/11/2024G), published Umm al-Qura Gazette Issue 5058 (29/11/2024G). Full text "
            "PRIMARY from SASO's own official site (administering authority) and its linked "
            "'أصل الوثيقة' PDF; decision identity independently confirmed by the Umm al-Qura "
            "Gazette's own API (fetched directly); cross-verified against qanoonsa.com (SECONDARY, "
            "content-identical, cosmetic numeral-style difference only) -> TIER_1")

SRC_AUTH_AR = ("قرار وزير التجارة رئيس مجلس إدارة الهيئة رقم (098) وتاريخ 18/5/1446هـ (20 نوفمبر "
               "2024م)، اعتمده مجلس إدارة الهيئة بقراره (02/203/2024) في اجتماعه رقم (203) وتاريخ "
               "15/11/2024م، ونُشر في جريدة أم القرى العدد (5058) بتاريخ 29/11/2024م. النص الكامل "
               "أساسي من موقع الهيئة السعودية للمواصفات والمقاييس والجودة (SASO) الرسمي (الجهة "
               "المصدرة) وملفها الموصوف بـ\"أصل الوثيقة\"؛ هوية القرار مؤكدة استقلاليا من واجهة "
               "برمجة تطبيقات جريدة أم القرى الرسمية (جُلبت مباشرة)؛ متقاطع مع qanoonsa.com (ثانوي، "
               "مطابق مضمونا، فارق شكلي في رسم الأرقام فقط) -- TIER_1")


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
        top_status = STATUS_UNCHANGED
        ver.append({"law_key": "standards_quality_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "STANDARDS_QUALITY_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "standards-quality-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "standards_quality_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام المواصفات والجودة"
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
    json.dump({"law_key": "standards_quality_regulation",
               "layer": "STANDARDS_QUALITY_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-standards-quality-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (23 مادة؛ جميعها أصلية)",
               "title_en": ("Implementing Regulation of the Standards and Quality Law — Arabic "
                            "LLM-ready layer (23 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 23], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Standards and Quality Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
