#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Implementing Regulation of the Payment Systems and Services Law
track (اللائحة التنفيذية لنظام المدفوعات وخدماتها، تعميم البنك المركزي السعودي
رقم 44093096 وتاريخ 24/11/1444هـ الموافق 13/6/2023م، صادرة استناداً إلى نظام
المدفوعات وخدماتها الصادر بالمرسوم الملكي رقم م/26 وتاريخ 22/3/1443هـ).

ARTICLE COUNT CORRECTION (the central finding this track's build pass turned
up): a prior research pass estimated "150+ articles" for this Regulation,
based on partial browsing of rulebook.sama.gov.sa's paginated HTML view
(which does not expose a running total, and had only been checked through
Part 4 / Chapter 1). This build fetched and fully parsed the Regulation's own
official Arabic PDF (74 pages, hosted directly on the SAMA Rulebook site's own
file store, sites/default/files/ar_net_file_store/SAMA_AR_1430_VER1.pdf --
same internal node/filename pair, "1430", as the equivalent English PDF
linked from the paired English page) and found the TRUE count is 133
articles across 12 أبواب (Part 4: 4 فصول; Part 5: 2 فصول; Part 6: 3 فصول;
Part 9: 4 فصول -- 13 فصول total). This is independently confirmed two ways:
(1) two different PDF text-extraction engines (pdftotext --layout and
PyMuPDF/fitz) agree on exactly 133 sequential, non-duplicated article
headings; (2) Article 133 (the last) reads verbatim "تسري هذه اللائحة من
تاريخ إصدارها" -- the standard closing "entry into force" clause that only
ever appears as a law/regulation's final article. See known_unresolved_
discrepancies key payment_systems_regulation_article_count_correction_133_vs_150plus
in the source artifact.

VERIFICATION TIER -- see sources/payment_systems_regulation/law/
official_source/payment_systems_regulation_official_source.json's
verification_methodology_note for the complete accounting. Summary:

SOURCE: the Regulation's own official Arabic PDF, hosted directly on
rulebook.sama.gov.sa (SAMA's own regulator "Rulebook" subdomain -- not a
third-party aggregator), fetched directly (HTTP 200). The direct SAMA DocLib
path (sama.gov.sa) remained unreachable (WAF/error page), consistent with a
prior research pass's finding; the Rulebook site's own PDF export was used
instead, and its cover page (line 1: "اللائحة التنفيذية لنظام المدفوعات
وخدماتها -- الصادرة بتاريخ 24/11/1444هـ الموافق 13/6/2023م") independently
matches the previously-confirmed SAMA Circular No. 44093096 date exactly.

TEXT-LAYER CORRUPTION FOUND AND CORRECTED: this specific PDF's text layer has
a confirmed, systematic character-transposition defect distinct from (and
more extensive than) the one documented in the Civil Service HR Regulation
track: whenever "ا" (alef) is immediately followed by one of {آ, أ, إ, م}
immediately followed by "ل" (lam) within a word, the two are extracted in
swapped order (e.g. "المدفوعات" -> "امللدفوعات"/"املدفوعات", 943 occurrences,
zero correctly-ordered counter-examples found across an exhaustive whole-
document word-frequency scan for each of the four trigger letters
individually). Unlike the Civil Service HR Regulation track (which declined
to auto-correct a similar-looking defect because real counter-example words
existed), this track's defect was verified to have ZERO exceptions across the
full document before a general regex correction was applied -- a materially
stronger evidentiary bar than "no counter-example found in a sample". Two
narrower, word-dictionary-based corrections (not blind regexes, since the
surface patterns collide with genuinely-correct words) were also applied:
the "لل"+"ا" ligature family (اللائحة/اللازمة/اللاحقة, extracted as
الالئحة/الالزمة/الالحقة, 17 confirmed tokens) and the "لـ"+ميم-initial-noun
family (لمقدم/لمستخدم/لمدة, extracted as ملقدم/ملستخدم/ملدة, 17 confirmed
tokens, explicitly excluding genuinely-correct لookalikes ملغى/مليون/ملتزمة
after per-word context review). See known_unresolved_discrepancies keys
payment_systems_regulation_alef_hamza_meem_lam_transposition_fix and
payment_systems_regulation_laa_ligature_and_lam_meem_prefix_dictionaries.

SINGLE SOURCE, NOT CROSS-CHECKED AGAINST A SECOND INDEPENDENT ARABIC SOURCE
THIS PASS: laws.boe.gov.sa / nezams.com / qanoonsa.com / web.archive.org were
not reachable or not checked for this specific Regulation this pass (time
constraints). This is disclosed, not silently assumed away -- see
payment_systems_regulation_single_source_no_independent_cross_check.

133 records, all اصلية (0 معدلة / 0 ملغاة / 0 مضافة): no evidence of any
amendment to this Regulation's own text was found since its 24/11/1444H/2023G
issuance. Article 131 explicitly repeals and replaces the prior "Rules for
Regulating Payment Service Providers" (5/6/1441H / 30 Jan 2020G) -- confirmed
directly from the Regulation's own extracted text, matching a prior research
pass's finding. 12 أبواب, with الباب الرابع (4 فصول), الباب الخامس (2 فصول),
الباب السادس (3 فصول), and الباب التاسع (4 فصول) further subdivided.

No legal text is altered beyond the disclosed text-layer corrections above,
decorative-tatweel/tashkeel stripping, and digit-glyph normalization, matching
this corpus's established convention. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "payment_systems_regulation", "law", "official_source",
                   "payment_systems_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "payment_systems_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "payment_systems_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "payment_systems_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "payment_systems_regulation_arabic_legal_llm",
                        "payment_systems_regulation_legal_llm_001_133.json")

LAW_ID = "sa-payment-systems-regulation-1444"
LAW_AR = "اللائحة التنفيذية لنظام المدفوعات وخدماتها"
KEY_RE = r"payment_systems_regulation_art_(\d{3})$"
TIER = "SAMA_RULEBOOK_PDF_SINGLE_SOURCE_LIGATURE_TRANSPOSITION_CORRECTED"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي البنك المركزي مقدم خدمات المدفوعات").split())


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
    return int(m.group(1))


GOV_NOTE = ("Arabic governs. All 133 articles rest on a single primary source (the Regulation's own "
            "official Arabic PDF, hosted directly on rulebook.sama.gov.sa -- SAMA's own regulator "
            "\"Rulebook\" subdomain), with a confirmed, zero-exception, whole-document-verified "
            "character-transposition defect in that PDF's text layer corrected (see "
            "verification_methodology_note and known_unresolved_discrepancies in the source "
            "artifact for the full accounting, including a corrected article-count finding of 133 "
            "vs. a prior estimate of \"150+\", and the disclosed absence of a second independent "
            "source cross-check this pass). No amendment to this Regulation's own text was found "
            "since its 24/11/1444H/2023G issuance; it explicitly repeals and replaces the prior "
            "2020 (5/6/1441H) payment-services rules in its own Article 131.")

SRC_AUTH = ("Implementing Regulation of the Payment Systems and Services Law, SAMA Circular No. "
            "44093096, dated 24/11/1444H (13 June 2023G), issued under the Payment Systems and "
            "Services Law (Royal Decree M/26, 22/3/1443H). Text source: rulebook.sama.gov.sa's own "
            "official Arabic PDF (single primary source, whole-document character-transposition "
            "defect corrected, not independently cross-checked against a second Arabic source this "
            "pass).")
SRC_AUTH_AR = ("اللائحة التنفيذية لنظام المدفوعات وخدماتها، تعميم البنك المركزي السعودي رقم "
               "(44093096) وتاريخ 24/11/1444هـ الموافق 13/6/2023م، صادرة استناداً إلى نظام المدفوعات "
               "وخدماتها (المرسوم الملكي رقم م/26 وتاريخ 22/3/1443هـ). مصدر النص: ملف PDF الرسمي "
               "العربي على rulebook.sama.gov.sa (مصدر أساسي منفرد، صُحح فيه عطب ترتيب حروف مؤكَّد "
               "بلا استثناء عبر الوثيقة الكاملة، ولم يُقاطَع مع مصدر عربي ثانٍ مستقل هذه الجولة).")


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = _sort_key(key)
        ls = a.get("legal_status_ar")
        text = a["text"]
        suffix = key.replace("payment_systems_regulation_art_", "")
        ver.append({"law_key": "payment_systems_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "PAYMENT_SYSTEMS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "original_text": a.get("original_text"),
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة",
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": a["status"],
                    "governing_source_note": GOV_NOTE,
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "payment-systems-regulation-llm-art-%s" % suffix,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "original_text": a.get("original_text"),
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "payment_systems_regulation/law/articles/%s" % suffix,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من اللائحة التنفيذية لنظام المدفوعات وخدماتها"
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
    json.dump({"law_key": "payment_systems_regulation",
               "layer": "PAYMENT_SYSTEMS_REGULATION_ARABIC_VERIFIED_TEXT",
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
    json.dump({"layer_id": "sa-payment-systems-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (133 مادة، جميعها أصلية)",
               "title_en": ("Implementing Regulation of the Payment Systems and Services Law — "
                            "Arabic LLM-ready layer (133 records, all original)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 133], "text_status": TIER,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Payment Systems Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
