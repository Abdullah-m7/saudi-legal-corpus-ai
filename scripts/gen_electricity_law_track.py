#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Arabian Electricity Law track (نظام الكهرباء, Royal Decree
M/44, 16/5/1442H -- the CURRENTLY IN-FORCE Electricity Law, which superseded the
older M/56 (20/10/1426H) Electricity Law).

WHICH VERSION IS IN FORCE, AND HOW CONFIRMED -- there are two Electricity Laws in
circulation: the older Royal Decree M/56 (20/10/1426H) and the newer Royal Decree
M/44 (16/5/1442H). This track ingests the NEWER (M/44) law, confirmed to be the
one currently in force via four independent, cross-checked signals: (1) Article 23
of this very Law explicitly repeals/replaces the M/56 law BY NAME ("يحل النظام محل
نظام الكهرباء الصادر بالمرسوم الملكي رقم (م/56) وتاريخ 20/10/1426هـ، وتعديلاته،
ويلغي ما يتعارض معه من أحكام") -- a named repeal-and-replace clause, not a generic
conflict-only clause; (2) laws.boe.gov.sa's current listing carries M/44 under
lawId b3060214-c11a-4709-b191-aca700cbcc58 while the older M/56 has a separate,
historical lawId 73fd9170-ee6a-4380-8181-a9a700f29b65; (3) the regulator itself
(Saudi Electricity Regulatory Authority, SERA, sera.gov.sa) and its 2025 decisions
still cite the M/44 law; (4) nezams.com lists the law's status as "ساري" (in force)
with "لم يجرى عليه تعديل" (no amendments). See the source artifact's
verification_methodology_note and known_unresolved_discrepancies for the full
account and the honest status of the older M/56 law.

VERIFICATION TIER -- TIER_3. laws.boe.gov.sa (this corpus's usual PRIMARY source)
was checked FIRST per standard methodology but is unreachable this pass (curl:
Connection reset by peer during TLS; WebFetch: HTTP 503) -- matching the pattern
this corpus's food_regulation and health_system_regulation tracks documented for
the same period. Wayback Machine (web.archive.org) is blocked by this session's
egress policy and was NOT circumvented. The full verbatim text of all 23 articles
was therefore extracted this pass from ONE full-text secondary aggregator,
nezams.com (a clean born-digital HTML page, HTTP 200 -- NOT a scanned/OCR PDF, so
there are NO systematic extraction/ligature defects of the kind the food_regulation
track had to correct). Every governing metadata fact (decree number/date, Council
of Ministers Resolution 262, Shura Resolution 9/47, publication date 24/5/1442H,
in-force status, 23-article count, 9-chapter structure, and the named M/56 repeal
clause) is cross-verified against multiple independent sources (WebSearch results
from laws.boe.gov.sa and Umm Al-Qura, Lexis Middle East, SERA's own site, and
qanoonsa.com for the related implementing-regulation ecosystem). A follow-up
re-verification of the verbatim text against laws.boe.gov.sa is recommended once
that portal is reachable.

23 articles across 9 chapters; all 23 اصلية (original/unamended -- the Law has had
NO amendments); 0 معدلة, 0 ملغاة, 0 مضافة. Diacritics (tashkeel) and decorative
kashida are stripped uniformly for consistency with this corpus's other BOE-family
tracks (the legitimate Hijri marker "هـ" and the 5th-letter bullet "هـ-" are
preserved). Two disclosed source-rendering quirks (concatenated lettered sub-items
in Articles 4 and 18, as rendered by nezams.com) are preserved verbatim, not
silently re-spaced. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "electricity", "law", "official_source",
                   "electricity_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "electricity", "law", "verified")
RECORDS = os.path.join(OUT_VER, "electricity_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "electricity_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "electricity_arabic_legal_llm",
                        "electricity_law_legal_llm_001_023.json")

LAW_ID = "sa-electricity-law-m44-1442"
LAW_AR = "نظام الكهرباء"
STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
KEY_RE = r"electricity_law_art_(\d{3})(?:_mukarrar(\d*))?$"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة اللوائح أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم الهيئة النظام المرخص الكهرباء الكهربائية").split())


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
        text_complete = a.get("text_complete", True)
        ver.append({"law_key": "electricity", "law_component": "law",
                    "language": "ar",
                    "record_layer": "ELECTRICITY_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; this is the CURRENTLY IN-FORCE "
                                              "Electricity Law (Royal Decree M/44, 16/5/1442H), "
                                              "which by its own Article 23 repealed and replaced "
                                              "the older M/56 (20/10/1426H) Electricity Law. "
                                              "laws.boe.gov.sa was checked FIRST per standard "
                                              "methodology but is unreachable this pass (connection "
                                              "reset / HTTP 503) and Wayback is egress-blocked; the "
                                              "verbatim text of all 23 articles was extracted from "
                                              "nezams.com (a single clean born-digital HTML "
                                              "aggregator page, no scan/OCR/ligature defects). All "
                                              "governing metadata (decree number/date, CoM Res 262, "
                                              "Shura Res 9/47, publication 24/5/1442H, in-force "
                                              "status, 23-article/9-chapter structure, named M/56 "
                                              "repeal clause) is cross-verified against multiple "
                                              "independent sources. TIER_3. See "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the source artifact "
                                              "before relying on this track -- in particular the "
                                              "recommended re-verification of verbatim text against "
                                              "laws.boe.gov.sa, and the disclosed concatenated "
                                              "sub-items in Articles 4 and 18."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_mukarrar, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar") or "",
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_added": is_added, "is_amended": is_amended,
                    "text_complete": text_complete,
                    "record_id": "electricity-law-llm-art-%03d" % idx,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "electricity/law/articles/%s" % key,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "%s من نظام الكهرباء" % a["number_label_ar"]],
                    "text_status": a["status"],
                    "source_trust": {"source_authority": ("Royal Decree No. (M/44), 16/5/1442H "
                                                          "(Council of Ministers Resolution 262, "
                                                          "14/5/1442H; Shura Resolution 9/47, "
                                                          "1/5/1442H; Umm Al-Qura 24/5/1442H) — the "
                                                          "currently in-force Electricity Law, which "
                                                          "by Article 23 repealed/replaced the older "
                                                          "M/56 (20/10/1426H) Law. Verbatim text from "
                                                          "nezams.com (single full-text aggregator; "
                                                          "laws.boe.gov.sa unreachable this pass, "
                                                          "Wayback egress-blocked), all metadata "
                                                          "cross-verified against multiple "
                                                          "independent sources. TIER_3."),
                                     "source_authority_ar": "المرسوم الملكي رقم (م/44) وتاريخ 16/5/1442هـ (قرار مجلس الوزراء 262 وتاريخ 14/5/1442هـ؛ قرار مجلس الشورى 9/47 وتاريخ 1/5/1442هـ؛ نشر أم القرى 24/5/1442هـ) — نظام الكهرباء النافذ حالياً، الذي حلّ بموجب مادته الثالثة والعشرين محل نظام الكهرباء الأقدم (م/56، 20/10/1426هـ). النص الحرفي من nezams.com (مصدر نص كامل واحد؛ laws.boe.gov.sa غير قابل للوصول هذه الجولة، وWayback محظور)، وجميع البيانات الوصفية متقاطعة عبر مصادر مستقلة متعددة. المستوى TIER_3.",
                                     "source_status": a["status"].lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "electricity",
               "layer": "ELECTRICITY_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver),
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "council_of_ministers_decision": src.get("council_of_ministers_decision"),
               "shura_council_decision": src.get("shura_council_decision"),
               "gazette_publication_hijri": src.get("gazette_publication_hijri"),
               "legal_status_ar": src.get("legal_status_ar"),
               "supersedes_ar": src.get("supersedes_ar"),
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "amendment_history": src.get("amendment_history", []),
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-electricity-law-arabic-legal-llm-full",
               "law_id": LAW_ID, "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (23 مادة؛ 23 أصلية، 0 معدلة، 0 مضافة، 0 ملغاة)",
               "title_en": ("The Saudi Arabian Electricity Law (Royal Decree M/44, 16/5/1442H) — "
                            "Arabic LLM-ready layer (23 records: 23 original, 0 amended, 0 added, "
                            "0 repealed)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 23], "text_status": STATUS_UNCHANGED,
               "consolidated_amended_law": src.get("consolidated_amended_law", False),
               "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Electricity Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
