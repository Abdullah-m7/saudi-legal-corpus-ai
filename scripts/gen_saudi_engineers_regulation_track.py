#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Law of the Saudi Council of
Engineers track (اللائحة التنفيذية لنظام الهيئة السعودية للمهندسين,
1445H/2024G consolidated edition, issued by the Council's own General
Assembly under the base law's Article 5(2)/7(3) rule-making delegation).

VERIFICATION TIER -- see sources/saudi_engineers_regulation/law/
official_source/saudi_engineers_regulation_official_source.json's
verification_methodology_note for the full account. Summary:

PRIMARY SOURCE: saudieng.sa/Admin/NPSCERules/sce-executive-regulations.pdf,
fetched via its single archived Wayback Machine snapshot (20250625074825,
25 Jun 2025) after a direct live fetch failed (TLS reset). The PDF's Arabic
text is stored in raw visual (right-to-left glyph-position) order without
correct Unicode logical ordering -- resolved via a from-scratch pdfplumber
word-level reconstruction (x/y bounding boxes, per-line descending-x sort,
per-word pre-normalization reversal, then NFKC) documented in full in the
source artifact, and independently cross-checked against poppler's
'pdftotext -layout' extraction of the same archived file: both agree,
word-for-word, on the full 32-article text after whitespace/tatweel
normalization.

STRUCTURE: 32 articles, 6 named فصول (no أبواب): الفصل الأول: التعريفات
(م1); الفصل الثاني: أجهزة الهيئة (م2-م9, five lettered subsections)؛ الفصل
الثالث: انتخابات مجلس إدارة الهيئة (م10-م25, by far the longest chapter)؛
الفصل الرابع: التسجيل والعضوية (م26-م27)؛ الفصل الخامس: الأحكام المالية
(م28-م29)؛ الفصل السادس: أحكام ختامية (م30-م32).

LEGAL STATUS: this Council-internal instrument carries no BOE-style
per-article amendment changelog. Only ONE archived capture of this exact
file was found; no earlier edition was located to diff against. All 32
articles are therefore recorded as 'اصلية' -- verified-current text of the
single consolidated 1445H/2024G edition, NOT an affirmative claim of
identity with any unverified earlier internal edition. A prior-research
claim that this edition was approved at the "20th Ordinary General Assembly
meeting, 2024" could NOT be independently confirmed this pass (the PDF's
own cover names only the year, no meeting number) -- flagged as an honest
unconfirmed attribution, not repeated as fact.

DISAMBIGUATION: this track is DISTINCT from the separate
engineering_practice_regulation track (اللائحة التنفيذية لنظام مزاولة المهن
الهندسية, issued by MINISTERIAL Resolution 4400942200/4, 26/5/1445H,
published in Umm Al-Qura Gazette No. 5013 -- a government regulation
implementing individual-engineer licensing/discipline under the SEPARATE
practice law, Royal Decree م/36 dated 19/4/1438H). This pass independently
fetched and read that sibling instrument's own PDF (saudieng.sa's
Admin/NPSCERules/67.pdf) specifically to confirm the two do not overlap.

Several confirmed source-level artifacts (an internally-inconsistent
hamza-under-alef spelling style, three isolated one-off misspellings, and a
stray duplicate-numeral artifact in Article 29) are preserved VERBATIM --
see known_unresolved_discrepancies in the source artifact. No legal text is
altered beyond whitespace/decorative-tatweel normalization. Arabic governs;
no translation/paraphrase/interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "saudi_engineers_regulation", "law", "official_source",
                   "saudi_engineers_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "saudi_engineers_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "saudi_engineers_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "saudi_engineers_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "saudi_engineers_regulation_arabic_legal_llm",
                        "saudi_engineers_regulation_legal_llm_001_032.json")

LAW_ID = "sa-saudi-engineers-regulation-1445"
LAW_AR = "اللائحة التنفيذية لنظام الهيئة السعودية للمهندسين"
TOP_STATUS = ("SAUDIENG_SA_WAYBACK_20250625_PRIMARY_X_PDFTOTEXT_POPPLER_AND_PDFPLUMBER_"
              "PDFMINER_DUAL_INDEPENDENT_EXTRACTION_CROSSCHECK_LIVE_FETCH_TLS_RESET")
KEY_RE = r"saudi_engineers_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك الهيئة المجلس الرئيس الأعضاء أعضاء").split())


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
        ver.append({"law_key": "saudi_engineers_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "SAUDI_ENGINEERS_REGULATION_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this track rests on a single "
                                              "archived Wayback Machine snapshot (20250625074825) "
                                              "of the Council's own hosted PDF, independently "
                                              "cross-extracted via two structurally different "
                                              "PDF-parsing pipelines (poppler pdftotext and a "
                                              "from-scratch pdfplumber word-level bidi "
                                              "reconstruction) that agree word-for-word after "
                                              "normalization. This is a Council-internal General-"
                                              "Assembly-approved instrument with no BOE-style "
                                              "per-article amendment changelog; all 32 articles "
                                              "are 'اصلية' relative to this single verified current "
                                              "consolidated (1445H/2024G) text -- not an affirmative "
                                              "claim of identity with any earlier internal edition. "
                                              "See verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source "
                                              "artifact before relying on this track's text, "
                                              "including a confirmed stray duplicate-numeral "
                                              "artifact preserved verbatim in Article 29 and three "
                                              "isolated confirmed spelling artifacts elsewhere."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "record_id": "saudi-engineers-regulation-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "saudi_engineers_regulation/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام الهيئة السعودية "
                                          "للمهندسين" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Implementing Regulation of the Law of "
                                                          "the Saudi Council of Engineers, 1445H/"
                                                          "2024G edition — saudieng.sa via a single "
                                                          "Wayback Machine snapshot (25 Jun 2025), "
                                                          "cross-extracted by two independent PDF "
                                                          "parsing pipelines; live saudieng.sa "
                                                          "fetch failed (TLS reset) this pass"),
                                     "source_authority_ar": "اللائحة التنفيذية لنظام الهيئة السعودية للمهندسين، إصدار 1445هـ/2024م — لقطة أرشيفية واحدة عبر Wayback Machine (25 يونيو 2025)، مطابقة عبر منظومتي استخراج مستقلتين",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "saudi_engineers_regulation",
               "layer": "SAUDI_ENGINEERS_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-saudi-engineers-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (32 مادة؛ كلها أصلية)",
               "title_en": "Implementing Regulation of the Law of the Saudi Council of Engineers "
                           "— Arabic LLM-ready layer (32 records, all اصلية)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 32], "text_status": TOP_STATUS,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Saudi Engineers Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
